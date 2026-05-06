"""Mapping entre nos cles d'email (j0, j1, ...) et les template IDs Brevo.

Ce fichier est genere/mis a jour automatiquement par scripts/sync_brevo_templates.py
apres chaque sync. Ne pas editer a la main.
"""
from __future__ import annotations

# Cle = nom logique utilise par le job onboarding (correspond aux fichiers HTML)
# Valeur = ID retourne par l'API Brevo lors de la creation du template
TEMPLATE_IDS: dict[str, int] = {
    # Sera rempli par scripts/sync_brevo_templates.py
    # Exemple : "j0": 12, "j1": 13, ...
}

# Subject lines par template (centralisees ici pour modifier sans toucher au HTML)
TEMPLATE_SUBJECTS: dict[str, str] = {
    "j0": "Bienvenue sur Valina-Bot, {{params.prenom}}",
    "j1": "3 conseils pour tes premieres conversations bot",
    "j3": "Comment ca se passe avec Valina-Bot ?",
    "j5": "L'astuce qui double les ventes via Valina-Bot",
    "j7": "Ton essai Valina-Bot se termine demain",
    "j14": "5 features avancees a debloquer cette semaine",
    "j30": "Une question rapide apres 30 jours",
}


def get_template_id(email_key: str) -> int | None:
    """Retourne l'ID Brevo pour un email_key, ou None si pas encore sync."""
    return TEMPLATE_IDS.get(email_key)
