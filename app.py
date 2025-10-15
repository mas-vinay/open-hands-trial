import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI(title="PDF to Markdown RAG System", version="1.0.0")

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for the RAG system
embedding_model = None
chroma_client = None
collection = None
document_store = {}

class PDFToMarkdownRAG:
    def __init__(self):
        # Configure PDF pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        
        # Set up format options
        pdf_format_option = PdfFormatOption(pipeline_options=pipeline_options)
        
        # Initialize converter with format options
        self.converter = DocumentConverter(
            format_options={InputFormat.PDF: pdf_format_option}
        )
        self.setup_embedding_model()
        self.setup_vector_store()
        
    def setup_embedding_model(self):
        """Initialize the sentence transformer model for embeddings"""
        global embedding_model
        print("Loading embedding model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded successfully!")
        
    def setup_vector_store(self):
        """Initialize ChromaDB for vector storage"""
        global chroma_client, collection
        print("Setting up vector store...")
        
        # Create a persistent ChromaDB client
        persist_directory = "./chroma_db"
        os.makedirs(persist_directory, exist_ok=True)
        
        chroma_client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        try:
            collection = chroma_client.get_collection("pdf_documents")
            print("Existing collection loaded!")
        except:
            collection = chroma_client.create_collection(
                name="pdf_documents",
                metadata={"hnsw:space": "cosine"}
            )
            print("New collection created!")
    
    def convert_pdf_to_markdown(self, pdf_path: str) -> str:
        """Convert PDF to Markdown using Docling"""
        try:
            print(f"Converting PDF: {pdf_path}")
            
            # Convert the document
            result = self.converter.convert(pdf_path)
            
            # Export to markdown
            markdown_content = result.document.export_to_markdown()
            
            print(f"Successfully converted PDF to Markdown ({len(markdown_content)} characters)")
            return markdown_content
            
        except Exception as e:
            print(f"Error converting PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting PDF: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    chunk = text[start:break_point + 1]
                    end = break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
                
        return [chunk for chunk in chunks if chunk]
    
    def add_document_to_store(self, doc_id: str, filename: str, markdown_content: str):
        """Add document chunks to vector store"""
        global collection, embedding_model, document_store
        
        try:
            print(f"Adding document {filename} to vector store...")
            
            # Chunk the markdown content
            chunks = self.chunk_text(markdown_content)
            print(f"Created {len(chunks)} chunks")
            
            # Generate embeddings for chunks
            embeddings = embedding_model.encode(chunks).tolist()
            
            # Prepare data for ChromaDB
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "document_id": doc_id,
                    "filename": filename,
                    "chunk_index": i,
                    "chunk_text": chunk[:200] + "..." if len(chunk) > 200 else chunk
                }
                for i, chunk in enumerate(chunks)
            ]
            
            # Add to ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            # Store document metadata
            document_store[doc_id] = {
                "filename": filename,
                "markdown_content": markdown_content,
                "chunk_count": len(chunks),
                "doc_id": doc_id
            }
            
            print(f"Successfully added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            print(f"Error adding document to store: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error adding document to store: {str(e)}")
    
    def query_documents(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Query the document store using semantic search"""
        global collection, embedding_model
        
        try:
            print(f"Querying documents with: '{query}'")
            
            # Generate embedding for query
            query_embedding = embedding_model.encode([query]).tolist()
            
            # Search in ChromaDB
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return {
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results)
            }
            
        except Exception as e:
            print(f"Error querying documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

# Initialize the RAG system
rag_system = PDFToMarkdownRAG()

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the main HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF to Markdown RAG System</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-section, .query-section {
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            input[type="file"], input[type="text"] {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-right: 10px;
            }
            button:hover {
                background-color: #0056b3;
            }
            button:disabled {
                background-color: #ccc;
                cursor: not-allowed;
            }
            .results {
                margin-top: 20px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #007bff;
            }
            .result-item {
                margin-bottom: 20px;
                padding: 15px;
                background: white;
                border-radius: 5px;
                border: 1px solid #e9ecef;
            }
            .result-meta {
                font-size: 12px;
                color: #666;
                margin-bottom: 10px;
            }
            .result-content {
                line-height: 1.6;
                white-space: pre-wrap;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 2s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .status.success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF to Markdown RAG System</h1>
            
            <div class="upload-section">
                <h2>Upload PDF Document</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="pdfFile">Select PDF File:</label>
                        <input type="file" id="pdfFile" name="file" accept=".pdf" required>
                    </div>
                    <button type="submit">Upload & Process PDF</button>
                </form>
                <div id="uploadStatus"></div>
                <div id="uploadLoading" class="loading">
                    <div class="spinner"></div>
                    <p>Processing PDF... This may take a few moments.</p>
                </div>
            </div>
            
            <div class="query-section">
                <h2>Query Documents</h2>
                <form id="queryForm">
                    <div class="form-group">
                        <label for="queryText">Enter your question:</label>
                        <input type="text" id="queryText" name="query" placeholder="e.g., What is the main topic of the document?" required>
                    </div>
                    <button type="submit">Search</button>
                </form>
                <div id="queryLoading" class="loading">
                    <div class="spinner"></div>
                    <p>Searching documents...</p>
                </div>
                <div id="queryResults"></div>
            </div>
        </div>

        <script>
            // Upload form handler
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                const fileInput = document.getElementById('pdfFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select a PDF file');
                    return;
                }
                
                formData.append('file', file);
                
                const statusDiv = document.getElementById('uploadStatus');
                const loadingDiv = document.getElementById('uploadLoading');
                
                statusDiv.innerHTML = '';
                loadingDiv.style.display = 'block';
                
                try {
                    const response = await fetch('/upload-pdf', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        statusDiv.innerHTML = `
                            <div class="status success">
                                <strong>Success!</strong> PDF processed successfully.<br>
                                Document ID: ${result.document_id}<br>
                                Chunks created: ${result.chunk_count}
                            </div>
                        `;
                        fileInput.value = '';
                    } else {
                        statusDiv.innerHTML = `
                            <div class="status error">
                                <strong>Error:</strong> ${result.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `
                        <div class="status error">
                            <strong>Error:</strong> ${error.message}
                        </div>
                    `;
                } finally {
                    loadingDiv.style.display = 'none';
                }
            });
            
            // Query form handler
            document.getElementById('queryForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const queryText = document.getElementById('queryText').value;
                const resultsDiv = document.getElementById('queryResults');
                const loadingDiv = document.getElementById('queryLoading');
                
                resultsDiv.innerHTML = '';
                loadingDiv.style.display = 'block';
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `query=${encodeURIComponent(queryText)}`
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        if (result.results.length === 0) {
                            resultsDiv.innerHTML = `
                                <div class="results">
                                    <p>No results found for your query.</p>
                                </div>
                            `;
                        } else {
                            let resultsHTML = `
                                <div class="results">
                                    <h3>Search Results (${result.total_results} found)</h3>
                            `;
                            
                            result.results.forEach((item, index) => {
                                const similarity = (item.similarity_score * 100).toFixed(1);
                                resultsHTML += `
                                    <div class="result-item">
                                        <div class="result-meta">
                                            <strong>Result ${index + 1}</strong> | 
                                            Similarity: ${similarity}% | 
                                            Document: ${item.metadata.filename} | 
                                            Chunk: ${item.metadata.chunk_index + 1}
                                        </div>
                                        <div class="result-content">${item.content}</div>
                                    </div>
                                `;
                            });
                            
                            resultsHTML += '</div>';
                            resultsDiv.innerHTML = resultsHTML;
                        }
                    } else {
                        resultsDiv.innerHTML = `
                            <div class="status error">
                                <strong>Error:</strong> ${result.detail}
                            </div>
                        `;
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `
                        <div class="status error">
                            <strong>Error:</strong> ${error.message}
                        </div>
                    `;
                } finally {
                    loadingDiv.style.display = 'none';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Convert PDF to Markdown
        markdown_content = rag_system.convert_pdf_to_markdown(temp_file_path)
        
        # Add to vector store
        rag_system.add_document_to_store(doc_id, file.filename, markdown_content)
        
        return JSONResponse({
            "message": "PDF processed successfully",
            "document_id": doc_id,
            "filename": file.filename,
            "chunk_count": document_store[doc_id]["chunk_count"]
        })
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

@app.post("/query")
async def query_documents(query: str = Form(...)):
    """Query the document store"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = rag_system.query_documents(query)
    return JSONResponse(results)

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    return JSONResponse({
        "documents": [
            {
                "doc_id": doc_id,
                "filename": info["filename"],
                "chunk_count": info["chunk_count"]
            }
            for doc_id, info in document_store.items()
        ]
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "message": "PDF to Markdown RAG System is running"})

if __name__ == "__main__":
    print("Starting PDF to Markdown RAG System...")
    print("Access the web interface at: http://localhost:12000")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=12000,
        reload=False
    )