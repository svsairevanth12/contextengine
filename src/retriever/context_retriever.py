"""
Context Retriever - Performs semantic search and retrieves relevant context.
Combines vector search with optional metadata filtering and reranking.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass


@dataclass
class RetrievalResult:
    """Represents a retrieved document with relevance information."""
    id: str
    text: str
    metadata: Dict[str, Any]
    similarity_score: float
    rank: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'text': self.text,
            'metadata': self.metadata,
            'similarity_score': self.similarity_score,
            'rank': self.rank
        }


class ContextRetriever:
    """Retrieves relevant context using semantic search."""

    def __init__(
        self,
        embedder,
        vectordb,
        top_k: int = 10,
        similarity_threshold: float = 0.3,
        rerank: bool = True
    ):
        """
        Initialize the context retriever.

        Args:
            embedder: Embedder instance for encoding queries
            vectordb: Vector database instance for searching
            top_k: Number of results to retrieve
            similarity_threshold: Minimum similarity score for results
            rerank: Whether to apply reranking
        """
        self.logger = logging.getLogger(__name__)
        self.embedder = embedder
        self.vectordb = vectordb
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.rerank = rerank

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        expand_context: bool = False
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant context for a query.

        Args:
            query: Query string
            top_k: Number of results (overrides default)
            filter_metadata: Optional metadata filter
            expand_context: Whether to include surrounding chunks

        Returns:
            List of retrieval results sorted by relevance
        """
        k = top_k or self.top_k

        try:
            # Embed the query
            self.logger.debug(f"Embedding query: {query[:100]}...")
            query_embedding = self.embedder.embed_text(query)

            # Search vector database
            self.logger.debug(f"Searching for top {k} results")
            search_results = self.vectordb.query(
                query_embedding=query_embedding,
                top_k=k * 2 if self.rerank else k,  # Get more if reranking
                filter_metadata=filter_metadata
            )

            # Convert to RetrievalResult objects
            results = []
            for i, (doc_id, doc_text, metadata, distance) in enumerate(zip(
                search_results['ids'],
                search_results['documents'],
                search_results['metadatas'],
                search_results['distances']
            )):
                # Convert distance to similarity score (for cosine distance)
                # ChromaDB returns cosine distance, we want similarity
                similarity = 1.0 - distance

                # Filter by threshold
                if similarity >= self.similarity_threshold:
                    results.append(RetrievalResult(
                        id=doc_id,
                        text=doc_text,
                        metadata=metadata or {},
                        similarity_score=similarity,
                        rank=i
                    ))

            # Rerank if enabled
            if self.rerank and len(results) > 0:
                results = self._rerank_results(query, results, query_embedding)

            # Limit to top_k
            results = results[:k]

            # Expand context if requested
            if expand_context:
                results = self._expand_context(results)

            self.logger.info(f"Retrieved {len(results)} results for query")
            return results

        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}")
            raise

    def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[List[RetrievalResult]]:
        """
        Retrieve context for multiple queries.

        Args:
            queries: List of query strings
            top_k: Number of results per query
            filter_metadata: Optional metadata filter

        Returns:
            List of result lists, one per query
        """
        k = top_k or self.top_k

        try:
            # Embed all queries
            self.logger.debug(f"Embedding {len(queries)} queries")
            query_embeddings = self.embedder.embed_batch(queries)

            # Search vector database
            batch_search_results = self.vectordb.query_batch(
                query_embeddings=query_embeddings,
                top_k=k,
                filter_metadata=filter_metadata
            )

            # Convert to RetrievalResult objects
            all_results = []
            for search_results in batch_search_results:
                results = []
                for i, (doc_id, doc_text, metadata, distance) in enumerate(zip(
                    search_results['ids'],
                    search_results['documents'],
                    search_results['metadatas'],
                    search_results['distances']
                )):
                    similarity = 1.0 - distance

                    if similarity >= self.similarity_threshold:
                        results.append(RetrievalResult(
                            id=doc_id,
                            text=doc_text,
                            metadata=metadata or {},
                            similarity_score=similarity,
                            rank=i
                        ))

                all_results.append(results)

            self.logger.info(f"Retrieved results for {len(queries)} queries")
            return all_results

        except Exception as e:
            self.logger.error(f"Error in batch retrieval: {e}")
            raise

    def retrieve_similar_to_document(
        self,
        doc_id: str,
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Find documents similar to a given document.

        Args:
            doc_id: ID of the document to find similar documents for
            top_k: Number of results

        Returns:
            List of similar documents
        """
        k = top_k or self.top_k

        try:
            # Get the document's embedding
            doc = self.vectordb.get_document(doc_id)
            if not doc or not doc.get('embedding'):
                self.logger.error(f"Document {doc_id} not found or has no embedding")
                return []

            embedding = np.array(doc['embedding'])

            # Search for similar documents
            search_results = self.vectordb.query(
                query_embedding=embedding,
                top_k=k + 1  # +1 to exclude the document itself
            )

            # Convert to results, excluding the original document
            results = []
            for i, (result_id, doc_text, metadata, distance) in enumerate(zip(
                search_results['ids'],
                search_results['documents'],
                search_results['metadatas'],
                search_results['distances']
            )):
                if result_id != doc_id:  # Exclude self
                    similarity = 1.0 - distance
                    results.append(RetrievalResult(
                        id=result_id,
                        text=doc_text,
                        metadata=metadata or {},
                        similarity_score=similarity,
                        rank=len(results)
                    ))

            return results[:k]

        except Exception as e:
            self.logger.error(f"Error finding similar documents: {e}")
            raise

    def _rerank_results(
        self,
        query: str,
        results: List[RetrievalResult],
        query_embedding: np.ndarray
    ) -> List[RetrievalResult]:
        """
        Rerank results using additional signals.

        Args:
            query: Original query
            results: Initial retrieval results
            query_embedding: Query embedding vector

        Returns:
            Reranked results
        """
        # For now, use a simple scoring combination
        # In production, you might use a cross-encoder or other reranking model

        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for result in results:
            # Compute keyword overlap score
            text_lower = result.text.lower()
            text_terms = set(text_lower.split())
            overlap = len(query_terms & text_terms) / max(len(query_terms), 1)

            # Combine with similarity score
            # 70% semantic similarity, 30% keyword overlap
            combined_score = 0.7 * result.similarity_score + 0.3 * overlap
            result.similarity_score = combined_score

        # Re-sort by combined score
        results.sort(key=lambda x: x.similarity_score, reverse=True)

        # Update ranks
        for i, result in enumerate(results):
            result.rank = i

        return results

    def _expand_context(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Expand results by including surrounding chunks.

        Args:
            results: Initial retrieval results

        Returns:
            Expanded results with context
        """
        # Group results by file
        file_groups: Dict[str, List[RetrievalResult]] = {}
        for result in results:
            file_path = result.metadata.get('file_path', '')
            if file_path:
                if file_path not in file_groups:
                    file_groups[file_path] = []
                file_groups[file_path].append(result)

        # For each file, try to get adjacent chunks
        # This is a simplified implementation
        # In production, you'd query the DB for adjacent chunk indices

        # For now, just return original results
        # Full implementation would require storing and retrieving adjacent chunks
        return results

    def retrieve_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve documents by metadata only (no semantic search).

        Args:
            metadata_filter: Metadata filter criteria
            top_k: Number of results

        Returns:
            List of matching documents
        """
        # This would require ChromaDB's get() method with where clause
        # For now, we'll do a dummy query and filter
        # In production, use proper metadata-only retrieval

        k = top_k or self.top_k
        results = []

        # Create a neutral embedding for broad search
        neutral_query = "retrieve documents"
        query_embedding = self.embedder.embed_text(neutral_query)

        search_results = self.vectordb.query(
            query_embedding=query_embedding,
            top_k=k,
            filter_metadata=metadata_filter
        )

        for i, (doc_id, doc_text, metadata, distance) in enumerate(zip(
            search_results['ids'],
            search_results['documents'],
            search_results['metadatas'],
            search_results['distances']
        )):
            results.append(RetrievalResult(
                id=doc_id,
                text=doc_text,
                metadata=metadata or {},
                similarity_score=1.0,  # Not based on similarity
                rank=i
            ))

        return results


if __name__ == "__main__":
    # Simple test (requires other modules)
    import sys
    sys.path.append('..')

    from embeddings import Embedder
    from vectordb import ChromaDBManager

    logging.basicConfig(level=logging.INFO)

    # Initialize components
    embedder = Embedder()
    vectordb = ChromaDBManager(persist_directory="./test_retriever_db")
    retriever = ContextRetriever(embedder, vectordb, top_k=3)

    # Add some test documents
    test_docs = [
        "Python is a high-level programming language.",
        "JavaScript is used for web development.",
        "Machine learning uses algorithms to learn from data.",
        "Vector databases store embeddings for semantic search.",
        "Context engines help AI assistants find relevant information."
    ]

    embeddings = embedder.embed_batch(test_docs)
    vectordb.add_documents(
        documents=test_docs,
        embeddings=embeddings,
        metadatas=[{"type": "test", "index": i} for i in range(len(test_docs))]
    )

    # Test retrieval
    query = "How do vector databases work?"
    results = retriever.retrieve(query)

    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")
    for result in results:
        print(f"[{result.rank}] Score: {result.similarity_score:.3f}")
        print(f"    {result.text[:100]}")
        print()

    # Cleanup
    vectordb.clear()
    print("Test completed")
