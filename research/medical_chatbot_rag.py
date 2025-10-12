"""
Medical Chatbot Pipeline with Gemini
This version uses Google's Gemini AI model directly without LangChain compatibility issues.
"""

import os
from typing import List
from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai


def load_pdf_files(data):
    """Extract text from PDF files in a directory."""
    loader = DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents


def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """Filter documents to minimal metadata."""
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        minimal_docs.append(Document(page_content=doc.page_content, metadata={"source": src}))
    return minimal_docs


def text_split(minimal_docs):
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    texts_chunk = text_splitter.split_documents(minimal_docs)
    return texts_chunk


def download_embeddings():
    """Download and return the HuggingFace embeddings model."""
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings


def setup_pinecone(api_key):
    """Initialize Pinecone client."""
    pc = Pinecone(api_key=api_key)
    return pc


def create_or_get_index(pc, index_name="medical-chatbot"):
    """Create Pinecone index if it doesn't exist."""
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(index_name)
    return index


def setup_vector_store(index, index_name, embedding, texts_chunk=None):
    """Setup vector store with Pinecone."""
    index_stats = index.describe_index_stats()
    total_vector_count = index_stats.get('total_vector_count', 0)
    
    print(f"📊 Vectors in index: {total_vector_count}")
    
    if total_vector_count == 0 and texts_chunk:
        print("📤 First run - uploading data...")
        docsearch = PineconeVectorStore.from_documents(
            documents=texts_chunk,
            embedding=embedding,
            index_name=index_name
        )
    else:
        print("✅ Data exists - loading index...")
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embedding
        )
    return docsearch


def setup_gemini(api_key, model_name="models/gemini-2.5-flash"):
    """Initialize Gemini model."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    print(f"✅ Successfully initialized {model_name}")
    return model


def query_with_gemini(gemini_model, retriever, question):
    """
    Query the medical chatbot using Gemini.
    
    Args:
        gemini_model: Gemini model instance
        retriever: Pinecone retriever
        question: User's question
        
    Returns:
        Answer string
    """
    # Retrieve relevant documents
    docs = retriever.invoke(question)
    
    # Prepare context from retrieved documents
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Create prompt
    prompt = f"""You are a medical assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, say that you don't know.
Use three sentences maximum and keep the answer concise.

Context:
{context}

Question: {question}

Answer:"""
    
    # Generate response
    response = gemini_model.generate_content(prompt)
    return response.text


def main():
    """Main function to run the complete pipeline."""
    # Get the script's directory and change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    print(f"Current directory: {os.getcwd()}")
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Check API keys
    print("\n🔑 API Key Status:")
    print(f"PINECONE_API_KEY: {'✅ Found' if PINECONE_API_KEY else '❌ Not found'}")
    print(f"GEMINI_API_KEY: {'✅ Found' if GEMINI_API_KEY else '❌ Not found'}")
    
    if not PINECONE_API_KEY or not GEMINI_API_KEY:
        print("\n❌ Error: Required API keys not found in .env file")
        return
    
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    
    print("\n📚 Step 1: Loading PDF files...")
    extracted_data = load_pdf_files("data")
    print(f"Loaded {len(extracted_data)} documents")
    
    print("\n🔧 Step 2: Filtering documents...")
    minimal_docs = filter_to_minimal_docs(extracted_data)
    print(f"Filtered {len(minimal_docs)} documents")
    
    print("\n✂️ Step 3: Splitting text into chunks...")
    texts_chunk = text_split(minimal_docs)
    print(f"Number of chunks: {len(texts_chunk)}")
    
    print("\n🤖 Step 4: Downloading embeddings model...")
    embedding = download_embeddings()
    print("Embeddings model loaded successfully")
    
    print("\n📌 Step 5: Setting up Pinecone...")
    pc = setup_pinecone(PINECONE_API_KEY)
    index_name = "medical-chatbot"
    index = create_or_get_index(pc, index_name)
    
    print("\n💾 Step 6: Setting up vector store...")
    docsearch = setup_vector_store(index, index_name, embedding, texts_chunk)
    
    print("\n🔍 Step 7: Creating retriever...")
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    print("\n💬 Step 8: Setting up Gemini...")
    gemini_model = setup_gemini(GEMINI_API_KEY)
    
    # Test the system
    print("\n🧪 Testing the system...")
    test_question = "what is Acromegaly and gigantism?"
    print(f"Question: {test_question}")
    
    answer = query_with_gemini(gemini_model, retriever, test_question)
    print(f"\nAnswer: {answer}")
    
    print("\n✅ Pipeline completed successfully!")
    
    return {
        'gemini_model': gemini_model,
        'retriever': retriever,
        'docsearch': docsearch,
        'embedding': embedding
    }


if __name__ == "__main__":
    result = main()
    
    # Interactive query loop (commented out by default)
    # if result and result.get('gemini_model'):
    #     gemini_model = result['gemini_model']
    #     retriever = result['retriever']
    #     
    #     print("\n" + "="*50)
    #     print("Medical Chatbot with Gemini is ready!")
    #     print("Type 'quit' or 'exit' to stop.")
    #     print("="*50 + "\n")
    #     
    #     while True:
    #         question = input("\n🩺 Your question: ").strip()
    #         
    #         if question.lower() in ['quit', 'exit', 'q']:
    #             print("\n👋 Goodbye!")
    #             break
    #         
    #         if not question:
    #             continue
    #         
    #         try:
    #             answer = query_with_gemini(gemini_model, retriever, question)
    #             print(f"\n💡 Answer: {answer}")
    #         except Exception as e:
    #             print(f"\n❌ Error: {e}")
