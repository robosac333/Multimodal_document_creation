import torch

# Importing necessary libraries and modules from Hugging Face's `peft` and `transformers` for model handling, tokenization, and fine-tuning.
from peft import LoraConfig, AutoPeftModelForCausalLM, prepare_model_for_kbit_training, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig, TrainingArguments
from transformers import AutoTokenizer, GenerationConfig
import os
import time
from langchain_community.vectorstores import FAISS  # For working with vector stores
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings  # For generating embeddings using Hugging Face models
from langchain.schema import Document  # For handling document schema

# -----------------------------------------------------------------------------------------------------
# Load the pre-trained Mistral 7B model with quantization configuration
# -----------------------------------------------------------------------------------------------------
# Load the tokenizer from a pre-trained GPTQ model and set the padding token to be the end-of-sequence token.
tokenizer = AutoTokenizer.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GPTQ")
tokenizer.pad_token = tokenizer.eos_token

# Load a quantization configuration for GPTQ, which reduces model precision to 4-bits for efficient inference.
quantization_config_loading = GPTQConfig(bits=4, disable_exllama=True, tokenizer=tokenizer)

# Load the pre-trained model with the quantization configuration, automatically assigning the model to the available devices.
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Mistral-7B-Instruct-v0.1-GPTQ",
    quantization_config=quantization_config_loading,
    device_map="auto"
)

# Disable caching of attention layers to save memory and enable gradient checkpointing to reduce memory usage during training.
model.config.use_cache = False
model.config.pretraining_tp = 1
model.gradient_checkpointing_enable()

# Prepare the model for 8-bit (k-bit) training using LoRA (Low-Rank Adaptation) for efficient fine-tuning.
model = prepare_model_for_kbit_training(model)

# Set up a LoRA configuration, targeting specific layers of the model (`q_proj`, `v_proj`) for fine-tuning.
peft_config = LoraConfig(
    r=16, lora_alpha=16, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM", target_modules=["q_proj", "v_proj"]
)
model = get_peft_model(model, peft_config)

# Configure generation settings for the model, including sampling strategies (e.g., `do_sample`, `top_k`, `temperature`) and maximum token length.
generation_config = GenerationConfig(
    do_sample=True,
    top_k=1,
    temperature=0.1,
    max_new_tokens=100,
    pad_token_id=tokenizer.eos_token_id
)

# Define a system prompt to instruct the model's behavior during interaction, focusing on providing helpful and accurate responses.
system_prompt = """
You are a helpful and informative assistant. Your goal is to answer questions accurately, thoroughly, and naturally. Provide detailed explanations and context when possible. If you do not understand or do not have enough information to answer, simply say - "Sorry, I don't know." Avoid formatting your response as a multiple-choice answer.
"""

# Initialize embeddings using a pre-trained sentence transformer model (`gtr-t5-large`) for query processing and document retrieval.
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/gtr-t5-large', 
                                   model_kwargs={'device': 'cuda'})

# ---------------------------------------------------------------------------------------------------------------

def retrieve_faiss(Db_faiss_path):
    # Load a FAISS vector database for efficient similarity search, using embeddings generated by the sentence transformer model.
    db = FAISS.load_local(Db_faiss_path, embeddings, allow_dangerous_deserialization=True)
    return db



# Function to retrieve the most relevant documents from the FAISS database given a query, returning the top `k` results.
def retrieve_context(query, db, k=10):
    query_embedding = embeddings.embed_query(query)
    docs = db.similarity_search_by_vector(query_embedding, k)
    ranked_docs = rank_documents(query, docs)
    return ranked_docs[:5]

# Function to rank documents based on their relevance to the query; currently a placeholder that returns the docs unmodified.
def rank_documents(query, docs):
    return docs 

# Function to generate a response from the model based on the query and retrieved context.
def generate_answer(query, context, image_context=None):
    # Combine the context documents into a single text block to include in the prompt.
    context_text = "\n\n".join([doc.page_content for doc in context])
    
    if image_context:
        context_text = image_context + "\n\n" + context_text

    # Create a structured input for the model with a clear prompt, context, and user query.
    input_text = (
        system_prompt +
        "\nContext: " + context_text + 
        "\n\nUser: " + query + 
        "\nBot:"
    )
    
    # Tokenize the input text and move it to the GPU for processing.
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
    
    # Generate a response using the configured generation settings.
    outputs = model.generate(**inputs, generation_config=generation_config)
    
    # Decode the generated tokens into a text response, removing special tokens and extraneous information.
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Return the clean answer, stripping out unnecessary prefixes or suffixes.
    return answer.strip().split("\nBot:")[-1].strip()
