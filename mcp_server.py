#!/usr/bin/env python3
"""
Context Engine MCP Server
Main entry point for running the MCP server.
"""

import sys
import os
import argparse
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp.server import create_server


def main():
    """Main entry point."""
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
        logging.info("MCP Server started successfully")
        server.run()

    except Exception as e:
        logging.error(f"Server failed to start: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
