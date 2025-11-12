import requests
import logging
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from backend.config import settings

logger = logging.getLogger(__name__)

# === 1️⃣ Modèle ChatOllama sur CPU ===
llm = ChatOllama(
    model=settings.OLLAMA_MODEL,  # par ex. "gemma:2b" pour modèle léger
    device="cpu",
    gpu=False,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0.5
)

# === 2️⃣ Outil de recherche Web ===
def web_search(query: str) -> str:
    """Recherche rapide sur DuckDuckGo."""
    try:
        r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json")
        data = r.json()
        return data.get("AbstractText") or "Aucune information pertinente trouvée."
    except Exception as e:
        logger.error(f"Erreur de recherche : {e}")
        return f"Erreur de recherche : {e}"

tools = [
    Tool(
        name="Web Search",
        func=web_search,
        description="Recherche des informations pertinentes pour l'apprentissage des langues."
    )
]

# === 3️⃣ Prompt system détaillé (backstory) ===
system_prompt = SystemMessagePromptTemplate.from_template(
    """Tu es un expert linguistique et polyglotte spécialisé dans l'enseignement des langues.
Tu excelles à :
- Trouver des explications claires de règles grammaticales et vocabulaire
- Fournir des exemples pratiques et des contextes culturels
- Prioriser les explications accessibles aux débutants
- Produire des résumés structurés et clairs pour aider l’apprenant"""
)

# === 4️⃣ Prompt complet pour l'agent ===
prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    HumanMessagePromptTemplate.from_template(
        """Requête : {input_text}

Utilise les informations de recherche disponibles et fournis :
- Règles grammaticales importantes
- Définitions et vocabulaire
- Exemples pratiques
- Contexte culturel pertinent"""
    )
])

# === 5️⃣ Création de l'agent LangChain ===
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,  # conversationnel + recherche
    verbose=True,
    prompt=prompt
)

# === 6️⃣ Fonction publique ===
def run_research_agent(query: str, context: str = "") -> str:
    """Exécute la recherche et renvoie un résumé structuré."""
    input_text = f"""
Query: {query}
Contexte disponible: {context}
"""
    try:
        # utiliser invoke() au lieu de run() car run() est déprécié
        result = agent.invoke({"input": input_text})["output"]
        return result
    except Exception as e:
        logger.error(f"❌ Research agent failed: {e}")
        logger.exception("Détails de l'erreur :")
        return "Le chercheur n'est pas disponible pour le moment."
