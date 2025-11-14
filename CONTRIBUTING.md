# Contributing to Context Engine

Thank you for your interest in contributing to Context Engine! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## How Can I Contribute?

### 1. Reporting Bugs

Before submitting a bug report:
- Check the [existing issues](https://github.com/svsairevanth12/contextengine/issues)
- Check the documentation: [INSTALL.md](INSTALL.md), [MCP_GUIDE.md](MCP_GUIDE.md)
- Try the latest version from the main development branch

**When reporting bugs, include:**
- Clear, descriptive title
- Detailed description of the issue
- Steps to reproduce the behavior
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details:
  - OS (macOS/Linux/Windows version)
  - Python version
  - Context Engine version/branch
  - Relevant configuration
- Error logs or stack traces

**Example:**
```markdown
## Bug: MCP server fails to start on Linux

**Environment:**
- Ubuntu 22.04
- Python 3.10.6
- Branch: claude/local-context-engine-01QbCguyLeCXRbad4kkgC7hD

**Steps to Reproduce:**
1. Install Context Engine
2. Run `python mcp_server.py`
3. Server exits with error

**Expected:** Server starts and waits for connections
**Actual:** Server exits with ImportError

**Error Log:**
```
ImportError: cannot import name 'SentenceTransformer'
```

**Additional Context:**
Works fine on macOS but fails on Linux.
```

### 2. Suggesting Features

Feature requests are welcome! Before suggesting:
- Check if the feature already exists
- Search existing issues for similar suggestions
- Consider if it fits the project's scope

**When suggesting features, include:**
- Clear, descriptive title
- Problem statement: What problem does this solve?
- Proposed solution: How should it work?
- Alternatives considered
- Use cases and examples
- Priority (nice-to-have vs. critical)

**Example:**
```markdown
## Feature Request: Support for PDF files

**Problem:**
Currently, Context Engine only supports code and text files. Users with technical documentation in PDF format cannot index them.

**Proposed Solution:**
Add PDF parsing using PyPDF2 or pdfplumber:
- Extract text from PDFs
- Maintain page numbers for reference
- Support both text and scanned PDFs (OCR optional)

**Use Cases:**
- Index API documentation (often in PDF)
- Search through technical specifications
- Reference architecture diagrams with OCR

**Alternatives:**
- Require users to convert PDFs to text manually
- Use external tool like pdf2txt

**Priority:** Medium - would be useful but not blocking
```

### 3. Contributing Code

We welcome code contributions! Areas where help is especially appreciated:

#### High Priority
- **AST-based code chunking** - Smarter parsing using language-specific AST
- **Cross-encoder reranking** - Improve search accuracy
- **Incremental indexing** - Faster updates for changed files
- **Performance optimizations** - Speed and memory improvements

#### Medium Priority
- **Additional file formats** - PDF, Office docs, etc.
- **More MCP tools** - Extend AI assistant capabilities
- **Web interface** - Browser-based UI
- **Better error handling** - More graceful failures

#### Lower Priority
- **Cloud sync** - Optional backup/sync feature
- **Multiple embedding models** - Support for other models
- **Internationalization** - Multi-language support

### 4. Improving Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples and tutorials
- Improve installation instructions
- Create video guides
- Translate documentation

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, conda)

### Setup Steps

1. **Fork the repository**
   ```bash
   # Go to https://github.com/svsairevanth12/contextengine
   # Click "Fork" button
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/contextengine.git
   cd contextengine
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/svsairevanth12/contextengine.git
   ```

4. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

5. **Install in development mode**
   ```bash
   # Install with dev dependencies
   pip install -e ".[dev]"

   # Download embedding model
   python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

6. **Verify installation**
   ```bash
   python main.py --help
   python tests/test_engine.py
   ```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test your changes**
   ```bash
   # Run tests
   python tests/test_engine.py
   python tests/test_mcp.py

   # Check code style
   black src/
   flake8 src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Keep your fork updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill in the PR template

---

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) style guidelines:

```python
# Good
def calculate_similarity(query_embedding, document_embedding):
    """Calculate cosine similarity between embeddings.

    Args:
        query_embedding: Query vector (numpy array)
        document_embedding: Document vector (numpy array)

    Returns:
        float: Similarity score between 0 and 1
    """
    dot_product = np.dot(query_embedding, document_embedding)
    query_norm = np.linalg.norm(query_embedding)
    doc_norm = np.linalg.norm(document_embedding)
    return dot_product / (query_norm * doc_norm)

# Bad
def calc_sim(q,d):
    return np.dot(q,d)/(np.linalg.norm(q)*np.linalg.norm(d))
```

### Code Organization

- **Modularity**: Keep functions and classes focused on single responsibilities
- **DRY**: Don't repeat yourself - extract common code
- **Readability**: Code should be self-documenting with clear names
- **Comments**: Explain "why", not "what"

