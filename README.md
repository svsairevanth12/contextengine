# Context Engine

A **local, end-to-end runnable context engine** that stores and retrieves context using embeddings and vector search, specifically designed for AI coding assistants. All processing is done on your own machine without any external API calls.

## Features

- **Fully Local & Offline**: No API keys required, runs entirely on your machine
- **Semantic Search**: Uses sentence transformers for intelligent code and documentation search
- **Vector Database**: ChromaDB for fast and efficient similarity search
- **Smart Chunking**: Intelligent file parsing with overlap for better context
- **Context Assembly**: Ranks, prunes, and assembles optimal context within token budgets
- **Session Management**: Stores conversation history and context across sessions
- **Multi-Format Support**: Handles code files, markdown, text, and conversation history
- **Fast & Lightweight**: Optimized for small to medium projects (<10k files)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Context Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Embedder   │  │  File Indexer│  │    Memory    │    │
│  │  (Sentence   │  │  (Chunking)  │  │   Manager    │    │
│  │ Transformers)│  │              │  │  (Sessions)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                                │
│                  ┌─────────▼─────────┐                     │
│                  │   Vector DB       │                     │
│                  │   (ChromaDB)      │                     │
│                  └─────────┬─────────┘                     │
│                            │                                │
│         ┌──────────────────┴──────────────────┐            │
│         │                                      │            │
│  ┌──────▼──────┐                    ┌─────────▼────────┐  │
│  │  Retriever  │                    │   Assembler      │  │
│  │ (Semantic   │───────────────────▶│  (Rank & Prune)  │  │
│  │   Search)   │                    │                  │  │
│  └─────────────┘                    └──────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- 2GB+ RAM recommended
- ~500MB disk space for models

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd contextengine

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py --help
```

### Optional: GPU Support

For faster embedding generation with NVIDIA GPUs:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Then update `config/config.yaml`:
```yaml
embedding:
  device: "cuda"  # Change from "cpu" to "cuda"
```

## Quick Start

### 1. Index Your Codebase

```bash
# Index a directory (recursively)
python main.py index ./my_project

# Index specific files
python main.py index ./src/main.py
```

### 2. Query for Context

```bash
# Simple query
python main.py query "How does authentication work?"

# Save context to file
python main.py query "API endpoints" --output context.txt

# Limit results
python main.py query "database schema" --top-k 5
```

### 3. Interactive Mode

```bash
# Start interactive session
python main.py interactive

>>> How do I configure the database?
>>> What are the main classes in this project?
>>> stats
>>> exit
```

## Usage Examples

### Index a Project

```bash
# Index your entire project
python main.py index ./myproject --recursive

# Clear existing index and reindex
python main.py index ./myproject --clear
```

Output:
```
Indexing: ./myproject
This may take a while for large codebases...

Indexing Complete!
  Files indexed: 47
  Chunks created: 312
  Total documents: 312
```

### Search for Context

```bash
# Find relevant context for a query
python main.py query "How do I handle user authentication?"
```

Output:
```
======================================================================
Retrieved 8 chunks (~2847 tokens)
======================================================================

============================================================
Source: src/auth/authenticator.py
============================================================
## authenticator.py (lines 15-45)
Relevance: 0.89

class Authenticator:
    '''Handles user authentication and session management.'''

    def __init__(self, config):
        self.config = config
        self.session_store = SessionStore()

    def authenticate(self, username, password):
        '''Authenticate a user with credentials.'''
        ...
```

### Interactive Mode

The interactive mode provides a conversational interface:

```bash
python main.py interactive
```

```
======================================================================
Context Engine - Interactive Mode
======================================================================
Started new session: a3f5e8c91b4d2e7a

Commands:
  Type your query to search for context
  'stats' - Show engine statistics
  'history' - Show conversation history
  'clear' - Clear conversation history
  'save <file>' - Export current session
  'exit' or 'quit' - Exit interactive mode

>>> How do I connect to the database?

----------------------------------------------------------------------
Found 5 relevant chunks:
----------------------------------------------------------------------

Sources (2):
  - database.py
  - config.yaml

