"""
RAG Pipeline Module - Semantic Search System for Document Retrieval

Implements a production-grade RAG pipeline with the following stages:
1. Document Vectorization: Convert text chunks to 384-dim embeddings using SentenceTransformer
2. FAISS Indexing: Store vectors in FAISS IndexFlatL2 for fast L2 distance similarity search
3. Persistence: Save index, embeddings, and documents to disk
4. Rehydration: Load pre-computed vectors and index from disk for fast retrieval
5. Top-K Retrieval: Retrieve most relevant document chunks via vector search

Error Handling:
- FileNotFoundError: If FAISS index not found during load
- ValueError: If document list is empty or invalid
- Exception: Wrapped with descriptive messages for debugging
"""

import json
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

from backend.config import VECTORSTORE_PATH, EMBEDDING_MODEL


# ============================================================================
# Stage 1: Vectorization & FAISS Index Creation
# ============================================================================

def create_embeddings_and_faiss_index(
    documents: List[Document],
) -> Tuple[faiss.IndexFlatL2, np.ndarray, List[Document], SentenceTransformer]:
    """
    Create embeddings using SentenceTransformer and build FAISS index directly.
    
    This function:
    - Loads the pre-trained SentenceTransformer model (384-dim vectors)
    - Batch encodes all document chunks to dense vectors
    - Creates FAISS IndexFlatL2 for L2 distance similarity search
    - Returns index, embeddings, documents, and model for later use
    
    Args:
        documents (List[Document]): List of split Document objects with .page_content and .metadata
        
    Returns:
        Tuple[faiss.IndexFlatL2, np.ndarray, List[Document], SentenceTransformer]:
            - index: FAISS index ready for searching
            - embeddings: NumPy array of shape (num_docs, 384)
            - documents: Original document list (unmodified)
            - model: SentenceTransformer model for future query encoding
    
    Raises:
        ValueError: If documents list is empty
        Exception: If embedding or FAISS creation fails
    """
    try:
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        print(f"🔄 Loading SentenceTransformer model ({EMBEDDING_MODEL})...")
        model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Extract text from documents
        doc_texts = [doc.page_content for doc in documents]
        
        print(f"🔄 Generating embeddings for {len(doc_texts)} documents (384-dim vectors)...")
        embeddings = model.encode(
            doc_texts,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Ensure embeddings are float32 for FAISS compatibility
        embeddings = embeddings.astype(np.float32)
        
        # Create FAISS index
        print(f"🔄 Creating FAISS IndexFlatL2...")
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        
        print(f"✓ FAISS index created successfully!")
        print(f"   - Embedding dimension: {dim}")
        print(f"   - Number of vectors: {index.ntotal}")
        
        return index, embeddings, documents, model
        
    except ValueError as e:
        print(f"❌ Validation Error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Error creating embeddings and FAISS index: {str(e)}")
        raise


# ============================================================================
# Stage 2: Persistence (Save to Disk)
# ============================================================================

def save_topics(
    topics: list,
    path: str
) -> None:
    """
    Save extracted topics to disk for validation during script generation.
    
    Args:
        topics (list): List of extracted topic strings
        path (str): Directory path where topics will be saved
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        topics_path = str(Path(path) / "topics.json")
        
        with open(topics_path, "w") as f:
            json.dump({"extracted_topics": topics}, f, indent=2)
        
        print(f"✓ Topics saved successfully! ({len(topics)} topics)")
        
    except Exception as e:
        print(f"❌ Error saving topics: {str(e)}")
        raise


def load_topics(path: str) -> list:
    """
    Load extracted topics from disk.
    
    Args:
        path (str): Directory path where topics are stored
        
    Returns:
        list: List of extracted topic strings, or empty list if not found
    """
    try:
        topics_path = Path(path) / "topics.json"
        if not topics_path.exists():
            return []
        
        with open(topics_path, "r") as f:
            data = json.load(f)
            return data.get("extracted_topics", [])
        
    except Exception as e:
        print(f"❌ Error loading topics: {str(e)}")
        return []


def clear_vectorstore(path: str) -> bool:
    """
    Clear all vectorstore files (restart flow).
    
    Args:
        path (str): Directory path to clear
        
    Returns:
        bool: True if cleared successfully, False otherwise
    """
    try:
        import shutil
        if Path(path).exists():
            shutil.rmtree(path)
            print(f"✓ Vectorstore cleared: {path}")
        return True
    except Exception as e:
        print(f"❌ Error clearing vectorstore: {str(e)}")
        return False


def save_faiss_index(
    index: faiss.IndexFlatL2,
    embeddings: np.ndarray,
    documents: List[Document],
    path: str
) -> None:
    """
    Save FAISS index, embeddings, and documents to disk for production use.
    
    This function persists:
    - faiss_index.bin: Serialized FAISS index for fast loading
    - embeddings.npy: NumPy array of all document vectors
    - documents.json: Document text content + metadata for reconstruction
    
    Args:
        index (faiss.IndexFlatL2): FAISS index to save
        embeddings (np.ndarray): Embeddings array of shape (num_docs, 384)
        documents (List[Document]): Documents with .page_content and .metadata
        path (str): Directory path where files will be saved
        
    Raises:
        Exception: If saving fails (permission, disk space, etc.)
    """
    try:
        # Create directory if it doesn't exist
        Path(path).mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = str(Path(path) / "faiss_index.bin")
        faiss.write_index(index, index_path)
        
        # Save embeddings as NumPy binary
        embeddings_path = str(Path(path) / "embeddings.npy")
        np.save(embeddings_path, embeddings)
        
        # Save documents as JSON for reference and reconstruction
        docs_path = str(Path(path) / "documents.json")
        docs_data = [
            {
                "text": doc.page_content,
                "metadata": doc.metadata if doc.metadata else {}
            }
            for doc in documents
        ]
        with open(docs_path, "w") as f:
            json.dump(docs_data, f, indent=2)
        
        print(f"✓ FAISS index and embeddings saved successfully!")
        print(f"   - Index: {index_path}")
        print(f"   - Embeddings: {embeddings_path}")
        print(f"   - Documents: {docs_path}")
        
    except Exception as e:
        print(f"❌ Error saving FAISS index: {str(e)}")
        raise


# ============================================================================
# Stage 3: Rehydration (Load from Disk)
# ============================================================================

def load_faiss_and_embeddings(
    path: str,
) -> Tuple[faiss.IndexFlatL2, np.ndarray, List[Document], SentenceTransformer]:
    """
    Load FAISS index, embeddings, and documents from disk for production inference.
    
    This function loads pre-computed vectors and index without rebuilding,
    enabling fast retrieval in new sessions without re-processing documents.
    
    Process:
    1. Check if FAISS index directory exists
    2. Load FAISS index from faiss_index.bin
    3. Load embeddings from embeddings.npy
    4. Load and reconstruct Document objects from documents.json
    5. Load embedding model for encoding new queries
    
    Args:
        path (str): Directory path where FAISS index is stored
        
    Returns:
        Tuple[faiss.IndexFlatL2, np.ndarray, List[Document], SentenceTransformer]:
            - index: FAISS index ready for searching
            - embeddings: NumPy array of shape (num_docs, 384)
            - documents: List of Document objects with original metadata
            - model: SentenceTransformer model for query encoding
    
    Raises:
        FileNotFoundError: If index directory or required files don't exist
        Exception: If loading or parsing fails
    """
    try:
        index_path = Path(path)
        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index directory not found at: {path}\n"
                "Run /api/extract-topics to create the vectorstore first."
            )
        
        print(f"🔄 Loading FAISS index and embeddings from {path}...")
        
        # Load FAISS index
        faiss_index_file = str(index_path / "faiss_index.bin")
        if not Path(faiss_index_file).exists():
            raise FileNotFoundError(f"FAISS index file not found: {faiss_index_file}")
        
        index = faiss.read_index(faiss_index_file)
        
        # Load embeddings
        embeddings_file = str(index_path / "embeddings.npy")
        if not Path(embeddings_file).exists():
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_file}")
        
        embeddings = np.load(embeddings_file)
        
        # Load documents
        docs_file = str(index_path / "documents.json")
        if not Path(docs_file).exists():
            raise FileNotFoundError(f"Documents file not found: {docs_file}")
        
        with open(docs_file, "r") as f:
            docs_data = json.load(f)
        
        # Reconstruct Document objects
        documents = [
            Document(
                page_content=doc["text"],
                metadata=doc.get("metadata", {})
            )
            for doc in docs_data
        ]
        
        # Load embedding model
        print(f"🔄 Loading SentenceTransformer model ({EMBEDDING_MODEL})...")
        model = SentenceTransformer(EMBEDDING_MODEL)
        
        print(f"✓ FAISS index and embeddings loaded successfully!")
        print(f"   - Number of vectors: {index.ntotal}")
        print(f"   - Embedding dimension: {embeddings.shape[1]}")
        print(f"   - Number of documents: {len(documents)}")
        
        return index, embeddings, documents, model
        
    except FileNotFoundError as e:
        print(f"❌ {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Error loading FAISS index: {str(e)}")
        raise


# ============================================================================
# Stage 4: Vector Search & Retrieval
# ============================================================================

def retrieve_top_k_chunks(
    query: str,
    k: int = 5
) -> List[Document]:
    """
    Retrieve top-K most relevant document chunks using FAISS similarity search.
    
    This function implements the complete retrieval pipeline:
    1. Encode query string to 384-dim vector using SentenceTransformer
    2. Perform L2 distance search in FAISS index
    3. Map returned indices to original documents
    4. Return document chunks with preserved metadata
    
    Args:
        query (str): User's search query or question
        k (int): Number of top results to retrieve (default: 5)
        
    Returns:
        List[Document]: Top-K Document objects with .page_content and .metadata intact
        
    Note:
        - Returns empty list if retrieval fails (no exception raised)
        - Uses L2 distance metric (lower distance = higher similarity)
        - Filters out invalid indices automatically
    """
    try:
        # Load index, embeddings, documents, and model
        index, embeddings, documents, model = load_faiss_and_embeddings(VECTORSTORE_PATH)
        
        # Encode query to 384-dim vector
        query_vector = model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True
        ).astype(np.float32)
        
        # Search FAISS index (L2 distance)
        distances, indices = index.search(query_vector, k)
        
        # Retrieve documents and filter valid indices
        retrieved_docs = [
            documents[idx]
            for idx in indices[0]
            if idx < len(documents) and idx >= 0
        ]
        
        return retrieved_docs
        
    except Exception as e:
        print(f"❌ Error retrieving chunks: {str(e)}")
        return []


# ============================================================================
# Backward Compatibility & Integration
# ============================================================================

def create_vectorstore(chunks: List[Document]):
    """
    Create FAISS vectorstore from document chunks.
    
    High-level wrapper that:
    1. Vectorizes chunks using SentenceTransformer
    2. Creates FAISS index
    3. Persists to disk
    
    Args:
        chunks (List[Document]): Document chunks to vectorize
        
    Returns:
        Tuple: (index, embeddings, documents, model) for further use
    """
    index, embeddings, documents, model = create_embeddings_and_faiss_index(chunks)
    save_faiss_index(index, embeddings, documents, VECTORSTORE_PATH)
    return index, embeddings, documents, model


def load_vectorstore():
    """
    Load existing FAISS vectorstore from disk.
    
    Returns:
        Tuple or None: (index, embeddings, documents, model) if exists, else None
    """
    try:
        return load_faiss_and_embeddings(VECTORSTORE_PATH)
    except FileNotFoundError:
        return None


def retrieve_context(query: str, k: int = 5) -> List[str]:
    """
    Retrieve relevant context (text content only) from vectorstore.
    
    Backward-compatible function that returns text content without metadata.
    
    Args:
        query (str): Search query
        k (int): Number of results (default: 5)
        
    Returns:
        List[str]: List of top-K document text content
    """
    retrieved_docs = retrieve_top_k_chunks(query, k)
    return [doc.page_content for doc in retrieved_docs]
