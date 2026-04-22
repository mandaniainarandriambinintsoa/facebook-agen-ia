"""
Generateur de reponses avec LLM
Groq (principal)
"""

from loguru import logger
from typing import List, Dict, Any
from abc import ABC, abstractmethod

from app.config import settings
from app.rag.models import RetrievedDocument


class BaseLLMClient(ABC):
    """Interface de base pour les clients LLM"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str) -> str:
        """Genere une reponse a partir d'un prompt"""
        pass


class OpenAIClient(BaseLLMClient):
    """Client pour l'API OpenAI (GPT)"""

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model if settings.llm_model else "gpt-4o-mini"
        logger.info(f"Client OpenAI initialise avec le modele: {self.model}")

    def generate(self, prompt: str, system_prompt: str) -> str:
        """Genere une reponse avec GPT"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur OpenAI: {e}")
            raise


class GroqClient(BaseLLMClient):
    """Client pour l'API Groq (Llama, Mixtral, etc.)"""

    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model if settings.groq_model else "llama-3.3-70b-versatile"
        logger.info(f"Client Groq initialise avec le modele: {self.model}")

    def generate(self, prompt: str, system_prompt: str) -> str:
        """Genere une reponse avec Groq"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur Groq: {e}")
            raise


class AnthropicClient(BaseLLMClient):
    """Client pour l'API Anthropic (Claude)"""

    def __init__(self):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model
        logger.info(f"Client Anthropic initialise avec le modele: {self.model}")

    def generate(self, prompt: str, system_prompt: str) -> str:
        """Genere une reponse avec Claude"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Erreur Anthropic: {e}")
            raise


class ResponseGenerator:
    """
    Generateur de reponses RAG
    OpenAI principal avec fallback automatique vers Groq
    """

    SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant IA pour une page Facebook. Tu dois repondre aux questions des utilisateurs de maniere professionnelle et utile.

REGLES IMPORTANTES:
1. Reponds UNIQUEMENT en te basant sur le contexte fourni ci-dessous
2. Si l'information n'est pas dans le contexte, dis clairement que tu n'as pas cette information
3. Sois concis (2-3 phrases maximum pour Messenger)
4. Sois poli et professionnel
5. Ne fais jamais de suppositions sur des informations non fournies
6. Si la question est hors sujet, propose de contacter le support

CONTEXTE (Base de connaissances):
{context}

INSTRUCTIONS SUPPLEMENTAIRES:
- Reponds en francais
- Utilise un ton amical mais professionnel
- Si tu proposes de contacter le support, utilise: {support_contact}
"""

    CLASSIC_MODE_PROMPT_TEMPLATE = """Tu es un assistant IA conversationnel pour une page Facebook. Tu reponds aux utilisateurs comme le ferait un agent de support humain, dans un style naturel et chaleureux.

REGLES IMPORTANTES:
1. Reponds UNIQUEMENT en te basant sur le contexte fourni ci-dessous
2. Si l'information n'est pas dans le contexte, dis-le poliment et propose de contacter le support
3. Style conversationnel pur: PAS de listes a puces, PAS de menus, PAS de catalogue, PAS de mentions "cliquez sur...", PAS d'emojis decoratifs
4. Reponses courtes et humaines (1-3 phrases), comme dans une vraie discussion
5. Ne propose JAMAIS de boutons ou d'options a choisir
6. Ne fais jamais de suppositions sur des informations non fournies

CONTEXTE (Base de connaissances):
{context}

INSTRUCTIONS SUPPLEMENTAIRES:
- Reponds en francais
- Ton amical, naturel, comme un vrai agent qui discute
- Si tu proposes de contacter le support, utilise: {support_contact}
"""

    CLASSIC_MODE_HINT = (
        "\n\nIMPORTANT - Mode conversation classique: reponds en texte naturel uniquement. "
        "Pas de listes a puces, pas de catalogue, pas de suggestions cliquables. Reponse courte et conversationnelle."
    )

    def __init__(self, custom_system_prompt: str = None, conversation_mode: str = "catalog"):
        """
        Initialise le generateur avec Groq comme LLM principal.
        custom_system_prompt: si fourni, remplace le template par defaut (multi-tenant).
        conversation_mode: "catalog" (defaut, style e-commerce structure) ou "classic" (conversation libre).
        """
        self.primary_client = None
        self.fallback_client = None
        self.custom_system_prompt = custom_system_prompt
        self.conversation_mode = conversation_mode if conversation_mode in ("catalog", "classic") else "catalog"

        # Client principal
        provider = settings.llm_provider
        if provider == "groq" and settings.groq_api_key:
            self.primary_client = GroqClient()
        elif provider == "anthropic" and settings.anthropic_api_key:
            self.primary_client = AnthropicClient()
        elif provider == "openai" and settings.openai_api_key:
            self.primary_client = OpenAIClient()

        if self.primary_client:
            logger.info(f"LLM principal: {provider}")
        if self.fallback_client:
            logger.info(f"LLM fallback configure")
        if not self.primary_client and not self.fallback_client:
            logger.warning("Aucun client LLM configure! Verifiez vos cles API dans .env")

    def _format_context(self, documents: List[RetrievedDocument]) -> str:
        """Formate les documents recuperes en contexte"""
        if not documents:
            return "Aucune information disponible dans la base de connaissances."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "inconnu")
            context_parts.append(f"[Source {i}: {source}]\n{doc.content}")

        return "\n\n".join(context_parts)

    def _get_support_contact(self) -> str:
        """Retourne les coordonnees du support"""
        contacts = []
        if settings.support_email:
            contacts.append(f"email: {settings.support_email}")
        if settings.support_phone:
            contacts.append(f"telephone: {settings.support_phone}")
        return " ou ".join(contacts) if contacts else "notre equipe support"

    def _call_llm(self, prompt: str, system_prompt: str) -> str:
        """Appelle le LLM principal, fallback vers Groq si erreur"""
        # Essayer le client principal
        if self.primary_client:
            try:
                return self.primary_client.generate(prompt, system_prompt)
            except Exception as e:
                logger.warning(f"Erreur LLM principal, tentative fallback: {e}")

        # Fallback
        if self.fallback_client:
            try:
                logger.info("Utilisation du LLM fallback")
                return self.fallback_client.generate(prompt, system_prompt)
            except Exception as e:
                logger.error(f"Erreur LLM fallback: {e}")
                raise

        raise RuntimeError("Aucun client LLM disponible")

    def generate_response(
        self,
        query: str,
        documents: List[RetrievedDocument],
        confidence_level: str = "high"
    ) -> str:
        """
        Genere une reponse a partir de la requete et des documents

        Args:
            query: Question de l'utilisateur
            documents: Documents recuperes par le retriever
            confidence_level: Niveau de confiance ("high", "medium", "low")

        Returns:
            Reponse generee
        """
        context = self._format_context(documents)
        support_contact = self._get_support_contact()

        if self.custom_system_prompt:
            system_prompt = self.custom_system_prompt + f"\n\nCONTEXTE:\n{context}"
            if self.conversation_mode == "classic":
                system_prompt += self.CLASSIC_MODE_HINT
        elif self.conversation_mode == "classic":
            system_prompt = self.CLASSIC_MODE_PROMPT_TEMPLATE.format(
                context=context,
                support_contact=support_contact
            )
        else:
            system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
                context=context,
                support_contact=support_contact
            )

        # Adapter le prompt selon le niveau de confiance
        if confidence_level == "low":
            user_prompt = f"""Question de l'utilisateur: {query}

ATTENTION: Le niveau de confiance est faible. Les informations disponibles ne correspondent peut-etre pas bien a la question.
Reponds avec prudence et propose de contacter le support si necessaire."""
        elif confidence_level == "medium":
            user_prompt = f"""Question de l'utilisateur: {query}

Note: Le niveau de confiance est moyen. Reponds en te basant sur les informations disponibles, mais mentionne que l'utilisateur peut contacter le support pour plus de details."""
        else:
            user_prompt = f"""Question de l'utilisateur: {query}

Reponds de maniere claire et concise."""

        try:
            response = self._call_llm(user_prompt, system_prompt)
            logger.debug(f"Reponse generee pour: '{query[:50]}...'")
            return response
        except Exception as e:
            logger.error(f"Erreur lors de la generation: {e}")
            return f"Desolee, je rencontre un probleme technique. Veuillez contacter {support_contact}."

    def generate_fallback_response(self) -> str:
        """Genere une reponse de fallback quand rien n'est trouve"""
        support = self._get_support_contact()
        return f"Je n'ai pas suffisamment d'informations pour repondre a cette question. N'hesitez pas a contacter {support} pour plus d'aide."
