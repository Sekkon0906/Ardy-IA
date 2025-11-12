"""
RAG service with web search and vector storage
COMPATIBLE con ChromaDB 0.4.24 EXACTAMENTE
"""
import uuid
import requests
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
from backend.config import settings
import logging
import os

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # ✅ CORRECCIÓN PARA CHROMADB 0.4.24
            # Usar PersistentClient en lugar de Client con Settings
            # Crear directorio si no existe
            os.makedirs(settings.CHROMADB_PATH, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH
            )
            
            # get_or_create_collection es correcto para 0.4.24
            self.collection = self.client.get_or_create_collection(
                name="language_learning",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"✅ RAG service initialized (ChromaDB 0.4.24)")
            logger.info(f"📁 Database path: {settings.CHROMADB_PATH}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG service: {e}")
            logger.exception("Detalles completos:")
            raise
    
    def web_search(self, query: str, num_results: int = 3) -> list:
        """Search the web using DuckDuckGo"""
        try:
            logger.info(f"🔎 Searching web: {query}")
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            response = requests.get(
                url, 
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, 
                timeout=10
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for link in soup.select("a.result__a")[:num_results]:
                try:
                    title = link.get_text().strip()
                    href = link.get("href")
                    
                    if href and href.startswith("http"):
                        # Fetch page content
                        page_response = requests.get(
                            href, 
                            headers={"User-Agent": "Mozilla/5.0"},
                            timeout=5
                        )
                        page_response.raise_for_status()
                        
                        page_soup = BeautifulSoup(page_response.text, "html.parser")
                        
                        # Extract paragraphs
                        paragraphs = [p.get_text().strip() for p in page_soup.find_all("p")]
                        text = " ".join(paragraphs)[:2000]
                        
                        if len(text) > 100:
                            results.append({
                                "url": href,
                                "title": title[:200],
                                "content": text
                            })
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fetch {href}: {e}")
                    continue
            
            logger.info(f"✅ Found {len(results)} web results")
            return results
        
        except Exception as e:
            logger.error(f"❌ Web search failed: {e}")
            logger.exception("Detalles:")
            return []
    
    def index_documents(self, documents: list, language: str = "es"):
        """Index documents into ChromaDB 0.4.24"""
        if not documents:
            logger.warning("No documents to index")
            return
        
        try:
            # Prepare data
            ids = []
            metadatas = []
            contents = []
            embeddings = []
            
            for doc in documents:
                doc_id = str(uuid.uuid4())
                content = doc["content"][:1500]  # Limit length
                
                # Generate embedding
                embedding = self.embedding_model.encode(content).tolist()
                
                ids.append(doc_id)
                contents.append(content)
                metadatas.append({
                    "lang": language,
                    "source": doc.get("url", "unknown")[:300],
                    "title": doc.get("title", "")[:200]
                })
                embeddings.append(embedding)
            
            # ChromaDB 0.4.24 API
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"📚 Indexed {len(documents)} documents")
        except Exception as e:
            logger.error(f"❌ Indexing failed: {e}")
            logger.exception("Detalles:")
    
    def search_context(self, query: str, n_results: int = 3) -> str:
        """Search ChromaDB 0.4.24"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # ChromaDB 0.4.24 API - usar query_embeddings
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Extract documents
            if results and "documents" in results:
                documents = results["documents"][0] if results["documents"] else []
                
                if documents:
                    context = "\n\n".join(documents)
                    logger.info(f"✅ Retrieved {len(documents)} context chunks")
                    return context
            
            logger.warning("No results from ChromaDB")
            return ""
        
        except Exception as e:
            logger.error(f"❌ Context search failed: {e}")
            logger.exception("Detalles:")
            return ""
    
    def rag_search(self, query: str, language: str = "es") -> str:
        """Full RAG pipeline"""
        try:
            logger.info(f"🔍 Starting RAG search: {query[:50]}...")
            
            # 1. Web search
            web_results = self.web_search(query, num_results=settings.MAX_SEARCH_RESULTS)
            
            if not web_results:
                logger.warning("No web results found")
                return ""
            
            # 2. Index documents
            self.index_documents(web_results, language)
            
            # 3. Retrieve context
            context = self.search_context(query, n_results=3)
            
            return context
        
        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            logger.exception("Detalles:")
            return ""
    
    def test_connection(self) -> bool:
        """Test ChromaDB connection"""
        try:
            collections = self.client.list_collections()
            logger.info(f"✅ ChromaDB OK. Collections: {[c.name for c in collections]}")
            return True
        except Exception as e:
            logger.error(f"❌ ChromaDB test failed: {e}")
            return False


# Singleton
rag_service = RAGService()