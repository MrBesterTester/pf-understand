from google import genai
import os
import logging
import json
from datetime import datetime

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
)

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"


# By default, we Google Gemini 2.5 pro, as it shows great performance for code understanding
def call_llm(prompt: str, use_cache: bool = True) -> str:
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")

    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except:
                logger.warning(f"Failed to load cache, starting with empty cache")

        # Return from cache if exists
        if prompt in cache:
            logger.info(f"RESPONSE: {cache[prompt]}")
            return cache[prompt]

    from google import genai

    # Configure the API key
    GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Get the model and generate content
    model = "models/gemini-2.5-pro-preview-03-25"  # Note the "models/" prefix
    response = client.models.generate_content(
        model=model, 
        contents=[prompt]
    )
    response_text = response.text

    # Log and return
    logger.info(f"RESPONSE: {response_text}")
    
    return response_text


# # Use Azure OpenAI
# def call_llm(prompt, use_cache: bool = True):
#     from openai import AzureOpenAI

#     endpoint = "https://<azure openai name>.openai.azure.com/"
#     deployment = "<deployment name>"

#     subscription_key = "<azure openai key>"
#     api_version = "<api version>"

#     client = AzureOpenAI(
#         api_version=api_version,
#         azure_endpoint=endpoint,
#         api_key=subscription_key,
#     )

#     r = client.chat.completions.create(
#         model=deployment,
#         messages=[{"role": "user", "content": prompt}],
#         response_format={
#             "type": "text"
#         },
#         max_completion_tokens=40000,
#         reasoning_effort="medium",
#         store=False
#     )
#     return r.choices[0].message.content

# Use Anthropic Claude 3.7 Sonnet Extended Thinking
# def call_llm(prompt, use_cache: bool = True):
#     from anthropic import Anthropic
#     import time
#     import random
    
#     # Log the prompt
#     logger.info(f"PROMPT: {prompt}")

#     # Check cache if enabled
#     if use_cache:
#         # Load cache from disk
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 logger.warning(f"Failed to load cache, starting with empty cache")

#         # Return from cache if exists
#         if prompt in cache:
#             logger.info(f"RESPONSE: {cache[prompt]}")
#             return cache[prompt]
    
#     # Initialize API client
#     client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key"))
    
#     # Retry configuration
#     max_retries = 5
#     retry_count = 0
#     backoff_time = 1  # Start with 1 second backoff
    
#     while retry_count < max_retries:
#         try:
#             response = client.messages.create(
#                 model="claude-3-7-sonnet-20250219",
#                 max_tokens=21000,
#                 thinking={
#                     "type": "enabled",
#                     "budget_tokens": 20000
#                 },
#                 messages=[
#                     {"role": "user", "content": prompt}
#                 ]
#             )
#             response_text = response.content[1].text
            
#             # Log the response
#             logger.info(f"RESPONSE: {response_text}")
            
#             # Update cache if enabled
#             if use_cache:
#                 # Load cache again to avoid overwrites
#                 cache = {}
#                 if os.path.exists(cache_file):
#                     try:
#                         with open(cache_file, "r", encoding="utf-8") as f:
#                             cache = json.load(f)
#                     except:
#                         pass

#                 # Add to cache and save
#                 cache[prompt] = response_text
#                 try:
#                     with open(cache_file, "w", encoding="utf-8") as f:
#                         json.dump(cache, f)
#                 except Exception as e:
#                     logger.error(f"Failed to save cache: {e}")
                    
#             return response_text
            
#         except Exception as e:
#             retry_count += 1
#             if "rate limit" in str(e).lower() or "429" in str(e):
#                 # Calculate backoff time with jitter
#                 jitter = random.uniform(0.8, 1.2)
#                 wait_time = backoff_time * jitter
                
#                 logger.warning(f"Rate limit exceeded. Retry {retry_count}/{max_retries}. Waiting for {wait_time:.2f} seconds...")
#                 print(f"Rate limit exceeded. Retry {retry_count}/{max_retries}. Waiting for {wait_time:.2f} seconds...")
                
#                 time.sleep(wait_time)
#                 # Exponential backoff - double the wait time for next attempt
#                 backoff_time *= 2
#             else:
#                 logger.error(f"API error: {e}")
#                 if retry_count >= max_retries:
#                     raise
#                 time.sleep(1)  # Brief pause before retrying other errors
    
#     raise Exception(f"Failed to get response after {max_retries} retries")

# # Use OpenAI o1
# def call_llm(prompt, use_cache: bool = True):
#     from openai import OpenAI
#     client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
#     r = client.chat.completions.create(
#         model="o1",
#         messages=[{"role": "user", "content": prompt}],
#         response_format={
#             "type": "text"
#         },
#         reasoning_effort="medium",
#         store=False
#     )
#     return r.choices[0].message.content

# Use OpenRouter API
# def call_llm(prompt: str, use_cache: bool = True) -> str:
#     import requests
#     # Log the prompt
#     logger.info(f"PROMPT: {prompt}")

#     # Check cache if enabled
#     if use_cache:
#         # Load cache from disk
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 logger.warning(f"Failed to load cache, starting with empty cache")

#         # Return from cache if exists
#         if prompt in cache:
#             logger.info(f"RESPONSE: {cache[prompt]}")
#             return cache[prompt]

#     # OpenRouter API configuration
#     api_key = os.getenv("OPENROUTER_API_KEY", "")
#     model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#     }

#     data = {
#         "model": model,
#         "messages": [{"role": "user", "content": prompt}]
#     }

#     response = requests.post(
#         "https://openrouter.ai/api/v1/chat/completions",
#         headers=headers,
#         json=data
#     )

#     if response.status_code != 200:
#         error_msg = f"OpenRouter API call failed with status {response.status_code}: {response.text}"
#         logger.error(error_msg)
#         raise Exception(error_msg)
#     try:
#         response_text = response.json()["choices"][0]["message"]["content"]
#     except Exception as e:
#         error_msg = f"Failed to parse OpenRouter response: {e}; Response: {response.text}"
#         logger.error(error_msg)        
#         raise Exception(error_msg)
    

#     # Log the response
#     logger.info(f"RESPONSE: {response_text}")

#     # Update cache if enabled
#     if use_cache:
#         # Load cache again to avoid overwrites
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 pass

#         # Add to cache and save
#         cache[prompt] = response_text
#         try:
#             with open(cache_file, "w", encoding="utf-8") as f:
#                 json.dump(cache, f)
#         except Exception as e:
#             logger.error(f"Failed to save cache: {e}")

#     return response_text

def list_gemini_models():
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY", ""),
    )
    # # Use the models property to access available models
    # print("Available models:")
    # for model in client.get_model("gemini-1.5-pro").list_models():
    #     if "gemini" in model.name:
    #         print(f"- {model.name}")
    
    # Alternative direct approach: try specific models
    test_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-pro-latest",
        "gemini-2.5-flash-latest",
        "gemini-2.5-flash-preview-04-17",
        "gemini-2.5-pro-exp-03-25"
    ]
    
    print("\nTesting specific models:")
    for model_name in test_models:
        try:
            model = client.get_model(model_name)
            print(f"✓ {model_name} - Available")
        except Exception as e:
            print(f"✗ {model_name} - Not available: {str(e)}")

if __name__ == "__main__":
    # list_gemini_models()
    
    test_prompt = "Hello, how are you?"

    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
