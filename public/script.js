const BACKEND_URL = "https://unicasttranslations.onrender.com"; // Our FastAPI backend URL

let deviceId = localStorage.getItem('deviceId');
let selectedLanguage = localStorage.getItem('selectedLanguage') || 'en';

const languageSelect = document.getElementById('language-select');
const alertsContainer = document.getElementById('alerts-container');

// --- Initialization ---
async function initializeApp() {
    if (!deviceId) {
        deviceId = 'web-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('deviceId', deviceId);
        console.log('Generated new deviceId:', deviceId);
    } else {
        console.log('Using existing deviceId:', deviceId);
    }
    
    languageSelect.value = selectedLanguage;
    languageSelect.addEventListener('change', handleLanguageChange);

    // Register device initially (or update its language/location)
    await registerDevice(selectedLanguage);
    
    // Start polling for alerts
    setInterval(fetchAndDisplayAlerts, 5000); // Poll every 5 seconds
    fetchAndDisplayAlerts(); // Fetch immediately on startup
}

// --- API Calls ---

async function registerDevice(lang) {
    try {
        const response = await fetch(`${BACKEND_URL}/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                device_token: deviceId,
                language: lang,
                latitude: 0.0, // Dummy data for now
                longitude: 0.0  // Dummy data for now
            })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log('Device registered/updated successfully:', await response.json());
    } catch (error) {
        console.error('Error registering device:', error);
    }
}

async function fetchAndDisplayAlerts() {
    try {
        // Now calling the correct endpoint for device-specific alerts
        const response = await fetch(`${BACKEND_URL}/alerts/me/${deviceId}`); 
        if (!response.ok) {
            // If device not found, try re-registering and then fetch again
            if (response.status === 404) {
                console.warn(`Device ${deviceId} not found on backend. Re-registering.`);
                await registerDevice(selectedLanguage);
                return; // Skip displaying this round, will fetch again next interval
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const alerts = await response.json(); // This will be a list of AlertDisplay objects
        
        displayAlerts(alerts);

    } catch (error) {
        console.error('Error fetching alerts:', error);
        alertsContainer.innerHTML = '<p class="no-alerts">Error loading alerts.</p>';
    }
}


// --- UI Handlers ---

function handleLanguageChange(event) {
    selectedLanguage = event.target.value;
    localStorage.setItem('selectedLanguage', selectedLanguage);
    registerDevice(selectedLanguage); // Update backend with new language
    fetchAndDisplayAlerts(); // Re-fetch alerts immediately after language change
}

function displayAlerts(alerts) {
    alertsContainer.innerHTML = ''; // Clear previous alerts
    if (alerts.length === 0) {
        alertsContainer.innerHTML = '<p class="no-alerts">No alerts received yet.</p>';
        return;
    }

    alerts.forEach(alert => {
        const alertCard = document.createElement('div');
        alertCard.className = `alert-card severity-${alert.severity}`; // Apply severity styling
        alertCard.innerHTML = `
            <h2>${alert.severity} Alert:</h2>
            <p>${alert.translated_message}</p> <!-- Display translated message -->
            <small>Original: "${alert.message}"</small><br>
            <small>ID: ${alert.alert_id}</small><br>
            <small>Time: ${new Date(alert.timestamp).toLocaleString()}</small>
        `;
        alertsContainer.appendChild(alertCard);
    });
}


// --- Start the app ---
initializeApp();