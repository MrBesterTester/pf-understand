from google import genai
import os
import logging
import json
from datetime import datetime
import time
import random
import threading
import signal

"""
call_llm.py - Google Gemini LLM API Interface
=============================================

A robust utility for interacting with Google's Gemini LLM API, featuring built-in 
error handling, rate limiting management, response caching, and large prompt chunking.

Features:
---------
- Automatic response caching to avoid redundant API calls
- Smart handling of large prompts by chunking with context-aware splitting
- Comprehensive error handling with exponential backoff for retries
- Detailed logging of all API interactions
- Rate limit detection and management with dynamic wait times
- Progress indicators for long-running operations
- Connection reset handling with cooldown periods

Dependencies:
------------
- google.genai: Google Generative AI client library
- Environment variable: GEMINI_API_KEY must be set

Configuration:
-------------
- LOG_DIR: Environment variable to specify logging directory (default: "logs")
- Cache file: "llm_cache.json" in the current directory

API Reference:
-------------

call_llm(prompt: str, use_cache: bool = True) -> str
    Send a prompt to the Google Gemini LLM and retrieve the response.
    
    Args:
        prompt (str): The text prompt to send to the LLM
        use_cache (bool, optional): Whether to use caching. Defaults to True.

    Returns:
        str: The LLM's text response
    
    Raises:
        Exception: If all retry attempts fail
    
    Example:
        >>> response = call_llm("Explain quantum computing")
        >>> print(response)

process_chunks_with_timeout(chunks: list, use_cache: bool) -> list
    Process multiple text chunks with timeout protection.
    
    Args:
        chunks (list): List of text chunks to process
        use_cache (bool): Whether to use caching
    
    Returns:
        list: List of responses for each chunk

chunk_text(text: str, max_size: int) -> list
    Split text into chunks of approximately max_size characters.
    
    Args:
        text (str): The text to split
        max_size (int): Maximum size of each chunk in characters
    
    Returns:
        list: List of text chunks
"""

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

def print_with_timestamp(message):
    """Print a message with a timestamp prefix."""
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # Format as HH:MM:SS.ms
    print(f"[{timestamp}] {message}")

