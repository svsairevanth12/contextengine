"""
ChromaDB Manager - Handles vector storage and retrieval using ChromaDB.
ChromaDB is a lightweight, local vector database perfect for embedding storage.
"""

import logging
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
import numpy as np


class ChromaDBManager:
    """Manages vector storage and retrieval using ChromaDB."""

    def __init__(
        self,
        persist_directory: str = "./data/embeddings",
        collection_name: str = "context_store",
        distance_metric: str = "cosine"
    ):
        """
        Initialize ChromaDB manager.

        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
            distance_metric: Distance metric for similarity search (cosine, l2, ip)
        """
        self.logger = logging.getLogger(__name__)
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Map distance metrics to ChromaDB space names
        self.metric_map = {
            "cosine": "cosine",
            "l2": "l2",
            "ip": "ip"  # Inner product
        }
        self.distance_metric = self.metric_map.get(distance_metric, "cosine")

        self.logger.info(f"Initializing ChromaDB at {persist_directory}")
        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": self.distance_metric}
            )

            self.logger.info(f"Collection '{collection_name}' ready with {self.collection.count()} documents")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[np.ndarray],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents with their embeddings to the database.

        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts for each document
            ids: Optional list of IDs for documents (auto-generated if not provided)

        Returns:
            List of document IDs
        """
        try:
            # Generate IDs if not provided
            if ids is None:
                current_count = self.collection.count()
                ids = [f"doc_{current_count + i}" for i in range(len(documents))]

            # Convert numpy arrays to lists for ChromaDB
            embeddings_list = [emb.tolist() if isinstance(emb, np.ndarray) else emb
                              for emb in embeddings]

            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids
            )

            self.logger.info(f"Added {len(documents)} documents to collection")
            return ids

        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            raise

    def query(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List]:
        """
        Query the database for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        try:
            # Convert numpy array to list
            query_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding

            # Query collection
            results = self.collection.query(
                query_embeddings=[query_list],
                n_results=top_k,
                where=filter_metadata
            )

            # Flatten results (query returns nested lists)
            return {
                'ids': results['ids'][0] if results['ids'] else [],
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }

        except Exception as e:
            self.logger.error(f"Error querying database: {e}")
            raise

    def query_batch(
        self,
        query_embeddings: List[np.ndarray],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, List]]:
        """
        Query the database with multiple query embeddings.

        Args:
            query_embeddings: List of query embedding vectors
            top_k: Number of results per query
            filter_metadata: Optional metadata filter

        Returns:
            List of result dictionaries
        """
        try:
            # Convert numpy arrays to lists
            query_lists = [emb.tolist() if isinstance(emb, np.ndarray) else emb
                          for emb in query_embeddings]

            # Query collection
            results = self.collection.query(
                query_embeddings=query_lists,
                n_results=top_k,
                where=filter_metadata
            )

            # Reshape results
            batch_results = []
            for i in range(len(query_embeddings)):
                batch_results.append({
                    'ids': results['ids'][i] if results['ids'] else [],
                    'documents': results['documents'][i] if results['documents'] else [],
                    'metadatas': results['metadatas'][i] if results['metadatas'] else [],
                    'distances': results['distances'][i] if results['distances'] else []
                })

            return batch_results

        except Exception as e:
            self.logger.error(f"Error in batch query: {e}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs."""
        try:
            self.collection.delete(ids=ids)
            self.logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            self.logger.error(f"Error deleting documents: {e}")
            raise

    def update_document(
        self,
        doc_id: str,
        document: Optional[str] = None,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update a document's content, embedding, or metadata."""
        try:
            update_dict = {"ids": [doc_id]}

            if document is not None:
                update_dict["documents"] = [document]

            if embedding is not None:
                emb_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                update_dict["embeddings"] = [emb_list]

            if metadata is not None:
                update_dict["metadatas"] = [metadata]

            self.collection.update(**update_dict)
            self.logger.info(f"Updated document {doc_id}")

        except Exception as e:
            self.logger.error(f"Error updating document: {e}")
            raise

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a specific document by ID."""
        try:
            result = self.collection.get(ids=[doc_id], include=["documents", "metadatas", "embeddings"])

            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0] if result['documents'] else None,
                    'metadata': result['metadatas'][0] if result['metadatas'] else None,
                    'embedding': result['embeddings'][0] if result['embeddings'] else None
                }
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving document: {e}")
            raise

    def count(self) -> int:
        """Get the total number of documents in the collection."""
        return self.collection.count()

    def clear(self) -> None:
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_metric}
            )
            self.logger.info("Collection cleared")
        except Exception as e:
            self.logger.error(f"Error clearing collection: {e}")
            raise

    def reset(self) -> None:
        """Reset the entire database (use with caution)."""
        try:
            self.client.reset()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_metric}
            )
            self.logger.warning("Database reset completed")
        except Exception as e:
            self.logger.error(f"Error resetting database: {e}")
            raise


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    # Initialize manager
    manager = ChromaDBManager(persist_directory="./test_db")

    # Create sample embeddings
    embeddings = [
        np.random.rand(384).astype(np.float32),
        np.random.rand(384).astype(np.float32),
        np.random.rand(384).astype(np.float32)
    ]

    documents = [
        "This is a Python function for data processing.",
        "JavaScript code for frontend development.",
        "SQL query for database operations."
    ]

    metadatas = [
        {"type": "code", "language": "python", "file": "data.py"},
        {"type": "code", "language": "javascript", "file": "app.js"},
        {"type": "code", "language": "sql", "file": "queries.sql"}
    ]

    # Add documents
    ids = manager.add_documents(documents, embeddings, metadatas)
    print(f"Added documents with IDs: {ids}")

    # Query
    query_emb = np.random.rand(384).astype(np.float32)
    results = manager.query(query_emb, top_k=2)
    print(f"\nQuery results: {len(results['documents'])} documents found")

    # Cleanup
    manager.clear()
    print("Test completed and cleaned up")
