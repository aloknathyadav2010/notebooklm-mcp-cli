# ContextBridge

ContextBridge is the connective tissue between your development environment and AI models. It synchronizes your custom skills across IDEs and configures Model Context Protocol (MCP) servers automatically, ensuring your AI assistants have the context they need to be truly effective.

## Quickstart

Get started with ContextBridge in seconds. Run the following command to install ContextBridge globally and configure your environment:

```bash
curl -sSL https://raw.githubusercontent.com/aloknathyadav2010/getkodex/newflow/scripts/install_contextbridge.sh | bash
```

### What this does
- Clones ContextBridge to `~/.contextbridge`
- Creates an isolated Python virtual environment
- Installs all necessary dependencies, including `notebooklm-mcp-cli`
- Automatically discovers and configures MCP servers for:
    - **Claude Desktop**
    - **Cursor**
    - **Claude Code**
    - **Antigravity**
- Syncs your custom skills to supported IDEs (VS Code, Cursor, etc.)

---

## Integration

ContextBridge is designed to work where you work.

### Supported Environments
| Environment | Integration Type | Status |
| :--- | :--- | :--- |
| **Claude Desktop** | MCP Config | ✅ Automatic |
| **Claude Code** | MCP Config | ✅ Automatic |
| **Cursor** | MCP Config & Skills | ✅ Automatic |
| **VS Code** | Skill Sync | ✅ Automatic |
| **Antigravity** | MCP Config | ✅ Automatic |

---

## Advanced Usage

### Local Project Setup
If you prefer to keep ContextBridge within a specific project directory:

```bash
git clone -b newflow https://github.com/aloknathyadav2010/getkodex.git my-project
cd my-project
./scripts/install_contextbridge.sh
```

### Command Line Interface
Once installed, you can use the `contextbridge-install` tool to manage your setup:

```bash
# Sync skills to a custom directory
contextbridge-install --skills-dir ./my-skills --ide-target ~/.custom-ide/skills

# Force overwrite existing skills
contextbridge-install --overwrite
```

### Bringing your own skills
To use your existing skills, place them in the `skills/` directory of your installation and run:

```bash
./scripts/install_contextbridge.sh --overwrite
```

---

## Support & Contributing
ContextBridge is currently in early access. If you encounter issues or have suggestions, please open an issue on GitHub.

Built for the next generation of AI-native development.