# By default, we Google Gemini 2.5 pro, as it shows great performance for code understanding
def call_llm(prompt: str, use_cache: bool = True) -> str:
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")
    print_with_timestamp(f"[LLM] Processing prompt ({len(prompt)} chars)...")
    
    # Define maximum chunk size (in characters)
    MAX_CHUNK_SIZE = 200000  # ~50K tokens - ensures critical context stays together
    
    # Check if we need to chunk
    if len(prompt) > MAX_CHUNK_SIZE:
        print_with_timestamp(f"[LLM] ⚠ Prompt exceeds {MAX_CHUNK_SIZE//1000}K character limit ({len(prompt)//1000}K chars)")
        print_with_timestamp(f"[LLM] 🧩 Automatically splitting into chunks for processing")
        
        # Split the prompt into chunks (try to break at paragraph boundaries)
        chunks = chunk_text(prompt, MAX_CHUNK_SIZE)
        print_with_timestamp(f"[LLM] 📑 Split into {len(chunks)} chunks")
        
        # Process each chunk
        results = process_chunks_with_timeout(chunks, use_cache)
        
        # Combine results
        combined_result = "\n\n".join(results)
        print_with_timestamp(f"[LLM] ✅ Successfully processed all chunks ({len(combined_result)} chars total)")
        return combined_result
    
    # Track statistics
    start_time = time.time()
    attempts = 0
    cache_hits = 0
    
    # Check cache if enabled
    if use_cache:
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except:
                logger.warning(f"Failed to load cache, starting with empty cache")

        # Return from cache if exists
        if prompt in cache:
            cache_hits += 1
            response_text = cache[prompt]
            logger.info(f"RESPONSE: {response_text}")
            print_with_timestamp(f"[LLM] ✓ Retrieved from cache ({len(response_text)} chars)")
            return response_text

    # Retry configuration
    max_retries = 20
    retry_count = 0
    base_wait_time = 15  # Base wait in seconds
    max_wait_time = 60   # Cap at 1 minute max
    connection_errors = 0
    max_connection_errors = 10
    
    while retry_count < max_retries:
        try:
            attempts += 1
            start_attempt_time = time.time()
            print_with_timestamp(f"[LLM] Attempt {attempts}/{max_retries+1} - Calling API (prompt: {len(prompt)} chars)...")
            
            from google import genai
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            
            # Log before API call
            print_with_timestamp(f"[LLM] 🔄 Sending request to Google API...")
            
            response = client.models.generate_content(
                model="models/gemini-2.5-pro-preview-03-25", 
                contents=[prompt]
            )
            
            # Log after API call
            api_time = time.time() - start_attempt_time
            print_with_timestamp(f"[LLM] ✓ Google API responded in {api_time:.2f}s")
            
            response_text = response.text
            
            # Cache the successful response
            if use_cache:
                cache = {}
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, "r", encoding="utf-8") as f:
                            cache = json.load(f)
                    except:
                        pass
                cache[prompt] = response_text
                try:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(cache, f)
                    print_with_timestamp(f"[LLM] ✓ Response cached for future use")
                except Exception as e:
                    logger.error(f"Failed to save cache: {e}")
                    
            elapsed = time.time() - start_time
            logger.info(f"RESPONSE: {response_text}")
            print_with_timestamp(f"[LLM] ✓ Success! ({len(response_text)} chars in {elapsed:.2f}s)")
            print_with_timestamp(f"[LLM] Preview: {response_text[:100]}..." if len(response_text) > 100 else response_text)
            return response_text
            
        except Exception as e:
            error_msg = str(e)
            retry_count += 1
            
            if "Connection reset" in error_msg or "ConnectError" in error_msg:
                connection_errors += 1
                wait_time = 45 + random.uniform(0, 15)
                print_with_timestamp(f"[LLM] ⚠ Connection reset detected. Retry {retry_count}/{max_retries}. Waiting {wait_time:.2f}s...")
                
                if connection_errors >= max_connection_errors:
                    extra_wait = 180  # 3 minute cooldown
                    print_with_timestamp(f"[LLM] ⚠ Too many connection errors. Taking a {extra_wait/60} minute break...")
                    time.sleep(extra_wait)
                    connection_errors = 0
            
            elif "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                # Default calculation (used as fallback)
                jitter = random.uniform(0.8, 1.2)
                default_wait = min(base_wait_time + (retry_count * 5), max_wait_time) * jitter
                
                # Try to extract Google's suggested wait time
                google_wait = None
                if "retryDelay" in error_msg:
                    try:
                        retry_delay_str = error_msg.split("'retryDelay': '")[1].split("s'")[0]
                        google_wait = float(retry_delay_str)
                        # Add slight jitter to Google's time to prevent synchronized requests
                        google_wait = google_wait * random.uniform(1.0, 1.2)
                        print_with_timestamp(f"[LLM] ℹ Google suggests waiting {retry_delay_str}s")
                    except:
                        pass
                
                # Extract and display which specific rate limit was hit
                limit_type = "Unknown rate limit"
                if "quotaId" in error_msg:
                    try:
                        # Extract quota ID details
                        quota_id = error_msg.split("'quotaId': '")[1].split("'")[0]
                        
                        # Categorize the rate limit
                        if "PerMinute" in quota_id:
                            time_span = "per-minute"
                        elif "PerDay" in quota_id:
                            time_span = "per-day (daily quota)"
                        else:
                            time_span = "unknown time period"
                            
                        if "InputTokens" in quota_id:
                            resource = "input tokens"
                        elif "OutputTokens" in quota_id:
                            resource = "output tokens"
                        elif "Requests" in quota_id:
                            resource = "requests"
                        else:
                            resource = "unknown resource"
                            
                        if "FreeTier" in quota_id:
                            tier = "free tier"
                        elif "PaidTier" in quota_id:
                            tier = "paid tier"
                        else:
                            tier = "unknown tier"
                            
                        limit_type = f"{resource} ({time_span}, {tier})"
                        print_with_timestamp(f"[LLM] 🛑 Rate limit exceeded: {limit_type}")
                        print_with_timestamp(f"[LLM] 🔍 Quota ID: {quota_id}")
                        
                        # Extract specific limit value if available
                        if "quotaValue" in error_msg:
                            try:
                                quota_value = error_msg.split("'quotaValue': '")[1].split("'")[0]
                                print_with_timestamp(f"[LLM] 📊 Limit value: {quota_value}")
                            except:
                                pass
                    except:
                        print_with_timestamp(f"[LLM] ⚠ Failed to parse specific rate limit details")
                
                # Use Google's time if available, otherwise use our default
                wait_time = google_wait if google_wait is not None else default_wait
                
                print_with_timestamp(f"[LLM] ⚠ Rate limit hit. Retry {retry_count}/{max_retries}. Waiting {wait_time:.2f}s...")
            
            else:
                wait_time = base_wait_time + random.uniform(0, 10)
                print_with_timestamp(f"[LLM] ⚠ Error: {error_msg[:100]}... Retry {retry_count}/{max_retries}. Waiting {wait_time:.2f}s...")
            
            time.sleep(wait_time)
    
    total_time = time.time() - start_time
    print_with_timestamp(f"[LLM] ✗ Failed after {retry_count} retries ({total_time:.2f}s elapsed)")
    raise Exception(f"Failed after {max_retries} retries")

