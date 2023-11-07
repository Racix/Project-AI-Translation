from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import json
import os

translate_model1 = "facebook/nllb-200-distilled-600M"
# translate_model2 = "facebook/nllb-200–1.3B"
# translate_model3 = "facebook/nllb-200–3.3B"
# translate_model4 = "facebook/nllb-200-distilled-1.3B"


def translate_to_lang(data: dict, from_language: str, to_language: str) -> dict:

    model = AutoModelForSeq2SeqLM.from_pretrained(translate_model1)
    tokenizer = AutoTokenizer.from_pretrained(translate_model1)
    #target_lang = "swe_Latn"
    translator = pipeline(
        "translation", model=model, tokenizer=tokenizer, src_lang=from_language, tgt_lang=to_language, max_length = 400
        )
    
    translated_data = []
    for sentence in data['diarization']['segments']:
        output = translator(sentence['text'])
        translated_text = output[0]["translation_text"]
        sentence['text'] = translated_text
        translated_data.append(sentence)
    print(translated_data)
    return translated_data

