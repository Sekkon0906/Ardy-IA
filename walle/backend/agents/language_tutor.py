"""
WALL-E AI Language Tutor - VERSIÓN FUNCIONAL
Conecta directamente con Ollama (tinyllama) para respuestas reales
"""
import logging
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)

# Prompts optimizados para TinyLlama (más simples y directos)
SYSTEM_PROMPTS = {
    "es": """Eres WALL-E, un tutor de español amigable.

Responde en español, de forma clara y breve (máximo 3 oraciones).
Corrige errores con amabilidad.
Da ejemplos simples cuando sea útil.
Usa emojis ocasionalmente.

Ejemplo:
Usuario: "Hola como estas"
Tú: "¡Hola! 😊 Estoy bien, gracias. Pequeña corrección: '¿Cómo estás?' con tildes. ¿En qué puedo ayudarte?"
""",
    
    "en": """You are WALL-E, a friendly English tutor.

Respond in English, clear and brief (maximum 3 sentences).
Correct mistakes kindly.
Give simple examples when useful.
Use emojis occasionally.

Example:
User: "Hello, how you are?"
You: "Hi! 👋 I'm great, thanks! Small correction: 'How are you?' What would you like to practice?"
""",
    
    "fr": """Tu es WALL-E, un tuteur de français amical.

Réponds en français, clair et bref (maximum 3 phrases).
Corrige les erreurs gentiment.
Donne des exemples simples si utile.
Utilise des emojis parfois.

Exemple:
Utilisateur: "Bonjour comment tu va"
Toi: "Bonjour! 👋 Ça va bien, merci! Correction: 'comment vas-tu?' Que veux-tu pratiquer?"
"""
}


def call_ollama(prompt: str, system_prompt: str, context: str = "") -> str:
    """
    Llama a Ollama para generar respuesta real
    
    Args:
        prompt: Pregunta del usuario
        system_prompt: Instrucciones del sistema
        context: Historial de conversación (opcional)
    
    Returns:
        Respuesta generada por el modelo
    """
    try:
        # Construir prompt completo (optimizado para TinyLlama)
        full_prompt = system_prompt
        
        # Agregar contexto limitado (TinyLlama funciona mejor con contexto corto)
        if context:
            context_lines = context.split('\n')[-6:]  # Solo últimas 6 líneas
            limited_context = '\n'.join(context_lines)
            full_prompt += f"\n\nCONVERSACIÓN RECIENTE:\n{limited_context}\n"
        
        full_prompt += f"\n\nUSUARIO: {prompt}\n\nWALL-E:"
        
        # Configuración para Ollama
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 250,
                "repeat_penalty": 1.1,
                "num_ctx": 2048,
            }
        }
        
        logger.info(f"🤖 Consultando Ollama ({settings.OLLAMA_MODEL})...")
        
        # Hacer petición HTTP
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("response", "").strip()
            
            if not answer:
                logger.error("❌ Ollama retornó respuesta vacía")
                return "Lo siento, hubo un problema. ¿Puedes intentar de nuevo?"
            
            logger.info(f"✅ Respuesta generada ({len(answer)} caracteres)")
            return answer
    
    except httpx.TimeoutException:
        logger.error("❌ Timeout esperando respuesta")
        return "⏱️ La respuesta está tardando mucho. Intenta con una pregunta más corta."
    
    except httpx.ConnectError:
        logger.error("❌ No se pudo conectar a Ollama")
        return f"❌ No puedo conectar con Ollama. Verifica que esté corriendo (ollama serve) y que el modelo {settings.OLLAMA_MODEL} esté instalado."
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"❌ Error al procesar tu mensaje. Verifica que Ollama esté funcionando correctamente."


def run_teaching_crew(
    query: str,
    language: str = "es",
    memory_context: str = "",
    research_context: str = ""
) -> str:
    """
    Procesa la consulta del usuario usando Ollama
    
    Args:
        query: Pregunta del usuario
        language: Código de idioma (es, en, fr)
        memory_context: Historial de conversación
        research_context: Contexto de RAG (opcional)
    
    Returns:
        Respuesta del tutor
    """
    logger.info(f"🎓 Procesando: {query[:50]}...")
    
    # Obtener prompt del sistema según idioma
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["es"])
    
    # Construir contexto combinado (limitado para TinyLlama)
    combined_context = ""
    
    if memory_context:
        combined_context += memory_context
    
    if research_context:
        # Limitar contexto RAG para no saturar el modelo
        combined_context += f"\n\nINFO ADICIONAL:\n{research_context[:500]}"
    
    # Llamar a Ollama y obtener respuesta real
    response = call_ollama(
        prompt=query,
        system_prompt=system_prompt,
        context=combined_context
    )
    
    logger.info("✅ Respuesta generada")
    return response