def chunk_text(text: str, max_size: int) -> list:
    """Split text into chunks of approximately max_size characters, breaking at paragraph boundaries."""
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first
    paragraphs = text.split("\n\n")
    
    for paragraph in paragraphs:
        # If adding this paragraph exceeds the limit, store the chunk and start a new one
        if len(current_chunk) + len(paragraph) + 2 > max_size:
            # If the current chunk is already close to max size
            if len(current_chunk) > max_size * 0.5:  # Only store if chunk is substantial
                chunks.append(current_chunk)
                current_chunk = paragraph
            else:
                # If the paragraph itself is too big, split it by sentences
                if len(paragraph) > max_size:
                    sentences = split_into_sentences(paragraph)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 > max_size:
                            chunks.append(current_chunk)
                            current_chunk = sentence
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
                else:
                    # This shouldn't normally happen (small current chunk + small paragraph > max)
                    # but handle it just in case
                    chunks.append(current_chunk)
                    current_chunk = paragraph
        else:
            # Add paragraph separator if not the first paragraph in chunk
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def split_into_sentences(text: str) -> list:
    """Split text into sentences, trying to preserve sentence boundaries."""
    # Simple splitting by common sentence terminators
    # In a real implementation, you might want a more sophisticated NLP approach
    for delimiter in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
        text = text.replace(delimiter, delimiter + "[SPLIT]")
    
    sentences = text.split("[SPLIT]")
    return [s.strip() for s in sentences if s.strip()]

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
    
    print_with_timestamp("\nTesting specific models:")
    for model_name in test_models:
        try:
            model = client.get_model(model_name)
            print_with_timestamp(f"✓ {model_name} - Available")
        except Exception as e:
            print_with_timestamp(f"✗ {model_name} - Not available: {str(e)}")

