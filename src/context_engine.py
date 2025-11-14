"""
Context Engine - Main orchestrator for the local context engine.
Coordinates all components to provide context retrieval for AI coding assistants.
"""

import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from embeddings import Embedder
from vectordb import ChromaDBManager
from indexer import FileIndexer, Chunk
from retriever import ContextRetriever, RetrievalResult
from assembler import ContextAssembler, AssembledContext
from memory import MemoryManager


class ContextEngine:
    """Main context engine orchestrating all components."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the context engine.

        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self._setup_logging()

        # Initialize components
        self.logger.info("Initializing Context Engine components...")

        self.embedder = Embedder(
            model_name=self.config['embedding']['model_name'],
            device=self.config['embedding']['device']
        )

        self.vectordb = ChromaDBManager(
            persist_directory=self.config['vectordb']['persist_directory'],
            collection_name=self.config['vectordb']['collection_name'],
            distance_metric=self.config['vectordb']['distance_metric']
        )

        self.indexer = FileIndexer(
            chunk_size=self.config['indexer']['chunk_size'],
            chunk_overlap=self.config['indexer']['chunk_overlap'],
            supported_extensions=self.config['indexer']['supported_extensions'],
            exclude_patterns=self.config['indexer']['exclude_patterns']
        )

        self.retriever = ContextRetriever(
            embedder=self.embedder,
            vectordb=self.vectordb,
            top_k=self.config['retriever']['top_k'],
            similarity_threshold=self.config['retriever']['similarity_threshold'],
            rerank=self.config['retriever']['rerank']
        )

        self.assembler = ContextAssembler(
            max_tokens=self.config['assembler']['max_tokens'],
            compression_enabled=self.config['assembler']['compression_enabled'],
            include_metadata=self.config['assembler']['include_metadata'],
            ranking_strategy=self.config['assembler']['ranking_strategy']
        )

        self.memory = MemoryManager(
            session_directory=self.config['memory']['session_directory'],
            max_history_items=self.config['memory']['max_history_items'],
            save_interval=self.config['memory']['save_interval']
        )

        self.logger.info("Context Engine initialized successfully")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logging.error(f"Error loading config from {config_path}: {e}")
            raise

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config['logging']['level']
        log_file = self.config['logging']['file']

        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def index_directory(
        self,
        directory: str,
        recursive: bool = True,
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Index a directory of files.

        Args:
            directory: Directory path to index
            recursive: Whether to index subdirectories
            clear_existing: Whether to clear existing index first

        Returns:
            Indexing statistics
        """
        self.logger.info(f"Indexing directory: {directory}")

        if clear_existing:
            self.logger.info("Clearing existing index...")
            self.vectordb.clear()

        # Index files
        chunks = self.indexer.index_directory(directory, recursive=recursive)

        if not chunks:
            self.logger.warning("No chunks created from directory")
            return {'chunks_indexed': 0, 'files_indexed': 0}

        # Embed chunks
        self.logger.info(f"Embedding {len(chunks)} chunks...")
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_batch(
            chunk_texts,
            batch_size=self.config['embedding']['batch_size'],
            show_progress=True
        )

        # Store in vector database
        self.logger.info("Storing embeddings in vector database...")
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.id for chunk in chunks]

        self.vectordb.add_documents(
            documents=chunk_texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        # Calculate statistics
        unique_files = len(set(chunk.file_path for chunk in chunks))

        stats = {
            'chunks_indexed': len(chunks),
            'files_indexed': unique_files,
            'total_documents': self.vectordb.count()
        }

        self.logger.info(f"Indexing complete: {stats}")
        return stats

    def index_files(
        self,
        file_paths: List[str],
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Index specific files.

        Args:
            file_paths: List of file paths to index
            clear_existing: Whether to clear existing index first

        Returns:
            Indexing statistics
        """
        self.logger.info(f"Indexing {len(file_paths)} files")

        if clear_existing:
            self.vectordb.clear()

        all_chunks = []
        for file_path in file_paths:
            try:
                chunks = self.indexer.index_file(file_path)
                all_chunks.extend(chunks)
            except Exception as e:
                self.logger.warning(f"Failed to index {file_path}: {e}")

        if not all_chunks:
            return {'chunks_indexed': 0, 'files_indexed': 0}

        # Embed and store
        chunk_texts = [chunk.text for chunk in all_chunks]
        embeddings = self.embedder.embed_batch(chunk_texts, show_progress=True)

        self.vectordb.add_documents(
            documents=chunk_texts,
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in all_chunks],
            ids=[chunk.id for chunk in all_chunks]
        )

        return {
            'chunks_indexed': len(all_chunks),
            'files_indexed': len(file_paths),
            'total_documents': self.vectordb.count()
        }

    def index_conversation(
        self,
        messages: List[Dict[str, str]],
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Index a conversation history.

        Args:
            messages: List of message dicts
            conversation_id: Unique conversation ID

        Returns:
            Indexing statistics
        """
        self.logger.info(f"Indexing conversation: {conversation_id}")

        chunks = self.indexer.index_conversation(messages, conversation_id)

        if not chunks:
            return {'chunks_indexed': 0}

        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_batch(chunk_texts)

        self.vectordb.add_documents(
            documents=chunk_texts,
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
            ids=[chunk.id for chunk in chunks]
        )

        return {'chunks_indexed': len(chunks)}

    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_conversation: bool = True
    ) -> AssembledContext:
        """
        Query the context engine.

        Args:
            query: Query string
            top_k: Number of results to retrieve
            filter_metadata: Optional metadata filter
            include_conversation: Whether to include conversation history

        Returns:
            Assembled context ready for LLM
        """
        self.logger.info(f"Processing query: {query[:100]}...")

        # Retrieve relevant chunks
        results = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            filter_metadata=filter_metadata
        )

        # Get conversation history if enabled
        conversation_history = None
        if include_conversation and self.memory.current_session_id:
            conversation_history = self.memory.get_conversation_history(last_n=5)

        # Assemble context
        context = self.assembler.assemble(
            retrieval_results=results,
            query=query,
            conversation_history=conversation_history
        )

        # Store query in conversation history
        if self.memory.current_session_id:
            self.memory.add_message(
                role="user",
                content=query,
                metadata={'context_chunks': len(results)}
            )

        self.logger.info(f"Query complete: {len(results)} chunks retrieved")
        return context

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new conversation session.

        Args:
            session_id: Optional session ID

        Returns:
            Session ID
        """
        return self.memory.create_session(session_id)

    def load_session(self, session_id: str) -> bool:
        """
        Load an existing session.

        Args:
            session_id: Session ID to load

        Returns:
            True if loaded successfully
        """
        return self.memory.load_session(session_id)

    def add_response(self, response: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add an assistant response to the current session.

        Args:
            response: Response text
            metadata: Optional metadata
        """
        if self.memory.current_session_id:
            self.memory.add_message("assistant", response, metadata)

    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        return self.memory.get_session_stats()

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions."""
        return self.memory.list_sessions()

    def export_session(self, output_file: str, format: str = "json") -> bool:
        """
        Export current session.

        Args:
            output_file: Output file path
            format: Export format (json, txt)

        Returns:
            True if exported successfully
        """
        return self.memory.export_session(output_file, format=format)

    def get_stats(self) -> Dict[str, Any]:
        """Get overall engine statistics."""
        return {
            'total_documents': self.vectordb.count(),
            'embedding_model': self.config['embedding']['model_name'],
            'embedding_dimension': self.embedder.get_embedding_dimension(),
            'session_info': self.memory.get_session_stats() if self.memory.current_session_id else None
        }

    def clear_index(self):
        """Clear the entire vector database."""
        self.logger.warning("Clearing entire index...")
        self.vectordb.clear()
        self.logger.info("Index cleared")

    def reset(self):
        """Reset the entire engine (use with caution)."""
        self.logger.warning("Resetting entire engine...")
        self.vectordb.reset()
        self.memory.clear_history()
        self.logger.info("Engine reset complete")


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    # Initialize engine
    engine = ContextEngine(config_path="../config/config.yaml")

    # Create a test session
    session_id = engine.start_session()
    print(f"Started session: {session_id}")

    # Test indexing (create a test file)
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def hello_world():
    '''A simple hello world function.'''
    print('Hello, World!')

def add_numbers(a, b):
    '''Add two numbers together.'''
    return a + b

class Calculator:
    '''A simple calculator class.'''

    def multiply(self, x, y):
        return x * y
""")
        test_file = f.name

    # Index the test file
    stats = engine.index_files([test_file])
    print(f"\nIndexing stats: {stats}")

    # Query the engine
    context = engine.query("How do I add numbers?")
    print(f"\nQuery result:")
    print(f"Chunks used: {len(context.chunks_used)}")
    print(f"Tokens: ~{context.total_tokens}")
    print(f"\nContext preview:")
    print(context.context_text[:500])

    # Get engine stats
    engine_stats = engine.get_stats()
    print(f"\nEngine stats: {engine_stats}")

    # Cleanup
    os.unlink(test_file)
    engine.clear_index()
    print("\nTest completed")
