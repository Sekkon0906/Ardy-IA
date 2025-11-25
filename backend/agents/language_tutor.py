"""
WALL-E AI Language Tutor - VERSION GROQ
Utilise Groq API (GRATUIT, RAPIDE, ILLIMITÉ)
"""
import logging
from groq import Groq
from backend.config import settings

logger = logging.getLogger(__name__)

# Prompts optimisés
SYSTEM_PROMPTS = {
    "es": """Eres WALL-E, un tutor de español amigable y experto.

Responde en español de forma clara y educativa (máximo 4 oraciones).
Corrige errores con amabilidad y explica las reglas.
Da ejemplos prácticos cuando sea útil.
Usa emojis ocasionalmente para mantener un tono amigable.

Ejemplo:
Usuario: "Hola como estas"
Tú: "¡Hola! 😊 Estoy muy bien, gracias por preguntar. Pequeña corrección: la pregunta correcta es '¿Cómo estás?' con tildes y signos de interrogación. Las tildes son importantes en español. ¿En qué puedo ayudarte hoy?"
""",
    
    "en": """You are WALL-E, a friendly and expert English tutor.

Respond in English clearly and educationally (maximum 4 sentences).
Correct mistakes kindly and explain the rules.
Give practical examples when useful.
Use emojis occasionally to maintain a friendly tone.

Example:
User: "Hello, how you are?"
You: "Hi! 👋 I'm doing great, thanks for asking! Small correction: the correct question is 'How are you?' In English, we need the auxiliary verb 'do/are' for questions. What would you like to practice today?"
""",
    
    "fr": """Tu es WALL-E, un tuteur de français amical et expert.

Réponds en français de façon claire et éducative (maximum 4 phrases).
Corrige les erreurs gentiment et explique les règles.
Donne des exemples pratiques si utile.
Utilise des emojis parfois pour garder un ton amical.

Exemple:
Utilisateur: "Bonjour comment tu va"
Toi: "Bonjour! 👋 Je vais très bien, merci! Correction: on dit 'comment vas-tu?' ou 'comment tu vas?' en français familier. N'oublie pas l's' à 'vas'. Que veux-tu pratiquer aujourd'hui?"
"""
}


def call_groq_api(prompt: str, system_prompt: str, context: str = "") -> str:
    """
    Appelle l'API Groq (GRATUIT)
    
    Args:
        prompt: Question de l'utilisateur
        system_prompt: Instructions système
        context: Historique de conversation
    
    Returns:
        Réponse générée par le modèle
    """
    try:
        # Vérifier que la clé API est configurée
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY non configurée dans le fichier .env")
        
        # Initialiser le client Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        # Construire les messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Ajouter le contexte si disponible (limité)
        if context:
            context_lines = context.split('\n')[-10:]  # Limiter à 10 dernières lignes
            limited_context = '\n'.join(context_lines)
            messages.append({
                "role": "system", 
                "content": f"Contexte de la conversation:\n{limited_context}"
            })
        
        # Ajouter la question de l'utilisateur
        messages.append({"role": "user", "content": prompt})
        
        logger.info(f"🤖 Appel Groq API ({settings.GROQ_MODEL})...")
        
        # Faire l'appel API
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=settings.MODEL_TEMPERATURE,
            max_tokens=settings.MODEL_MAX_TOKENS,
            top_p=0.9,
            stream=False
        )
        
        # Extraire la réponse
        answer = response.choices[0].message.content.strip()
        
        if not answer:
            logger.error("❌ Groq a retourné une réponse vide")
            return "Désolé, je n'ai pas pu générer une réponse. Peux-tu reformuler ta question ?"
        
        logger.info(f"✅ Réponse Groq générée ({len(answer)} caractères)")
        return answer
    
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return f"❌ Erreur de configuration: {str(e)}\n\nObtiens une clé API gratuite sur: https://console.groq.com/"
    
    except Exception as e:
        logger.error(f"❌ Groq API error: {e}")
        error_msg = str(e)
        
        # Messages d'erreur plus clairs
        if "invalid_api_key" in error_msg or "authentication" in error_msg.lower():
            return "❌ Clé API Groq invalide. Vérifie ton fichier .env\n\nObtiens une clé gratuite sur: https://console.groq.com/"
        elif "rate_limit" in error_msg.lower():
            return "⏱️ Limite de requêtes atteinte. Attends quelques secondes et réessaye."
        else:
            return f"❌ Erreur Groq: {error_msg}"


def run_teaching_crew(
    query: str,
    language: str = "es",
    memory_context: str = "",
    research_context: str = ""
) -> str:
    """
    Traite la requête de l'utilisateur avec Groq
    
    Args:
        query: Question de l'utilisateur
        language: Code de langue (es, en, fr)
        memory_context: Historique de conversation
        research_context: Contexte RAG (optionnel)
    
    Returns:
        Réponse du tuteur
    """
    logger.info(f"🎓 Traitement de la question: {query[:50]}...")
    
    # Obtenir le prompt système selon la langue
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["es"])
    
    # Construire le contexte combiné
    combined_context = ""
    
    if memory_context:
        combined_context += memory_context
    
    if research_context:
        # Limiter le contexte RAG
        combined_context += f"\n\nINFO ADDITIONNELLE:\n{research_context[:500]}"
    
    # Appeler Groq et obtenir la réponse
    response = call_groq_api(
        prompt=query,
        system_prompt=system_prompt,
        context=combined_context
    )
    
    logger.info("✅ Réponse générée avec succès")
    return response
