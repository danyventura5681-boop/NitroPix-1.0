import json
import os

def load_translations():
    translations = {}
    locales_dir = os.path.join(os.path.dirname(__file__), '..', 'locales')
    for lang in ['en', 'es']:
        with open(os.path.join(locales_dir, f'{lang}.json'), 'r', encoding='utf-8') as f:
            translations[lang] = json.load(f)
    return translations

_translations = load_translations()

def get_text(key, lang='en', **kwargs):
    text = _translations.get(lang, {}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text