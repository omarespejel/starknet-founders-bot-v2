#!/bin/bash
#
# Description:
# This script generates a comprehensive prompt for an LLM by concatenating key source
# files from the Telegram AI Bot project, including Python bot code, database schemas,
# configuration files, and project structure.
#
# Usage:
# ./generate-context.sh
#

# --- Configuration ---

# Get current date for the output filename
DATE=$(date +%Y%m%d-%H%M)

# Output filename with a timestamp
OUTPUT_FILE="telegram-bot-context-prompt-${DATE}.txt"

# --- Script Body ---

# Clean up any previous output file to start fresh
rm -f "$OUTPUT_FILE"

echo "🚀 Starting LLM prompt generation for the Telegram AI Bot project..."
echo "------------------------------------------------------------"
echo "Output will be saved to: $OUTPUT_FILE"
echo ""

# 1. Add a Preamble and Goal for the LLM
echo "Adding LLM preamble and goal..."
{
  echo "# Telegram AI Bot Project Context & Goal"
  echo ""
  echo "## Goal for the LLM"
  echo "You are an expert Python developer and AI bot architect with deep expertise in:"
  echo "- Telegram Bot API and python-telegram-bot library"
  echo "- AI/LLM integration (OpenAI/OpenRouter APIs)"
  echo "- Database design with Supabase/PostgreSQL"
  echo "- Modern Python development with UV package manager"
  echo "- Bot conversation design and user experience"
  echo ""
  echo "Your task is to analyze the complete context of this Telegram AI Bot project. The bot features:"
  echo "- Two AI personalities (Product Manager & VC/Angel Investor)"
  echo "- Conversation persistence with Supabase"
  echo "- Real-time AI responses via OpenRouter/Perplexity"
  echo "- Rich Telegram UI with inline keyboards"
  echo "- User statistics and session management"
  echo ""
  echo "Please review the project structure, dependencies, source code, database schema, and configuration,"
  echo "then provide specific, actionable advice for improvement. Focus on:"
  echo "- Code quality and Python best practices"
  echo "- Bot conversation flow and UX"
  echo "- Database optimization and design"
  echo "- AI prompt engineering and response quality"
  echo "- Security and error handling"
  echo "- Performance and scalability"
  echo "- Deployment and production readiness"
  echo ""
  echo "---"
  echo ""
} >> "$OUTPUT_FILE"

# 2. Add the project's directory structure (cleaned up)
echo "Adding cleaned directory structure..."
echo "## Directory Structure" >> "$OUTPUT_FILE"
if command -v tree &> /dev/null; then
    echo "  -> Adding directory structure (tree -L 4)"
    # Exclude common noise from the tree view
    tree -L 4 -I "__pycache__|.venv|venv|.git|.pytest_cache|.ruff_cache|.mypy_cache|htmlcov|*.pyc|uv.lock" >> "$OUTPUT_FILE"
else
    echo "  -> WARNING: 'tree' command not found. Using ls -la instead."
    echo "NOTE: 'tree' command was not found. Directory listing:" >> "$OUTPUT_FILE"
    ls -la >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# 3. Add Core Project and Configuration Files
echo "Adding core project and configuration files..."
# Core files that provide project context
CORE_FILES=(
  "README.md"
  "pyproject.toml"
  ".env.example"
  ".gitignore"
  "render.yaml"
  "$0" # This script itself
)

for file in "${CORE_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  -> Adding $file"
    echo "## FILE: $file" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  else
    echo "  -> WARNING: $file not found. Skipping."
  fi
done

# 4. Add all Python source files from src/bot/
echo "Adding all Python source files from 'src/bot/'..."
# Find all Python files, excluding common directories we don't want
find "src/bot" -type f -name "*.py" \
  -not -path "*/.venv/*" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/.pytest_cache/*" \
  | while read -r py_file; do
    echo "  -> Adding Python file: $py_file"
    echo "## FILE: $py_file" >> "$OUTPUT_FILE"
    cat "$py_file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  done

# 5. Add test files
echo "Adding test files from 'tests/'..."
if [ -d "tests" ]; then
  find "tests" -type f -name "*.py" \
    -not -path "*/__pycache__/*" \
    | while read -r test_file; do
      echo "  -> Adding test file: $test_file"
      echo "## FILE: $test_file" >> "$OUTPUT_FILE"
      cat "$test_file" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "---" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    done
else
  echo "  -> No tests directory found. Skipping."
fi

# 6. Add script files
echo "Adding script files from 'scripts/'..."
if [ -d "scripts" ]; then
  find "scripts" -type f -name "*.py" \
    | while read -r script_file; do
      echo "  -> Adding script file: $script_file"
      echo "## FILE: $script_file" >> "$OUTPUT_FILE"
      cat "$script_file" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "---" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    done
else
  echo "  -> No scripts directory found. Skipping."
fi

# 7. Add database migration files
echo "Adding database migration files from 'migrations/'..."
if [ -d "migrations" ]; then
  find "migrations" -type f \( -name "*.sql" -o -name "*.py" \) \
    | while read -r migration_file; do
      echo "  -> Adding migration file: $migration_file"
      echo "## FILE: $migration_file" >> "$OUTPUT_FILE"
      cat "$migration_file" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
      echo "---" >> "$OUTPUT_FILE"
      echo "" >> "$OUTPUT_FILE"
    done
else
  echo "  -> No migrations directory found. Skipping."
fi

# 8. Add any additional Python files in the root
echo "Adding any additional Python files in root..."
find . -maxdepth 1 -type f -name "*.py" \
  | while read -r root_py_file; do
    echo "  -> Adding root Python file: $root_py_file"
    echo "## FILE: $root_py_file" >> "$OUTPUT_FILE"
    cat "$root_py_file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
  done

# --- Completion Summary ---

echo ""
echo "-------------------------------------"
echo "✅ Prompt generation complete!"
echo ""
echo "This context file now includes:"
echo "  ✓ A clear goal and preamble for the LLM"
echo "  ✓ A cleaned project directory structure"
echo "  ✓ Core project files (README.md, pyproject.toml, .env.example)"
echo "  ✓ Configuration files (.gitignore, render.yaml)"
echo "  ✓ This generation script itself"
echo "  ✓ All Python source code from the 'src/bot' directory (*.py)"
echo "  ✓ All test files from the 'tests' directory"
echo "  ✓ All script files from the 'scripts' directory"
echo "  ✓ All database migration files from the 'migrations' directory"
echo "  ✓ Any additional Python files in the root directory"
echo ""
echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "Total lines: $(wc -l < "$OUTPUT_FILE" | xargs)"
echo ""
echo "You can now use the content of '$OUTPUT_FILE' as a context prompt for your LLM."
echo "Perfect for getting comprehensive code reviews, architecture advice, or feature suggestions!"
echo ""
echo "💡 Tip: This is especially useful for:"
echo "   - Code reviews and optimization suggestions"
echo "   - Bot conversation flow improvements"
echo "   - Database schema optimization"
echo "   - AI prompt engineering enhancements"
echo "   - Production deployment planning"
