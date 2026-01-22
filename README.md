# self-improve-skill

A Claude Code plugin that automatically reflects on skills used during sessions and proposes improvements.

## Installation

### From Marketplace

First, add this repository as a marketplace:

```
/plugin marketplace add yorrick/claude-code-plugins
```

Then install the plugin:

```
/plugin install self-improve-skill
```

You can choose the installation scope:
- **User scope** (default): Available across all your projects
- **Project scope**: Available to all collaborators on the repository
- **Local scope**: Available only to you in the current repository

### Local Development

For testing or development, load the plugin directly:

```bash
claude --plugin-dir ./self-improve-skill
```

## Skills

### `/self-improve-skill:reflect`

Analyze the current session and propose improvements to skills based on what worked, what didn't, and edge cases discovered.

**Usage:**
```
/self-improve-skill:reflect [skill-name]
```

**Modes:**
- **Interactive** (default): Shows proposed changes and asks for approval before applying
- **Non-interactive**: Applies changes directly without prompting (used by the session end hook)

### `/self-improve-skill:python-development`

Expert Python development assistance with modern best practices, type hints, and clean architecture.

## Hooks

### SessionEnd

Automatically triggers reflection for any skills used during the session. When a session ends:

1. Parses the session transcript
2. Detects which skills were used
3. Launches background reflection for each skill (excluding `reflect` itself to avoid loops)

Logs are written to `skills/reflect/.logs/`.

## Plugin Structure

```
self-improve-skill/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── hooks/
│   └── hooks.json            # SessionEnd hook configuration
└── skills/
    ├── python-development/
    │   └── SKILL.md
    └── reflect/
        ├── SKILL.md
        └── session_end_hook.py
```

## Requirements

- Claude Code CLI
- Python 3.8+ with `uv` (for the session end hook script)
