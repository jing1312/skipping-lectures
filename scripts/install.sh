#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="skipping-lectures"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/skills/$SKILL_NAME"

usage() {
  cat <<EOF
Usage: $0 [--target codex|claude|agents|custom] [--destination DIR] [--force]

Installs the $SKILL_NAME skill into an AI agent's skills directory.
  --target codex|claude|agents   install into ~/.codex, ~/.claude, or ~/.agents
  --target custom                requires --destination
  --destination DIR              install into a custom directory
  --force                        overwrite an existing install (old version is backed up)
EOF
}

TARGET="agents"
DESTINATION=""
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --destination) DESTINATION="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

case "$TARGET" in
  codex)
    SKILLS_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
    ;;
  claude)
    SKILLS_ROOT="${CLAUDE_HOME:-$HOME/.claude}/skills"
    ;;
  agents)
    SKILLS_ROOT="$HOME/.agents/skills"
    ;;
  custom)
    if [[ -z "$DESTINATION" ]]; then
      echo "Target custom requires --destination" >&2
      exit 1
    fi
    SKILLS_ROOT="${DESTINATION/#\~/$HOME}"
    ;;
  *)
    echo "Unsupported target: $TARGET" >&2
    exit 1
    ;;
esac

if [[ ! -f "$SOURCE_DIR/SKILL.md" ]]; then
  echo "Skill source missing: $SOURCE_DIR" >&2
  exit 1
fi

TARGET_DIR="$SKILLS_ROOT/$SKILL_NAME"
if [[ -d "$TARGET_DIR" && "$FORCE" -ne 1 ]]; then
  echo "Target already exists: $TARGET_DIR (use --force to overwrite)" >&2
  exit 1
fi

mkdir -p "$SKILLS_ROOT"
STAGE_DIR="$SKILLS_ROOT/.${SKILL_NAME}.install.$$"
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"
cp -R "$SOURCE_DIR/." "$STAGE_DIR/"

BACKUP_DIR=""
if [[ -d "$TARGET_DIR" ]]; then
  BACKUP_DIR="$(dirname "$SKILLS_ROOT")/external/$SKILL_NAME/backups/$(date +%Y%m%d-%H%M%S%N)"
  mkdir -p "$BACKUP_DIR"
  mv "$TARGET_DIR" "$BACKUP_DIR"
  echo "Old version backed up to: $BACKUP_DIR"
fi

mv "$STAGE_DIR" "$TARGET_DIR"
echo "Installed: $TARGET_DIR"
echo "Restart your agent to refresh the skills list and use $SKILL_NAME."