```python
# Good - Clear purpose, documented
class ContextRetriever:
    """Retrieves relevant context from vector database.

    Performs semantic search and optional reranking to find
    the most relevant code chunks for a given query.
    """

    def __init__(self, vectordb, embedder, rerank=True):
        self.vectordb = vectordb
        self.embedder = embedder
        self.rerank = rerank

    def retrieve(self, query, top_k=10):
        """Retrieve top_k most relevant chunks for query."""
        # Generate embedding for semantic search
        query_embedding = self.embedder.embed_text(query)

        # Query vector database
        results = self.vectordb.query(query_embedding, top_k)

        # Optionally rerank for better precision
        if self.rerank:
            results = self._rerank_results(query, results)

        return results
```

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Dict, Optional, Tuple

def index_file(
    file_path: str,
    chunk_size: int = 512,
    chunk_overlap: int = 128
) -> List[Dict[str, any]]:
    """Index a file and return chunks."""
    pass

def query(
    text: str,
    top_k: int = 10,
    filter_metadata: Optional[Dict] = None
) -> Tuple[List[Dict], int]:
    """Query for relevant context."""
    pass
```

### Error Handling

Handle errors gracefully with informative messages:

```python
# Good
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except UnicodeDecodeError:
    logger.warning(f"Cannot decode file: {file_path}, trying binary mode")
    with open(file_path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

# Bad
try:
    content = open(file_path).read()
except:
    pass
```

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# Good - Informative logs at appropriate levels
logger.info(f"Indexing {len(files)} files")
logger.debug(f"Processing file: {file_path}")
logger.warning(f"Skipping binary file: {file_path}")
logger.error(f"Failed to index {file_path}: {error}")
```

### Documentation

Every module, class, and public function should have docstrings:

```python
def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 128
) -> List[str]:
    """Split text into overlapping chunks.

    Chunks are created with specified size and overlap to maintain
    context continuity across chunk boundaries.

    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Characters to overlap between chunks

    Returns:
        List of text chunks

    Example:
        >>> text = "Long document..."
        >>> chunks = chunk_text(text, chunk_size=100, overlap=20)
        >>> len(chunks)
        15
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks
```

---

## Submitting Changes

### Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Ensure all tests pass** locally
4. **Follow code style** (run black and flake8)
5. **Write clear commit messages**
6. **Fill out the PR template** completely

### Commit Message Format

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add PDF file support using PyPDF2"
git commit -m "Fix memory leak in embedder batch processing"
git commit -m "Update documentation for MCP configuration"

# Bad
git commit -m "fix bug"
git commit -m "updates"
git commit -m "wip"
```

### Pull Request Template

When opening a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Detailed list of changes
- What was modified and why

## Testing
- How the changes were tested
- Test cases added

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings

## Screenshots (if applicable)
Add screenshots for UI changes

## Additional Notes
Any additional context or notes
```

---

## Project Structure

Understanding the codebase:

```
contextengine/
├── src/
│   ├── embeddings/       # Embedding generation
│   ├── vectordb/         # Vector database management
│   ├── indexer/          # File parsing and chunking
│   ├── retriever/        # Semantic search
│   ├── assembler/        # Context optimization
│   ├── memory/           # Session management
│   ├── mcp/             # MCP server implementation
│   └── context_engine.py # Main orchestrator
├── tests/               # Test suite
├── config/              # Configuration files
├── main.py             # CLI interface
└── mcp_server.py       # MCP server entry point
```

### Key Modules

- **embeddings/embedder.py**: Wraps Sentence Transformers for embedding generation
- **vectordb/chromadb_manager.py**: Interface to ChromaDB vector database
- **indexer/file_indexer.py**: Parses files and creates chunks
- **retriever/context_retriever.py**: Semantic search and retrieval
- **assembler/context_assembler.py**: Context ranking and assembly
- **memory/memory_manager.py**: Session persistence
- **mcp/server.py**: MCP protocol implementation
- **mcp/tools.py**: MCP tool definitions
- **mcp/prompts.py**: Smart prompt templates
- **mcp/resources.py**: MCP resource definitions

---

## Testing

### Running Tests

```bash
# Run all tests
python tests/test_engine.py
python tests/test_mcp.py

# Run specific test
python -m pytest tests/test_engine.py::TestContextEngine::test_indexing

# Run with coverage
pytest --cov=src tests/
```

### Writing Tests

Add tests for new features:

```python
import unittest
from context_engine import ContextEngine

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ContextEngine()

    def test_feature_works(self):
        """Test that feature works correctly."""
        result = self.engine.new_feature("input")
        self.assertEqual(result, "expected_output")

    def test_feature_handles_errors(self):
        """Test error handling."""
        with self.assertRaises(ValueError):
            self.engine.new_feature(invalid_input)
```

### Test Coverage

Aim for high test coverage:
- Unit tests for individual functions
- Integration tests for component interactions
- End-to-end tests for full workflows

---

## Documentation

### Documentation Standards

- **Clear and concise**: Use simple language
- **Examples**: Include code examples
- **Complete**: Cover all parameters and return values
- **Up-to-date**: Update docs when code changes

### Building Documentation

```bash
# Install documentation tools
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

---

## Questions?

If you have questions:
- Check [README.md](README.md), [INSTALL.md](INSTALL.md), [MCP_GUIDE.md](MCP_GUIDE.md)
- Open a [GitHub Discussion](https://github.com/svsairevanth12/contextengine/discussions)
- Open an issue with the `question` label

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to Context Engine! 🚀
