#!/usr/bin/env python3
"""
Create a sample PDF for testing the RAG system
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_sample_pdf():
    """Create a sample PDF document for testing"""
    
    # Check if reportlab is available
    try:
        from reportlab.lib.pagesizes import letter
    except ImportError:
        print("reportlab not installed. Installing...")
        os.system("pip install reportlab")
        from reportlab.lib.pagesizes import letter
    
    filename = "sample_document.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Content
    story = []
    
    # Title
    story.append(Paragraph("Sample Document for RAG Testing", title_style))
    story.append(Spacer(1, 20))
    
    # Introduction
    story.append(Paragraph("Introduction", styles['Heading2']))
    story.append(Paragraph(
        "This is a sample PDF document created specifically for testing the PDF to Markdown RAG system. "
        "The document contains various sections with different types of content to demonstrate the "
        "system's ability to process and retrieve information from PDF documents.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    # Technology Section
    story.append(Paragraph("Technology Stack", styles['Heading2']))
    story.append(Paragraph(
        "The RAG system uses several key technologies:",
        styles['Normal']
    ))
    story.append(Paragraph(
        "• Docling library for PDF to Markdown conversion<br/>"
        "• SentenceTransformers for generating embeddings<br/>"
        "• ChromaDB for vector storage and similarity search<br/>"
        "• FastAPI for the web service backend<br/>"
        "• HTML/CSS/JavaScript for the user interface",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    # Features Section
    story.append(Paragraph("Key Features", styles['Heading2']))
    story.append(Paragraph(
        "The system provides several important capabilities:",
        styles['Normal']
    ))
    story.append(Paragraph(
        "1. High-quality PDF to Markdown conversion with OCR support<br/>"
        "2. Intelligent text chunking for better context preservation<br/>"
        "3. Semantic search using vector embeddings<br/>"
        "4. Persistent storage of documents and embeddings<br/>"
        "5. RESTful API for programmatic access<br/>"
        "6. User-friendly web interface for easy interaction",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    # Use Cases Section
    story.append(Paragraph("Use Cases", styles['Heading2']))
    story.append(Paragraph(
        "This RAG system can be used for various applications:",
        styles['Normal']
    ))
    story.append(Paragraph(
        "• Document search and retrieval in corporate knowledge bases<br/>"
        "• Research paper analysis and question answering<br/>"
        "• Legal document review and information extraction<br/>"
        "• Educational content organization and querying<br/>"
        "• Technical documentation search and support",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    # Technical Details
    story.append(Paragraph("Technical Implementation", styles['Heading2']))
    story.append(Paragraph(
        "The system implements a sophisticated pipeline for document processing. "
        "When a PDF is uploaded, it goes through several stages: first, the Docling library "
        "converts the PDF to Markdown format while preserving structure and handling OCR for "
        "scanned documents. Next, the text is split into overlapping chunks to maintain context. "
        "Each chunk is then converted to a vector embedding using the all-MiniLM-L6-v2 model. "
        "Finally, the embeddings are stored in ChromaDB for efficient similarity search.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    # Performance Section
    story.append(Paragraph("Performance Characteristics", styles['Heading2']))
    story.append(Paragraph(
        "The system is designed for efficiency and scalability. The embedding model requires "
        "approximately 100MB of RAM and provides 384-dimensional vectors. ChromaDB uses "
        "cosine similarity for matching and supports persistent storage. Processing time "
        "depends on document size and complexity, with typical documents processing in "
        "seconds to minutes.",
        styles['Normal']
    ))
    story.append(Spacer(1, 12))
    
    # Conclusion
    story.append(Paragraph("Conclusion", styles['Heading2']))
    story.append(Paragraph(
        "This sample document demonstrates the type of content that can be processed by the "
        "PDF to Markdown RAG system. Users can upload this document and then query it with "
        "questions like 'What technologies are used?', 'What are the key features?', or "
        "'How does the system work?' to see the retrieval capabilities in action.",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Sample PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_sample_pdf()