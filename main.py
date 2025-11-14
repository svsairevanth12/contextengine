#!/usr/bin/env python3
"""
Context Engine - Main CLI Interface
Local, end-to-end runnable context engine for AI coding assistants.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from context_engine import ContextEngine


def setup_cli():
    """Setup command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Local Context Engine for AI Coding Assistants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index a directory
  python main.py index ./my_project

  # Query the context
  python main.py query "How does authentication work?"

  # Start interactive mode
  python main.py interactive

  # Clear the index
  python main.py clear

  # Show statistics
  python main.py stats
        """
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Index command
    index_parser = subparsers.add_parser('index', help='Index files or directories')
    index_parser.add_argument(
        'path',
        help='Path to file or directory to index'
    )
    index_parser.add_argument(
        '--recursive',
        '-r',
        action='store_true',
        default=True,
        help='Recursively index directories (default: True)'
    )
    index_parser.add_argument(
        '--clear',
        '-c',
        action='store_true',
        help='Clear existing index before indexing'
    )

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the context engine')
    query_parser.add_argument(
        'query',
        help='Query string'
    )
    query_parser.add_argument(
        '--top-k',
        '-k',
        type=int,
        help='Number of results to retrieve'
    )
    query_parser.add_argument(
        '--no-conversation',
        action='store_true',
        help='Disable conversation history in context'
    )
    query_parser.add_argument(
        '--output',
        '-o',
        help='Save context to file'
    )

    # Interactive mode
    interactive_parser = subparsers.add_parser(
        'interactive',
        help='Start interactive query session'
    )
    interactive_parser.add_argument(
        '--session',
        '-s',
        help='Load specific session ID'
    )

    # Stats command
    subparsers.add_parser('stats', help='Show engine statistics')

    # Clear command
    subparsers.add_parser('clear', help='Clear the vector database')

    # List sessions command
    subparsers.add_parser('sessions', help='List all sessions')

    # Export session command
    export_parser = subparsers.add_parser('export', help='Export a session')
    export_parser.add_argument(
        'output_file',
        help='Output file path'
    )
    export_parser.add_argument(
        '--format',
        '-f',
        choices=['json', 'txt'],
        default='json',
        help='Export format (default: json)'
    )
    export_parser.add_argument(
        '--session',
        '-s',
        help='Session ID to export (current if not specified)'
    )

    return parser


def cmd_index(engine: ContextEngine, args):
    """Handle index command."""
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path not found: {path}")
        return 1

    print(f"Indexing: {path}")
    print("This may take a while for large codebases...")

    try:
        if path.is_dir():
            stats = engine.index_directory(
                str(path),
                recursive=args.recursive,
                clear_existing=args.clear
            )
        else:
            stats = engine.index_files(
                [str(path)],
                clear_existing=args.clear
            )

        print("\nIndexing Complete!")
        print(f"  Files indexed: {stats['files_indexed']}")
        print(f"  Chunks created: {stats['chunks_indexed']}")
        print(f"  Total documents: {stats['total_documents']}")

        return 0

    except Exception as e:
        print(f"Error during indexing: {e}")
        return 1


def cmd_query(engine: ContextEngine, args):
    """Handle query command."""
    print(f"Query: {args.query}\n")

    try:
        context = engine.query(
            query=args.query,
            top_k=args.top_k,
            include_conversation=not args.no_conversation
        )

        print("=" * 70)
        print(f"Retrieved {len(context.chunks_used)} chunks (~{context.total_tokens} tokens)")
        print("=" * 70)
        print(context.context_text)
        print("=" * 70)

        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(context.context_text)
            print(f"\nContext saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"Error during query: {e}")
        return 1


def cmd_interactive(engine: ContextEngine, args):
    """Handle interactive mode."""
    print("=" * 70)
    print("Context Engine - Interactive Mode")
    print("=" * 70)

    # Load or create session
    if args.session:
        if engine.load_session(args.session):
            print(f"Loaded session: {args.session}")
        else:
            print(f"Could not load session {args.session}, creating new session")
            session_id = engine.start_session()
            print(f"Started new session: {session_id}")
    else:
        session_id = engine.start_session()
        print(f"Started new session: {session_id}")

    print("\nCommands:")
    print("  Type your query to search for context")
    print("  'stats' - Show engine statistics")
    print("  'history' - Show conversation history")
    print("  'clear' - Clear conversation history")
    print("  'save <file>' - Export current session")
    print("  'exit' or 'quit' - Exit interactive mode")
    print()

    while True:
        try:
            user_input = input(">>> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break

            elif user_input.lower() == 'stats':
                stats = engine.get_stats()
                session_info = stats.get('session_info')
                print(f"\nEngine Statistics:")
                print(f"  Total documents: {stats['total_documents']}")
                print(f"  Embedding model: {stats['embedding_model']}")
                print(f"  Embedding dimension: {stats['embedding_dimension']}")
                if session_info:
                    print(f"\nSession Statistics:")
                    print(f"  Session ID: {session_info['session_id']}")
                    print(f"  Total messages: {session_info['total_messages']}")
                    print(f"  Interactions: {session_info['interaction_count']}")
                print()

            elif user_input.lower() == 'history':
                history = engine.memory.get_conversation_history(last_n=10)
                print("\nRecent Conversation:")
                for msg in history:
                    role = msg['role'].upper()
                    content = msg['content'][:100]
                    print(f"  [{role}] {content}...")
                print()

            elif user_input.lower() == 'clear':
                engine.memory.clear_history()
                print("Conversation history cleared\n")

            elif user_input.lower().startswith('save '):
                output_file = user_input[5:].strip()
                if engine.export_session(output_file):
                    print(f"Session exported to: {output_file}\n")
                else:
                    print("Failed to export session\n")

            else:
                # Process as query
                try:
                    context = engine.query(user_input)

                    print(f"\n{'-'*70}")
                    print(f"Found {len(context.chunks_used)} relevant chunks:")
                    print(f"{'-'*70}")

                    # Show sources
                    sources = set()
                    for chunk in context.chunks_used:
                        file_path = chunk.get('metadata', {}).get('file_path', 'unknown')
                        sources.add(file_path)

                    print(f"\nSources ({len(sources)}):")
                    for source in list(sources)[:5]:
                        print(f"  - {source}")
                    if len(sources) > 5:
                        print(f"  ... and {len(sources) - 5} more")

                    print(f"\nContext Preview:")
                    preview = context.context_text[:500]
                    print(preview)
                    if len(context.context_text) > 500:
                        print(f"\n... ({context.total_tokens} tokens total)")

                    print()

                except Exception as e:
                    print(f"Error: {e}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break

    return 0


def cmd_stats(engine: ContextEngine, args):
    """Handle stats command."""
    stats = engine.get_stats()

    print("=" * 70)
    print("Context Engine Statistics")
    print("=" * 70)
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Embedding Model: {stats['embedding_model']}")
    print(f"Embedding Dimension: {stats['embedding_dimension']}")

    session_info = stats.get('session_info')
    if session_info:
        print(f"\nCurrent Session:")
        print(f"  Session ID: {session_info['session_id']}")
        print(f"  Total Messages: {session_info['total_messages']}")
        print(f"  User Messages: {session_info['user_messages']}")
        print(f"  Assistant Messages: {session_info['assistant_messages']}")
        print(f"  Created: {session_info['created_at']}")
        print(f"  Last Updated: {session_info['last_updated']}")

    return 0


def cmd_clear(engine: ContextEngine, args):
    """Handle clear command."""
    confirm = input("Are you sure you want to clear the entire index? (yes/no): ")

    if confirm.lower() == 'yes':
        engine.clear_index()
        print("Index cleared successfully")
        return 0
    else:
        print("Operation cancelled")
        return 0


def cmd_sessions(engine: ContextEngine, args):
    """Handle sessions command."""
    sessions = engine.list_sessions()

    if not sessions:
        print("No sessions found")
        return 0

    print(f"Found {len(sessions)} sessions:\n")
    for session in sessions:
        print(f"ID: {session['session_id']}")
        print(f"  Created: {session['created_at']}")
        print(f"  Updated: {session['last_updated']}")
        print(f"  Interactions: {session['interaction_count']}")
        print()

    return 0


def cmd_export(engine: ContextEngine, args):
    """Handle export command."""
    try:
        if engine.export_session(
            args.output_file,
            format=args.format
        ):
            print(f"Session exported to: {args.output_file}")
            return 0
        else:
            print("Failed to export session")
            return 1
    except Exception as e:
        print(f"Error exporting session: {e}")
        return 1


def main():
    """Main entry point."""
    parser = setup_cli()
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format='%(levelname)s: %(message)s'
        )

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0

    # Initialize engine
    try:
        print("Initializing Context Engine...")
        engine = ContextEngine(config_path=args.config)
        print("Engine initialized successfully\n")
    except Exception as e:
        print(f"Error initializing engine: {e}")
        return 1

    # Execute command
    commands = {
        'index': cmd_index,
        'query': cmd_query,
        'interactive': cmd_interactive,
        'stats': cmd_stats,
        'clear': cmd_clear,
        'sessions': cmd_sessions,
        'export': cmd_export
    }

    handler = commands.get(args.command)
    if handler:
        return handler(engine, args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
