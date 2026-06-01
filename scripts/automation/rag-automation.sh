#!/bin/bash

# RAG (Retrieval-Augmented Generation) automation script
# Automatically updates vector database when documentation changes

set -e

echo "🔍 RAG System Automation"
echo "================================================================"

# Default values
ACTION="update"  # update, rebuild, query, status
SOURCE_DIR="docs"
CHROMA_HOST="localhost"
CHROMA_PORT="8001"
COLLECTION_NAME="portfolio-docs"
EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -s|--source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        -h|--host)
            CHROMA_HOST="$2"
            shift 2
            ;;
        -p|--port)
            CHROMA_PORT="$2"
            shift 2
            ;;
        -c|--collection)
            COLLECTION_NAME="$2"
            shift 2
            ;;
        -m|--model)
            EMBEDDING_MODEL="$2"
            shift 2
            ;;
        -q|--query)
            QUERY="$2"
            ACTION="query"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -a, --action ACTION      Action: update, rebuild, query, status (default: update)"
            echo "  -s, --source DIR         Source directory for documents (default: docs)"
            echo "  -h, --host HOST          ChromaDB host (default: localhost)"
            echo "  -p, --port PORT          ChromaDB port (default: 8001)"
            echo "  -c, --collection NAME    Collection name (default: portfolio-docs)"
            echo "  -m, --model MODEL        Embedding model (default: all-MiniLM-L6-v2)"
            echo "  -q, --query TEXT         Query text (sets action to query)"
            echo "  --help                   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --action update        # Update vector database with new documents"
            echo "  $0 --action rebuild       # Rebuild entire vector database"
            echo "  $0 --query \"how to deploy\" # Query the vector database"
            echo "  $0 --action status        # Check RAG system status"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Action: $ACTION"
echo "Source: $SOURCE_DIR"
echo "ChromaDB: $CHROMA_HOST:$CHROMA_PORT"
echo "Collection: $COLLECTION_NAME"
echo "Model: $EMBEDDING_MODEL"
echo ""

# Function to check ChromaDB connection
check_chromadb() {
    echo "🔌 Checking ChromaDB connection..."

    if curl -s "http://$CHROMA_HOST:$CHROMA_PORT/api/v1/heartbeat" > /dev/null; then
        echo "✅ ChromaDB is running"
        return 0
    else
        echo "❌ ChromaDB is not responding at http://$CHROMA_HOST:$CHROMA_PORT"
        echo "   Start ChromaDB with: docker-compose up -d chromadb"
        return 1
    fi
}

# Function to check Python dependencies
check_dependencies() {
    echo "📦 Checking Python dependencies..."

    # Check if required packages are installed
    for package in chromadb sentence-transformers langchain; do
        if python -c "import $package" 2>/dev/null; then
            echo "✅ $package is installed"
        else
            echo "❌ $package is not installed"
            echo "   Install with: pip install $package"
            return 1
        fi
    done

    return 0
}

# Function to get document changes
get_document_changes() {
    echo "📄 Checking for document changes..."

    # Create documents index if it doesn't exist
    if [ ! -f ".rag-documents-index.json" ]; then
        echo "   Creating new document index"
        echo "{}" > .rag-documents-index.json
    fi

    # Find all markdown files
    find "$SOURCE_DIR" -name "*.md" -type f | while read -r file; do
        filename=$(basename "$file")
        filepath=$(realpath "$file")
        checksum=$(md5sum "$file" | cut -d' ' -f1)

        # Check if file has changed
        if jq -e --arg f "$filepath" --arg c "$checksum" '.[$f] == $c' .rag-documents-index.json > /dev/null 2>&1; then
            echo "   ✓ $filename (unchanged)"
        else
            echo "   ✗ $filename (changed or new)"
            echo "$filepath"
        fi
    done
}

