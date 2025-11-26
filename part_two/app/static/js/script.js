var socket = io();
var running = true;
var currentLang = 'en';

const translations = {
    'en': {
        'analyze': '🔍 Analyze',
        'analyzing': '⏳ Analyzing...', 
        'stop': '⏹ Stop',
        'resume': '▶️ Resume',
        'settings': '⚙️ Settings',
        'settingsTitle': 'Settings',
        'apiKeyLabel': 'API Key:',
        'modelLabel': 'Model:',
        'promptLabel': 'Prompt:',
        'languageLabel': 'Language:',
        'panelHeader': 'Assistant Response',
        'save': 'Save',
        'cancel': 'Cancel',
        'appStopped': 'The application has been stopped.',
        'appResumed': 'The application has resumed.',
        'settingsSaved': 'Settings saved successfully!',
        'errorSaving': 'Error saving settings.',
        'analysisSuccess': 'Analysis success:',
        'analysisFailed': 'Analysis failed:',
        'errorAnalyzing': 'Error analyzing:',
        'thinking': 'Thinking...', 
        'error': 'Error: '
    },
    'pt': {
        'analyze': '🔍 Analisar',
        'analyzing': '⏳ Analisando...', 
        'stop': '⏹ Parar',
        'resume': '▶️ Retomar',
        'settings': '⚙️ Configurações',
        'settingsTitle': 'Configurações',
        'apiKeyLabel': 'Chave da API:',
        'modelLabel': 'Modelo:',
        'promptLabel': 'Prompt:',
        'languageLabel': 'Idioma:',
        'panelHeader': 'Resposta do Assistente',
        'save': 'Salvar',
        'cancel': 'Cancelar',
        'appStopped': 'A aplicação foi parada.',
        'appResumed': 'A aplicação foi retomada.',
        'settingsSaved': 'Configurações salvas com sucesso!',
        'errorSaving': 'Erro ao salvar configurações.',
        'analysisSuccess': 'Análise bem-sucedida:',
        'analysisFailed': 'Falha na análise:',
        'errorAnalyzing': 'Erro ao analisar:',
        'thinking': 'Pensando...', 
        'error': 'Erro: '
    },
    'es': {
        'analyze': '🔍 Analizar',
        'analyzing': '⏳ Analizando...', 
        'stop': '⏹ Detener',
        'resume': '▶️ Reanudar',
        'settings': '⚙️ Configuración',
        'settingsTitle': 'Configuración',
        'apiKeyLabel': 'Clave API:',
        'modelLabel': 'Modelo:',
        'promptLabel': 'Prompt:',
        'languageLabel': 'Idioma:',
        'panelHeader': 'Respuesta del Asistente',
        'save': 'Guardar',
        'cancel': 'Cancelar',
        'appStopped': 'La aplicación se ha detenido.',
        'appResumed': 'La aplicación se ha reanudado.',
        'settingsSaved': '¡Configuración guardada con éxito!',
        'errorSaving': 'Error al guardar la configuración.',
        'analysisSuccess': 'Análisis exitoso:',
        'analysisFailed': 'Análisis fallido:',
        'errorAnalyzing': 'Error al analizar:',
        'thinking': 'Pensando...', 
        'error': 'Error: '
    },
    'fr': {
        'analyze': '🔍 Analyser',
        'analyzing': '⏳ Analyse...', 
        'stop': '⏹ Arrêter',
        'resume': '▶️ Reprendre',
        'settings': '⚙️ Paramètres',
        'settingsTitle': 'Paramètres',
        'apiKeyLabel': 'Clé API:',
        'modelLabel': 'Modèle:',
        'promptLabel': 'Prompt:',
        'languageLabel': 'Langue:',
        'panelHeader': 'Réponse de l\'assistant',
        'save': 'Enregistrer',
        'cancel': 'Annuler',
        'appStopped': 'L\'application a été arrêtée.',
        'appResumed': 'L\'application a repris.',
        'settingsSaved': 'Paramètres enregistrés avec succès !',
        'errorSaving': 'Erreur lors de l\'enregistrement des paramètres.',
        'analysisSuccess': 'Analyse réussie :',
        'analysisFailed': 'Échec de l\'analyse :',
        'errorAnalyzing': 'Erreur lors de l\'analyse :',
        'thinking': 'Réflexion...', 
        'error': 'Erreur : '
    },
    'de': {
        'analyze': '🔍 Analysieren',
        'analyzing': '⏳ Analysieren...', 
        'stop': '⏹ Stopp',
        'resume': '▶️ Fortsetzen',
        'settings': '⚙️ Einstellungen',
        'settingsTitle': 'Einstellungen',
        'apiKeyLabel': 'API-Schlüssel:',
        'modelLabel': 'Modell:',
        'promptLabel': 'Prompt:',
        'languageLabel': 'Sprache:',
        'panelHeader': 'Antwort des Assistenten',
        'save': 'Speichern',
        'cancel': 'Abbrechen',
        'appStopped': 'Die Anwendung wurde gestoppt.',
        'appResumed': 'Die Anwendung wurde fortgesetzt.',
        'settingsSaved': 'Einstellungen erfolgreich gespeichert!',
        'errorSaving': 'Fehler beim Speichern der Einstellungen.',
        'analysisSuccess': 'Analyse erfolgreich:',
        'analysisFailed': 'Analyse fehlgeschlagen:',
        'errorAnalyzing': 'Fehler bei der Analyse:',
        'thinking': 'Nachdenken...', 
        'error': 'Fehler: '
    }
};

function getTrans(key) {
    return (translations[currentLang] || translations['en'])[key];
}

