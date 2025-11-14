"""
Context Assembler - Ranks, prunes, and assembles optimal context for LLM queries.
Manages token budgets and intelligently combines retrieved chunks.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class AssembledContext:
    """Represents assembled context ready for LLM consumption."""
    context_text: str
    chunks_used: List[Dict[str, Any]]
    total_tokens: int
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'context_text': self.context_text,
            'chunks_used': self.chunks_used,
            'total_tokens': self.total_tokens,
            'metadata': self.metadata
        }


class ContextAssembler:
    """Assembles and optimizes context from retrieved chunks."""

    def __init__(
        self,
        max_tokens: int = 4000,
        compression_enabled: bool = True,
        include_metadata: bool = True,
        ranking_strategy: str = "hybrid"
    ):
        """
        Initialize the context assembler.

        Args:
            max_tokens: Maximum tokens for assembled context
            compression_enabled: Whether to compress older/less relevant content
            include_metadata: Whether to include file paths and line numbers
            ranking_strategy: Strategy for ranking chunks (hybrid, similarity, recency)
        """
        self.logger = logging.getLogger(__name__)
        self.max_tokens = max_tokens
        self.compression_enabled = compression_enabled
        self.include_metadata = include_metadata
        self.ranking_strategy = ranking_strategy

        # Rough token estimation: ~4 chars per token for English
        self.chars_per_token = 4

    def assemble(
        self,
        retrieval_results: List,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AssembledContext:
        """
        Assemble context from retrieval results.

        Args:
            retrieval_results: List of RetrievalResult objects
            query: Original query
            conversation_history: Optional conversation history

        Returns:
            Assembled context object
        """
        try:
            # Rank chunks according to strategy
            ranked_chunks = self._rank_chunks(retrieval_results, query)

            # Deduplicate similar chunks
            unique_chunks = self._deduplicate_chunks(ranked_chunks)

            # Group chunks by source file
            grouped_chunks = self._group_by_source(unique_chunks)

            # Assemble context within token budget
            context_text, chunks_used = self._build_context(
                grouped_chunks,
                query,
                conversation_history
            )

            # Estimate token count
            token_count = self._estimate_tokens(context_text)

            metadata = {
                'query': query,
                'chunks_count': len(chunks_used),
                'sources_count': len(grouped_chunks),
                'ranking_strategy': self.ranking_strategy,
                'timestamp': datetime.now().isoformat()
            }

            self.logger.info(
                f"Assembled context: {len(chunks_used)} chunks, "
                f"~{token_count} tokens from {len(grouped_chunks)} sources"
            )

            return AssembledContext(
                context_text=context_text,
                chunks_used=chunks_used,
                total_tokens=token_count,
                metadata=metadata
            )

        except Exception as e:
            self.logger.error(f"Error assembling context: {e}")
            raise

    def _rank_chunks(self, chunks: List, query: str) -> List:
        """
        Rank chunks according to the selected strategy.

        Args:
            chunks: List of retrieval results
            query: Query string

        Returns:
            Ranked list of chunks
        """
        if self.ranking_strategy == "similarity":
            # Already sorted by similarity from retriever
            return chunks

        elif self.ranking_strategy == "recency":
            # Sort by recency (if timestamp available)
            return sorted(
                chunks,
                key=lambda x: x.metadata.get('timestamp', 0),
                reverse=True
            )

        elif self.ranking_strategy == "hybrid":
            # Combine similarity and other signals
            query_terms = set(query.lower().split())

            for chunk in chunks:
                # Base score from similarity
                score = chunk.similarity_score

                # Boost for keyword matches
                text_lower = chunk.text.lower()
                keyword_matches = sum(1 for term in query_terms if term in text_lower)
                keyword_boost = min(keyword_matches * 0.1, 0.3)
                score += keyword_boost

                # Boost for code files (often more relevant for coding assistants)
                if chunk.metadata.get('is_code', False):
                    score += 0.05

                # Store combined score
                chunk.combined_score = score

            # Sort by combined score
            return sorted(chunks, key=lambda x: x.combined_score, reverse=True)

        return chunks

    def _deduplicate_chunks(self, chunks: List) -> List:
        """
        Remove duplicate or highly similar chunks.

        Args:
            chunks: List of chunks

        Returns:
            Deduplicated list
        """
        unique_chunks = []
        seen_texts = set()

        for chunk in chunks:
            # Create a normalized version for comparison
            normalized = self._normalize_text(chunk.text)

            if normalized not in seen_texts:
                unique_chunks.append(chunk)
                seen_texts.add(normalized)

        self.logger.debug(f"Deduplicated {len(chunks)} to {len(unique_chunks)} chunks")
        return unique_chunks

    def _normalize_text(self, text: str) -> str:
        """Normalize text for deduplication."""
        # Remove extra whitespace and lowercase
        return re.sub(r'\s+', ' ', text.lower()).strip()

    def _group_by_source(self, chunks: List) -> Dict[str, List]:
        """
        Group chunks by their source file.

        Args:
            chunks: List of chunks

        Returns:
            Dictionary mapping source files to chunks
        """
        grouped = {}

        for chunk in chunks:
            source = chunk.metadata.get('file_path', 'unknown')

            if source not in grouped:
                grouped[source] = []

            grouped[source].append(chunk)

        # Sort chunks within each group by chunk_index if available
        for source in grouped:
            grouped[source].sort(
                key=lambda x: x.metadata.get('chunk_index', 0)
            )

        return grouped

    def _build_context(
        self,
        grouped_chunks: Dict[str, List],
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Build the final context string within token budget.

        Args:
            grouped_chunks: Chunks grouped by source
            query: Query string
            conversation_history: Optional conversation history

        Returns:
            Tuple of (context_text, chunks_used)
        """
        context_parts = []
        chunks_used = []
        current_tokens = 0

        # Reserve tokens for query and conversation history
        reserved_tokens = self._estimate_tokens(query)
        if conversation_history:
            history_text = self._format_conversation_history(conversation_history)
            reserved_tokens += self._estimate_tokens(history_text)

        available_tokens = self.max_tokens - reserved_tokens - 100  # 100 token buffer

        # Add context from each source
        for source, chunks in grouped_chunks.items():
            if current_tokens >= available_tokens:
                break

            # Add source header if metadata is enabled
            if self.include_metadata:
                source_header = f"\n{'='*60}\nSource: {source}\n{'='*60}\n"
                header_tokens = self._estimate_tokens(source_header)

                if current_tokens + header_tokens < available_tokens:
                    context_parts.append(source_header)
                    current_tokens += header_tokens

            # Add chunks from this source
            for chunk in chunks:
                chunk_text = self._format_chunk(chunk)
                chunk_tokens = self._estimate_tokens(chunk_text)

                # Check if we have room
                if current_tokens + chunk_tokens > available_tokens:
                    # Try compression if enabled
                    if self.compression_enabled:
                        compressed = self._compress_chunk(chunk)
                        compressed_tokens = self._estimate_tokens(compressed)

                        if current_tokens + compressed_tokens <= available_tokens:
                            context_parts.append(compressed)
                            current_tokens += compressed_tokens
                            chunks_used.append(chunk.to_dict())
                    break
                else:
                    context_parts.append(chunk_text)
                    current_tokens += chunk_tokens
                    chunks_used.append(chunk.to_dict())

        # Combine all parts
        context_text = '\n'.join(context_parts)

        return context_text, chunks_used

    def _format_chunk(self, chunk) -> str:
        """
        Format a chunk for inclusion in context.

        Args:
            chunk: Chunk object

        Returns:
            Formatted chunk text
        """
        parts = []

        if self.include_metadata:
            # Add metadata header
            file_name = chunk.metadata.get('file_name', 'unknown')
            start_line = chunk.metadata.get('start_line', 0)
            end_line = chunk.metadata.get('end_line', 0)

            parts.append(f"## {file_name} (lines {start_line}-{end_line})")
            parts.append(f"Relevance: {chunk.similarity_score:.2f}\n")

        parts.append(chunk.text)
        parts.append("")  # Empty line separator

        return '\n'.join(parts)

    def _compress_chunk(self, chunk) -> str:
        """
        Compress a chunk by summarizing or truncating.

        Args:
            chunk: Chunk to compress

        Returns:
            Compressed text
        """
        # Simple compression: take first and last few lines
        lines = chunk.text.split('\n')

        if len(lines) > 10:
            compressed_lines = lines[:5] + ['...'] + lines[-3:]
            compressed_text = '\n'.join(compressed_lines)

            if self.include_metadata:
                file_name = chunk.metadata.get('file_name', 'unknown')
                return f"## {file_name} (compressed)\n{compressed_text}\n"
            return compressed_text

        return chunk.text

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for context."""
        parts = ["## Recent Conversation\n"]

        for msg in history[-5:]:  # Last 5 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            parts.append(f"**{role.upper()}**: {content}\n")

        return '\n'.join(parts)

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Simple estimation: chars / chars_per_token
        return max(1, len(text) // self.chars_per_token)

    def assemble_for_indexing(self, chunks: List) -> str:
        """
        Assemble chunks for indexing purposes (no token limit).

        Args:
            chunks: List of chunks

        Returns:
            Combined text
        """
        return '\n\n'.join([chunk.text for chunk in chunks])

    def create_summary(self, context: AssembledContext) -> str:
        """
        Create a summary of the assembled context.

        Args:
            context: Assembled context object

        Returns:
            Summary text
        """
        summary_parts = [
            f"Context Summary:",
            f"- Chunks used: {len(context.chunks_used)}",
            f"- Total tokens: ~{context.total_tokens}",
            f"- Sources: {context.metadata.get('sources_count', 0)}",
            f"- Query: {context.metadata.get('query', 'N/A')[:50]}..."
        ]

        return '\n'.join(summary_parts)


if __name__ == "__main__":
    # Simple test
    import sys
    sys.path.append('..')

    from retriever import RetrievalResult

    logging.basicConfig(level=logging.INFO)

    # Create mock retrieval results
    results = [
        RetrievalResult(
            id="chunk_1",
            text="This is the first chunk of code.\ndef hello():\n    print('Hello')",
            metadata={
                'file_path': 'test.py',
                'file_name': 'test.py',
                'start_line': 1,
                'end_line': 3,
                'is_code': True
            },
            similarity_score=0.92,
            rank=0
        ),
        RetrievalResult(
            id="chunk_2",
            text="This is documentation.\nExplains how to use the function.",
            metadata={
                'file_path': 'README.md',
                'file_name': 'README.md',
                'start_line': 10,
                'end_line': 12
            },
            similarity_score=0.85,
            rank=1
        )
    ]

    # Assemble context
    assembler = ContextAssembler(max_tokens=2000)
    context = assembler.assemble(results, query="How to use hello function?")

    print(assembler.create_summary(context))
    print("\nAssembled Context:")
    print(context.context_text)