# Function to update vector database
update_vector_db() {
    echo "🔄 Updating vector database..."

    # Create Python script for updating ChromaDB
    cat > /tmp/update_chromadb.py << EOF
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import hashlib

# Configuration
chroma_host = "$CHROMA_HOST"
chroma_port = $CHROMA_PORT
collection_name = "$COLLECTION_NAME"
source_dir = "$SOURCE_DIR"
embedding_model = "$EMBEDDING_MODEL"

# Initialize ChromaDB client
client = chromadb.HttpClient(
    host=chroma_host,
    port=chroma_port,
    settings=Settings(allow_reset=True)
)

# Get or create collection
try:
    collection = client.get_collection(collection_name)
    print(f"Using existing collection: {collection_name}")
except:
    collection = client.create_collection(collection_name)
    print(f"Created new collection: {collection_name}")

# Initialize embedding model
print(f"Loading embedding model: {embedding_model}")
model = SentenceTransformer(embedding_model)

# Function to process markdown files
def process_markdown_files():
    documents = []
    metadatas = []
    ids = []

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, source_dir)

                # Read file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Generate ID from filepath
                file_id = hashlib.md5(filepath.encode()).hexdigest()

                # Split content into chunks (simple splitting)
                chunks = split_into_chunks(content, 1000)

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{file_id}_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "source": relative_path,
                        "filename": file,
                        "chunk": i,
                        "total_chunks": len(chunks)
                    })
                    ids.append(chunk_id)

    return documents, metadatas, ids

def split_into_chunks(text, chunk_size):
    """Split text into chunks of approximately chunk_size characters"""
    chunks = []
    current_chunk = ""

    for paragraph in text.split('\n\n'):
        if len(current_chunk) + len(paragraph) < chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Process documents
print("Processing documents...")
documents, metadatas, ids = process_markdown_files()

print(f"Found {len(documents)} document chunks")

if documents:
    # Add documents to collection
    print("Adding documents to ChromaDB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully added {len(documents)} chunks to collection")
else:
    print("No documents to add")

# Get collection info
print(f"\nCollection info:")
print(f"  Name: {collection_name}")
print(f"  Count: {collection.count()} documents")
EOF

    # Run the Python script
    python /tmp/update_chromadb.py

    # Update document index
    echo "Updating document index..."
    find "$SOURCE_DIR" -name "*.md" -type f | while read -r file; do
        filepath=$(realpath "$file")
        checksum=$(md5sum "$file" | cut -d' ' -f1)
        jq --arg f "$filepath" --arg c "$checksum" '.[$f] = $c' .rag-documents-index.json > /tmp/tmp_index.json && mv /tmp/tmp_index.json .rag-documents-index.json
    done

    echo "✅ Vector database updated"
}

# Function to rebuild vector database
rebuild_vector_db() {
    echo "🔨 Rebuilding vector database..."

    # Reset document index
    rm -f .rag-documents-index.json

    # Delete and recreate collection
    cat > /tmp/rebuild_chromadb.py << EOF
import chromadb
from chromadb.config import Settings

chroma_host = "$CHROMA_HOST"
chroma_port = $CHROMA_PORT
collection_name = "$COLLECTION_NAME"

client = chromadb.HttpClient(
    host=chroma_host,
    port=chroma_port,
    settings=Settings(allow_reset=True)
)

# Delete collection if it exists
try:
    client.delete_collection(collection_name)
    print(f"Deleted collection: {collection_name}")
except:
    print(f"Collection {collection_name} does not exist")

# Create new collection
collection = client.create_collection(collection_name)
print(f"Created new collection: {collection_name}")
EOF

    python /tmp/rebuild_chromadb.py

    # Update with all documents
    update_vector_db

    echo "✅ Vector database rebuilt"
}

