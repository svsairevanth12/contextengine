"""
File Indexer - Parses, chunks, and indexes files and documents.
Supports various file types and intelligent chunking strategies for code and text.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import fnmatch
import hashlib
from dataclasses import dataclass, asdict


@dataclass
class Chunk:
    """Represents a chunk of text from a file."""
    id: str
    text: str
    file_path: str
    start_line: int
    end_line: int
    chunk_index: int
    file_type: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return asdict(self)


class FileIndexer:
    """Indexes files and creates searchable chunks."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
        supported_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ):
        """
        Initialize the file indexer.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
            supported_extensions: List of file extensions to index
            exclude_patterns: Glob patterns for files/directories to exclude
        """
        self.logger = logging.getLogger(__name__)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.supported_extensions = supported_extensions or [
            ".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs",
            ".md", ".txt", ".json", ".yaml", ".yml"
        ]

        self.exclude_patterns = exclude_patterns or [
            "**/node_modules/**", "**/.git/**", "**/__pycache__/**",
            "**/dist/**", "**/build/**", "**/.venv/**", "**/venv/**"
        ]

    def should_index_file(self, file_path: str) -> bool:
        """
        Check if a file should be indexed.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be indexed
        """
        # Check extension
        _, ext = os.path.splitext(file_path)
        if ext not in self.supported_extensions:
            return False

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return False

        return True

    def index_directory(
        self,
        directory: str,
        recursive: bool = True
    ) -> List[Chunk]:
        """
        Index all supported files in a directory.

        Args:
            directory: Directory path to index
            recursive: Whether to index subdirectories

        Returns:
            List of chunks from all indexed files
        """
        all_chunks = []
        directory_path = Path(directory)

        if not directory_path.exists():
            self.logger.error(f"Directory not found: {directory}")
            return all_chunks

        # Find all files to index
        if recursive:
            files = directory_path.rglob("*")
        else:
            files = directory_path.glob("*")

        indexed_count = 0
        for file_path in files:
            if file_path.is_file():
                file_str = str(file_path)
                if self.should_index_file(file_str):
                    try:
                        chunks = self.index_file(file_str)
                        all_chunks.extend(chunks)
                        indexed_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to index {file_str}: {e}")

        self.logger.info(f"Indexed {indexed_count} files, created {len(all_chunks)} chunks")
        return all_chunks

    def index_file(self, file_path: str) -> List[Chunk]:
        """
        Index a single file and create chunks.

        Args:
            file_path: Path to the file

        Returns:
            List of chunks from the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            _, ext = os.path.splitext(file_path)
            file_type = ext[1:] if ext else "unknown"

            # Determine chunking strategy based on file type
            if ext in [".md", ".txt"]:
                chunks = self._chunk_text(content, file_path, file_type)
            elif ext in [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"]:
                chunks = self._chunk_code(content, file_path, file_type)
            else:
                chunks = self._chunk_text(content, file_path, file_type)

            return chunks

        except Exception as e:
            self.logger.error(f"Error indexing file {file_path}: {e}")
            raise

    def _chunk_text(self, content: str, file_path: str, file_type: str) -> List[Chunk]:
        """
        Chunk text files using sliding window approach.

        Args:
            content: File content
            file_path: Path to the file
            file_type: Type of file

        Returns:
            List of chunks
        """
        chunks = []
        lines = content.split('\n')

        # Create chunks with overlap
        current_chunk = []
        current_size = 0
        chunk_index = 0
        start_line = 0

        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline

            if current_size + line_size > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = '\n'.join(current_chunk)
                chunk_id = self._generate_chunk_id(file_path, chunk_index)

                chunks.append(Chunk(
                    id=chunk_id,
                    text=chunk_text,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=i,
                    chunk_index=chunk_index,
                    file_type=file_type,
                    metadata={
                        "file_name": os.path.basename(file_path),
                        "size": len(chunk_text)
                    }
                ))

                # Create overlap for next chunk
                overlap_size = 0
                overlap_lines = []
                for line_idx in range(len(current_chunk) - 1, -1, -1):
                    line_len = len(current_chunk[line_idx]) + 1
                    if overlap_size + line_len <= self.chunk_overlap:
                        overlap_lines.insert(0, current_chunk[line_idx])
                        overlap_size += line_len
                    else:
                        break

                current_chunk = overlap_lines + [line]
                current_size = sum(len(l) + 1 for l in current_chunk)
                start_line = i - len(overlap_lines)
                chunk_index += 1
            else:
                current_chunk.append(line)
                current_size += line_size

        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunk_id = self._generate_chunk_id(file_path, chunk_index)

            chunks.append(Chunk(
                id=chunk_id,
                text=chunk_text,
                file_path=file_path,
                start_line=start_line,
                end_line=len(lines),
                chunk_index=chunk_index,
                file_type=file_type,
                metadata={
                    "file_name": os.path.basename(file_path),
                    "size": len(chunk_text)
                }
            ))

        return chunks

    def _chunk_code(self, content: str, file_path: str, file_type: str) -> List[Chunk]:
        """
        Chunk code files with awareness of logical boundaries.

        Args:
            content: File content
            file_path: Path to the file
            file_type: Type of file

        Returns:
            List of chunks
        """
        # For now, use the same text chunking strategy
        # In a production system, you might use AST parsing for better code-aware chunking
        chunks = self._chunk_text(content, file_path, file_type)

        # Add code-specific metadata
        for chunk in chunks:
            chunk.metadata.update({
                "is_code": True,
                "language": file_type
            })

        return chunks

    def _generate_chunk_id(self, file_path: str, chunk_index: int) -> str:
        """
        Generate a unique ID for a chunk.

        Args:
            file_path: Path to the file
            chunk_index: Index of the chunk in the file

        Returns:
            Unique chunk ID
        """
        # Create hash of file path + chunk index
        content = f"{file_path}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()

    def index_conversation(
        self,
        messages: List[Dict[str, str]],
        conversation_id: str
    ) -> List[Chunk]:
        """
        Index a conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            conversation_id: Unique ID for the conversation

        Returns:
            List of chunks from the conversation
        """
        chunks = []

        for i, message in enumerate(messages):
            role = message.get('role', 'unknown')
            content = message.get('content', '')

            if not content:
                continue

            # Each message becomes its own chunk
            chunk_id = self._generate_chunk_id(f"conversation_{conversation_id}", i)

            chunks.append(Chunk(
                id=chunk_id,
                text=f"[{role}]: {content}",
                file_path=f"conversation://{conversation_id}",
                start_line=i,
                end_line=i,
                chunk_index=i,
                file_type="conversation",
                metadata={
                    "role": role,
                    "message_index": i,
                    "conversation_id": conversation_id
                }
            ))

        self.logger.info(f"Indexed conversation {conversation_id} with {len(chunks)} messages")
        return chunks


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    indexer = FileIndexer(chunk_size=200, chunk_overlap=50)

    # Test text chunking
    test_text = """This is a test document.
It has multiple lines.
We want to test the chunking functionality.
Each chunk should have some overlap with the next.
This helps maintain context when searching.
""" * 5

    # Create a temporary test file
    test_file = "/tmp/test_index.txt"
    with open(test_file, 'w') as f:
        f.write(test_text)

    # Index the file
    chunks = indexer.index_file(test_file)
    print(f"Created {len(chunks)} chunks from test file")

    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"\nChunk {i}:")
        print(f"  Lines: {chunk.start_line}-{chunk.end_line}")
        print(f"  Size: {len(chunk.text)} chars")
        print(f"  Preview: {chunk.text[:100]}...")

    # Clean up
    os.remove(test_file)
    print("\nTest completed")
