import deepl
from decouple import config

# --- Configuration ---
TRANSLATE_API_KEY = config('TRANSLATE_API_KEY', default="dummy_key")

# Initialize the translator object once for efficiency.
try:
    translator = deepl.Translator(TRANSLATE_API_KEY)
except ValueError:
    # Handle case where the dummy key is invalid on startup
    translator = None

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
        # Format language code for the DeepL API (e.g., 'es' -> 'ES')
        target_lang_code = target_language.upper()
        
        print(f"--- Calling DeepL API to translate to {target_lang_code}... ---")
        result = translator.translate_text(text, target_lang=target_lang_code)
        return result.text

    except deepl.AuthorizationException:
        print("\n--- WARNING: DeepL Authorization FAILED. Invalid API Key? ---")
        print("--- Falling back to MOCK translation for demo. ---\
")
        return _get_mock_translation(text, target_language)
        
    except Exception as e:
        print(f"\n--- WARNING: An error occurred with the DeepL API: {e} ---")
        print("--- Falling back to MOCK translation for demo. ---\
")
        return _get_mock_translation(text, target_language)

def _get_mock_translation(text: str, target_language: str) -> str:
    """
    Provides a placeholder translation for demo purposes.
    """
    return f"[{target_language.upper()} MOCK TRANSLATION] {text}"