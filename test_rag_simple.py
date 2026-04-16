#!/usr/bin/env python3
"""
Simple test for RAG implementation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from embedding_agent.embedder import DocumentEmbedder
    from embedding_agent.indexer import DocumentIndexer
    from embedding_agent.search import DocumentSearcher
    print("✅ Successfully imported embedding_agent modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_embedder():
    """Test the document embedder."""
    print("\n🔧 Testing DocumentEmbedder...")
    embedder = DocumentEmbedder()
    
    # Test single embedding
    text = "This is a test document about microservices architecture."
    embedding = embedder.embed(text)
    
    if embedding:
        print(f"✅ Embedding generated: {len(embedding)} dimensions")
        
        # Test similarity
        text2 = "Another document about distributed systems."
        embedding2 = embedder.embed(text2)
        similarity = embedder.compute_similarity(embedding, embedding2)
        print(f"✅ Similarity between texts: {similarity:.4f}")
        
        # Test batch
        texts = ["First document", "Second document", "Third document"]
        embeddings = embedder.embed_batch(texts)
        print(f"✅ Batch embeddings: {len(embeddings)}")
        
        return True
    else:
        print("❌ Failed to generate embedding")
        return False

def test_indexer():
    """Test the document indexer."""
    print("\n🔧 Testing DocumentIndexer...")
    indexer = DocumentIndexer()
    
    # Add some test documents
    doc1_id = indexer.add_document(
        "Microservices architecture is a design pattern where applications are composed of small, independent services.",
        {"source": "test", "topic": "architecture"}
    )
    doc2_id = indexer.add_document(
        "Kubernetes is a container orchestration platform for managing microservices deployments.",
        {"source": "test", "topic": "deployment"}
    )
    
    print(f"✅ Added documents: {doc1_id}, {doc2_id}")
    print(f"✅ Total documents: {len(indexer.documents)}")
    
    # Test search
    results = indexer.search("microservices orchestration", top_k=2)
    print(f"✅ Search results: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"  {i+1}. Score: {result['score']:.3f}, Text: {result['text'][:50]}...")
    
    return len(results) > 0

def test_searcher():
    """Test the high-level searcher."""
    print("\n🔧 Testing DocumentSearcher...")
    searcher = DocumentSearcher()
    
    # Add a test document
    from embedding_agent.indexer import DocumentIndexer
    searcher.indexer.add_document(
        "RAG stands for Retrieval-Augmented Generation, a technique for enhancing LLMs with external knowledge.",
        {"source": "test", "topic": "AI"}
    )
    
    results = searcher.search("What is RAG?", top_k=1)
    
    if results:
        print(f"✅ Search successful: {len(results)} results")
        for result in results:
            print(f"  - {result['text'][:60]}...")
        return True
    else:
        print("❌ No search results")
        return False

def test_rag_advisor():
    """Test the RAG advisor plugin."""
    print("\n🔧 Testing RAGAdvisor plugin...")
    
    try:
        from assistant_orchestrator.plugins.rag_advisor import RAGAdvisor
        import tempfile
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            advisor = RAGAdvisor(Path(tmpdir))
            stats = advisor.get_stats()
            
            print(f"✅ RAGAdvisor initialized: {stats}")
            
            # Test advice
            advice = advisor.get_advice("architecture")
            print(f"✅ Got advice: {advice.get('advice', 'No advice')[:50]}...")
            
            return True
    except ImportError as e:
        print(f"❌ Failed to import RAGAdvisor: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing RAGAdvisor: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running Priority 1 Implementation Tests")
    print("=" * 60)
    
    tests = [
        ("DocumentEmbedder", test_embedder),
        ("DocumentIndexer", test_indexer),
        ("DocumentSearcher", test_searcher),
        ("RAGAdvisor Plugin", test_rag_advisor),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    all_passed = True
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All Priority 1 tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
