"""Cron quotidien : envoie les emails J0/J1/J3/J5/J7/J14/J30 selon l'age des tenants.

Usage manuel :
    python -m app.jobs.onboarding_emails

A lancer 1x/jour via Coolify cron (ou cron systeme). Idempotent : la table
sent_onboarding_emails empeche les doublons si le job est lance plusieurs fois.

Logique :
1. Pour chaque tenant actif :
   age = today - tenant.created_at (en jours)
2. Si age in {0, 1, 3, 5, 7, 14, 30} :
   - check qu'on n'a pas deja envoye cet email_key pour ce tenant
   - check les conditions metier (J5: photos manquantes, J14: paye, etc.)
   - envoie via Brevo
   - INSERT dans sent_onboarding_emails

Conditions par email (cf docs/onboarding-emails/README.md) :
- J0  : aucune
- J1  : aucune
- J3  : aucune
- J5  : nb_produits > 0 ET nb_avec_photo < nb_produits
- J7  : tenant pas encore en paye (statut "trial")
- J14 : tenant paye (post-essai)
- J30 : tenant paye

Pour l'instant, on n'a pas de table 'subscription' en DB, donc J14/J30 sont
desactives par defaut tant que la facturation n'est pas branchee. Sinon ils
seraient envoyes a tous les utilisateurs y compris ceux qui n'ont pas paye.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ajouter racine au path quand lance via `python -m app.jobs.onboarding_emails`
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402
from loguru import logger  # noqa: E402

from app.config import settings  # noqa: E402
from app.db.database import init_db, AsyncSessionLocal, close_db  # noqa: E402
from app.db.models import Tenant, SentOnboardingEmail, Product  # noqa: E402
from app.services.brevo import send_template_email, BrevoError  # noqa: E402


# Map age (en jours) -> email_key
AGE_TO_KEY: dict[int, str] = {
    0: "j0",
    1: "j1",
    3: "j3",
    5: "j5",
    7: "j7",
    14: "j14",
    30: "j30",
}

# Emails desactives tant que la facturation n'est pas branchee (cf docstring)
PAYMENT_DEPENDENT_KEYS = {"j14", "j30"}


def _extract_prenom(email: str, page_name: str) -> str:
    """Devine un prenom a partir de l'email ou du nom de page."""
    # 1. partie locale de l'email avant @, en title case si format clean
    local = email.split("@")[0]
    if "." in local:
        return local.split(".")[0].title()
    if "_" in local:
        return local.split("_")[0].title()
    # 2. fallback : 1er mot du nom de page
    return page_name.split()[0] if page_name else "tu"


async def _build_params(db: AsyncSession, tenant: Tenant) -> dict:
    """Construit les variables {{params.X}} pour le template Brevo."""
    prenom = _extract_prenom(tenant.owner_email, tenant.page_name)
    dashboard = settings.dashboard_base_url.rstrip("/")

    # Stats produits (utiles pour J5)
    products = (await db.execute(
        select(Product).where(Product.tenant_id == tenant.id)
    )).scalars().all()
    nb_produits = len(products)
    nb_avec_photo = sum(1 for p in products if getattr(p, "image_url", None))

    # Note : nb_messages_*, nb_prospects_chauds, nb_commandes peuvent etre
    # calcules avec count_messages_since/etc. de crud.py si les emails J1/J7
    # veulent les inclure. Pour l'instant valeurs neutres.

    return {
        "prenom": prenom,
        "nom_page": tenant.page_name,
        "lien_dashboard": dashboard,
        "lien_upload_catalog": f"{dashboard}/catalog",
        "lien_message_setup": f"{dashboard}/config",
        "lien_subscribe": f"{dashboard}/billing",
        "lien_tuto_photos": "https://valina-bot.com/tuto/photos-catalogue",
        "lien_unsubscribe": f"{dashboard}/unsubscribe?tenant={tenant.id}",
        "nb_messages_hier": 0,
        "nb_messages_total": 0,
        "nb_prospects_chauds": 0,
        "nb_commandes": 0,
        "heures_economisees": 0,
        "nb_produits": nb_produits,
        "nb_avec_photo": nb_avec_photo,
    }


