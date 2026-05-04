"""
Detecteur de prospects — identifie les messages indiquant une intention d'achat.
Detecte les mots-cles de paiement, livraison, commande dans les messages clients.
"""

import re
from typing import Optional
from loguru import logger


# Keywords avec match en mot entier (regex \b...\b strict).
# Le suffixe optionnel \w* permet de matcher les variantes flexionnelles
# ("commande", "commandes", "commander") sans lister chaque forme.
PAYMENT_KEYWORDS = {
    "mvola": [r"mvola\w*", r"m-vola", r"m vola"],
    "orange_money": [r"orange\s*money", r"orangemoney", r"orange-money", r"om"],  # "om" reste strict (mot entier)
    "airtel_money": [r"airtel\s*money", r"airtelmoney", r"airtel-money"],
    "paiement": [r"paiement\w*", r"payer", r"paye\w*", r"virement\w*", r"transfert\w*", r"mobile\s*money"],
    "cash": [r"cash", r"espece\w*", r"espèce\w*"],  # "vola" retire car ambigu (= argent en general MG)
}

ORDER_KEYWORDS = {
    "commande": [r"command\w*", r"manafatra", r"order\w*", r"afatra"],
    "livraison": [r"livr\w*", r"deliver\w*", r"delivery", r"fanaterana", r"ateraka"],
    "achat": [r"achet\w*", r"achat\w*", r"hividy", r"vidiana", r"mividy", r"te\s+hividy"],
    "prix": [r"combien", r"ohatrinona", r"prix", r"tarif\w*", r"coût\w*", r"cout\w*", r"firy"],
    "disponible": [r"dispo", r"disponibl\w*", r"mbola\s+misy", r"misy\s+ve", r"stock\w*"],
    "adresse": [r"adresse\w*", r"adiresy", r"aiza", r"toerana"],
    "telephone": [r"num[eé]ro\w*", r"telephone\w*", r"laharana", r"nomerao"],
}

# Mots qui ressemblent a des keywords mais sont des QUESTIONS, pas des intents d'achat.
# Si un message contient ces patterns ET se termine par "?", on ignore (= question pure).
QUESTION_INDICATORS = (r"\?$", r"\bve\b", r"\best[\s-]?ce\b")


def _has_word_match(pattern: str, text: str) -> bool:
    """Match en frontiere de mot (\\b...\\b) avec le pattern fourni."""
    full_pattern = r"\b" + pattern + r"\b"
    return re.search(full_pattern, text, re.IGNORECASE) is not None


def detect_prospect_intent(message: str) -> Optional[dict]:
    """
    Analyse un message pour detecter une intention d'achat.
    Retourne None si pas de signal, ou un dict avec:
    - keyword: le mot-cle detecte
    - category: la categorie (payment, order)
    - confidence: score de confiance (0.0-1.0)

    Heuristiques anti-faux-positifs:
    - Match en frontiere de mot uniquement (pas substring)
    - Question pure ("dispo ?", "combien ?") = signal faible, requiert match payment
      OU plusieurs matchs order pour declencher
    - Salutations malgaches/francaises explicitement exclues
    """
    if not message:
        return None

    msg_lower = message.lower().strip()

    # Ignore messages tres courts ou salutations
    if len(msg_lower) < 3:
        return None

    greetings = (
        "bonjour", "salut", "hello", "hi", "bonsoir",
        "miarahaba", "manao ahoana", "salama tompoko", "salama"
    )
    if msg_lower in greetings:
        return None

    # Detecter si le message est une question pure (pas une commande)
    is_question = any(
        re.search(p, msg_lower, re.IGNORECASE) for p in QUESTION_INDICATORS
    )

    # Check payment keywords first (signal le plus fort, valide meme en question)
    for category, patterns in PAYMENT_KEYWORDS.items():
        for pattern in patterns:
            if _has_word_match(pattern, msg_lower):
                return {
                    "keyword": pattern,
                    "category": f"payment_{category}",
                    "confidence": 0.95,
                }

    # Check order keywords (signal fort, mais on filtre les questions pures)
    matches = []
    for category, patterns in ORDER_KEYWORDS.items():
        for pattern in patterns:
            if _has_word_match(pattern, msg_lower):
                matches.append({
                    "keyword": pattern,
                    "category": f"order_{category}",
                    "confidence": 0.80,
                })

    if not matches:
        return None

    # Si question pure ET tous les matches sont des "signaux faibles" (renseignements
    # avant achat : prix, dispo, adresse, telephone), on ignore — c'est une question
    # exploratoire, pas une intention de commander.
    weak_categories = {
        "order_disponible", "order_prix", "order_adresse", "order_telephone"
    }
    if is_question and all(m["category"] in weak_categories for m in matches):
        return None

    return max(matches, key=lambda x: x["confidence"])


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
