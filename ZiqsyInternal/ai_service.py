import json
import os
import pandas as pd
from openai import OpenAI
import anthropic
from anthropic import Anthropic

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
# the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

openai_client = None
anthropic_client = None

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

if ANTHROPIC_API_KEY:
    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Available LLM models
AVAILABLE_MODELS = {
    "gpt-4o": {"provider": "openai", "name": "GPT-4o (OpenAI)", "max_tokens": 4096},
    "gpt-4o-mini": {"provider": "openai", "name": "GPT-4o Mini (OpenAI)", "max_tokens": 4096},
    "claude-3-5-sonnet-20241022": {"provider": "anthropic", "name": "Claude 3.5 Sonnet (Anthropic)", "max_tokens": 4096},
    "claude-3-haiku-20240307": {"provider": "anthropic", "name": "Claude 3 Haiku (Anthropic)", "max_tokens": 4096}
}

def get_available_models():
    """Get list of available AI models based on configured API keys"""
    available = {}
    for model_id, config in AVAILABLE_MODELS.items():
        if config["provider"] == "openai" and openai_client:
            available[model_id] = config
        elif config["provider"] == "anthropic" and anthropic_client:
            available[model_id] = config
    return available

def analyze_dataset_with_ai(dataset_df, question, model_id="gpt-4o"):
    """Analyze dataset with AI using the selected model"""
    available_models = get_available_models()
    
    if not available_models:
        return {"error": "No AI models are available. Please configure API keys."}
    
    if model_id not in available_models:
        model_id = list(available_models.keys())[0]  # Use first available model
    
    model_config = available_models[model_id]
    
    # Prepare dataset summary for context
    dataset_info = {
        "shape": dataset_df.shape,
        "columns": list(dataset_df.columns),
        "dtypes": dataset_df.dtypes.to_dict(),
        "sample_data": dataset_df.head(5).to_dict('records'),
        "summary_stats": dataset_df.describe().to_dict() if len(dataset_df.select_dtypes(include='number').columns) > 0 else {}
    }
    
    # Create context prompt
    context_prompt = f"""
    You are analyzing a dataset with the following characteristics:
    
    Dataset Shape: {dataset_info['shape'][0]} rows, {dataset_info['shape'][1]} columns
    
    Columns and Types:
    {json.dumps(dataset_info['dtypes'], indent=2)}
    
    Sample Data (first 5 rows):
    {json.dumps(dataset_info['sample_data'], indent=2)}
    
    Summary Statistics:
    {json.dumps(dataset_info['summary_stats'], indent=2)}
    
    User Question: {question}
    
    Please provide a detailed, insightful analysis based on the dataset context above. 
    Focus on actionable insights and patterns you can identify from the data structure and sample.
    """
    
    try:
        if model_config["provider"] == "openai":
            response = openai_client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst expert. Provide clear, actionable insights about datasets based on their structure and content."
                    },
                    {
                        "role": "user",
                        "content": context_prompt
                    }
                ],
                max_tokens=model_config["max_tokens"]
            )
            return {
                "response": response.choices[0].message.content,
                "model_used": model_config["name"],
                "provider": "OpenAI"
            }
            
        elif model_config["provider"] == "anthropic":
            response = anthropic_client.messages.create(
                model=model_id,
                max_tokens=model_config["max_tokens"],
                messages=[
                    {
                        "role": "user",
                        "content": context_prompt
                    }
                ],
                system="You are a data analyst expert. Provide clear, actionable insights about datasets based on their structure and content."
            )
            return {
                "response": response.content[0].text,
                "model_used": model_config["name"],
                "provider": "Anthropic"
            }
            
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}

def generate_file_description(file_path, file_name, file_extension):
    """Generate AI description for a file based on its path, name, and extension"""
    if not openai_client:
        return "AI descriptions require OpenAI API key configuration"
    
    try:
        prompt = f"""
        Analyze this file and provide a brief, professional description of what it likely contains:
        
        File path: {file_path}
        File name: {file_name}
        File extension: {file_extension}
        
        Based on the file name, extension, and path structure, describe what this file likely contains and its purpose.
        Keep the description concise (1-2 sentences) and professional.
        
        Respond with JSON in this format:
        {{"description": "your description here"}}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical file analyst. Provide accurate, concise descriptions of files based on their names and extensions."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
            return result.get("description", "File description unavailable")
        else:
            return "File description unavailable"
        
    except Exception as e:
        return f"Unable to generate description: {str(e)}"

def generate_folder_description(folder_path, folder_name, file_list):
    """Generate AI description for a folder based on its contents"""
    if not openai_client:
        return "AI descriptions require OpenAI API key configuration"
    
    try:
        file_summary = ", ".join(file_list[:10])  # First 10 files
        if len(file_list) > 10:
            file_summary += f" and {len(file_list) - 10} more files"
            
        prompt = f"""
        Analyze this folder and provide a brief description of what it contains:
        
        Folder path: {folder_path}
        Folder name: {folder_name}
        Contains: {file_summary}
        Total files: {len(file_list)}
        
        Based on the folder name, path, and contents, describe what this folder is used for.
        Keep the description concise (1-2 sentences) and professional.
        
        Respond with JSON in this format:
        {{"description": "your description here"}}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical folder analyst. Provide accurate, concise descriptions of folders based on their names and contents."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
            return result.get("description", "Folder description unavailable")
        else:
            return "Folder description unavailable"
        
    except Exception as e:
        return f"Unable to generate description: {str(e)}"