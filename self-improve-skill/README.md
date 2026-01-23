# Self-Improve Skill Plugin

A Claude Code plugin that enables skills to learn and improve from session feedback.

## Installation

Add this plugin to your Claude Code configuration to enable automatic skill reflection.

## Features

### `/reflect` Skill

Analyze conversations and propose improvements to skills based on:
- **Corrections** - When users say "no", "not like that", or explicitly correct output
- **Successes** - When users accept output or build on it
- **Edge cases** - Scenarios the skill didn't anticipate
- **Preferences** - Patterns in user choices over time

### Automatic Reflection (SessionEnd Hook)

The plugin includes a hook that automatically triggers reflection when a session ends:
1. Parses the session transcript to detect which skills were used
2. Launches background reflection for each skill
3. Logs results to `.claude/.logs/reflect/`

Changes are applied but not committed, allowing manual review.

## Usage

### Interactive Mode

```
/reflect [skill-name]
```

Shows proposed changes and prompts for approval before committing.

### Non-Interactive Mode (used by hooks)

```
claude -p "/reflect skill-name --non-interactive" < transcript.jsonl
```

Applies changes directly without prompting.

## Potential Improvements

### File Type Reflection Mapping

Currently, reflection logic is embedded in the reflect skill and focused on `SKILL.md` files. A more extensible approach would map file types to specialized reflection prompts:

| File Type | Example Files | Reflection Focus |
|-----------|---------------|------------------|
| `skill` | `SKILL.md` | Workflow gaps, edge cases, constraint violations |
| `hook` | `hooks.json` | Missing triggers, timing issues, failed executions |
| `observation` | `OBSERVATIONS.md` | Pattern consolidation, promotion to skill rules |
| `config` | `settings.json`, `plugin.json` | Preference drift, unused options |
| `doc` | `README.md`, guides | Outdated info, missing sections, unclear instructions |
| `session` | session context files | Context relevance, stale information |

**Proposed structure:**

```
prompts/
├── reflect_skill.md
├── reflect_hook.md
├── reflect_config.md
├── reflect_doc.md
└── reflect_observation.md

mappings.json  # file patterns → prompt type
```

Example `mappings.json`:

```json
{
  "*/SKILL.md": "skill",
  "*/hooks.json": "hook",
  "*/OBSERVATIONS.md": "observation",
  "*.md": "doc",
  "*.json": "config"
}
```

**Benefits:**
- Each file type gets reflection logic tailored to its structure and purpose
- Signals differ by type (skill corrections vs hook failures vs doc gaps)
- Single reflection prompt per type works across all instances
- Easily extensible by adding new file types and prompts
- Reflection prompts live in the repo, making them versionable and customizable

### Git Worktree + PR Workflow

Currently, reflection applies changes directly to files in the working directory. This works but offers no review step before changes take effect. Since reflection runs via a hook *after* Claude Code exits, there's no interactive session to approve changes.

A more robust approach would use Git worktrees and pull requests:

**How it would work:**

1. **Create worktree** - On session end, create a new worktree for the reflection branch
2. **Apply changes** - Make all edits in the isolated worktree
3. **Open PR** - Create a pull request with the proposed improvements
4. **User reviews** - User reviews changes in GitHub/GitLab UI at their leisure
5. **Merge or reject** - Clear accept/reject workflow with full diff visibility

**Benefits:**
- Changes are isolated until explicitly approved
- Full diff review before anything affects the main working directory
- Can add comments and discussion on proposed changes
- CI can run on proposed changes (lint, test, etc.)
- History of all proposed improvements, even rejected ones
- Easy to batch-review multiple session reflections

**Considerations:**
- Requires worktree cleanup after merge/reject
- More complex implementation than direct file edits
- Needs GitHub/GitLab CLI (`gh` or `glab`) for PR creation
- May want to batch changes across multiple sessions into single PR

**Alternative: Local Branch without Worktree**

A lighter-weight option that doesn't require worktrees:
1. Stash any uncommitted changes
2. Create and checkout a new branch
3. Apply reflection changes and commit
4. Switch back to original branch and pop stash
5. Print message: "Review reflection changes: `git diff main..reflect-2024-01-22`"

This avoids worktree complexity but briefly modifies the working directory.
