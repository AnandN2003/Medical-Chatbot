"""
Medical Chatbot Pipeline
This script contains the complete pipeline for processing medical documents,
creating embeddings, and setting up a RAG-based question-answering system.
"""

import os
from typing import List
from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


def load_pdf_files(data):
    """
    Extract text from PDF files in a directory.
    
    Args:
        data: Path to the directory containing PDF files
        
    Returns:
        List of Document objects containing extracted text
    """
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents


def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """
    Given a list of Document objects, return a new list of Document objects
    containing only 'source' in metadata and the original page_content.
    
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


def text_split(minimal_docs):
    """
    Split the documents into smaller chunks.
    
    Args:
        minimal_docs: List of Document objects to split
        
    Returns:
        List of chunked Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
    )
    texts_chunk = text_splitter.split_documents(minimal_docs)
    return texts_chunk


def download_embeddings():
    """
    Download and return the HuggingFace embeddings model.
    
    Returns:
        HuggingFaceEmbeddings object
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )
    return embeddings


def setup_pinecone(api_key):
    """
    Initialize Pinecone client.
    
    Args:
        api_key: Pinecone API key
        
    Returns:
        Pinecone client object
    """
    pc = Pinecone(api_key=api_key)
    return pc


def create_or_get_index(pc, index_name="medical-chatbot"):
    """
    Create Pinecone index if it doesn't exist, otherwise get existing index.
    
    Args:
        pc: Pinecone client object
        index_name: Name of the index to create/get
        
    Returns:
        Pinecone index object
    """
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=384,  # Dimension of the embeddings
            metric="cosine",  # Cosine similarity
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    index = pc.Index(index_name)
    return index


def setup_vector_store(index, index_name, embedding, texts_chunk=None):
    """
    Setup vector store with Pinecone.
    
    Args:
        index: Pinecone index object
        index_name: Name of the index
        embedding: Embedding model
        texts_chunk: Optional list of documents to add
        
    Returns:
        PineconeVectorStore object
    """
    # Check if index has data
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


def setup_chat_model(gemini_api_key=None, openai_api_key=None):
    """
    Initialize chat model. Tries OpenAI first (Gemini support available).
    
    Args:
        gemini_api_key: Gemini API key (optional - has compatibility issues with current langchain version)
        openai_api_key: OpenAI API key (primary)
        
    Returns:
        Chat model object
    """
    # Use OpenAI as primary (most stable with langchain)
    if openai_api_key:
        try:
            chatModel = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=openai_api_key,
                temperature=0.3,
                max_tokens=150
            )
            print("✅ Successfully initialized OpenAI GPT-3.5-turbo")
            return chatModel
        except Exception as e:
            print(f"❌ OpenAI setup failed: {e}")
    
    # Note: Gemini integration has version conflicts with current langchain-google-genai
    # To use Gemini, you would need to:
    # 1. Downgrade langchain-google-genai or upgrade google-ai-generativelanguage
    # 2. Use model="gemini-1.5-flash-latest" or "gemini-pro"
    # 3. Add convert_system_message_to_human=True parameter
    
    if gemini_api_key:
        print("⚠️ Gemini API key found but not used due to library version conflicts")
        print("   Using OpenAI as fallback. Update langchain-google-genai to use Gemini.")
    
    print("❌ No valid API configuration")
    return None


def create_rag_chain(chatModel, retriever):
    """
    Create RAG (Retrieval-Augmented Generation) chain.
    
    Args:
        chatModel: Chat model object
        retriever: Document retriever object
        
    Returns:
        RAG chain object
    """
    system_prompt = (
        "You are an Medical assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    
    question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain


def main():
    """
    Main function to run the complete pipeline.
    """
    # Get the script's directory and change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from research/
    os.chdir(project_root)
    print(f"Current directory: {os.getcwd()}")
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Check and set environment variables safely
    print("\n🔑 API Key Status:")
    print(f"PINECONE_API_KEY: {'✅ Found' if PINECONE_API_KEY else '❌ Not found'}")
    print(f"OPENAI_API_KEY: {'✅ Found' if OPENAI_API_KEY else '❌ Not found'}")
    print(f"GEMINI_API_KEY: {'✅ Found' if GEMINI_API_KEY else '❌ Not found'}")
    
    if not PINECONE_API_KEY or not OPENAI_API_KEY:
        print("\n❌ Error: Required API keys not found in .env file")
        return
    
    # Set environment variables
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    if GEMINI_API_KEY:
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
    
    print("\n💬 Step 8: Setting up chat model...")
    chatModel = setup_chat_model(GEMINI_API_KEY, OPENAI_API_KEY)
    
    if chatModel is None:
        print("❌ Failed to initialize chat model")
        return
    
    print("\n⛓️ Step 9: Creating RAG chain...")
    rag_chain = create_rag_chain(chatModel, retriever)
    print("RAG chain created successfully")
    
    # Test the system
    print("\n🧪 Testing the system...")
    test_question = "what is Acromegaly and gigantism?"
    print(f"Question: {test_question}")
    
    response = rag_chain.invoke({"input": test_question})
    print(f"\nAnswer: {response['answer']}")
    
    print("\n✅ Pipeline completed successfully!")
    
    # Return objects for interactive use
    return {
        'rag_chain': rag_chain,
        'retriever': retriever,
        'docsearch': docsearch,
        'chatModel': chatModel,
        'embedding': embedding
    }


if __name__ == "__main__":
    # Run the main pipeline
    result = main()
    
    # Optional: Uncomment below for Interactive query loop
    # print("\n" + "="*50)
    # print("Medical Chatbot is ready!")
    # print("You can now ask questions interactively.")
    # print("Type 'quit' or 'exit' to stop.")
    # print("="*50 + "\n")
    # 
    # if result and result.get('rag_chain'):
    #     rag_chain = result['rag_chain']
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
    #             response = rag_chain.invoke({"input": question})
    #             print(f"\n💡 Answer: {response['answer']}")
    #         except Exception as e:
    #             print(f"\n❌ Error: {e}")
