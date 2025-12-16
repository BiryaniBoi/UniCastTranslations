import deepl
from decouple import config

# --- Configuration ---
TRANSLATE_API_KEY = config('TRANSLATE_API_KEY', default="dummy_key")

# Initialize the translator object once for efficiency.
translator = None
try:
    translator = deepl.Translator(TRANSLATE_API_KEY)
except ValueError:
    # Handle case where the dummy key is invalid on startup
    pass # translator remains None

def translate_text(text: str, target_language: str) -> str:
    """
    Translates text using the DeepL API.

    If the API call fails (e.g., due to an invalid API key), it logs a
    warning and returns a mock translation for demo purposes.
    """
    if not translator:
        print("\n--- WARNING: DeepL Translator not initialized. Check API Key. ---")
        return _get_mock_translation(text, target_language)

    try:
        # DeepL specific language code adjustments
        target_lang_code_deepl = target_language.upper()
        if target_lang_code_deepl == "ZH": # DeepL uses ZH for Chinese simplified
            target_lang_code_deepl = "ZH"
        elif target_lang_code_deepl == "HI": # DeepL uses HI for Hindi
            target_lang_code_deepl = "HI"
        elif target_lang_code_deepl == "ES": # DeepL uses ES for Spanish
            target_lang_code_deepl = "ES"
        # For other languages, just use the upper-cased code.

        print(f"--- Calling DeepL API to translate to {target_lang_code_deepl}... ---")
        result = translator.translate_text(text, target_lang=target_lang_code_deepl)
        return result.text

    except deepl.AuthorizationException:
        print("\n--- WARNING: DeepL Authorization FAILED. Invalid API Key? ---")
        print("--- Falling back to MOCK translation for demo. ---\n")
        return _get_mock_translation(text, target_language)
        
    except Exception as e:
        print(f"\n--- WARNING: An error occurred with the DeepL API: {e} ---")
        print("--- Falling back to MOCK translation for demo. ---\n")
        return _get_mock_translation(text, target_language)

def _get_mock_translation(text: str, target_language: str) -> str:
    """
    Provides a placeholder translation for demo purposes.
    """
    if target_language.lower() == "es":
        return f"[MOCK SPANISH] {text}"
    elif target_language.lower() == "fr":
        return f"[MOCK FRENCH] {text}"
    elif target_language.lower() == "hi":
        return f"[MOCK HINDI] {text}"
    elif target_language.lower() == "zh":
        return f"[MOCK MANDARIN] {text}"
    
    return f"[{target_language.upper()} MOCK TRANSLATION] {text}"