function updateUIText(lang) {
    currentLang = lang;
    const t = translations[lang] || translations['en'];
    
    // Buttons
    const analyzeBtn = document.getElementById('analyze-button');
    if (analyzeBtn && !analyzeBtn.disabled) analyzeBtn.querySelector('span').textContent = t.analyze;
    
    const controlBtn = document.getElementById('control-button');
    if (controlBtn) {
        if (running) {
            controlBtn.querySelector('span').textContent = t.stop;
        } else {
            controlBtn.querySelector('span').textContent = t.resume;
        }
    }

    const settingsBtn = document.getElementById('settings-button');
    if (settingsBtn) settingsBtn.querySelector('span').textContent = t.settings;

    // Settings Modal
    const settingsTitle = document.getElementById('settings-title');
    if (settingsTitle) settingsTitle.textContent = t.settingsTitle;

    const apiKeyLabel = document.getElementById('api-key-label');
    if (apiKeyLabel) apiKeyLabel.textContent = t.apiKeyLabel;

    const modelLabel = document.getElementById('model-label');
    if (modelLabel) modelLabel.textContent = t.modelLabel;

    const promptLabel = document.getElementById('prompt-label');
    if (promptLabel) promptLabel.textContent = t.promptLabel;

    const languageLabel = document.getElementById('language-label');
    if (languageLabel) languageLabel.textContent = t.languageLabel;

    // Modal Actions
    const modalActions = document.querySelector('.modal-actions');
    if (modalActions) {
        const buttons = modalActions.querySelectorAll('button');
        if (buttons.length >= 2) {
            buttons[0].textContent = t.save;
            buttons[1].textContent = t.cancel;
        }
    }

    // Panel Header
    const panelHeader = document.getElementById('panel-header');
    if (panelHeader) panelHeader.textContent = t.panelHeader;
}

function appendMessage(text, isSystem = false) {
    var textContainer = document.getElementById('text-container');
    var newMessage = document.createElement('div');
    newMessage.classList.add('message');
    if (isSystem) {
        newMessage.style.fontStyle = 'italic';
        newMessage.style.opacity = '0.7';
    }
    newMessage.textContent = text;
    textContainer.appendChild(newMessage);
    textContainer.scrollTop = textContainer.scrollHeight;
    return newMessage;
}

function toggleApp() {
    var controlButton = document.getElementById('control-button');
    var video = document.getElementById('video');

    if (running) {
        // Pause video
        if (video) video.pause();
        console.log('App stopped (video paused)');
        alert(getTrans('appStopped'));
        controlButton.innerHTML = '<span>' + getTrans('resume') + '</span>';
        running = false;
    } else {
        // Resume video
        if (video) video.play();
        console.log('App resumed (video playing)');
        alert(getTrans('appResumed'));
        controlButton.innerHTML = '<span>' + getTrans('stop') + '</span>';
        running = true;
    }
}

function analyze() {
    var analyzeButton = document.getElementById('analyze-button');
    var video = document.getElementById('video');
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');

    if (!video || !canvas) return;

    analyzeButton.disabled = true;
    analyzeButton.innerHTML = '<span>' + getTrans('analyzing') + '</span>';

    // Add temporary thinking message
    var thinkingMsg = appendMessage(getTrans('thinking'), true);

    // Capture current video frame
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64 (remove the data URL prefix)
    var imageData = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];

    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
    })
        .then(response => response.json())
        .then(data => {
            // Remove thinking message
            thinkingMsg.remove();
            
            if (data.status === 'success') {
                console.log('Analysis success:', data.message);
                appendMessage(data.message);
            } else {
                console.error('Analysis failed:', data.message);
                appendMessage(getTrans('error') + data.message, true);
                alert(getTrans('analysisFailed') + ' ' + data.message);
            }
        })
        .catch(error => {
            thinkingMsg.remove();
            console.error('Error analyzing:', error);
            appendMessage(getTrans('error') + error, true);
            alert(getTrans('errorAnalyzing') + ' ' + error);
        })
        .finally(() => {
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = '<span>' + getTrans('analyze') + '</span>';
        });
}

// Settings Modal Logic
var modal = document.getElementById("settings-modal");

function openSettings() {
    fetch('/settings')
        .then(response => response.json())
        .then(data => {
            document.getElementById('api-key').value = data.api_key;
            document.getElementById('model').value = data.model;
            document.getElementById('prompt').value = data.prompt;
            // Set language dropdown if it exists in settings, default to 'en'
            document.getElementById('language').value = data.language || 'en';
            modal.style.display = "block";
        })
        .catch(error => console.error('Error loading settings:', error));
}

function closeSettings() {
    modal.style.display = "none";
}

function saveSettings() {
    var apiKey = document.getElementById('api-key').value;
    var model = document.getElementById('model').value;
    var prompt = document.getElementById('prompt').value;
    var language = document.getElementById('language').value;

    fetch('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            api_key: apiKey,
            model: model,
            prompt: prompt,
            language: language
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateUIText(language); // Update UI immediately
                alert(getTrans('settingsSaved'));
                closeSettings();
            } else {
                alert(getTrans('errorSaving'));
            }
        })
        .catch(error => console.error('Error saving settings:', error));
}

// Close modal when clicking outside of it
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Initialize UI with correct language on load
document.addEventListener('DOMContentLoaded', () => {
    // Start Video Stream
    var video = document.getElementById('video');
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
                video.play();
            })
            .catch(function (error) {
                console.error("Error accessing webcam:", error);
                alert("Error accessing webcam. Please make sure it is connected and permissions are granted.");
            });
    } else {
        console.error("getUserMedia not supported");
        alert("Your browser does not support webcam access.");
    }

    fetch('/settings')
        .then(response => response.json())
        .then(data => {
            if (data.language) {
                updateUIText(data.language);
            }
        })
        .catch(console.error);
});