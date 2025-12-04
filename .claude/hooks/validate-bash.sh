#!/bin/bash
# validate-bash.sh
# Claude Code hook for validating Bash commands before execution
# Place in: .claude/hooks/validate-bash.sh
# Make executable: chmod +x .claude/hooks/validate-bash.sh

# Read input from stdin (JSON payload from Claude Code)
INPUT=$(cat)

# Extract command from JSON
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# If no command, allow
if [ -z "$COMMAND" ]; then
    exit 0
fi

# =============================================================================
# DANGEROUS PATTERNS - Block immediately
# =============================================================================

DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf /*"
    "rm -rf \$HOME"
    "sudo rm"
    "sudo dd"
    "> /dev/sd"
    "> /dev/nvme"
    "mkfs."
    "dd if="
    ":(){:|:&};:"           # Fork bomb
    "chmod 777 /"
    "chown -R"
    "wget.*|.*bash"         # Pipe remote script to bash
    "curl.*|.*bash"
    "eval \$(curl"
    "eval \$(wget"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        echo "🚫 BLOCKED: Dangerous command pattern detected" >&2
        echo "Pattern: $pattern" >&2
        echo "Command: $COMMAND" >&2
        exit 2  # Exit code 2 blocks the tool and shows error to Claude
    fi
done

# =============================================================================
# SENSITIVE FILE ACCESS - Block or warn
# =============================================================================

# Block direct .env file access (reading secrets)
if echo "$COMMAND" | grep -qE '(cat|less|more|head|tail|vim|nano|code|bat)\s+.*\.env'; then
    echo "🚫 BLOCKED: Direct .env file access not allowed" >&2
    echo "Use environment variables instead of reading .env directly" >&2
    exit 2
fi

# Block access to common secret files
SENSITIVE_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    "secrets.json"
    "credentials.json"
    ".aws/credentials"
    ".ssh/id_rsa"
    ".ssh/id_ed25519"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if echo "$COMMAND" | grep -qE "(cat|less|more|head|tail|vim)\s+.*$file"; then
        echo "🚫 BLOCKED: Access to sensitive file: $file" >&2
        exit 2
    fi
done

# =============================================================================
# GIT PUSH WARNING
# =============================================================================

if echo "$COMMAND" | grep -qE "git\s+push"; then
    echo "⚠️ WARNING: git push detected" >&2
    echo "Make sure user has approved pushing to remote" >&2
    # Don't block, just warn (exit 0)
fi

# =============================================================================
# NETWORK COMMANDS - Log for awareness
# =============================================================================

if echo "$COMMAND" | grep -qE "(curl|wget|nc|ncat|ssh)\s+"; then
    echo "ℹ️ Network command detected: $COMMAND" >&2
    # Log but don't block
fi

# =============================================================================
# PACKAGE INSTALLATION - Warn
# =============================================================================

if echo "$COMMAND" | grep -qE "(npm|yarn|pnpm)\s+install\s+[^-]"; then
    echo "ℹ️ Package installation detected" >&2
    # Could add verification step here in future
fi

if echo "$COMMAND" | grep -qE "pip\s+install"; then
    echo "ℹ️ Python package installation detected" >&2
fi

# =============================================================================
# All checks passed
# =============================================================================

exit 0
