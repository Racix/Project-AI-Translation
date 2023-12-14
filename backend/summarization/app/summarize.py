from llama_index import ListIndex, SimpleDirectoryReader, ServiceContext, set_global_tokenizer
from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import (
    completion_to_prompt,
)
import json, tempfile, os
from transformers import AutoTokenizer

set_global_tokenizer(
    AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1").encode
)
import torch
import gc
import llama_cpp

def load_data(file_path: str):
    with open(file_path, 'r') as file:
        json_data = file.read()
    
    json_data = json.loads(json_data)
    segments = json_data['segments']
    text_data = ' '.join([segment['text'] for segment in segments])
 
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        # Write data to the temporary file
        temp_file.write(text_data)
        temp_file_path = temp_file.name  # Store the path of the temporary file

    # Load data using SimpleDirectoryReader
    reader = SimpleDirectoryReader(input_files=[temp_file_path])
    documents = reader.load_data()
    os.remove(temp_file_path)
    return documents

def messages_to_prompt(messages):
  prompt = ""
  for message in messages:
    if message.role == 'system':
      prompt += f"<|im_start|>system\n{message.content}<im_end>\n"
    elif message.role == 'user':
      prompt += f"<|im_start|>user\n{message.content}<im_end>\n"
    elif message.role == 'assistant':
      prompt += f"<|im_start|>assistant\n{message.content}<im_end>\n"

  # ensure we start with a system prompt, insert blank if needed
  if not prompt.startswith("<|im_start|>system\n"):
    prompt = "<|im_start|>\n<im_end>\n" + prompt

  # add final assistant prompt
  prompt = prompt + "<|im_start|>assistant\n"

  return prompt
  

def create_summarize(file_path: str):
    try:
        documents = load_data(file_path)
        llm = LlamaCPP(
        # optionally, you can set the path to a pre-downloaded model instead of model_url
        model_path="models/mistral7b",
        temperature=0.1,
        max_new_tokens=256,
        # llama2 has a context window of 4096 tokens, but we set it lower to allow for some wiggle room
        context_window=3900,
        # kwargs to pass to __call__()
        generate_kwargs={},
        # kwargs to pass to __init__()
        # set to at least 1 to use GPU
        model_kwargs={"n_gpu_layers": -1}, #MAX 35 layers can be offloaded to GPU if using mistral 7b
        # transform inputs into Llama2 format
        messages_to_prompt=messages_to_prompt,
        completion_to_prompt=completion_to_prompt,
        verbose=True,
    )
        service_context = ServiceContext.from_defaults(llm=llm, embed_model="local:BAAI/bge-base-en-v1.5", context_window = 3700)
        list_index = ListIndex.from_documents(documents, service_context=service_context)

        query_engine = list_index.as_query_engine(response_mode="tree_summarize")
        response = query_engine.query("Summarize in detail.")
        return response
    except Exception as e:
       print(e)
    finally:
        llama_cpp.llama_free_model(llm)
        del llm
        del service_context
        del list_index
        del query_engine
        del response
        torch.cuda.empty_cache()  
        gc.collect()
        # cache still won't clear for some reason ^^