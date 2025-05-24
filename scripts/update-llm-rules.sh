#!/bin/bash

# Script to update all LLM rule files from the central LLM_RULES.md file
# This ensures all AI assistants have the same guidelines

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
SOURCE_FILE="$PROJECT_ROOT/LLM_RULES.md"

# List of target files to update
TARGET_FILES=(
  "$PROJECT_ROOT/.windsurfrules"
  "$PROJECT_ROOT/.cursorrules"
  "$PROJECT_ROOT/.augment-guidelines"
  "$PROJECT_ROOT/.github/copilot-instructions.md"
)

# Check if source file exists
if [ ! -f "$SOURCE_FILE" ]; then
  echo "Error: Source file $SOURCE_FILE does not exist."
  exit 1
fi

echo "Checking LLM rule files against $SOURCE_FILE..."

# Get the modification time of the source file
source_mtime=$(stat -f "%m" "$SOURCE_FILE")

# Flags to track file status
updated=false
skipped=false

# Copy source file to each target file if needed
for target in "${TARGET_FILES[@]}"; do
  # Ensure target directory exists
  target_dir=$(dirname "$target")
  mkdir -p "$target_dir"

  # Check if target file exists
  if [ -f "$target" ]; then
    # Get the modification time of the target file
    target_mtime=$(stat -f "%m" "$target")

    # Check if target file is newer than source file
    if [ "$target_mtime" -gt "$source_mtime" ]; then
      # Compare file contents to see if they're actually different
      if cmp -s "$SOURCE_FILE" "$target"; then
        echo "Target file $target is newer but has identical content. No update needed."
      else
        echo "Warning: Target file $target is newer than source file and has different content."
        echo "Source last modified: $(date -r "$source_mtime")"
        echo "Target last modified: $(date -r "$target_mtime")"
        echo "Skipping this file to preserve newer changes."
        skipped=true
      fi
      continue
    fi
  fi

  # Copy the file
  cp "$SOURCE_FILE" "$target"
  echo "Updated: $target"
  updated=true
done

# Determine exit status based on what happened
if [ "$updated" = true ]; then
  echo "LLM rule files have been updated successfully."
  exit 2
elif [ "$skipped" = true ]; then
  echo "Some files were skipped because they were newer than the source."
  echo "Consider updating LLM_RULES.md with any changes from these files."
  exit 3
else
  echo "No files needed updating."
  exit 0
fi
