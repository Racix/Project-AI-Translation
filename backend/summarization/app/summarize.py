from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, load_index_from_storage, SummaryIndex
from transformers import BitsAndBytesConfig
from llama_index.prompts import PromptTemplate
from llama_index.llms import HuggingFaceLLM
from llama_index.response.notebook_utils import display_response
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import RouterQueryEngine
import torch

def load_data(file_path: str):
    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()
    return documents

def messages_to_prompt(messages):
  prompt = ""
  for message in messages:
    if message.role == 'system':
      prompt += f"<|system|>\n{message.content}</s>\n"
    elif message.role == 'user':
      prompt += f"<|user|>\n{message.content}</s>\n"
    elif message.role == 'assistant':
      prompt += f"<|assistant|>\n{message.content}</s>\n"

  # ensure we start with a system prompt, insert blank if needed
  if not prompt.startswith("<|system|>\n"):
    prompt = "<|system|>\n</s>\n" + prompt

  # add final assistant prompt
  prompt = prompt + "<|assistant|>\n"

  return prompt

def model():
    print("model1")
    quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)
    print("model2")
    llm = HuggingFaceLLM(
    model_name="HuggingFaceH4/zephyr-7b-beta",
    tokenizer_name="HuggingFaceH4/zephyr-7b-beta",
    query_wrapper_prompt=PromptTemplate("<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n"),
    context_window=3900,
    max_new_tokens=256,
    model_kwargs={"quantization_config": quantization_config},
    # tokenizer_kwargs={},
    generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    messages_to_prompt=messages_to_prompt,
    device_map="auto",
)
    print("model3")
    return llm
    
def create_index(llm, documents):
    print("create_summarize4\n")
    service_context = ServiceContext.from_defaults(llm=llm, embed_model="local:BAAI/bge-base-en-v1.5", chunk_size = 1024)
    print("create_summarize5\n")
    vector_index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    print("create_summarize6\n")
    return vector_index
    
def summarize(vector_index):
    query_engine = vector_index.as_query_engine(response_mode="tree_summarize")
    response = query_engine.query("Can you summarize the text for me?")
    return response

def create_summarize(file_path: str):
    print("create_summarize1\n")
    documents = load_data(file_path)
    print("create_summarize2\n")
    llm = model()
    print("create_summarize3\n")
    vector_index = create_index(llm, documents)
    print("create_summarize7\n")
    return summarize(vector_index)