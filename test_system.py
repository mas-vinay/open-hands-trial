#!/usr/bin/env python3
"""
Simple test script for the PDF to Markdown RAG System
"""

import requests
import time
import os

def test_system():
    """Test the PDF to Markdown RAG system"""
    base_url = "http://localhost:12000"
    
    print("🧪 Testing PDF to Markdown RAG System")
    print("=" * 50)
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running.")
        return False
    
    # Test document listing (should be empty initially)
    print("\n2. Testing document listing...")
    try:
        response = requests.get(f"{base_url}/documents")
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ Document listing works. Found {len(docs['documents'])} documents")
        else:
            print("❌ Document listing failed")
    except Exception as e:
        print(f"❌ Document listing error: {e}")
    
    # Test query (should work even with no documents)
    print("\n3. Testing query system...")
    try:
        response = requests.post(
            f"{base_url}/query",
            data={"query": "test query"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query system works. Found {result['total_results']} results")
        else:
            print("❌ Query system failed")
    except Exception as e:
        print(f"❌ Query system error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Basic system tests completed!")
    print("\nTo test with actual PDFs:")
    print("1. Open your browser and go to http://localhost:12000")
    print("2. Upload a PDF file using the web interface")
    print("3. Try querying the content")
    
    return True

if __name__ == "__main__":
    test_system()