# Function to query vector database
query_vector_db() {
    local query_text="${QUERY:-$1}"

    if [ -z "$query_text" ]; then
        echo "❌ No query provided"
        return 1
    fi

    echo "🔎 Querying: \"$query_text\""

    cat > /tmp/query_chromadb.py << EOF
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

chroma_host = "$CHROMA_HOST"
chroma_port = $CHROMA_PORT
collection_name = "$COLLECTION_NAME"
embedding_model = "$EMBEDDING_MODEL"
query_text = """$query_text"""

# Initialize clients
client = chromadb.HttpClient(
    host=chroma_host,
    port=chroma_port,
    settings=Settings(allow_reset=True)
)

model = SentenceTransformer(embedding_model)

# Get collection
try:
    collection = client.get_collection(collection_name)
except:
    print(f"Collection {collection_name} not found")
    exit(1)

# Query
results = collection.query(
    query_texts=[query_text],
    n_results=5
)

print("Top 5 results:")
print("=" * 80)

for i in range(len(results['documents'][0])):
    doc = results['documents'][0][i]
    metadata = results['metadatas'][0][i]
    distance = results['distances'][0][i]

    print(f"\nResult {i+1} (distance: {distance:.4f}):")
    print(f"Source: {metadata['filename']} (chunk {metadata['chunk']+1}/{metadata['total_chunks']})")
    print(f"Content: {doc[:200]}...")
    print("-" * 80)
EOF

    python /tmp/query_chromadb.py
}

# Function to check RAG system status
check_rag_status() {
    echo "📊 RAG System Status"
    echo "===================="

    # Check ChromaDB
    if check_chromadb; then
        echo "✅ ChromaDB: Running"

        # Get collection info
        cat > /tmp/status_chromadb.py << EOF
import chromadb
from chromadb.config import Settings

chroma_host = "$CHROMA_HOST"
chroma_port = $CHROMA_PORT
collection_name = "$COLLECTION_NAME"

try:
    client = chromadb.HttpClient(
        host=chroma_host,
        port=chroma_port,
        settings=Settings(allow_reset=True)
    )

    collections = client.list_collections()
    print(f"Collections: {[c.name for c in collections]}")

    if collection_name in [c.name for c in collections]:
        collection = client.get_collection(collection_name)
        print(f"Collection '{collection_name}': {collection.count()} documents")
    else:
        print(f"Collection '{collection_name}': Not found")

except Exception as e:
    print(f"Error: {e}")
EOF

        python /tmp/status_chromadb.py
    else
        echo "❌ ChromaDB: Not running"
    fi

    echo ""

    # Check document index
    if [ -f ".rag-documents-index.json" ]; then
        DOC_COUNT=$(jq 'length' .rag-documents-index.json)
        echo "✅ Document index: $DOC_COUNT files indexed"
    else
        echo "❌ Document index: Not found"
    fi

    echo ""

    # Check source directory
    if [ -d "$SOURCE_DIR" ]; then
        MD_COUNT=$(find "$SOURCE_DIR" -name "*.md" -type f | wc -l)
        echo "✅ Source directory: $MD_COUNT markdown files in $SOURCE_DIR"
    else
        echo "❌ Source directory: $SOURCE_DIR not found"
    fi
}

# Main function
main() {
    echo "Starting RAG automation..."
    echo ""

    # Check dependencies
    if ! check_dependencies; then
        echo "❌ Missing dependencies. Please install required packages."
        exit 1
    fi

    # Check ChromaDB connection for most actions
    if [[ "$ACTION" != "status" ]]; then
        if ! check_chromadb; then
            echo "❌ Cannot proceed without ChromaDB"
            exit 1
        fi
    fi

    # Execute action
    case $ACTION in
        update)
            update_vector_db
            ;;
        rebuild)
            rebuild_vector_db
            ;;
        query)
            if [ -n "$QUERY" ]; then
                query_vector_db "$QUERY"
            else
                echo "❌ No query provided for query action"
                exit 1
            fi
            ;;
        status)
            check_rag_status
            ;;
        *)
            echo "❌ Unknown action: $ACTION"
            exit 1
            ;;
    esac

    echo ""
    echo "================================================================"
    echo "🎉 RAG automation completed!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Integrate RAG with your application"
    echo "  2. Set up automatic updates on documentation changes"
    echo "  3. Monitor query performance and accuracy"
    echo "  4. Fine-tune embedding model if needed"
    echo ""
    echo "🔧 Configuration:"
    echo "  - ChromaDB: http://$CHROMA_HOST:$CHROMA_PORT"
    echo "  - Collection: $COLLECTION_NAME"
    echo "  - Source: $SOURCE_DIR"
    echo "================================================================"
}

# Run main function
main
