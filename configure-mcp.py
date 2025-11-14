#!/usr/bin/env python3
"""
Auto-configure MCP server for Claude Desktop or Cline
Generates the JSON configuration snippet with correct paths.
"""

import json
import os
import sys
import platform
from pathlib import Path


def get_config_path():
    """Get Claude Desktop config path based on OS."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"

    return None


def get_install_dir():
    """Get context engine installation directory."""
    # Check if running from installed location
    home_install = Path.home() / ".context-engine"
    if home_install.exists():
        return home_install

    # Otherwise, use current directory
    return Path.cwd()


def get_python_path():
    """Get Python path (prefer venv if exists)."""
    install_dir = get_install_dir()
    venv_python = install_dir / "venv" / "bin" / "python"

    if venv_python.exists():
        return str(venv_python)

    return sys.executable


def generate_config(codebase_path=None):
    """Generate MCP configuration."""
    install_dir = get_install_dir()
    python_path = get_python_path()
    mcp_server_path = install_dir / "mcp_server.py"

    config = {
        "mcpServers": {
            "context-engine": {
                "command": python_path,
                "args": [str(mcp_server_path)],
                "env": {
                    "CODEBASE_PATH": codebase_path or "REPLACE_WITH_YOUR_PROJECT_PATH"
                }
            }
        }
    }

    return config


def print_config(config):
    """Print configuration in a nice format."""
    print("\n" + "="*70)
    print("MCP Server Configuration")
    print("="*70)
    print("\nAdd this to your Claude Desktop config file:")

    config_path = get_config_path()
    if config_path:
        print(f"\nConfig file location:\n  {config_path}")

    print("\nConfiguration:")
    print(json.dumps(config, indent=2))
    print("\n" + "="*70)


def merge_config(existing_config, new_config):
    """Merge new MCP config into existing config."""
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}

    existing_config["mcpServers"].update(new_config["mcpServers"])
    return existing_config


def auto_configure(codebase_path):
    """Automatically configure Claude Desktop."""
    config_path = get_config_path()

    if not config_path:
        print("❌ Could not determine Claude Desktop config path for your OS.")
        return False

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate new config
    new_config = generate_config(codebase_path)

    # Read existing config
    existing_config = {}
    if config_path.exists():
        print(f"📁 Found existing config at: {config_path}")
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)

            # Backup
            backup_path = config_path.with_suffix('.json.backup')
            with open(backup_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            print(f"💾 Backup saved to: {backup_path}")

        except json.JSONDecodeError:
            print("⚠️  Existing config is invalid JSON. Creating new config.")
            existing_config = {}
    else:
        print(f"📝 Creating new config at: {config_path}")

    # Merge configs
    merged_config = merge_config(existing_config, new_config)

    # Write config
    try:
        with open(config_path, 'w') as f:
            json.dump(merged_config, f, indent=2)

        print("\n✅ Configuration updated successfully!")
        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print("\n1. Restart Claude Desktop completely")
        print("2. Look for the 🔌 icon in Claude")
        print("3. Ask Claude to search your codebase!")
        print(f"\nCodebase indexed: {codebase_path}")
        print("\n" + "="*70)

        return True

    except Exception as e:
        print(f"\n❌ Error writing config: {e}")
        return False


def save_config_snippet(config, output_file="mcp-config-snippet.json"):
    """Save config snippet to file."""
    output_path = get_install_dir() / output_file

    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n💾 Config snippet saved to: {output_path}")
    print(f"\nYou can manually add this to your Claude Desktop config if auto-config didn't work.")


def main():
    """Main function."""
    print("\n╔══════════════════════════════════════════════════════════════════════╗")
    print("║        Context Engine MCP - Configuration Generator                 ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")

    # Parse arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage:")
        print("  python configure-mcp.py                    # Generate config snippet")
        print("  python configure-mcp.py /path/to/project   # Auto-configure with path")
        print("  python configure-mcp.py --show             # Show current config")
        return

    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        config_path = get_config_path()
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(json.dumps(config, indent=2))
        else:
            print("No config file found.")
        return

    # Check if codebase path provided
    if len(sys.argv) > 1:
        codebase_path = sys.argv[1]

        # Expand and verify path
        codebase_path = os.path.expanduser(codebase_path)
        codebase_path = os.path.abspath(codebase_path)

        if not os.path.exists(codebase_path):
            print(f"❌ Path does not exist: {codebase_path}")
            return

        if not os.path.isdir(codebase_path):
            print(f"❌ Path is not a directory: {codebase_path}")
            return

        print(f"📂 Codebase path: {codebase_path}\n")

        # Try auto-configure
        if auto_configure(codebase_path):
            # Also save snippet
            config = generate_config(codebase_path)
            save_config_snippet(config)
        else:
            print("\n⚠️  Auto-configuration failed. Use the generated snippet instead:")
            config = generate_config(codebase_path)
            print_config(config)
            save_config_snippet(config)

    else:
        # No path provided, just generate snippet
        print("ℹ️  No codebase path provided. Generating template config.\n")
        print("   To auto-configure, run:")
        print("   python configure-mcp.py /path/to/your/project\n")

        config = generate_config()
        print_config(config)
        save_config_snippet(config)

        print("\nTo configure manually:")
        print("1. Replace CODEBASE_PATH with your project path")
        print("2. Add to your Claude Desktop config")
        print("3. Restart Claude Desktop")


if __name__ == "__main__":
    main()
