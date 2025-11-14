#!/usr/bin/env python3
"""
Test script for MCP server functionality.
Tests the MCP tools, resources, and prompts.
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_engine import ContextEngine
from mcp.server import MCPServer
from mcp.tools import MCPTools
from mcp.resources import MCPResources
from mcp.prompts import MCPPrompts


def test_mcp_tools():
    """Test MCP tools functionality."""
    print("=" * 70)
    print("Testing MCP Tools")
    print("=" * 70)

    # Initialize engine
    engine = ContextEngine(config_path="../config/config.yaml")

    # Index test directory
    print("\n1. Indexing source code...")
    stats = engine.index_directory("../src", clear_existing=True)
    print(f"   Indexed {stats['files_indexed']} files, {stats['chunks_indexed']} chunks")

    # Initialize MCP tools
    tools = MCPTools(engine)

    # Test 1: Get tool definitions
    print("\n2. Getting tool definitions...")
    tool_defs = tools.get_tool_definitions()
    print(f"   Found {len(tool_defs)} tools:")
    for tool in tool_defs:
        print(f"   - {tool['name']}: {tool['description'][:50]}...")

    # Test 2: Search codebase
    print("\n3. Testing search_codebase...")
    result = tools.handle_tool_call("search_codebase", {
        "query": "vector database chromadb",
        "top_k": 3
    })
    print(f"   Success: {result.get('success')}")
    print(f"   Results: {result.get('results_count')}")
    if result.get('results'):
        top_result = result['results'][0]
        print(f"   Top result: {top_result['file_name']} (score: {top_result['relevance_score']:.3f})")

    # Test 3: Get codebase stats
    print("\n4. Testing get_codebase_stats...")
    result = tools.handle_tool_call("get_codebase_stats", {})
    print(f"   Success: {result.get('success')}")
    print(f"   Total documents: {result.get('total_documents')}")
    print(f"   Embedding model: {result.get('embedding_model')}")

    # Test 4: Find definitions
    print("\n5. Testing find_definitions...")
    result = tools.handle_tool_call("find_definitions", {
        "name": "ContextEngine",
        "type": "class"
    })
    print(f"   Success: {result.get('success')}")
    print(f"   Definitions found: {result.get('definitions_count')}")

    # Cleanup
    engine.clear_index()
    print("\n✓ MCP Tools tests completed\n")


def test_mcp_resources():
    """Test MCP resources functionality."""
    print("=" * 70)
    print("Testing MCP Resources")
    print("=" * 70)

    # Initialize engine
    engine = ContextEngine(config_path="../config/config.yaml")
    resources = MCPResources(engine)

    # Test 1: Get resource definitions
    print("\n1. Getting resource definitions...")
    resource_defs = resources.get_resource_definitions()
    print(f"   Found {len(resource_defs)} resources:")
    for resource in resource_defs:
        print(f"   - {resource['uri']}: {resource['name']}")

    # Test 2: Get stats resource
    print("\n2. Testing codebase://stats...")
    result = resources.get_resource("codebase://stats")
    print(f"   URI: {result.get('uri')}")
    print(f"   Total documents: {result.get('content', {}).get('total_documents')}")

    # Test 3: Get config resource
    print("\n3. Testing codebase://config...")
    result = resources.get_resource("codebase://config")
    print(f"   URI: {result.get('uri')}")
    print(f"   Chunk size: {result.get('content', {}).get('indexer', {}).get('chunk_size')}")

    print("\n✓ MCP Resources tests completed\n")


def test_mcp_prompts():
    """Test MCP prompts functionality."""
    print("=" * 70)
    print("Testing MCP Prompts")
    print("=" * 70)

    # Initialize engine
    engine = ContextEngine(config_path="../config/config.yaml")

    # Index for context
    print("\n1. Indexing source code...")
    engine.index_directory("../src", clear_existing=True)

    prompts = MCPPrompts(engine)

    # Test 1: Get prompt definitions
    print("\n2. Getting prompt definitions...")
    prompt_defs = prompts.get_prompt_definitions()
    print(f"   Found {len(prompt_defs)} prompts:")
    for prompt in prompt_defs:
        print(f"   - {prompt['name']}: {prompt['description'][:50]}...")

    # Test 2: Analyze feature prompt
    print("\n3. Testing analyze_feature prompt...")
    result = prompts.get_prompt("analyze_feature", {
        "feature": "embeddings"
    })
    print(f"   Success: {result.get('success')}")
    print(f"   Context chunks: {result.get('context_chunks')}")
    print(f"   Prompt length: {len(result.get('prompt', ''))} chars")

    # Test 3: Debug error prompt
    print("\n4. Testing debug_error prompt...")
    result = prompts.get_prompt("debug_error", {
        "error_message": "ChromaDB connection failed",
        "context": "During indexing"
    })
    print(f"   Success: {result.get('success')}")
    print(f"   Context chunks: {result.get('context_chunks')}")

    # Cleanup
    engine.clear_index()
    print("\n✓ MCP Prompts tests completed\n")


def test_mcp_server():
    """Test MCP server message handling."""
    print("=" * 70)
    print("Testing MCP Server")
    print("=" * 70)

    # Initialize engine and server
    engine = ContextEngine(config_path="../config/config.yaml")
    server = MCPServer(engine)

    # Test 1: Initialize
    print("\n1. Testing initialize...")
    response = server.handle_message({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    })
    print(f"   Protocol version: {response['result']['protocolVersion']}")
    print(f"   Server name: {response['result']['serverInfo']['name']}")

    # Test 2: List tools
    print("\n2. Testing tools/list...")
    response = server.handle_message({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    tools_count = len(response['result']['tools'])
    print(f"   Tools available: {tools_count}")

    # Test 3: List resources
    print("\n3. Testing resources/list...")
    response = server.handle_message({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "resources/list",
        "params": {}
    })
    resources_count = len(response['result']['resources'])
    print(f"   Resources available: {resources_count}")

    # Test 4: List prompts
    print("\n4. Testing prompts/list...")
    response = server.handle_message({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "prompts/list",
        "params": {}
    })
    prompts_count = len(response['result']['prompts'])
    print(f"   Prompts available: {prompts_count}")

    print("\n✓ MCP Server tests completed\n")


def main():
    """Run all MCP tests."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                 MCP Server Test Suite                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    try:
        test_mcp_tools()
        test_mcp_resources()
        test_mcp_prompts()
        test_mcp_server()

        print("=" * 70)
        print("All MCP tests completed successfully!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  - Configure MCP in Claude Desktop (see MCP_GUIDE.md)")
        print("  - Start the MCP server: python mcp_server.py")
        print("  - Use your AI agent with codebase context!")
        print()

        return 0

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
