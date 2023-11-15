from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_name = "facebook/nllb-200-distilled-600M"

def cache_model():
    # Download and cache model and tokenizer
    AutoModelForSeq2SeqLM.from_pretrained(model_name)
    AutoTokenizer.from_pretrained(model_name)

if __name__ == '__main__':
    cache_model()
