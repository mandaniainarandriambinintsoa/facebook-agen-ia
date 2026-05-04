#!/usr/bin/env python
"""
Force-deploy Coolify apps via API.

Usage:
    python scripts/coolify_deploy.py --env prod --app backend
    python scripts/coolify_deploy.py --env prod --app both
    python scripts/coolify_deploy.py --env stagging --app frontend

Setup une seule fois :
    1. Coolify -> Profile (ou Keys & Tokens) -> API Tokens -> New token
       Name: "claude-deploy", Permissions: minimum "deploy:write" si dispo
       sinon "all"
    2. Copier le token et l'ajouter dans .env a la racine du projet :
            COOLIFY_API_TOKEN=ckp_xxxxxxxxxxxxx
       (.env est deja gitignored, donc safe)

    Alternativement, exporter la variable dans le shell :
        PowerShell : $env:COOLIFY_API_TOKEN="ckp_..."
        Bash       : export COOLIFY_API_TOKEN="ckp_..."

Le script utilise le mapping UUIDs ci-dessous (visible dans l'URL Coolify
quand on clique sur une app : /application/<UUID>/...).
Si on renomme/recrée des apps, mettre a jour APPS ci-dessous.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable

# --- Configuration -----------------------------------------------------------

COOLIFY_BASE_URL = "https://coolify.manda-ia.com"

APPS: dict[str, dict[str, str]] = {
    "prod": {
        "backend": "brwbk3cq7epdjm4nhmha6k5e",
        "frontend": "rcnp2e4re8emv183pktytnge",
    },
    "stagging": {
        "backend": "nv8i0vzksm75m9vplj42mn1k",
        "frontend": "bqk6o4eerfk82jvrnwun8jxq",
    },
}


# --- Helpers -----------------------------------------------------------------

def _load_dotenv_if_present() -> None:
    """Charge .env a la racine du projet si present, sans dependance externe."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        # Strip optional surrounding quotes
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _http_get(url: str, token: str, timeout: int = 30) -> tuple[int, dict | str]:
    """GET request via urllib (stdlib, pas de dependance httpx)."""
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body
    except urllib.error.URLError as e:
        raise RuntimeError(f"Reseau injoignable: {e.reason}") from e


def _resolve_apps(env: str, target: str) -> list[tuple[str, str]]:
    """Retourne la liste [(label, uuid), ...] a deployer."""
    if env not in APPS:
        raise SystemExit(f"Env inconnu: {env}. Choix: {list(APPS)}")
    available = APPS[env]
    if target == "both":
        return [(name, uuid) for name, uuid in available.items()]
    if target not in available:
        raise SystemExit(f"App inconnue pour env={env}: {target}. Choix: {list(available)}")
    return [(target, available[target])]


def trigger_deploy(uuid: str, token: str, force: bool = True) -> tuple[int, dict | str]:
    """Trigger un deploy via l'API Coolify.

    Endpoint correct pour Coolify v4 : /api/v1/deploy?uuid=...&force=true
    (PAS /api/v1/applications/{uuid}/deploy qui renvoie 404).
    """
    params = {"uuid": uuid, "force": "true" if force else "false"}
    qs = urllib.parse.urlencode(params)
    url = f"{COOLIFY_BASE_URL}/api/v1/deploy?{qs}"
    return _http_get(url, token)


# --- Main --------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Force-deploy Coolify apps for facebook-agent-ia.",
    )
    parser.add_argument(
        "--env",
        choices=["prod", "stagging"],
        required=True,
        help="Environnement Coolify cible.",
    )
    parser.add_argument(
        "--app",
        choices=["backend", "frontend", "both"],
        default="backend",
        help="App(s) a deployer (defaut: backend).",
    )
    parser.add_argument(
        "--no-force",
        action="store_true",
        help="Desactive le flag force (deploy 'redeploy' au lieu de 'force deploy').",
    )
    args = parser.parse_args(argv)

    _load_dotenv_if_present()

    token = os.environ.get("COOLIFY_API_TOKEN")
    if not token:
        print(
            "ERREUR: env var COOLIFY_API_TOKEN absente.\n"
            "Definir via .env ou shell. Voir docstring du script pour details.",
            file=sys.stderr,
        )
        return 2

    targets = _resolve_apps(args.env, args.app)
    force = not args.no_force

    print(f"Coolify: {COOLIFY_BASE_URL}")
    print(f"Env: {args.env} | Force deploy: {force}")
    print(f"Apps: {[name for name, _ in targets]}")
    print("-" * 60)

    exit_code = 0
    for label, uuid in targets:
        print(f"[{args.env}/{label}] uuid={uuid} -> trigger...")
        try:
            status, body = trigger_deploy(uuid, token, force=force)
        except Exception as e:
            print(f"  -> ERREUR exception: {e}", file=sys.stderr)
            exit_code = 1
            continue

        if 200 <= status < 300:
            preview = json.dumps(body, ensure_ascii=False)[:200] if isinstance(body, dict) else str(body)[:200]
            print(f"  -> OK status={status} body={preview}")
        else:
            preview = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
            print(
                f"  -> ECHEC status={status} body={preview[:300]}",
                file=sys.stderr,
            )
            exit_code = 1

    print("-" * 60)
    if exit_code == 0:
        print("Deploys declenches. Suivre la progression dans Coolify -> Deployments.")
    else:
        print("Au moins un deploy a echoue.", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
