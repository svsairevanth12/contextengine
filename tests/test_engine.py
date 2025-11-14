"""
End-to-end tests for the Context Engine
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_engine import ContextEngine


def create_test_files(directory):
    """Create test files for indexing."""
    # Python file
    (directory / "test_code.py").write_text("""
def calculate_sum(numbers):
    '''Calculate the sum of a list of numbers.'''
    total = 0
    for num in numbers:
        total += num
    return total

class DataProcessor:
    '''Process data with various methods.'''

    def __init__(self, data):
        self.data = data

    def filter_positive(self):
        '''Filter positive numbers from data.'''
        return [x for x in self.data if x > 0]

    def calculate_average(self):
        '''Calculate the average of the data.'''
        if not self.data:
            return 0
        return sum(self.data) / len(self.data)
""")

    # Markdown file
    (directory / "README.md").write_text("""
# Test Project

This is a test project for the context engine.

## Features

- Data processing capabilities
- Mathematical calculations
- Easy to use API

## Usage

```python
from test_code import DataProcessor

processor = DataProcessor([1, 2, 3, 4, 5])
average = processor.calculate_average()
print(f"Average: {average}")
```

## API Reference

### calculate_sum(numbers)

Calculates the sum of a list of numbers.

**Parameters:**
- numbers: List of numbers to sum

**Returns:**
- Total sum as a number
""")

    # JavaScript file
    (directory / "app.js").write_text("""
// Simple JavaScript application

function greet(name) {
    return `Hello, ${name}!`;
}

class UserManager {
    constructor() {
        this.users = [];
    }

    addUser(user) {
        this.users.push(user);
    }

    findUser(id) {
        return this.users.find(u => u.id === id);
    }
}

module.exports = { greet, UserManager };
""")


def test_basic_workflow():
    """Test the basic workflow of the context engine."""
    print("=" * 70)
    print("Running End-to-End Test")
    print("=" * 70)

    # Create temporary directory for test data
    test_dir = tempfile.mkdtemp()
    test_project = Path(test_dir) / "test_project"
    test_project.mkdir()

    try:
        # Create test files
        print("\n1. Creating test files...")
        create_test_files(test_project)
        print(f"   Created test files in: {test_project}")

        # Initialize engine
        print("\n2. Initializing Context Engine...")
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        engine = ContextEngine(config_path=str(config_path))
        print("   Engine initialized successfully")

        # Clear any existing index
        print("\n3. Clearing existing index...")
        engine.clear_index()

        # Index the test directory
        print("\n4. Indexing test directory...")
        stats = engine.index_directory(str(test_project), recursive=True)
        print(f"   Files indexed: {stats['files_indexed']}")
        print(f"   Chunks created: {stats['chunks_indexed']}")
        print(f"   Total documents: {stats['total_documents']}")

        # Start a session
        print("\n5. Starting a session...")
        session_id = engine.start_session()
        print(f"   Session ID: {session_id}")

        # Test queries
        test_queries = [
            "How do I calculate the sum of numbers?",
            "What is the DataProcessor class used for?",
            "How do I use the UserManager?",
            "What are the features of this project?"
        ]

        print("\n6. Testing queries...")
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: {query}")
            context = engine.query(query, top_k=3)
            print(f"   Retrieved: {len(context.chunks_used)} chunks")
            print(f"   Tokens: ~{context.total_tokens}")

            # Show top source
            if context.chunks_used:
                top_chunk = context.chunks_used[0]
                file_path = top_chunk.get('metadata', {}).get('file_path', 'unknown')
                score = top_chunk.get('similarity_score', 0)
                print(f"   Top source: {Path(file_path).name} (score: {score:.3f})")

        # Test session management
        print("\n7. Testing session management...")
        session_stats = engine.get_session_info()
        print(f"   Total messages: {session_stats['total_messages']}")
        print(f"   Interactions: {session_stats['interaction_count']}")

        # Export session
        print("\n8. Exporting session...")
        export_file = Path(test_dir) / "session_export.json"
        engine.export_session(str(export_file), format="json")
        print(f"   Exported to: {export_file}")
        print(f"   File exists: {export_file.exists()}")

        # Get engine stats
        print("\n9. Engine statistics...")
        engine_stats = engine.get_stats()
        print(f"   Total documents: {engine_stats['total_documents']}")
        print(f"   Embedding model: {engine_stats['embedding_model']}")
        print(f"   Embedding dimension: {engine_stats['embedding_dimension']}")

        # Clean up index
        print("\n10. Cleaning up...")
        engine.clear_index()
        print("    Index cleared")

        print("\n" + "=" * 70)
        print("Test completed successfully!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    success = test_basic_workflow()
    sys.exit(0 if success else 1)
