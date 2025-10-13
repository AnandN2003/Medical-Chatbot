"""
LLM Configuration Module
Handles Large Language Model setup and configuration.
"""

import google.generativeai as genai
from typing import Optional


class LLMConfig:
    """Manages LLM model configuration and initialization."""
    
    @staticmethod
    def setup_gemini(api_key: str, model_name: str = "models/gemini-2.5-flash"):
        """
        Initialize and configure Google Gemini model.
        
        Args:
            api_key: Google Gemini API key
            model_name: Name of the Gemini model to use
            
        Returns:
            Gemini GenerativeModel object
        """
        print(f"💬 Setting up Gemini model: {model_name}...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        print(f"   ✅ Successfully initialized {model_name}")
        return model
    
    @staticmethod
    def list_available_models(api_key: str):
        """
        List all available Gemini models that support content generation.
        
        Args:
            api_key: Google Gemini API key
            
        Returns:
            List of model names
        """
        genai.configure(api_key=api_key)
        models = genai.list_models()
        available_models = [
            m.name for m in models 
            if 'generateContent' in m.supported_generation_methods
        ]
        return available_models
    
    @staticmethod
    def get_model_info(api_key: str, model_name: str):
        """
        Get information about a specific model.
        
        Args:
            api_key: Google Gemini API key
            model_name: Name of the model
            
        Returns:
            Model information dictionary
        """
        genai.configure(api_key=api_key)
        try:
            model = genai.get_model(model_name)
            return {
                'name': model.name,
                'description': model.description,
                'supported_methods': model.supported_generation_methods,
                'input_token_limit': getattr(model, 'input_token_limit', 'N/A'),
                'output_token_limit': getattr(model, 'output_token_limit', 'N/A'),
            }
        except Exception as e:
            return {'error': str(e)}
