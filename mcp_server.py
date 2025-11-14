#!/usr/bin/env python3
"""
Context Engine MCP Server
Main entry point for running the MCP server.
"""

import sys
import os
import argparse
import logging
import signal
import atexit

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp.server import create_server

# Global server instance for cleanup
_server_instance = None


def cleanup_handler(signum=None, frame=None):
    """Handle cleanup on shutdown signals."""
    global _server_instance
    logging.info(f"Received shutdown signal: {signum}")
    if _server_instance:
        _server_instance.cleanup()
    sys.exit(0)


def main():
    """Main entry point."""
    global _server_instance

    parser = argparse.ArgumentParser(
        description="Context Engine MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MCP Server for Context Engine - provides semantic code search for AI agents.

Usage with Claude Desktop:
  Add to claude_desktop_config.json:
  {
    "mcpServers": {
      "context-engine": {
        "command": "python",
        "args": ["/path/to/contextengine/mcp_server.py"],
        "env": {
          "CODEBASE_PATH": "/path/to/your/project"
        }
      }
    }
  }

Environment Variables:
  CODEBASE_PATH - Path to codebase to index on startup
  LOG_LEVEL - Logging level (DEBUG, INFO, WARNING, ERROR)

Note: Embeddings are ephemeral and cleared on startup/shutdown.
      Each server start will re-index the codebase fresh.
        """
    )

    parser.add_argument(
        '--codebase',
        '-c',
        help='Path to codebase to index on startup (overrides CODEBASE_PATH env var)'
    )

    parser.add_argument(
        '--log-level',
        '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=os.environ.get('LOG_LEVEL', 'INFO'),
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--log-file',
        help='Log file path (default: stderr)'
    )

    args = parser.parse_args()

    # Setup logging
    log_handlers = []

    if args.log_file:
        log_handlers.append(logging.FileHandler(args.log_file))
    else:
        log_handlers.append(logging.StreamHandler(sys.stderr))

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=log_handlers
    )

    # Get codebase path
    codebase_path = args.codebase or os.environ.get('CODEBASE_PATH')

    if codebase_path:
        logging.info(f"Will index codebase: {codebase_path}")
    else:
        logging.warning("No codebase path provided - starting with empty index")

    # Create and run server
    try:
        server = create_server(codebase_path=codebase_path)
        _server_instance = server

        # Register cleanup handlers for graceful shutdown
        signal.signal(signal.SIGTERM, cleanup_handler)
        signal.signal(signal.SIGINT, cleanup_handler)
        atexit.register(lambda: _server_instance.cleanup() if _server_instance else None)

        logging.info("MCP Server started successfully")
        logging.info("Embeddings will be cleared on shutdown for fresh indexing next time")
        server.run()

    except Exception as e:
        logging.error(f"Server failed to start: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