async def _should_send(db: AsyncSession, tenant: Tenant, email_key: str) -> bool:
    """Verifie les conditions metier specifiques a chaque email."""
    if email_key in PAYMENT_DEPENDENT_KEYS:
        # TODO : reactiver quand la facturation est branchee
        logger.debug(f"[skip] {email_key} desactive (facturation pas encore branchee)")
        return False

    if email_key == "j5":
        nb_total = (await db.execute(
            select(Product).where(Product.tenant_id == tenant.id)
        )).scalars().all()
        nb_produits = len(nb_total)
        nb_avec_photo = sum(1 for p in nb_total if getattr(p, "image_url", None))
        if nb_produits == 0:
            logger.debug(f"[skip j5 {tenant.id}] aucun produit charge")
            return False
        if nb_avec_photo >= nb_produits:
            logger.debug(f"[skip j5 {tenant.id}] toutes les photos deja la")
            return False

    return True


async def _already_sent(db: AsyncSession, tenant_id, email_key: str) -> bool:
    row = (await db.execute(
        select(SentOnboardingEmail).where(
            SentOnboardingEmail.tenant_id == tenant_id,
            SentOnboardingEmail.email_key == email_key,
        )
    )).scalar_one_or_none()
    return row is not None


async def _record_sent(db: AsyncSession, tenant_id, email_key: str, msg_id: str | None) -> None:
    db.add(SentOnboardingEmail(
        tenant_id=tenant_id,
        email_key=email_key,
        sent_at=datetime.now(timezone.utc),
        brevo_message_id=msg_id or None,
    ))
    await db.commit()


def _is_real_email(email: str) -> bool:
    """Skip le fallback `{user_id}@facebook.com` (pas envoyable)."""
    return bool(email) and not email.endswith("@facebook.com")


async def run_once() -> dict[str, int]:
    """Execute le job une fois. Retourne stats {email_key: nb_envoyes}."""
    if not settings.brevo_api_key:
        logger.warning("[onboarding] BREVO_API_KEY non defini, abort")
        return {}

    init_db()
    if AsyncSessionLocal is None:
        logger.error("[onboarding] DB non initialisee, abort")
        return {}

    stats: dict[str, int] = {k: 0 for k in AGE_TO_KEY.values()}
    skipped = 0
    failed = 0

    today = datetime.now(timezone.utc).date()

    async with AsyncSessionLocal() as db:
        tenants = (await db.execute(
            select(Tenant).where(Tenant.is_active == True)  # noqa: E712
        )).scalars().all()

        logger.info(f"[onboarding] {len(tenants)} tenants actifs a evaluer")

        for tenant in tenants:
            if not _is_real_email(tenant.owner_email):
                skipped += 1
                continue

            age_days = (today - tenant.created_at.date()).days
            email_key = AGE_TO_KEY.get(age_days)
            if email_key is None:
                continue  # pas un jour J0/J1/J3/J5/J7/J14/J30

            if await _already_sent(db, tenant.id, email_key):
                continue

            if not await _should_send(db, tenant, email_key):
                skipped += 1
                continue

            try:
                params = await _build_params(db, tenant)
                msg_id = await send_template_email(
                    email_key=email_key,
                    to_email=tenant.owner_email,
                    to_name=tenant.page_name,
                    params=params,
                )
                await _record_sent(db, tenant.id, email_key, msg_id)
                stats[email_key] += 1
                logger.info(f"[onboarding] {email_key} -> {tenant.owner_email} (tenant {tenant.id})")
            except BrevoError as e:
                failed += 1
                logger.error(f"[onboarding] {email_key} {tenant.id} BrevoError: {e}")
            except Exception as e:
                failed += 1
                logger.exception(f"[onboarding] {email_key} {tenant.id} unexpected: {e}")

    await close_db()

    total_sent = sum(stats.values())
    logger.info(f"[onboarding] DONE. envoyes={total_sent} skipped={skipped} failed={failed} detail={stats}")
    return stats


if __name__ == "__main__":
    asyncio.run(run_once())
