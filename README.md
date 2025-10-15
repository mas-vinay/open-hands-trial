# PDF to Markdown RAG System

A simple yet powerful system that converts PDF documents to Markdown format using the Docling library and provides RAG (Retrieval-Augmented Generation) capabilities for querying document content.

## Features

- **PDF to Markdown Conversion**: Uses Docling library for high-quality PDF to Markdown conversion
- **OCR Support**: Handles scanned PDFs with OCR capabilities
- **Table Structure Recognition**: Preserves table structures during conversion
- **Semantic Search**: Uses sentence transformers for semantic similarity search
- **Vector Storage**: ChromaDB for efficient vector storage and retrieval
- **Web Interface**: Clean, responsive web UI for easy interaction
- **Chunking Strategy**: Intelligent text chunking with overlap for better context preservation
- **RESTful API**: Complete API for programmatic access

## Technology Stack

- **Backend**: FastAPI
- **PDF Processing**: Docling
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB
- **Frontend**: HTML/CSS/JavaScript
- **Additional**: NumPy, Pandas, Pillow

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd open-hands-trial
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:12000`

### Web Interface

1. Open your browser and navigate to `http://localhost:12000`
2. Upload a PDF file using the upload form
3. Wait for processing to complete
4. Use the query form to search through your documents

### API Endpoints

#### Upload PDF
```bash
curl -X POST "http://localhost:12000/upload-pdf" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

#### Query Documents
```bash
curl -X POST "http://localhost:12000/query" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "query=your search query here"
```

#### List Documents
```bash
curl -X GET "http://localhost:12000/documents"
```

#### Health Check
```bash
curl -X GET "http://localhost:12000/health"
```

## System Architecture

### PDF Processing Pipeline
1. **Upload**: PDF file is uploaded via web interface or API
2. **Conversion**: Docling converts PDF to Markdown with OCR and table recognition
3. **Chunking**: Text is split into overlapping chunks for better retrieval
4. **Embedding**: Each chunk is converted to vector embeddings using SentenceTransformers
5. **Storage**: Embeddings and metadata are stored in ChromaDB

### Query Pipeline
1. **Query Processing**: User query is converted to vector embedding
2. **Similarity Search**: ChromaDB performs cosine similarity search
3. **Ranking**: Results are ranked by similarity score
4. **Response**: Top results are returned with metadata and content

## Configuration

### Chunking Parameters
- **Chunk Size**: 1000 characters (configurable)
- **Overlap**: 200 characters (configurable)
- **Breaking Strategy**: Sentence and paragraph boundaries

### Embedding Model
- **Model**: all-MiniLM-L6-v2
- **Dimensions**: 384
- **Language**: English (multilingual support available)

### Vector Database
- **Database**: ChromaDB (persistent storage)
- **Distance Metric**: Cosine similarity
- **Storage Location**: `./chroma_db/`

## Testing

Run the test script to verify system functionality:

```bash
python test_system.py
```

## File Structure

```
open-hands-trial/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── test_system.py        # Test script
├── README.md             # This file
└── chroma_db/            # ChromaDB storage (created automatically)
```

## Performance Considerations

- **Memory Usage**: Embedding model requires ~100MB RAM
- **Storage**: ChromaDB uses disk storage for persistence
- **Processing Time**: PDF conversion time depends on document size and complexity
- **Concurrent Users**: FastAPI supports multiple concurrent requests

## Limitations

- **File Size**: Large PDFs may take longer to process
- **Language**: Optimized for English text (multilingual models available)
- **Image Content**: OCR quality depends on image resolution and clarity
- **Complex Layouts**: Some complex PDF layouts may not convert perfectly

## Future Enhancements

- [ ] Support for multiple embedding models
- [ ] Document summarization capabilities
- [ ] Advanced filtering and search options
- [ ] User authentication and document management
- [ ] Batch processing for multiple PDFs
- [ ] Integration with external LLMs for answer generation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Change port in `app.py` if 12000 is occupied
3. **Memory Issues**: Consider using smaller embedding models for limited RAM
4. **PDF Processing Errors**: Check PDF file integrity and format

### Logs

The application provides detailed console logging for debugging:
- PDF conversion progress
- Embedding generation status
- Query processing information
- Error messages with stack traces

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.
