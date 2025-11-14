#!/usr/bin/env python3
"""
Example Usage of Context Engine
Demonstrates the main features and capabilities.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from context_engine import ContextEngine


def example_basic_usage():
    """Example 1: Basic indexing and querying."""
    print("=" * 70)
    print("Example 1: Basic Usage")
    print("=" * 70)

    # Initialize the engine
    engine = ContextEngine(config_path="config/config.yaml")

    # Index the source code of the context engine itself
    print("\n1. Indexing the context engine source code...")
    stats = engine.index_directory("./src", clear_existing=True)
    print(f"   Indexed {stats['files_indexed']} files")
    print(f"   Created {stats['chunks_indexed']} chunks")

    # Query for context
    print("\n2. Querying: 'How does the embedder work?'")
    context = engine.query("How does the embedder work?", top_k=3)
    print(f"   Found {len(context.chunks_used)} relevant chunks")
    print(f"   Total tokens: ~{context.total_tokens}")

    # Show a preview
    print("\n3. Context preview:")
    print("-" * 70)
    print(context.context_text[:500])
    print("...")
    print("-" * 70)

    # Clean up
    engine.clear_index()
    print("\n✓ Example 1 complete\n")


def example_session_management():
    """Example 2: Working with sessions."""
    print("=" * 70)
    print("Example 2: Session Management")
    print("=" * 70)

    engine = ContextEngine()

    # Create a new session
    print("\n1. Creating a new session...")
    session_id = engine.start_session()
    print(f"   Session ID: {session_id}")

    # Add messages to the session
    print("\n2. Adding messages to session...")
    engine.memory.add_message("user", "How do I use the context engine?")
    engine.memory.add_message("assistant", "You can use it by indexing files and querying for context.")
    engine.memory.add_message("user", "Can you show me an example?")

    # Get conversation history
    print("\n3. Retrieving conversation history...")
    history = engine.memory.get_conversation_history()
    print(f"   Total messages: {len(history)}")

    for msg in history:
        print(f"   [{msg['role']}]: {msg['content'][:50]}...")

    # Export session
    print("\n4. Exporting session...")
    export_file = "/tmp/example_session.json"
    engine.export_session(export_file, format="json")
    print(f"   Exported to: {export_file}")

    # Get session stats
    stats = engine.get_session_info()
    print(f"\n5. Session statistics:")
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   User messages: {stats['user_messages']}")
    print(f"   Assistant messages: {stats['assistant_messages']}")

    # Clean up
    os.remove(export_file)
    print("\n✓ Example 2 complete\n")


def example_advanced_querying():
    """Example 3: Advanced querying features."""
    print("=" * 70)
    print("Example 3: Advanced Querying")
    print("=" * 70)

    engine = ContextEngine()

    # Index with metadata
    print("\n1. Indexing files...")
    stats = engine.index_directory("./src", clear_existing=True)
    print(f"   Indexed {stats['chunks_indexed']} chunks")

    # Query with different parameters
    queries = [
        ("vector database", 3),
        ("file indexing", 5),
        ("memory management", 2)
    ]

    print("\n2. Running multiple queries...")
    for query, top_k in queries:
        context = engine.query(query, top_k=top_k)
        print(f"\n   Query: '{query}' (top_k={top_k})")
        print(f"   Results: {len(context.chunks_used)} chunks")

        if context.chunks_used:
            # Show sources
            sources = set()
            for chunk in context.chunks_used:
                file_path = chunk.get('metadata', {}).get('file_name', 'unknown')
                sources.add(file_path)

            print(f"   Sources: {', '.join(list(sources)[:3])}")

    # Get engine statistics
    print("\n3. Engine statistics:")
    stats = engine.get_stats()
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Embedding model: {stats['embedding_model']}")
    print(f"   Embedding dimension: {stats['embedding_dimension']}")

    # Clean up
    engine.clear_index()
    print("\n✓ Example 3 complete\n")


def example_conversation_indexing():
    """Example 4: Indexing conversation history."""
    print("=" * 70)
    print("Example 4: Conversation Indexing")
    print("=" * 70)

    engine = ContextEngine()

    # Create a sample conversation
    conversation = [
        {"role": "user", "content": "How do I set up a Python virtual environment?"},
        {"role": "assistant", "content": "You can create a virtual environment using: python -m venv venv"},
        {"role": "user", "content": "How do I activate it?"},
        {"role": "assistant", "content": "On Linux/Mac: source venv/bin/activate, On Windows: venv\\Scripts\\activate"},
        {"role": "user", "content": "What about installing packages?"},
        {"role": "assistant", "content": "Use pip install <package_name> after activating the virtual environment"}
    ]

    # Index the conversation
    print("\n1. Indexing conversation...")
    stats = engine.index_conversation(conversation, conversation_id="setup_help_001")
    print(f"   Indexed {stats['chunks_indexed']} messages")

    # Query the conversation
    print("\n2. Querying conversation: 'virtual environment activation'")
    context = engine.query("virtual environment activation", top_k=2)
    print(f"   Found {len(context.chunks_used)} relevant messages")

    # Show results
    print("\n3. Retrieved context:")
    print("-" * 70)
    for chunk in context.chunks_used[:2]:
        text = chunk.get('text', '')[:100]
        score = chunk.get('similarity_score', 0)
        print(f"   Score {score:.3f}: {text}...")
    print("-" * 70)

    # Clean up
    engine.clear_index()
    print("\n✓ Example 4 complete\n")


def example_ai_assistant_integration():
    """Example 5: Integration with AI assistant."""
    print("=" * 70)
    print("Example 5: AI Assistant Integration Pattern")
    print("=" * 70)

    print("""
This example shows how to integrate Context Engine with an AI assistant:

```python
from context_engine import ContextEngine

# One-time setup
engine = ContextEngine()
engine.index_directory("./your_codebase")
session_id = engine.start_session()

# In your chat loop
while True:
    user_input = get_user_input()

    # Get relevant context
    context = engine.query(user_input, top_k=5)

    # Prepare prompt for LLM
    prompt = f'''
Relevant context from codebase:
{context.context_text}

Previous conversation:
{engine.memory.get_context_summary(last_n=3)}

User question: {user_input}

Please provide a helpful answer based on the context above.
'''

    # Send to your LLM (OpenAI, Anthropic, local model, etc.)
    response = your_llm.generate(prompt)

    # Store in memory
    engine.memory.add_message("user", user_input)
    engine.memory.add_message("assistant", response)

    print(response)
```

Key benefits:
- Automatic context retrieval from your codebase
- Session memory for conversation continuity
- Token budget management
- Semantic search for relevant code snippets
""")

    print("\n✓ Example 5 complete\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║           Context Engine - Example Usage                      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    try:
        example_basic_usage()
        example_session_management()
        example_advanced_querying()
        example_conversation_indexing()
        example_ai_assistant_integration()

        print("=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  - Try the interactive mode: python main.py interactive")
        print("  - Index your own project: python main.py index ./your_project")
        print("  - Read the README.md for more details")
        print()

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