Context Preview:
============================================================
Source: src/db/database.py
============================================================
## database.py (lines 10-30)
Relevance: 0.92

class DatabaseConnection:
    '''Manages database connections and pooling.'''

    def connect(self, host, port, database):
        '''
        Establish connection to the database.

        Args:
            host: Database host address
            port: Database port
            database: Database name
        '''
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            database=database
        )
...

>>> stats

Engine Statistics:
  Total documents: 312
  Embedding model: all-MiniLM-L6-v2
  Embedding dimension: 384

Session Statistics:
  Session ID: a3f5e8c91b4d2e7a
  Total messages: 2
  Interactions: 1

>>> exit
Goodbye!
```

## Configuration

Edit `config/config.yaml` to customize behavior:

```yaml
# Embedding Model Settings
embedding:
  model_name: "all-MiniLM-L6-v2"  # Fast, 384-dim embeddings
  # Alternative models:
  # "all-mpnet-base-v2"  # Higher quality, 768-dim, slower
  # "multi-qa-MiniLM-L6-cos-v1"  # Optimized for Q&A
  device: "cpu"  # Use "cuda" for GPU
  batch_size: 32

# Retriever Settings
retriever:
  top_k: 10  # Number of chunks to retrieve
  similarity_threshold: 0.3  # Minimum similarity (0-1)
  rerank: true  # Apply reranking for better results

# Context Assembly Settings
assembler:
  max_tokens: 4000  # Max context size
  compression_enabled: true
  include_metadata: true  # Include file paths and line numbers
  ranking_strategy: "hybrid"  # hybrid, similarity, or recency

# Indexer Settings
indexer:
  chunk_size: 512  # Characters per chunk
  chunk_overlap: 128  # Overlap between chunks
  supported_extensions:
    - ".py"
    - ".js"
    - ".ts"
    - ".md"
    # Add more as needed
```

## Advanced Usage

### Programmatic API

```python
from context_engine import ContextEngine

# Initialize engine
engine = ContextEngine(config_path="config/config.yaml")

# Index files
stats = engine.index_directory("./my_project")
print(f"Indexed {stats['chunks_indexed']} chunks")

# Query for context
context = engine.query("How does the API work?", top_k=5)

print(f"Retrieved {len(context.chunks_used)} chunks")
print(f"Context tokens: ~{context.total_tokens}")
print(context.context_text)

# Start a session
session_id = engine.start_session()

# Add conversation to memory
engine.memory.add_message("user", "How do I use the API?")
engine.memory.add_message("assistant", "Here's how...")

# Query with conversation context
context = engine.query("Tell me more", include_conversation=True)
```

### Index Conversation History

```python
# Index past conversations for future reference
conversation = [
    {"role": "user", "content": "How do I set up the database?"},
    {"role": "assistant", "content": "You can configure..."},
    {"role": "user", "content": "What about migrations?"},
    {"role": "assistant", "content": "Use the migrate command..."}
]

engine.index_conversation(conversation, conversation_id="conv_001")
```

### Metadata Filtering

```python
# Filter by file type
context = engine.query(
    "authentication logic",
    filter_metadata={"language": "python"}
)

# Filter by directory
context = engine.query(
    "API routes",
    filter_metadata={"file_path": "**/api/**"}
)
```

## CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `index` | Index files or directories | `python main.py index ./src` |
| `query` | Search for context | `python main.py query "search term"` |
| `interactive` | Start interactive mode | `python main.py interactive` |
| `stats` | Show engine statistics | `python main.py stats` |
| `sessions` | List all sessions | `python main.py sessions` |
| `export` | Export a session | `python main.py export output.json` |
| `clear` | Clear the vector database | `python main.py clear` |

### Command Options

```bash
# Index with options
python main.py index ./project --recursive --clear

# Query with options
python main.py query "search" --top-k 15 --output results.txt

# Interactive with session
python main.py interactive --session abc123