def process_chunks_with_timeout(chunks, use_cache):
    MAX_CHUNK_WAIT = 180  # 3 minutes maximum per chunk
    MAX_CHUNK_RETRIES = 3  # Try each chunk up to 3 times before giving up
    
    results = []
    for i, chunk in enumerate(chunks):
        print_with_timestamp(f"\n[LLM] 🔄 Processing chunk {i+1}/{len(chunks)} ({len(chunk)//1000}K chars)")
        
        chunk_result = None
        used_cache = False
        chunk_successful = False
        
        # Try the cache first
        if use_cache and os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                if chunk in cache:
                    chunk_result = cache[chunk]
                    used_cache = True
                    chunk_successful = True
                    print_with_timestamp(f"[LLM] ✓ Retrieved chunk {i+1} from cache ({len(chunk_result)} chars)")
            except Exception as e:
                print_with_timestamp(f"[LLM] ⚠️ Cache error: {str(e)}")
        
        # If not in cache, try with retries
        retry_count = 0
        while not chunk_successful and retry_count < MAX_CHUNK_RETRIES:
            print_with_timestamp(f"[LLM] Chunk {i+1} - Attempt {retry_count+1}/{MAX_CHUNK_RETRIES}")
            print_with_timestamp(f"[LLM] Starting API call with {MAX_CHUNK_WAIT}s timeout")
            start_time = time.time()
            
            # Set up timeout handler
            def timeout_handler(signum, frame):
                raise TimeoutError(f"API call timed out after {MAX_CHUNK_WAIT} seconds")
            
            # Set the timeout handler
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(MAX_CHUNK_WAIT)  # Set alarm for MAX_CHUNK_WAIT seconds
            
            try:
                # Make the API call directly
                client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                response = client.models.generate_content(
                    model="models/gemini-2.5-pro-preview-03-25", 
                    contents=[chunk]
                )
                chunk_result = response.text
                chunk_successful = True
                
                # Save to cache if successful
                if use_cache:
                    try:
                        cache = {}
                        if os.path.exists(cache_file):
                            with open(cache_file, "r", encoding="utf-8") as f:
                                cache = json.load(f)
                        cache[chunk] = chunk_result
                        with open(cache_file, "w", encoding="utf-8") as f:
                            json.dump(cache, f)
                    except Exception as e:
                        print_with_timestamp(f"[LLM] ⚠️ Failed to save to cache: {str(e)}")
                
            except (TimeoutError, Exception) as e:
                retry_count += 1
                print_with_timestamp(f"[LLM] ⚠️ Chunk {i+1} - Attempt {retry_count}/{MAX_CHUNK_RETRIES} failed: {str(e)}")
                
                # Only wait between retries, not after the final attempt
                if retry_count < MAX_CHUNK_RETRIES:
                    # Exponential backoff for retries
                    wait_time = 30 * (2 ** (retry_count - 1))  # 30s, 60s, 120s...
                    print_with_timestamp(f"[LLM] Waiting {wait_time}s before next attempt...")
                    time.sleep(wait_time)
                
            finally:
                # Cancel the alarm
                signal.alarm(0)
                elapsed = time.time() - start_time
                print_with_timestamp(f"[LLM] API call attempt completed in {elapsed:.1f}s")
        
        # If all retries failed, add a placeholder
        if not chunk_successful:
            chunk_result = f"[Failed to process chunk {i+1} after {MAX_CHUNK_RETRIES} attempts]"
        
        # Add result and continue
        results.append(chunk_result)
        
        # Pause between chunks
        if i < len(chunks) - 1 and not used_cache:
            wait_time = 30 + random.uniform(0, 15)
            print_with_timestamp(f"[LLM] ⏱️ Pausing for {wait_time:.2f}s before next chunk")
            time.sleep(wait_time)
            
    return results

# Helper functions for progress indicator and cache management
def check_progress_repeatedly(stop_flag, chunk_num):
    count = 0
    while not stop_flag.is_set():
        count += 1
        print_with_timestamp(f"[LLM] ⏳ Still working on chunk {chunk_num+1}... ({count} minute(s) elapsed)")
        stop_flag.wait(60)

def check_cache(prompt):
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
            return prompt in cache
        except:
            pass
    return False

def get_from_cache(prompt):
    with open(cache_file, "r", encoding="utf-8") as f:
        cache = json.load(f)
    return cache[prompt]

def save_to_cache(prompt, response):
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except:
            pass
    cache[prompt] = response
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        print_with_timestamp(f"[LLM] ⚠️ Failed to save to cache: {str(e)}")

if __name__ == "__main__":
    # list_gemini_models()
    
    test_prompt = "Hello, how are you?"

    # First call - should hit the API
    print_with_timestamp("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print_with_timestamp(f"Response: {response1}")

    # In your application code where you parse relationships
    def validate_relationships(relationships, max_index=6):
        valid_relationships = []
        for rel in relationships:
            if 1 <= rel['from_abstraction'] <= max_index and 1 <= rel['to_abstraction'] <= max_index:
                valid_relationships.append(rel)
            else:
                print_with_timestamp(f"[WARNING] Filtered out invalid relationship: {rel}")
        return valid_relationships
