"""
Embedder Module - Generates vector embeddings from text using Sentence Transformers.
This module runs entirely locally without requiring external API calls.
"""

import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """Generates embeddings using local sentence transformer models."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """
        Initialize the embedder with a specific model.

        Args:
            model_name: Name of the sentence transformer model
            device: Device to run on ('cpu' or 'cuda')
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.device = device

        self.logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name, device=device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as numpy array
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            self.logger.error(f"Error embedding text: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar

        Returns:
            Array of embeddings
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            self.logger.error(f"Error embedding batch: {e}")
            raise

    def embed_documents(self, documents: List[dict], text_key: str = "text",
                       batch_size: int = 32) -> List[dict]:
        """
        Embed a list of documents, adding embeddings to each document dict.

        Args:
            documents: List of document dictionaries
            text_key: Key in document dict containing text to embed
            batch_size: Batch size for processing

        Returns:
            Documents with added 'embedding' key
        """
        texts = [doc[text_key] for doc in documents]
        embeddings = self.embed_batch(texts, batch_size=batch_size)

        for doc, embedding in zip(documents, embeddings):
            doc['embedding'] = embedding

        return documents

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score
        """
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.embedding_dim


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    embedder = Embedder()

    # Test single embedding
    text = "This is a test sentence for the context engine."
    embedding = embedder.embed_text(text)
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding dimension: {embedder.get_embedding_dimension()}")

    # Test batch embedding
    texts = [
        "First document about Python programming.",
        "Second document about machine learning.",
        "Third document about vector databases."
    ]
    embeddings = embedder.embed_batch(texts)
    print(f"Batch embeddings shape: {embeddings.shape}")

    # Test similarity
    similarity = embedder.similarity(embeddings[0], embeddings[1])
    print(f"Similarity between doc 1 and 2: {similarity:.4f}")