# Export with format
python main.py export output.txt --format txt
```

## Performance Tips

1. **Chunk Size**: Adjust based on your needs
   - Smaller chunks (256-512): Better precision, more chunks
   - Larger chunks (1024-2048): More context, fewer chunks

2. **Embedding Model**: Choose based on requirements
   - `all-MiniLM-L6-v2`: Fast, good for most cases (384-dim)
   - `all-mpnet-base-v2`: Higher quality, slower (768-dim)
   - `multi-qa-MiniLM-L6-cos-v1`: Optimized for Q&A

3. **GPU Acceleration**: Use CUDA for 5-10x faster embedding
   - Install: `pip install torch`
   - Configure: Set `device: "cuda"` in config

4. **Batch Size**: Increase for faster indexing (if RAM allows)
   - Default: 32
   - Higher RAM: 64-128

## Project Structure

```
contextengine/
├── config/
│   └── config.yaml              # Configuration file
├── src/
│   ├── embeddings/
│   │   └── embedder.py          # Sentence transformer wrapper
│   ├── vectordb/
│   │   └── chromadb_manager.py  # Vector database interface
│   ├── indexer/
│   │   └── file_indexer.py      # File parsing and chunking
│   ├── retriever/
│   │   └── context_retriever.py # Semantic search
│   ├── assembler/
│   │   └── context_assembler.py # Context optimization
│   ├── memory/
│   │   └── memory_manager.py    # Session management
│   └── context_engine.py        # Main orchestrator
├── data/
│   ├── embeddings/              # ChromaDB storage
│   └── sessions/                # Session files
├── logs/                        # Log files
├── tests/
│   └── test_engine.py           # End-to-end tests
├── main.py                      # CLI interface
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## Testing

Run the end-to-end test:

```bash
python tests/test_engine.py
```

This will:
1. Create test files
2. Index them
3. Run multiple queries
4. Test session management
5. Verify all components work together

## Use Cases

### AI Coding Assistant Integration

```python
# In your AI assistant code
from context_engine import ContextEngine

engine = ContextEngine()

# One-time indexing
engine.index_directory("./codebase")

# During conversation
user_query = "How do I implement OAuth?"
context = engine.query(user_query)

# Send to LLM
prompt = f"""
Context:
{context.context_text}

User Question: {user_query}

Answer:
"""

response = llm.generate(prompt)
engine.add_response(response)
```

### Documentation Search

```bash
# Index documentation
python main.py index ./docs --clear

# Search for specific topics
python main.py query "installation instructions"
python main.py query "API reference for authentication"
```

### Code Understanding

```bash
# Index a new codebase
python main.py index ./unfamiliar_project

# Ask questions
python main.py interactive
>>> What is the main entry point?
>>> How is configuration handled?
>>> Where are the API routes defined?
```

## Troubleshooting

### Model Download Issues

If the embedding model fails to download:

```bash
# Manually download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Memory Issues

If you run out of memory during indexing:

1. Reduce batch size in `config/config.yaml`:
   ```yaml
   embedding:
     batch_size: 16  # Reduce from 32
   ```

2. Index in smaller batches:
   ```bash
   python main.py index ./src/module1
   python main.py index ./src/module2
   ```

### Slow Indexing

1. Use GPU acceleration (see Installation section)
2. Increase batch size if RAM allows
3. Use a smaller/faster embedding model

## Limitations

- **Project Size**: Optimized for <10k files. Larger projects may require tuning.
- **Embedding Model**: Fixed after indexing. Changing models requires reindexing.
- **Language Support**: Works best with English code/docs. Multilingual models available.
- **Context Window**: Limited by `max_tokens` setting. Adjust based on your LLM.

## Contributing

Contributions are welcome! Areas for improvement:

- AST-based code chunking for better code understanding
- Cross-encoder reranking for improved accuracy
- Support for more file formats (PDF, Office docs)
- Incremental indexing for faster updates
- Web interface for easier interaction

## License

MIT License - See LICENSE file for details

## Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [ChromaDB](https://www.trychroma.com/) for vector storage
- Built for the AI coding assistant community

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the documentation
- Run with `--verbose` flag for detailed logging

---

**Happy Coding with Context! 🚀**
