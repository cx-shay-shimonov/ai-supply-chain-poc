#!/bin/bash
# Delete all .embeddings files from sample projects
# This is useful when you want to regenerate embeddings from scratch

BASEDIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="$BASEDIR/projects-samples"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           🗑️  Delete All Embeddings Files                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if projects-samples directory exists
if [ ! -d "$PROJECTS_DIR" ]; then
    echo "❌ Error: projects-samples directory not found!"
    exit 1
fi

# Find all .embeddings files
FOUND_COUNT=0
echo "🔍 Searching for .embeddings files..."
echo ""

# Loop through each directory in projects-samples
for PROJECT_DIR in "$PROJECTS_DIR"/*; do
    # Skip if not a directory
    if [ ! -d "$PROJECT_DIR" ]; then
        continue
    fi
    
    # Skip README.md
    if [ "$(basename "$PROJECT_DIR")" = "README.md" ]; then
        continue
    fi
    
    PROJECT_NAME=$(basename "$PROJECT_DIR")
    EMBEDDINGS_FILE="$PROJECT_DIR/.embeddings"
    
    if [ -f "$EMBEDDINGS_FILE" ]; then
        FOUND_COUNT=$((FOUND_COUNT + 1))
        FILE_SIZE=$(du -h "$EMBEDDINGS_FILE" | cut -f1)
        echo "   📄 Found: $PROJECT_NAME/.embeddings ($FILE_SIZE)"
    fi
done

echo ""

if [ "$FOUND_COUNT" -eq 0 ]; then
    echo "✅ No .embeddings files found"
    exit 0
fi

echo "📊 Total found: $FOUND_COUNT file(s)"
echo ""

# Ask for confirmation
read -p "⚠️  Delete all .embeddings files? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled - no files deleted"
    exit 0
fi

echo ""
echo "🗑️  Deleting .embeddings files..."
echo ""

DELETED_COUNT=0

# Loop through each directory again and delete
for PROJECT_DIR in "$PROJECTS_DIR"/*; do
    # Skip if not a directory
    if [ ! -d "$PROJECT_DIR" ]; then
        continue
    fi
    
    PROJECT_NAME=$(basename "$PROJECT_DIR")
    EMBEDDINGS_FILE="$PROJECT_DIR/.embeddings"
    
    if [ -f "$EMBEDDINGS_FILE" ]; then
        rm "$EMBEDDINGS_FILE"
        if [ $? -eq 0 ]; then
            echo "   ✅ Deleted: $PROJECT_NAME/.embeddings"
            DELETED_COUNT=$((DELETED_COUNT + 1))
        else
            echo "   ❌ Failed: $PROJECT_NAME/.embeddings"
        fi
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Deleted $DELETED_COUNT file(s)"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "💡 To regenerate embeddings, run:"
echo "   sem/venv/bin/sem --embed -p projects-samples/<project-name>"
echo ""
