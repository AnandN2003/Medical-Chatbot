"""
Data Loader Module
Handles loading and processing PDF documents.
"""

from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document


def load_pdf_files(data_path: str):
    """
    Extract text from PDF files in a directory.
    
    Args:
        data_path: Path to the directory containing PDF files
        
    Returns:
        List of Document objects containing extracted text
    """
    loader = DirectoryLoader(
        data_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents


def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """
    Filter documents to keep only essential metadata.
    
    Args:
        docs: List of Document objects to filter
        
    Returns:
        List of filtered Document objects with minimal metadata
    """
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src}
            )
        )
    return minimal_docs


def split_documents(documents: List[Document], chunk_size: int = 500, chunk_overlap: int = 20):
    """
    Split documents into smaller chunks for better retrieval.
    
    Args:
        documents: List of Document objects to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of chunked Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def process_documents(data_path: str, chunk_size: int = 500, chunk_overlap: int = 20):
    """
    Complete pipeline: Load PDFs, filter metadata, and split into chunks.
    
    Args:
        data_path: Path to the directory containing PDF files
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of processed and chunked Document objects
    """
    print(f"📚 Loading PDF files from {data_path}...")
    documents = load_pdf_files(data_path)
    print(f"   Loaded {len(documents)} documents")
    
    print("🔧 Filtering documents...")
    filtered_docs = filter_to_minimal_docs(documents)
    print(f"   Filtered {len(filtered_docs)} documents")
    
    print("✂️ Splitting documents into chunks...")
    chunks = split_documents(filtered_docs, chunk_size, chunk_overlap)
    print(f"   Created {len(chunks)} chunks")
    
    return chunks
