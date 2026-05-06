"""Sync les 7 templates HTML onboarding (J0-J30) vers Brevo.

Usage :
    python scripts/sync_brevo_templates.py

Ce script :
1. Lit docs/onboarding-emails/templates/*.html
2. Pour chaque fichier (j0.html -> j30.html) :
   - Si un template Brevo nomme "valina_onboarding_<key>" existe deja -> update
   - Sinon -> create
3. Met a jour app/services/brevo_templates.py avec le mapping {key: template_id}

Idempotent : peut etre relance autant de fois que necessaire apres edit des HTML.

Prerequis :
- BREVO_API_KEY defini dans .env
- Sender hello@valina-bot.com confirme dans Brevo
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ajouter la racine du projet au path (pour import app.*)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.brevo import (  # noqa: E402
    create_or_update_template,
    list_templates,
)
from app.services.brevo_templates import TEMPLATE_SUBJECTS  # noqa: E402


TEMPLATE_PREFIX = "valina_onboarding_"
TEMPLATES_DIR = ROOT / "docs" / "onboarding-emails" / "templates"
MAPPING_FILE = ROOT / "app" / "services" / "brevo_templates.py"

EMAIL_KEYS = ["j0", "j1", "j3", "j5", "j7", "j14", "j30"]


async def sync_all() -> dict[str, int]:
    """Sync tous les templates et retourne le mapping {key: template_id}."""
    print(f"[sync] Lecture des templates Brevo existants...")
    existing = await list_templates()
    existing_by_name = {t["name"]: t["id"] for t in existing}
    print(f"[sync] {len(existing)} templates Brevo existants au total")

    mapping: dict[str, int] = {}

    for key in EMAIL_KEYS:
        html_file = TEMPLATES_DIR / f"{key}.html"
        if not html_file.exists():
            print(f"[sync] !!! {html_file} introuvable, skip")
            continue

        html = html_file.read_text(encoding="utf-8")
        subject = TEMPLATE_SUBJECTS.get(key, f"Email {key}")
        name = f"{TEMPLATE_PREFIX}{key}"

        existing_id = existing_by_name.get(name)
        if existing_id:
            print(f"[sync] update template '{name}' (id={existing_id})")
            tid = await create_or_update_template(name, subject, html, template_id=existing_id)
        else:
            print(f"[sync] create template '{name}'")
            tid = await create_or_update_template(name, subject, html)

        mapping[key] = tid
        print(f"[sync]   -> {key} = {tid}")

    return mapping


def write_mapping_file(mapping: dict[str, int]) -> None:
    """Reecrit app/services/brevo_templates.py avec le mapping a jour."""
    subjects_repr = ",\n    ".join(
        f'"{k}": {repr(v)}' for k, v in TEMPLATE_SUBJECTS.items()
    )
    mapping_repr = ",\n    ".join(
        f'"{k}": {v}' for k, v in mapping.items()
    )

    content = f'''"""Mapping entre nos cles d'email (j0, j1, ...) et les template IDs Brevo.

Ce fichier est genere/mis a jour automatiquement par scripts/sync_brevo_templates.py
apres chaque sync. Ne pas editer a la main.
"""
from __future__ import annotations

# Cle = nom logique utilise par le job onboarding (correspond aux fichiers HTML)
# Valeur = ID retourne par l'API Brevo lors de la creation du template
TEMPLATE_IDS: dict[str, int] = {{
    {mapping_repr},
}}

# Subject lines par template (centralisees ici pour modifier sans toucher au HTML)
TEMPLATE_SUBJECTS: dict[str, str] = {{
    {subjects_repr},
}}


def get_template_id(email_key: str) -> int | None:
    """Retourne l'ID Brevo pour un email_key, ou None si pas encore sync."""
    return TEMPLATE_IDS.get(email_key)
'''
    MAPPING_FILE.write_text(content, encoding="utf-8")
    print(f"[sync] mapping ecrit dans {MAPPING_FILE.relative_to(ROOT)}")


async def main() -> None:
    if not TEMPLATES_DIR.exists():
        print(f"!!! Dossier introuvable : {TEMPLATES_DIR}")
        sys.exit(1)

    mapping = await sync_all()
    if not mapping:
        print("!!! Aucun template synchronise (HTML manquants ?)")
        sys.exit(1)

    write_mapping_file(mapping)
    print(f"\n[OK] {len(mapping)}/{len(EMAIL_KEYS)} templates sync.")
    print(f"     N'oublie pas de commit : git add docs/onboarding-emails/templates/ app/services/brevo_templates.py")


if __name__ == "__main__":
    asyncio.run(main())
