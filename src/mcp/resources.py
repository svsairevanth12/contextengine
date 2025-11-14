"""
MCP Resources - Provides read-only resources about the indexed codebase.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime


class MCPResources:
    """Implements MCP resources for context engine."""

    def __init__(self, context_engine):
        """
        Initialize MCP resources.

        Args:
            context_engine: ContextEngine instance
        """
        self.engine = context_engine
        self.logger = logging.getLogger(__name__)

    def get_resource_definitions(self) -> List[Dict[str, Any]]:
        """Get list of available resource definitions."""
        return [
            {
                "uri": "codebase://stats",
                "name": "Codebase Statistics",
                "description": "Overall statistics about the indexed codebase",
                "mimeType": "application/json"
            },
            {
                "uri": "codebase://files",
                "name": "Indexed Files List",
                "description": "List of all files currently in the index",
                "mimeType": "application/json"
            },
            {
                "uri": "codebase://languages",
                "name": "Programming Languages",
                "description": "Distribution of programming languages in the codebase",
                "mimeType": "application/json"
            },
            {
                "uri": "codebase://config",
                "name": "Engine Configuration",
                "description": "Current configuration of the context engine",
                "mimeType": "application/json"
            }
        ]

    def get_resource(self, uri: str) -> Dict[str, Any]:
        """
        Get a resource by URI.

        Args:
            uri: Resource URI

        Returns:
            Resource data
        """
        try:
            if uri == "codebase://stats":
                return self._get_stats_resource()
            elif uri == "codebase://files":
                return self._get_files_resource()
            elif uri == "codebase://languages":
                return self._get_languages_resource()
            elif uri == "codebase://config":
                return self._get_config_resource()
            else:
                return {
                    "error": f"Unknown resource URI: {uri}",
                    "available_resources": [r["uri"] for r in self.get_resource_definitions()]
                }

        except Exception as e:
            self.logger.error(f"Error getting resource {uri}: {e}")
            return {
                "error": str(e),
                "uri": uri
            }

    def _get_stats_resource(self) -> Dict[str, Any]:
        """Get codebase statistics resource."""
        stats = self.engine.get_stats()

        return {
            "uri": "codebase://stats",
            "content": {
                "total_documents": stats.get('total_documents', 0),
                "embedding_model": stats.get('embedding_model', 'unknown'),
                "embedding_dimension": stats.get('embedding_dimension', 0),
                "session_active": stats.get('session_info') is not None,
                "timestamp": datetime.now().isoformat()
            },
            "mimeType": "application/json"
        }

    def _get_files_resource(self) -> Dict[str, Any]:
        """Get list of indexed files."""
        # This is a simplified version
        # In production, you'd want to track files during indexing
        return {
            "uri": "codebase://files",
            "content": {
                "message": "File listing requires tracking during indexing",
                "total_chunks": self.engine.vectordb.count(),
                "note": "Use search_codebase tool to find specific files"
            },
            "mimeType": "application/json"
        }

    def _get_languages_resource(self) -> Dict[str, Any]:
        """Get programming language distribution."""
        # This is a simplified version
        # You'd track this during indexing in production
        return {
            "uri": "codebase://languages",
            "content": {
                "message": "Language distribution requires tracking during indexing",
                "supported_extensions": self.engine.config.get('indexer', {}).get('supported_extensions', [])
            },
            "mimeType": "application/json"
        }

    def _get_config_resource(self) -> Dict[str, Any]:
        """Get engine configuration."""
        return {
            "uri": "codebase://config",
            "content": {
                "embedding": self.engine.config.get('embedding', {}),
                "retriever": self.engine.config.get('retriever', {}),
                "assembler": self.engine.config.get('assembler', {}),
                "indexer": {
                    "chunk_size": self.engine.config.get('indexer', {}).get('chunk_size'),
                    "chunk_overlap": self.engine.config.get('indexer', {}).get('chunk_overlap'),
                    "supported_extensions": self.engine.config.get('indexer', {}).get('supported_extensions', [])
                }
            },
            "mimeType": "application/json"
        }
