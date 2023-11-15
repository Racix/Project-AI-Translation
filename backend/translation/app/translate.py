from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import time

translate_model1 = "facebook/nllb-200-distilled-600M"
# translate_model2 = "facebook/nllb-200–1.3B"
# translate_model3 = "facebook/nllb-200–3.3B"
# translate_model4 = "facebook/nllb-200-distilled-1.3B"

language_mapped = {
    "sv": "swe_Latn",
    "en": "en_Latn",
    "ru": "rus_Cyrl",
    "ja": "jpn_Jpan",
    "fa": "pes_Arab",
    "zh": "zho_Hans",
    "es": "spa_Latn",
    "fr": "fra_Latn",
}


def translate_to_lang(data: dict, from_language: str, to_language: str) -> list:
    print(f"Translation started...")
    start_time = time.time() # TODO only for time print, remove later
    
    model = AutoModelForSeq2SeqLM.from_pretrained(translate_model1)
    tokenizer = AutoTokenizer.from_pretrained(translate_model1)
    translator = pipeline(
        "translation",
        model=model,
        tokenizer=tokenizer,
        src_lang=language_mapped.get(from_language),  
        tgt_lang=language_mapped.get(to_language),    
        max_length=400                                 
)
    
    translated_data = []
    for sentence in data['diarization']['segments']:
        output = translator(sentence['text'])
        translated_text = output[0]["translation_text"]
        sentence['text'] = translated_text
        translated_data.append(sentence)

    # TODO only for time print, remove later
    end_time = time.time() 
    total_time = end_time - start_time
    print(f"Translation finished. Total time: {str(total_time)}")
    return translated_data
