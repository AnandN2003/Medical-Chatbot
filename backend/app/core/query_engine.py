"""
Query Engine Module
Handles RAG (Retrieval-Augmented Generation) query processing.
"""

from typing import List
from langchain.schema import Document


class QueryEngine:
    """Manages RAG query processing and response generation."""
    
    def __init__(self, llm_model, retriever):
        """
        Initialize query engine.
        
        Args:
            llm_model: Language model for generation
            retriever: Document retriever for context
        """
        self.llm_model = llm_model
        self.retriever = retriever
        
    def create_prompt(self, question: str, context: str) -> str:
        """
        Create a prompt combining context and question.
        
        Args:
            question: User's question
            context: Retrieved context from documents
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a medical assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, say that you don't know.
Use three sentences maximum and keep the answer concise.

Context:
{context}

Question: {question}

Answer:"""
        return prompt
    
    def retrieve_context(self, question: str, top_k: int = 3) -> tuple[List[Document], str]:
        """
        Retrieve relevant documents and format as context.
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            
        Returns:
            Tuple of (list of documents, formatted context string)
        """
        # Retrieve relevant documents
        docs = self.retriever.invoke(question)
        
        # Combine document contents into context
        context = "\n\n".join([doc.page_content for doc in docs])
        
        return docs, context
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate response using the LLM.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            Generated response text
        """
        response = self.llm_model.generate_content(prompt)
        return response.text
    
    def query(self, question: str, top_k: int = 3, return_sources: bool = False):
        """
        Process a query through the RAG pipeline.
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve for context
            return_sources: Whether to return source documents
            
        Returns:
            Answer string or dict with answer and sources
        """
        # Retrieve context
        docs, context = self.retrieve_context(question, top_k)
        
        # Create prompt
        prompt = self.create_prompt(question, context)
        
        # Generate response
        answer = self.generate_response(prompt)
        
        if return_sources:
            sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
            return {
                'answer': answer,
                'sources': sources,
                'context_docs': docs
            }
        
        return answer
    
    def interactive_query(self):
        """
        Start an interactive query session.
        """
        print("\n" + "="*60)
        print("🩺 Medical Chatbot - Interactive Mode")
        print("Type 'quit', 'exit', or 'q' to stop.")
        print("="*60 + "\n")
        
        while True:
            question = input("\n💬 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                print("⚠️ Please enter a question.")
                continue
            
            try:
                print("\n🔍 Searching for relevant information...")
                result = self.query(question, return_sources=True)
                
                print(f"\n💡 Answer: {result['answer']}")
                print(f"\n📚 Sources: {', '.join(set(result['sources']))}")
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
