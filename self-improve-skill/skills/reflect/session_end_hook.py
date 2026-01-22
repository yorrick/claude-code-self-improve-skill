"""Reflect Skill - End of Session Hook.

Receives JSON via stdin with transcript_path.
Detects skills used in the session and triggers reflection for each.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / ".logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE: Path | None = None


def init_log_file(session_id: str) -> None:
    """Initialize the log file with session ID and timestamp."""
    global LOG_FILE
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE = LOG_DIR / f"{timestamp}_{session_id}.log"


def log(message: str) -> None:
    """Append a message to the log file."""
    if LOG_FILE is None:
        return
    with LOG_FILE.open("a") as f:
        f.write(message + "\n")


def extract_skills_from_transcript(transcript_content: str) -> set[str]:
    """Extract skill names used in the session from transcript content.

    Detects two patterns:
    1. Manual trigger: <command-name>/skill-name</command-name>
    2. Automatic trigger: tool_use with name="Skill" and input.skill="skill-name"

    Args:
        transcript_content: The full transcript content as a string.

    Returns:
        A set of skill names that were used in the session.
    """
    skills: set[str] = set()

    for line in transcript_content.splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Check for automatic skill trigger (Claude uses Skill tool)
        # Pattern: {"type": "tool_use", "name": "Skill", "input": {"skill": "skill-name"}}
        if entry.get("type") == "tool_use" and entry.get("name") == "Skill":
            skill_input = entry.get("input", {})
            if isinstance(skill_input, dict) and "skill" in skill_input:
                skills.add(skill_input["skill"])
                continue

        # Check assistant messages for Skill tool use in content array
        message = entry.get("message", {})
        if message.get("role") == "assistant":
            content = message.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if (
                        isinstance(item, dict)
                        and item.get("type") == "tool_use"
                        and item.get("name") == "Skill"
                    ):
                        skill_input = item.get("input", {})
                        if isinstance(skill_input, dict) and "skill" in skill_input:
                            skills.add(skill_input["skill"])

        # Check for manual skill trigger (user types /skill-name)
        # Pattern: <command-name>/skill-name</command-name>
        if entry.get("type") == "user":
            user_content = message.get("content", "")
            if isinstance(user_content, str):
                # Match <command-name>/skill-name</command-name>
                matches = re.findall(
                    r"<command-name>/([^<]+)</command-name>", user_content
                )
                skills.update(matches)

    return skills


def run_reflect_for_skill(
    skill_name: str, session_id: str, transcript_path: Path
) -> None:
    """Run claude -p '/reflect <skill-name>' for the given skill in background.

    Passes the transcript file as stdin for context.

    Args:
        skill_name: The name of the skill to reflect on.
        session_id: The session ID for naming output files.
        transcript_path: Path to the transcript file to pass as stdin.
    """
    log(f"Launching background reflection for skill: {skill_name}")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stdout_file = (
            LOG_DIR / f"{timestamp}_{session_id}_reflect_{skill_name}.stdout.log"
        )
        stderr_file = (
            LOG_DIR / f"{timestamp}_{session_id}_reflect_{skill_name}.stderr.log"
        )

        with (
            transcript_path.open("r") as stdin_f,
            stdout_file.open("w") as stdout_f,
            stderr_file.open("w") as stderr_f,
        ):
            # Detach subprocess so it runs in background
            # Use --permission-mode bypassPermissions to allow edits to skill files
            skills_dir = Path.home() / ".claude" / "skills"
            subprocess.Popen(
                [
                    "claude",
                    "--add-dir",
                    str(skills_dir),
                    "--permission-mode",
                    "bypassPermissions",
                    "-p",
                    f"/reflect {skill_name} --non-interactive",
                ],
                stdout=stdout_f,
                stderr=stderr_f,
                stdin=stdin_f,
                start_new_session=True,
            )
        log(f"Background reflection launched for: {skill_name}")
        log(f"  transcript: {transcript_path}")
        log(f"  stdout: {stdout_file}")
        log(f"  stderr: {stderr_file}")
    except FileNotFoundError:
        log("claude command not found - is it installed and in PATH?")
    except Exception as e:
        log(f"Error launching reflection for {skill_name}: {e}")


def main() -> None:
    # Read JSON input from stdin
    raw_input = sys.stdin.read()

    # Parse JSON and extract transcript path and session ID
    try:
        data = json.loads(raw_input)
        transcript_path = Path(data.get("transcript_path", ""))
        session_id = data.get("session_id", "unknown")
    except json.JSONDecodeError:
        # Can't log yet since we don't have session_id
        print("Failed to parse JSON input")
        return

    # Initialize log file with session ID and timestamp
    init_log_file(session_id)

    log(f"=== Hook triggered at {datetime.now()} ===")
    log(f"Session ID: {session_id}")
    log(f"Raw input: {raw_input}")
    log(f"Transcript path: {transcript_path}")

    # Extract tools/skills used from transcript
    if not transcript_path.is_file():
        log(f"Transcript file not found: {transcript_path}")
        print(f"Session ended. Transcript not found at: {transcript_path}")
        return

    transcript_content = transcript_path.read_text()

    # Parse transcript as JSON lines and count tool usage
    log("--- Tools used ---")
    tool_counts: Counter[str] = Counter()
    for line in transcript_content.splitlines():
        try:
            entry = json.loads(line)
            if entry.get("type") == "tool_use":
                tool_name = entry.get("name", "unknown")
                tool_counts[tool_name] += 1
        except json.JSONDecodeError:
            continue

    for tool, count in sorted(tool_counts.items()):
        log(f"  {count:4d} {tool}")

    # Extract skills referenced via SKILL.md paths
    log("--- Skills referenced (via SKILL.md paths) ---")
    skill_paths = set(re.findall(r"skills/([^/]*)/SKILL\.md", transcript_content))
    for skill in sorted(skill_paths):
        log(f"  {skill}")

    # Extract skills actually used in the session (excluding 'reflect' to avoid loops)
    log("--- Skills used in session ---")
    skills_used = extract_skills_from_transcript(transcript_content)
    skills_used.discard("reflect")  # Avoid infinite loops
    for skill in sorted(skills_used):
        log(f"  {skill}")

    # Run reflection for each skill used
    if skills_used:
        log("--- Running reflections ---")
        for skill in sorted(skills_used):
            run_reflect_for_skill(skill, session_id, transcript_path)
    else:
        log("No skills were used in this session - skipping reflection")

    print(f"Session ended. Transcript available at: {transcript_path}")
    if skills_used:
        print(f"Skills used: {', '.join(sorted(skills_used))}")


if __name__ == "__main__":
    main()
