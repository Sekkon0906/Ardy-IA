"""
RAG service with web search and vector storage
COMPATIBLE con ChromaDB 0.4.24

Version améliorée:
- DuckDuckGo JSON API -> HTML scraping fallback -> Bing HTML fallback
- Logs détaillés pour diagnostiquer pourquoi aucune résultat n'est retourné
- Robustesse contre timeouts / pages non accessibles
- Conservation de l'indexation et de la recherche ChromaDB
"""
import uuid
import requests
import logging
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
from backend.config import settings
import os
from typing import List, Dict, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

            # ✅ Compatibilité ChromaDB 0.4.24
            os.makedirs(settings.CHROMADB_PATH, exist_ok=True)
            self.client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)

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

    # --------------------------
    # Helpers
    # --------------------------
    @staticmethod
    def _clean_text(text: str, max_len: int = 2000) -> str:
        if not text:
            return ""
        cleaned = " ".join(text.split())
        return cleaned[:max_len]

    # --------------------------
    # Web search (DuckDuckGo JSON -> HTML fallback -> Bing fallback)
    # --------------------------
    def web_search(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """
        Return list of dicts {url, title, content} using:
         1) DuckDuckGo Instant Answer JSON
         2) DuckDuckGo HTML scraping fallback
         3) Bing HTML scraping fallback (if previous returned none)
        This layered approach increases chance of getting usable results for conversational queries.
        """
        results: List[Dict[str, Any]] = []
        logger.info(f"🔎 Searching web: {query!r} (max {num_results})")

        try:
            max_results = max(1, int(num_results))
        except Exception:
            max_results = 3

        # 1) DuckDuckGo Instant Answer API (JSON)
        try:
            ddg_url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
            logger.debug(f"Calling DuckDuckGo JSON API: {ddg_url} params={params}")
            r = requests.get(ddg_url, params=params, timeout=8, headers={"User-Agent": "WALLE-RAG/1.0"})
            logger.debug(f"DDG JSON status={r.status_code} text_head={r.text[:1000]!r}")
            r.raise_for_status()
            data = r.json()

            if data.get("AbstractText"):
                results.append({
                    "url": data.get("AbstractURL") or f"https://duckduckgo.com/?q={query}",
                    "title": data.get("Heading") or query,
                    "content": self._clean_text(data.get("AbstractText"), max_len=2000)
                })

            related = data.get("RelatedTopics", [])
            for item in related:
                if len(results) >= max_results:
                    break
                if isinstance(item, dict):
                    if item.get("Text") and item.get("FirstURL"):
                        results.append({
                            "url": item.get("FirstURL"),
                            "title": item.get("Text")[:200],
                            "content": self._clean_text(item.get("Text"), max_len=2000)
                        })
                    elif item.get("Topics"):
                        for sub in item.get("Topics", []):
                            if len(results) >= max_results:
                                break
                            if sub.get("Text") and sub.get("FirstURL"):
                                results.append({
                                    "url": sub.get("FirstURL"),
                                    "title": sub.get("Text")[:200],
                                    "content": self._clean_text(sub.get("Text"), max_len=2000)
                                })
            logger.info(f"✅ DuckDuckGo JSON returned {len(results)} preliminary results")
        except Exception as e:
            logger.debug(f"DuckDuckGo JSON API failed or returned no usable data: {e}", exc_info=True)

        # 2) HTML fallback (DuckDuckGo)
        if len(results) < max_results:
            try:
                search_url = "https://html.duckduckgo.com/html/"
                params = {"q": query}
                logger.debug(f"Falling back to DuckDuckGo HTML scraping: {search_url} params={params}")
                r = requests.get(search_url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                logger.debug(f"HTML search status={r.status_code} text_head={r.text[:1000]!r}")
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")

                candidates = soup.select("a.result__a")
                logger.debug(f"Found {len(candidates)} candidate links in DuckDuckGo HTML")
                for link in candidates:
                    if len(results) >= max_results:
                        break
                    try:
                        title = link.get_text().strip()
                        href = link.get("href")
                        if not href or not href.startswith("http"):
                            continue
                        page_response = requests.get(href, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
                        page_response.raise_for_status()
                        page_soup = BeautifulSoup(page_response.text, "html.parser")
                        paragraphs = [p.get_text().strip() for p in page_soup.find_all("p")]
                        text = " ".join(paragraphs)
                        text = self._clean_text(text, max_len=2000)
                        if len(text) > 100:
                            results.append({
                                "url": href,
                                "title": title[:200],
                                "content": text
                            })
                    except Exception as e:
                        logger.debug(f"Failed to fetch or parse page {href}: {e}")
                        continue
                logger.info(f"✅ DuckDuckGo HTML fallback added results; total {len(results)}")
            except Exception as e:
                logger.debug(f"DuckDuckGo HTML fallback failed: {e}", exc_info=True)

        # 3) Bing fallback (HTML) — often returns usable results for short/conversational queries
        if len(results) < max_results:
            try:
                bing_url = "https://www.bing.com/search"
                params = {"q": query}
                logger.debug(f"Falling back to Bing scraping: {bing_url} params={params}")
                r = requests.get(bing_url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                logger.debug(f"Bing status={r.status_code} text_head={r.text[:1000]!r}")
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")

                candidates = soup.select("li.b_algo h2 a")
                logger.debug(f"Found {len(candidates)} candidate links in Bing")
                for a in candidates:
                    if len(results) >= max_results:
                        break
                    try:
                        href = a.get("href")
                        title = a.get_text().strip()
                        if not href or not href.startswith("http"):
                            continue
                        page_response = requests.get(href, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
                        page_response.raise_for_status()
                        page_soup = BeautifulSoup(page_response.text, "html.parser")
                        paragraphs = [p.get_text().strip() for p in page_soup.find_all("p")]
                        text = " ".join(paragraphs)
                        text = self._clean_text(text, max_len=2000)
                        if len(text) > 100:
                            results.append({
                                "url": href,
                                "title": title[:200],
                                "content": text
                            })
                    except Exception as e:
                        logger.debug(f"Failed to fetch or parse page {href}: {e}")
                        continue
                logger.info(f"✅ Bing fallback added results; total {len(results)}")
            except Exception as e:
                logger.debug(f"Bing fallback failed: {e}", exc_info=True)

        # Trim to requested number
        if len(results) > max_results:
            results = results[:max_results]

        logger.info(f"🔎 Final web search results: {len(results)}")
        # For debugging: if still 0, log more diagnostic info
        if len(results) == 0:
            logger.debug("No web results after all fallbacks. Possible causes: network blocked, heavy anti-scraping, or query too conversational/short.")
        return results

    # --------------------------
    # Indexing
    # --------------------------
    def index_documents(self, documents: List[Dict[str, Any]], language: str = "es"):
        if not documents:
            logger.warning("No documents to index")
            return
        try:
            ids, metadatas, contents, embeddings = [], [], [], []
            for doc in documents:
                doc_id = str(uuid.uuid4())
                content = doc.get("content", "")[:1500]
                embedding = self.embedding_model.encode(content).tolist()
                ids.append(doc_id)
                contents.append(content)
                metadatas.append({
                    "lang": language,
                    "source": doc.get("url", "unknown")[:300],
                    "title": doc.get("title", "")[:200]
                })
                embeddings.append(embedding)

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

    # --------------------------
    # Search in vector DB
    # --------------------------
    def search_context(self, query: str, n_results: int = 3) -> str:
        try:
            if not query:
                return ""
            query_embedding = self.embedding_model.encode(query).tolist()
            logger.debug("Querying ChromaDB with n_results=%s", n_results)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            logger.debug(f"ChromaDB raw query result keys: {list(results.keys()) if isinstance(results, dict) else type(results)}")
            documents = []

            if isinstance(results, dict) and "documents" in results and results["documents"]:
                docs_for_query = results["documents"][0] if isinstance(results["documents"][0], list) else results["documents"][0]
                documents = [d for d in docs_for_query if d]
            elif isinstance(results, dict) and "metadatas" in results and results["metadatas"]:
                metas = results.get("metadatas", [])
                if metas and isinstance(metas[0], list):
                    for meta in metas[0]:
                        if meta and meta.get("title"):
                            documents.append(meta.get("title") + " " + (meta.get("source") or ""))
            else:
                logger.debug("No documents key in ChromaDB response or empty response")

            if documents:
                context = "\n\n".join(documents)
                context = self._clean_text(context, max_len=2000)
                logger.info(f"✅ Retrieved {len(documents)} context chunks")
                return context

            logger.warning("No results from ChromaDB")
            return ""
        except Exception as e:
            logger.error(f"❌ Context search failed: {e}")
            logger.exception("Detalles:")
            return ""

    # --------------------------
    # Full RAG pipeline
    # --------------------------
    def rag_search(self, query: str, language: str = "es") -> str:
        try:
            logger.info(f"🔍 Starting RAG search: {query[:50]}...")
            try:
                num_results = int(getattr(settings, "MAX_SEARCH_RESULTS", 3))
            except Exception:
                num_results = 3

            web_results = self.web_search(query, num_results=num_results)
            if not web_results:
                logger.warning("No web results found")
                return ""

            try:
                self.index_documents(web_results, language)
            except Exception as e:
                logger.error(f"❌ Index step failed (continuing): {e}", exc_info=True)

            context = self.search_context(query, n_results=min(3, len(web_results)))
            return context
        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            logger.exception("Detalles:")
            return ""

    # --------------------------
    # Health / test
    # --------------------------
    def test_connection(self) -> bool:
        try:
            collections = self.client.list_collections()
            names = [c.name for c in collections]
            logger.info(f"✅ ChromaDB OK. Collections: {names}")
            try:
                info = self.collection.count()
                logger.info(f"📊 Collection '{self.collection.name}' count: {info}")
            except Exception:
                logger.debug("Could not get collection count (method may not exist in this chromadb version)")
            return True
        except Exception as e:
            logger.error(f"❌ ChromaDB test failed: {e}")
            logger.exception("Detalles:")
            return False


# Singleton
rag_service = RAGService()
