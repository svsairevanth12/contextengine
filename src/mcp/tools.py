"""
MCP Tools - Implements tool handlers for the Context Engine MCP server.
Provides semantic search, indexing, and context retrieval capabilities.
"""

import logging
from typing import Dict, Any, List, Optional


class MCPTools:
    """Implements MCP tools for context engine operations."""

    def __init__(self, context_engine):
        """
        Initialize MCP tools.

        Args:
            context_engine: ContextEngine instance
        """
        self.engine = context_engine
        self.logger = logging.getLogger(__name__)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get list of available tool definitions for MCP."""
        return [
            {
                "name": "search_codebase",
                "description": "Semantically search the indexed codebase for relevant code snippets, functions, classes, or documentation. Returns chunks with file paths, line numbers, and relevance scores.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'authentication middleware', 'database connection', 'error handling')"
                        },
                        "top_k": {
                            "type": "number",
                            "description": "Number of results to return (default: 10)",
                            "default": 10
                        },
                        "language": {
                            "type": "string",
                            "description": "Filter by programming language (e.g., 'python', 'javascript')",
                            "default": None
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_file_context",
                "description": "Get all indexed chunks from a specific file with full context. Useful when you need to understand an entire file's contents.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file (relative or absolute)"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "find_similar_code",
                "description": "Find code files similar to a given file. Useful for discovering related implementations, patterns, or dependencies.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the reference file"
                        },
                        "top_k": {
                            "type": "number",
                            "description": "Number of similar files to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "index_paths",
                "description": "Index or reindex specific files or directories. Use this to add new code to the searchable index or update existing code.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file or directory paths to index"
                        },
                        "clear_existing": {
                            "type": "boolean",
                            "description": "Clear existing index before indexing (default: false)",
                            "default": False
                        }
                    },
                    "required": ["paths"]
                }
            },
            {
                "name": "get_codebase_stats",
                "description": "Get statistics about the indexed codebase including total files, chunks, languages, and last index time.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "search_by_file_type",
                "description": "Search within specific file types or languages. Useful when you want to focus on specific parts of the codebase.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "file_type": {
                            "type": "string",
                            "description": "File extension (e.g., '.py', '.js') or language name"
                        },
                        "top_k": {
                            "type": "number",
                            "description": "Number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query", "file_type"]
                }
            },
            {
                "name": "find_definitions",
                "description": "Search for class, function, or variable definitions. Optimized for finding where things are defined.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the class, function, or variable to find"
                        },
                        "type": {
                            "type": "string",
                            "description": "Type of definition: 'class', 'function', 'variable', or 'any'",
                            "default": "any"
                        }
                    },
                    "required": ["name"]
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call from the MCP client.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            if tool_name == "search_codebase":
                return self._search_codebase(**arguments)
            elif tool_name == "get_file_context":
                return self._get_file_context(**arguments)
            elif tool_name == "find_similar_code":
                return self._find_similar_code(**arguments)
            elif tool_name == "index_paths":
                return self._index_paths(**arguments)
            elif tool_name == "get_codebase_stats":
                return self._get_codebase_stats()
            elif tool_name == "search_by_file_type":
                return self._search_by_file_type(**arguments)
            elif tool_name == "find_definitions":
                return self._find_definitions(**arguments)
            else:
                return {
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": [t["name"] for t in self.get_tool_definitions()]
                }

        except Exception as e:
            self.logger.error(f"Error handling tool call {tool_name}: {e}")
            return {
                "error": str(e),
                "tool": tool_name,
                "arguments": arguments
            }

    def _search_codebase(
        self,
        query: str,
        top_k: int = 10,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search the codebase semantically."""
        self.logger.info(f"Searching codebase: {query} (top_k={top_k}, language={language})")

        # Build metadata filter
        filter_metadata = {}
        if language:
            filter_metadata["language"] = language

        # Query the engine
        context = self.engine.query(
            query=query,
            top_k=top_k,
            filter_metadata=filter_metadata if filter_metadata else None,
            include_conversation=False
        )

        # Format results for agent consumption
        results = []
        for chunk in context.chunks_used:
            metadata = chunk.get('metadata', {})
            results.append({
                "file_path": metadata.get('file_path', 'unknown'),
                "file_name": metadata.get('file_name', 'unknown'),
                "start_line": metadata.get('start_line', 0),
                "end_line": metadata.get('end_line', 0),
                "relevance_score": chunk.get('similarity_score', 0.0),
                "language": metadata.get('language', metadata.get('file_type', 'unknown')),
                "content": chunk.get('text', ''),
                "is_code": metadata.get('is_code', False)
            })

        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results,
            "total_tokens": context.total_tokens
        }

    def _get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get all chunks from a specific file."""
        self.logger.info(f"Getting file context: {file_path}")

        # Search for chunks from this file
        # We use a broad query and filter by file path
        context = self.engine.query(
            query=f"file content from {file_path}",
            top_k=100,  # Get many chunks
            include_conversation=False
        )

        # Filter to only chunks from this file
        file_chunks = [
            chunk for chunk in context.chunks_used
            if file_path in chunk.get('metadata', {}).get('file_path', '')
        ]

        # Sort by line number
        file_chunks.sort(key=lambda x: x.get('metadata', {}).get('start_line', 0))

        # Format results
        chunks = []
        for chunk in file_chunks:
            metadata = chunk.get('metadata', {})
            chunks.append({
                "start_line": metadata.get('start_line', 0),
                "end_line": metadata.get('end_line', 0),
                "content": chunk.get('text', ''),
                "chunk_index": metadata.get('chunk_index', 0)
            })

        return {
            "success": True,
            "file_path": file_path,
            "chunks_count": len(chunks),
            "chunks": chunks
        }

    def _find_similar_code(self, file_path: str, top_k: int = 5) -> Dict[str, Any]:
        """Find files similar to the given file."""
        self.logger.info(f"Finding similar code to: {file_path}")

        # First, get content from the target file
        file_context = self._get_file_context(file_path)

        if not file_context.get('chunks'):
            return {
                "success": False,
                "error": f"No content found for {file_path}"
            }

        # Use the file's content as a query
        # Combine first few chunks as query
        query_chunks = file_context['chunks'][:3]
        query_text = '\n'.join([c['content'] for c in query_chunks])

        # Search for similar code
        context = self.engine.query(
            query=query_text,
            top_k=top_k * 3,  # Get more to filter
            include_conversation=False
        )

        # Group by file and exclude the source file
        file_scores = {}
        for chunk in context.chunks_used:
            chunk_file = chunk.get('metadata', {}).get('file_path', '')
            if chunk_file and chunk_file != file_path:
                if chunk_file not in file_scores:
                    file_scores[chunk_file] = {
                        'score': 0,
                        'count': 0,
                        'language': chunk.get('metadata', {}).get('language', 'unknown')
                    }
                file_scores[chunk_file]['score'] += chunk.get('similarity_score', 0)
                file_scores[chunk_file]['count'] += 1

        # Calculate average scores and sort
        similar_files = []
        for file, data in file_scores.items():
            avg_score = data['score'] / data['count'] if data['count'] > 0 else 0
            similar_files.append({
                'file_path': file,
                'similarity_score': avg_score,
                'matching_chunks': data['count'],
                'language': data['language']
            })

        similar_files.sort(key=lambda x: x['similarity_score'], reverse=True)

        return {
            "success": True,
            "reference_file": file_path,
            "similar_files_count": len(similar_files[:top_k]),
            "similar_files": similar_files[:top_k]
        }

    def _index_paths(
        self,
        paths: List[str],
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """Index or reindex specified paths."""
        self.logger.info(f"Indexing paths: {paths} (clear_existing={clear_existing})")

        total_files = 0
        total_chunks = 0

        for path in paths:
            try:
                stats = self.engine.index_directory(
                    path,
                    recursive=True,
                    clear_existing=clear_existing and (path == paths[0])  # Clear only on first
                )
                total_files += stats.get('files_indexed', 0)
                total_chunks += stats.get('chunks_indexed', 0)

            except Exception as e:
                self.logger.error(f"Error indexing {path}: {e}")
                return {
                    "success": False,
                    "error": f"Failed to index {path}: {str(e)}"
                }

        return {
            "success": True,
            "paths_indexed": len(paths),
            "files_indexed": total_files,
            "chunks_indexed": total_chunks,
            "total_documents": self.engine.vectordb.count()
        }

    def _get_codebase_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed codebase."""
        self.logger.info("Getting codebase statistics")

        stats = self.engine.get_stats()

        return {
            "success": True,
            "total_documents": stats.get('total_documents', 0),
            "embedding_model": stats.get('embedding_model', 'unknown'),
            "embedding_dimension": stats.get('embedding_dimension', 0),
            "session_active": stats.get('session_info') is not None
        }

    def _search_by_file_type(
        self,
        query: str,
        file_type: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Search within specific file types."""
        self.logger.info(f"Searching in {file_type} files: {query}")

        # Normalize file type
        if not file_type.startswith('.'):
            file_type = f".{file_type}"

        # Create metadata filter
        # This is a simplified version - in production you'd want more sophisticated filtering
        context = self.engine.query(
            query=query,
            top_k=top_k * 2,  # Get more to filter
            include_conversation=False
        )

        # Filter results by file type
        filtered_results = []
        for chunk in context.chunks_used:
            file_path = chunk.get('metadata', {}).get('file_path', '')
            if file_path.endswith(file_type):
                metadata = chunk.get('metadata', {})
                filtered_results.append({
                    "file_path": file_path,
                    "file_name": metadata.get('file_name', 'unknown'),
                    "start_line": metadata.get('start_line', 0),
                    "end_line": metadata.get('end_line', 0),
                    "relevance_score": chunk.get('similarity_score', 0.0),
                    "content": chunk.get('text', '')
                })

        # Limit to top_k
        filtered_results = filtered_results[:top_k]

        return {
            "success": True,
            "query": query,
            "file_type": file_type,
            "results_count": len(filtered_results),
            "results": filtered_results
        }

    def _find_definitions(self, name: str, type: str = "any") -> Dict[str, Any]:
        """Find class, function, or variable definitions."""
        self.logger.info(f"Finding {type} definition: {name}")

        # Build search query based on type
        type_keywords = {
            "class": f"class {name}",
            "function": f"def {name}",
            "variable": f"{name} =",
            "any": name
        }

        query = type_keywords.get(type, name)

        # Search with high top_k to find all occurrences
        context = self.engine.query(
            query=query,
            top_k=20,
            include_conversation=False
        )

        # Filter for likely definitions (high relevance, contains the name)
        definitions = []
        for chunk in context.chunks_used:
            content = chunk.get('text', '')
            metadata = chunk.get('metadata', {})

            # Check if this looks like a definition
            is_definition = False
            if type == "class" or type == "any":
                if f"class {name}" in content:
                    is_definition = True
            if type == "function" or type == "any":
                if f"def {name}" in content or f"function {name}" in content:
                    is_definition = True
            if type == "variable" or type == "any":
                if f"{name} =" in content or f"const {name}" in content or f"let {name}" in content:
                    is_definition = True

            if is_definition or chunk.get('similarity_score', 0) > 0.7:
                definitions.append({
                    "file_path": metadata.get('file_path', 'unknown'),
                    "file_name": metadata.get('file_name', 'unknown'),
                    "start_line": metadata.get('start_line', 0),
                    "end_line": metadata.get('end_line', 0),
                    "relevance_score": chunk.get('similarity_score', 0.0),
                    "content": content,
                    "language": metadata.get('language', 'unknown')
                })

        return {
            "success": True,
            "name": name,
            "type": type,
            "definitions_count": len(definitions),
            "definitions": definitions
        }
