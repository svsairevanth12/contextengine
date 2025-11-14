# Quick Start Guide

Get started with Context Engine in 5 minutes!

## Installation

### Automated Setup (Recommended)

```bash
# Run the quick start script
./quickstart.sh
```

This will:
- Check Python version
- Create a virtual environment
- Install all dependencies
- Download the embedding model
- Create necessary directories

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/embeddings data/sessions logs
```

## Your First Commands

### 1. Index Your Code

```bash
# Index the context engine itself as an example
python main.py index ./src

# Output:
# Indexing: ./src
# Indexed 13 files, created 156 chunks
```

### 2. Query for Context

```bash
# Ask a question about the indexed code
python main.py query "How does the embedder work?"

# Output shows:
# - Number of relevant chunks found
# - Source files and relevance scores
# - The actual context text
```

### 3. Try Interactive Mode

```bash
python main.py interactive

# Then type queries interactively:
>>> What is the ContextEngine class?
>>> How do I index files?
>>> stats
>>> exit
```

## Real-World Example

Here's a complete workflow:

```bash
# 1. Clone or navigate to your project
cd /path/to/your/project

# 2. Index your project
python /path/to/contextengine/main.py index .

# 3. Ask questions about your code
python /path/to/contextengine/main.py query "Where is the database configured?"

# 4. Start an interactive session
python /path/to/contextengine/main.py interactive
>>> How does authentication work?
>>> What are the main API endpoints?
>>> Show me the user model
```

## Integration with AI Assistant

```python
from context_engine import ContextEngine

# Initialize once
engine = ContextEngine()

# Index your codebase
engine.index_directory("./my_project")

# In your AI chat loop:
while True:
    user_query = input("Ask about your code: ")

    # Get relevant context
    context = engine.query(user_query)

    # Send to your LLM
    prompt = f"""
    Context from codebase:
    {context.context_text}

    User question: {user_query}

    Answer:
    """

    # Your LLM call here
    # response = llm.generate(prompt)
    # print(response)
```

## Configuration

Edit `config/config.yaml` for customization:

```yaml
# Most important settings:

embedding:
  model_name: "all-MiniLM-L6-v2"  # Change for different quality/speed
  device: "cpu"                    # Change to "cuda" for GPU

retriever:
  top_k: 10              # More chunks = more context
  similarity_threshold: 0.3  # Higher = stricter matching

assembler:
  max_tokens: 4000       # Adjust based on your LLM's context window
```

## Common Tasks

### Clear and Reindex

```bash
python main.py clear
python main.py index ./my_project
```

### Export a Session

```bash
python main.py interactive
>>> # Ask some questions...
>>> save my_session.json
>>> exit

# Or from command line:
python main.py export my_session.json --format json
```

### Check Statistics

```bash
python main.py stats
```

Output:
```
Total Documents: 156
Embedding Model: all-MiniLM-L6-v2
Embedding Dimension: 384
```

## Troubleshooting

### "No module named 'sentence_transformers'"

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "Out of memory" during indexing

Reduce batch size in `config/config.yaml`:
```yaml
embedding:
  batch_size: 16  # Default is 32
```

### Slow indexing

1. Use GPU: Set `device: "cuda"` in config (requires CUDA-capable GPU)
2. Use smaller model: Set `model_name: "all-MiniLM-L6-v2"` (default, fastest)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Run the test suite: `python tests/test_engine.py`
- Explore the [examples](#) directory (if available)
- Customize `config/config.yaml` for your use case

## Getting Help

- Check logs in `logs/context_engine.log`
- Run with verbose flag: `python main.py --verbose query "test"`
- Review error messages - they're usually helpful!

---

**You're ready to go! Start indexing and querying your code.** 🚀
