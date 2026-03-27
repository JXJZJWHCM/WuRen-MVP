import os
import glob
import logging
from typing import List, Dict, Optional, Tuple
import hashlib
import math
import re
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import RAG dependencies
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("RAG dependencies not found. Please install chromadb and sentence-transformers.")

class RAGEngine:
    def __init__(self, persist_directory: str = "data/vector_db", cache_directory: str = "data/models"):
        self.persist_directory = persist_directory
        self.cache_directory = cache_directory
        self.collection_name = "pentest_knowledge"
        self.model_name = "all-MiniLM-L6-v2"
        self.client = None
        self.collection = None
        self.model = None
        self._initialized = False
        self._lexical_index = None
        self._lexical_index_dirs = None

    def initialize(self):
        """Initialize ChromaDB client and embedding model."""
        if not RAG_AVAILABLE:
            logger.error("Cannot initialize RAG Engine: Missing dependencies.")
            return False

        try:
            # Initialize Embedding Model
            logger.info(f"Loading embedding model: {self.model_name}")
            os.makedirs(self.cache_directory, exist_ok=True)
            self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_directory)

            # Initialize ChromaDB Client
            logger.info(f"Initializing ChromaDB in {self.persist_directory}")
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or Create Collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            self._initialized = True
            logger.info("RAG Engine initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RAG Engine: {e}", exc_info=True)
            return False

    def _generate_id(self, content: str, source: str) -> str:
        """Generate a unique ID for a document chunk."""
        data = f"{content}{source}".encode('utf-8')
        return hashlib.md5(data).hexdigest()

    def add_document(self, content: str, source: str, metadata: Dict = None):
        """Add a document to the vector store."""
        if not self._initialized:
            if not self.initialize():
                return False

        try:
            # Simple chunking: Split by paragraphs for now
            # In production, use a proper text splitter (e.g. RecursiveCharacterTextSplitter)
            chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
            
            ids = []
            embeddings = []
            metadatas = []
            documents = []

            for chunk in chunks:
                if len(chunk) < 50: # Skip very short chunks
                    continue
                    
                chunk_id = self._generate_id(chunk, source)
                embedding = self.model.encode(chunk).tolist()
                
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata['source'] = source
                
                ids.append(chunk_id)
                embeddings.append(embedding)
                metadatas.append(chunk_metadata)
                documents.append(chunk)

            if ids:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )
                logger.info(f"Added {len(ids)} chunks from {source}")
            return True
        except Exception as e:
            logger.error(f"Error adding document {source}: {e}")
            return False

    def query(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """Query the knowledge base."""
        if not self._initialized:
            if not self.initialize():
                return []

        try:
            query_embedding = self.model.encode(query_text).tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying RAG: {e}")
            return []

    def _tokenize(self, text: str) -> List[str]:
        s = (text or "").lower()
        tokens = re.findall(r"[a-z0-9_]+", s)
        return [t for t in tokens if len(t) >= 2]

    def _build_lexical_index(self, directories: List[str], max_files: int = 8000, max_chars_per_file: int = 200000) -> None:
        docs = []
        file_paths = []
        for d in directories or []:
            if not d:
                continue
            if not os.path.exists(d):
                continue
            for fp in glob.glob(os.path.join(d, "**/*.md"), recursive=True):
                file_paths.append(fp)
            for fp in glob.glob(os.path.join(d, "**/*.txt"), recursive=True):
                file_paths.append(fp)

        file_paths = sorted(set(file_paths))
        if max_files and len(file_paths) > max_files:
            file_paths = file_paths[:max_files]

        tokenized = []
        lens = []
        dfs = Counter()
        for fp in file_paths:
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read(max_chars_per_file)
            except Exception:
                continue
            tokens = self._tokenize(os.path.basename(fp) + "\n" + text)
            if not tokens:
                continue
            docs.append(
                {
                    "source": fp,
                    "filename": os.path.basename(fp),
                    "text": text,
                }
            )
            tokenized.append(tokens)
            lens.append(len(tokens))
            for t in set(tokens):
                dfs[t] += 1

        n = len(docs)
        if n == 0:
            self._lexical_index = {"docs": [], "tokenized": [], "lens": [], "avgdl": 0.0, "idf": {}}
            self._lexical_index_dirs = tuple(directories or [])
            return

        avgdl = sum(lens) / float(n)
        idf = {}
        for t, df in dfs.items():
            idf[t] = math.log((n - df + 0.5) / (df + 0.5) + 1.0)

        self._lexical_index = {
            "docs": docs,
            "tokenized": tokenized,
            "lens": lens,
            "avgdl": avgdl,
            "idf": idf,
        }
        self._lexical_index_dirs = tuple(directories or [])

    def _bm25_scores(self, query_tokens: List[str], k1: float = 1.5, b: float = 0.75) -> List[float]:
        idx = self._lexical_index or {}
        docs_tokens = idx.get("tokenized") or []
        lens = idx.get("lens") or []
        avgdl = float(idx.get("avgdl") or 0.0)
        idf = idx.get("idf") or {}
        if not docs_tokens or not query_tokens or avgdl <= 0:
            return []

        q_terms = [t for t in query_tokens if t in idf]
        if not q_terms:
            return [0.0 for _ in docs_tokens]

        scores = [0.0 for _ in docs_tokens]
        for i, doc_tokens in enumerate(docs_tokens):
            tf = Counter(doc_tokens)
            dl = lens[i] if i < len(lens) else len(doc_tokens)
            denom_base = k1 * (1.0 - b + b * (dl / avgdl))
            s = 0.0
            for t in q_terms:
                f = tf.get(t, 0)
                if f <= 0:
                    continue
                s += idf.get(t, 0.0) * ((f * (k1 + 1.0)) / (f + denom_base))
            scores[i] = s
        return scores

    def keyword_query(self, query_text: str, n_results: int = 3, directories: Optional[List[str]] = None) -> List[Dict]:
        dirs = directories or []
        if self._lexical_index is None or tuple(dirs) != (self._lexical_index_dirs or tuple()):
            self._build_lexical_index(dirs)
        idx = self._lexical_index or {}
        docs = idx.get("docs") or []
        if not docs:
            return []
        q_tokens = self._tokenize(query_text)
        scores = self._bm25_scores(q_tokens)
        if not scores:
            return []

        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out = []
        for i in ranked[: max(1, int(n_results))]:
            sc = scores[i]
            if sc <= 0:
                continue
            d = docs[i]
            text = d.get("text") or ""
            snippet = text[:1200]
            out.append(
                {
                    "content": snippet,
                    "metadata": {"source": d.get("source"), "filename": d.get("filename")},
                    "lexical_score": sc,
                }
            )
        return out

    def hybrid_query(
        self,
        query_text: str,
        n_results: int = 3,
        directories: Optional[List[str]] = None,
        vector_n: int = 10,
        lexical_n: int = 20,
        rrf_k: int = 60,
    ) -> List[Dict]:
        dirs = directories or []
        vector_results: List[Dict] = []
        if self._initialized:
            vector_results = self.query(query_text, n_results=max(1, int(vector_n)))

        lexical_results = self.keyword_query(query_text, n_results=max(1, int(lexical_n)), directories=dirs)

        def _key(r: Dict) -> str:
            meta = r.get("metadata") or {}
            src = meta.get("source") or meta.get("filename") or ""
            return str(src)

        scores = {}
        merged = {}
        for rank, r in enumerate(vector_results, start=1):
            k = _key(r)
            if not k:
                continue
            scores[k] = scores.get(k, 0.0) + 1.0 / (float(rrf_k) + float(rank))
            base = merged.get(k) or {}
            merged[k] = {**base, **r, "rrf_score": scores[k], "vector_rank": rank}
        for rank, r in enumerate(lexical_results, start=1):
            k = _key(r)
            if not k:
                continue
            scores[k] = scores.get(k, 0.0) + 1.0 / (float(rrf_k) + float(rank))
            base = merged.get(k) or {}
            combined = {**base, **r, "rrf_score": scores[k], "lexical_rank": rank}
            if "content" in base and base.get("content") and r.get("content"):
                combined["lexical_content"] = r.get("content")
            merged[k] = combined

        ranked_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        out = []
        for k in ranked_keys[: max(1, int(n_results))]:
            out.append(merged[k])
        return out

    def index_directory(self, directory_path: str):
        """Index all markdown files in a directory."""
        if not os.path.exists(directory_path):
            logger.warning(f"Directory not found: {directory_path}")
            return

        files = glob.glob(os.path.join(directory_path, "**/*.md"), recursive=True)
        logger.info(f"Found {len(files)} markdown files in {directory_path}")

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.add_document(
                    content=content, 
                    source=file_path, 
                    metadata={"filename": os.path.basename(file_path)}
                )
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
