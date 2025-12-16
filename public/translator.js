// This script will run on static pages like "About Us" and "Know Your Rights"

// Backend URL needs to be consistent with the main script.js
// If you change it in one place, change it here too.
const BACKEND_URL = "https://unicasttranslations.onrender.com";

document.addEventListener('DOMContentLoaded', () => {
    const selectedLanguage = localStorage.getItem('selectedLanguage') || 'en';

    // Only run the translation logic if the selected language is not English
    if (selectedLanguage !== 'en') {
        translatePageContent(selectedLanguage);
    }
});

async function translatePageContent(lang) {
    // 1. Find all elements that have the 'data-translate' attribute
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    
    if (elementsToTranslate.length === 0) {
        return; // No work to do
    }

    // 2. Collect all the text content from these elements
    const originalTexts = Array.from(elementsToTranslate).map(el => el.textContent);

    try {
        // 3. Send the texts to our new backend endpoint
        const response = await fetch(`${BACKEND_URL}/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                texts: originalTexts,
                target_lang: lang,
            }),
        });

        if (!response.ok) {
            throw new Error(`Translation API failed with status: ${response.status}`);
        }

        const data = await response.json();
        const translatedTexts = data.translations;

        // 4. Replace the content of each element with its translation
        elementsToTranslate.forEach((el, index) => {
            if (translatedTexts[index]) {
                el.textContent = translatedTexts[index];
            }
        });

    } catch (error) {
        console.error('Failed to translate page content:', error);
        // If translation fails, the page will just remain in English.
    }
}
