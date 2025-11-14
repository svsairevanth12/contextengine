"""
MCP Server - Main server implementation for Context Engine.
Implements the Model Context Protocol for AI coding agents.
"""

import json
import sys
import logging
from typing import Dict, Any, Optional
import os

from .tools import MCPTools
from .resources import MCPResources
from .prompts import MCPPrompts


class MCPServer:
    """
    MCP Server implementation for Context Engine.
    Communicates via stdio using JSON-RPC protocol.
    """

    def __init__(self, context_engine):
        """
        Initialize MCP server.

        Args:
            context_engine: ContextEngine instance
        """
        self.engine = context_engine
        self.logger = logging.getLogger(__name__)

        # Initialize handlers
        self.tools = MCPTools(context_engine)
        self.resources = MCPResources(context_engine)
        self.prompts = MCPPrompts(context_engine)

        self.logger.info("MCP Server initialized")

    def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an incoming MCP message.

        Args:
            message: JSON-RPC message

        Returns:
            Response message or None for notifications
        """
        try:
            # Extract message components
            jsonrpc = message.get("jsonrpc", "2.0")
            method = message.get("method")
            params = message.get("params", {})
            msg_id = message.get("id")

            self.logger.debug(f"Handling method: {method}")

            # Handle different methods
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                result = self._handle_tools_call(params)
            elif method == "resources/list":
                result = self._handle_resources_list()
            elif method == "resources/read":
                result = self._handle_resources_read(params)
            elif method == "prompts/list":
                result = self._handle_prompts_list()
            elif method == "prompts/get":
                result = self._handle_prompts_get(params)
            elif method == "ping":
                result = {"status": "ok"}
            else:
                return self._error_response(
                    msg_id,
                    -32601,
                    f"Method not found: {method}"
                )

            # Return response
            if msg_id is not None:
                return {
                    "jsonrpc": jsonrpc,
                    "id": msg_id,
                    "result": result
                }

            return None

        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)
            if msg_id is not None:
                return self._error_response(msg_id, -32603, str(e))
            return None

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "0.1.0",
            "serverInfo": {
                "name": "context-engine-mcp",
                "version": "0.1.0",
                "description": "Local context engine for AI coding assistants"
            },
            "capabilities": {
                "tools": {
                    "listChanged": False
                },
                "resources": {
                    "listChanged": False
                },
                "prompts": {
                    "listChanged": False
                }
            }
        }

    def _handle_tools_list(self) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": self.tools.get_tool_definitions()
        }

    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        result = self.tools.handle_tool_call(tool_name, arguments)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }

    def _handle_resources_list(self) -> Dict[str, Any]:
        """Handle resources/list request."""
        return {
            "resources": self.resources.get_resource_definitions()
        }

    def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request."""
        uri = params.get("uri")
        resource_data = self.resources.get_resource(uri)

        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": resource_data.get("mimeType", "application/json"),
                    "text": json.dumps(resource_data.get("content", resource_data), indent=2)
                }
            ]
        }

    def _handle_prompts_list(self) -> Dict[str, Any]:
        """Handle prompts/list request."""
        return {
            "prompts": self.prompts.get_prompt_definitions()
        }

    def _handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request."""
        name = params.get("name")
        arguments = params.get("arguments", {})

        prompt_data = self.prompts.get_prompt(name, arguments)

        return {
            "description": f"Prompt for {name}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_data.get("prompt", "")
                    }
                }
            ]
        }

    def _error_response(
        self,
        msg_id: Any,
        code: int,
        message: str
    ) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def cleanup(self):
        """Clean up resources when server shuts down."""
        self.logger.info("Cleaning up resources...")
        try:
            # Clear the index to remove embeddings
            self.engine.clear_index()
            self.logger.info("Index cleared successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}", exc_info=True)

    def run(self):
        """Run the MCP server (stdio mode)."""
        self.logger.info("Starting MCP server in stdio mode")

        try:
            # Read from stdin, write to stdout
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse JSON-RPC message
                    message = json.loads(line)

                    # Handle message
                    response = self.handle_message(message)

                    # Send response if not a notification
                    if response is not None:
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()

                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON: {e}")
                    error_response = self._error_response(
                        None,
                        -32700,
                        "Parse error"
                    )
                    sys.stdout.write(json.dumps(error_response) + "\n")
                    sys.stdout.flush()

        except KeyboardInterrupt:
            self.logger.info("Server interrupted by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}", exc_info=True)
        finally:
            # Always cleanup on shutdown
            self.cleanup()


def create_server(codebase_path: Optional[str] = None) -> MCPServer:
    """
    Create and configure an MCP server instance.

    Args:
        codebase_path: Path to codebase to index (optional)

    Returns:
        Configured MCPServer instance
    """
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

    from context_engine import ContextEngine

    # Initialize context engine
    config_path = os.path.join(
        os.path.dirname(__file__),
        '../../config/config.yaml'
    )

    engine = ContextEngine(config_path=config_path)

    # Clear old embeddings and index fresh if codebase provided
    if codebase_path and os.path.exists(codebase_path):
        logging.info("Clearing old embeddings before fresh indexing...")
        engine.clear_index()

        logging.info(f"Indexing codebase: {codebase_path}")
        engine.index_directory(codebase_path, recursive=True)
        logging.info("Fresh indexing complete")

    # Create MCP server
    server = MCPServer(engine)

    return server
