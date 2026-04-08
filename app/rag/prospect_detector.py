"""
Detecteur de prospects — identifie les messages indiquant une intention d'achat.
Detecte les mots-cles de paiement, livraison, commande dans les messages clients.
"""

import re
from typing import Optional
from loguru import logger


# Mots-cles groupes par categorie
PAYMENT_KEYWORDS = {
    "mvola": ["mvola", "m-vola", "m vola"],
    "orange_money": ["orange money", "orangemoney", "orange-money", "om"],
    "airtel_money": ["airtel money", "airtelmoney", "airtel-money"],
    "paiement": ["paiement", "payer", "virement", "transfert", "mobile money"],
    "cash": ["cash", "espece", "espèce", "vola"],
}

ORDER_KEYWORDS = {
    "commande": ["commande", "commander", "commandez", "manafatra", "order", "afatra"],
    "livraison": ["livraison", "livrer", "livrez", "delivery", "fanaterana", "ateraka"],
    "achat": ["acheter", "achat", "hividy", "vidiana", "mividy", "tiako", "te hividy"],
    "prix": ["combien", "ohatrinona", "prix", "tarif", "coût", "cout", "firy"],
    "disponible": ["dispo", "disponible", "mbola misy", "misy ve", "stock"],
    "adresse": ["adresse", "adiresy", "aiza", "toerana"],
    "telephone": ["numero", "numéro", "telephone", "laharana", "nomerao"],
}


def detect_prospect_intent(message: str) -> Optional[dict]:
    """
    Analyse un message pour detecter une intention d'achat.
    Retourne None si pas de signal, ou un dict avec:
    - keyword: le mot-cle detecte
    - category: la categorie (payment, order)
    - confidence: score de confiance (0.0-1.0)
    """
    if not message:
        return None

    msg_lower = message.lower().strip()

    # Ignore messages tres courts (moins de 3 chars) ou salutations
    if len(msg_lower) < 3:
        return None

    greetings = ["bonjour", "salut", "hello", "hi", "bonsoir", "miarahaba", "manao ahoana", "salama"]
    if msg_lower in greetings:
        return None

    # Check payment keywords first (highest signal)
    for category, keywords in PAYMENT_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                return {
                    "keyword": kw,
                    "category": f"payment_{category}",
                    "confidence": 0.95,
                }

    # Check order keywords (strong signal)
    matches = []
    for category, keywords in ORDER_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                matches.append({
                    "keyword": kw,
                    "category": f"order_{category}",
                    "confidence": 0.80,
                })

    if matches:
        # Return highest confidence match
        return max(matches, key=lambda x: x["confidence"])

    return None


def extract_order_info(message: str) -> dict:
    """
    Extrait les informations de commande d'un message.
    Retourne un dict avec les champs trouves.
    """
    info = {}
    msg_lower = message.lower()

    # Detect phone numbers (034, 032, 033, 038 + 7 digits)
    phone_pattern = r'(?:0(?:32|33|34|38)\s?\d{2}\s?\d{3}\s?\d{2})'
    phones = re.findall(phone_pattern, message)
    if phones:
        info["phone"] = phones[0].replace(" ", "")

    # Detect payment method
    for method, keywords in PAYMENT_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                info["payment_method"] = method
                break

    # Detect amounts (Ar, Ariary, MGA)
    amount_pattern = r'(\d[\d\s]*(?:\.\d+)?)\s*(?:ar|ariary|mga|fmg)'
    amounts = re.findall(amount_pattern, msg_lower)
    if amounts:
        info["amount"] = amounts[0].replace(" ", "")

    return info
