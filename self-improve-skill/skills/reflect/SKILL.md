---
name: reflect
description: Analyze the current session and propose improvements to skills. Run after using a skill to capture learnings. Use when user says "reflect", "improve skill", "learn from this", or at end of skill-heavy sessions.
---

# Reflect Skill

Analyze the current conversation and propose improvements to skills based on what worked, what didn't, and edge cases discovered.

## Trigger

Run `/self-improve-skill:reflect` or `/self-improve-skill:reflect [skill-name]` after a session where you used a skill.

## Modes

### Interactive Mode (default)
When run by a user in a conversation, follow the full workflow below with prompts and confirmations.

### Non-Interactive Mode (--non-interactive flag)
When invoked with `--non-interactive` flag (e.g., `claude -p "/reflect skill-name --non-interactive" < transcript.jsonl`), operate autonomously:
- Parse the JSONL transcript from stdin
- Analyze the session for the specified skill
- Apply changes directly to skill files WITHOUT committing
- Do NOT prompt for user input
- Do NOT run git commands (no add, commit, or push)
- Output a summary of changes made to stdout

Detect mode by checking if `--non-interactive` is present in the arguments.

## Workflow

### Step 1: Identify the Skill

If skill name not provided, ask:

```
Which skill should I analyze this session for?
- frontend-design
- code-reviewer
- [other]
```

### Step 2: Analyze the Conversation

Look for these signals in the current conversation:

**Corrections** (HIGH confidence):
- User said "no", "not like that", "I meant..."
- User explicitly corrected output
- User asked for changes immediately after generation
- Agent try run run a command that initially failed because of a simple issue, then succeeded

**Successes** (MEDIUM confidence):
- User said "perfect", "great", "yes", "exactly"
- User accepted output without modification
- User built on top of the output

**Edge Cases** (MEDIUM confidence):
- Questions the skill didn't anticipate
- Scenarios requiring workarounds
- Features user asked for that weren't covered

**Preferences** (accumulate over sessions):
- Repeated patterns in user choices
- Style preferences shown implicitly
- Tool/framework preferences

### Step 3: Propose Changes

Present findings using accessible colors (WCAG AA 4.5:1 contrast ratio):

```
┌─ Skill Reflection: [skill-name] ─────────────────────────┐
│                                                          │
│ Signals: X corrections, Y successes                      │
│                                                          │
│ Proposed changes:                                        │
│                                                          │
│ 🔴 [HIGH] + Add constraint: "[specific constraint]"      │
│ 🟡 [MED]  + Add preference: "[specific preference]"      │
│ 🟡 [LOW]  + Flag for review: "[observation]"             │
│                                                          │
│ Commit: "[skill]: [summary of changes]"                  │
└──────────────────────────────────────────────────────────┘
```

Color guide (use ANSI codes in terminal output):
- HIGH: \033[1;31m (bold red #FF6B6B - 4.5:1 on dark)
- MED: \033[1;33m (bold yellow #FFE066 - 4.8:1 on dark)
- LOW: \033[1;36m (bold cyan #6BC5FF - 4.6:1 on dark)

Avoid: pure red (#FF0000) on black, green on red (colorblind users)

- Y — Apply changes, commit, and push
- n — Skip this update
- Or describe any tweaks to the proposed changes

### Step 4: If Approved (Interactive Mode Only)

1. Read the current skill file from `~/.claude/skills/[skill-name]/SKILL.md`
2. Apply the changes using the Edit tool
3. Run git commands:

```bash
cd ~/.claude/skills
git add [skill-name]/SKILL.md
git commit -m "[skill]: [change summary]"
git push origin main
```

4. Confirm: "Skill updated and pushed to GitHub"

### Step 4: Non-Interactive Mode

1. Read the current skill file from `~/.claude/skills/[skill-name]/SKILL.md`
2. Apply the changes using the Edit tool
3. Do NOT run any git commands
4. Output summary of changes to stdout

### Step 5: If Declined (Interactive Mode Only)

Ask: "Would you like to save these observations for later review?"

If yes, append to `~/.claude/skills/[skill-name]/OBSERVATIONS.md`

## Example Session

User runs `/reflect frontend-design` after a UI session:

```
┌─ Skill Reflection: frontend-design ──────────────────────┐
│                                                          │
│ Signals: 2 corrections, 3 successes                      │
│                                                          │
│ Proposed changes:                                        │
│                                                          │
│ 🔴 [HIGH] + Constraints/NEVER:                           │
│           "Use gradients unless explicitly requested"    │
│ 🔴 [HIGH] + Color & Theme:                               │
│           "Dark backgrounds: use #000, not #1a1a1a"      │
│ 🟡 [MED]  + Layout:                                      │
│           "Prefer CSS Grid for card layouts"             │
│                                                          │
│ Commit: "frontend-design: no gradients, #000 dark"       │
└──────────────────────────────────────────────────────────┘

Apply these changes? [Y/n] or describe tweaks
```

## Git Integration (Interactive Mode Only)

This skill has permission to:

- Read skill files from `~/.claude/skills/`
- Edit skill files (with user approval)
- Run `git add`, `git commit`, `git push` in the skills directory

The skills repo should be initialized at `~/.claude/skills` with a remote origin.

## Important Notes

### Interactive Mode
- Always show the exact changes before applying
- Never modify skills without explicit user approval
- Commit messages should be concise and descriptive
- Push only after successful commit

### Non-Interactive Mode
- Apply changes directly without prompting
- NEVER commit or push changes
- Output a clear summary of what was changed
- User will review and commit changes manually later
