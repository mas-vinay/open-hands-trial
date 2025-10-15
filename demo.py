#!/usr/bin/env python3
"""
Demonstration script for the PDF to Markdown RAG System
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:12000"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print(f"✅ Health check passed: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    print()

def upload_pdf(filename):
    """Upload a PDF file"""
    print(f"📄 Uploading PDF: {filename}")
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return None
    
    with open(filename, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload-pdf", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful!")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Filename: {result['filename']}")
        print(f"   Chunks created: {result['chunk_count']}")
        return result['document_id']
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None
    print()

def list_documents():
    """List all uploaded documents"""
    print("📚 Listing documents...")
    response = requests.get(f"{BASE_URL}/documents")
    if response.status_code == 200:
        docs = response.json()['documents']
        print(f"✅ Found {len(docs)} documents:")
        for doc in docs:
            print(f"   - {doc['filename']} (ID: {doc['doc_id'][:8]}..., {doc['chunk_count']} chunks)")
    else:
        print(f"❌ Failed to list documents: {response.status_code}")
    print()

def query_document(query):
    """Query the document collection"""
    print(f"🔍 Querying: '{query}'")
    data = {'query': query}
    response = requests.post(f"{BASE_URL}/query", data=data)
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Found {results['total_results']} results:")
        for i, result in enumerate(results['results'][:3], 1):  # Show top 3
            print(f"\n   Result {i} (similarity: {result['similarity_score']:.3f}):")
            print(f"   Source: {result['metadata']['filename']}")
            content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            print(f"   Content: {content}")
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(f"   Error: {response.text}")
    print()

def main():
    """Run the complete demonstration"""
    print("🚀 PDF to Markdown RAG System Demonstration")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # List existing documents
    list_documents()
    
    # Upload sample PDF if it exists
    if os.path.exists("sample_document.pdf"):
        doc_id = upload_pdf("sample_document.pdf")
        if doc_id:
            # Wait a moment for processing
            time.sleep(2)
            
            # List documents again
            list_documents()
            
            # Test various queries
            queries = [
                "What technologies are used in the system?",
                "How does the system work?",
                "What are the key features?",
                "What are the use cases?",
                "How is performance characterized?"
            ]
            
            for query in queries:
                query_document(query)
                time.sleep(1)  # Brief pause between queries
    else:
        print("⚠️  Sample PDF not found. Please create one first with:")
        print("   python create_sample_pdf.py")
    
    print("🎉 Demonstration complete!")
    print(f"\n🌐 Access the web interface at: {BASE_URL}")

if __name__ == "__main__":
    main()