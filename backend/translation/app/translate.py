import json
import argostranslate.package
import argostranslate.translate



language_codes = {"en", "sv", "fr", "es", "de", "ar", "zh", "zt", "nl", "fi", "hi", "pl", "ru"}

def install_language(from_language: str, to_language: str):
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_language and x.to_code == to_language, available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())

def translate_json(data: dict, from_language: str, to_language: str):
    text_to_translate = []  
    for sentence in data['diarization']['segments']:
        text_to_translate.append(sentence['text'])
    combined_text = " ".join(text_to_translate)
    translated_text = argostranslate.translate.translate(combined_text, from_language, to_language)
    return translated_text

def translate_to_lang(data: dict, from_language: str, to_language: str) -> dict:
    if from_language not in language_codes:
        translation =  "Not a viable language"
        return translation
    elif from_language != "en" and to_language != "en":
        install_language(from_language, "en")
        whole_text_translated = translate_json(data, from_language, "en")
        install_language("en", to_language)
        translated_text = argostranslate.translate.translate(whole_text_translated, "en", to_language)
        translation = translated_text
    else:
        install_language(from_language, to_language)
        translation = translate_json(data, from_language, to_language)
    return translation