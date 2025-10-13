"""
Embeddings Module
Handles embedding model configuration and initialization.
"""

from langchain_community.embeddings import HuggingFaceEmbeddings


def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """
    Initialize and return the HuggingFace embeddings model.
    
    Args:
        model_name: Name of the sentence transformer model to use
        
    Returns:
        HuggingFaceEmbeddings object
    """
    print(f"🤖 Loading embedding model: {model_name}...")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    print("   Embedding model loaded successfully")
    return embeddings


def get_embedding_dimension(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> int:
    """
    Get the dimension of embeddings for a given model.
    
    Args:
        model_name: Name of the sentence transformer model
        
    Returns:
        Dimension of the embedding vectors
    """
    # Common embedding dimensions
    dimension_map = {
        "sentence-transformers/all-MiniLM-L6-v2": 384,
        "sentence-transformers/all-mpnet-base-v2": 768,
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
    }
    
    return dimension_map.get(model_name, 384)  # Default to 384
