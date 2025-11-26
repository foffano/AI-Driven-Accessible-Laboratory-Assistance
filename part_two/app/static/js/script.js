var socket = io();
var running = true;

socket.on('stream', function (data) {
    var img = document.getElementById('video');
    img.src = 'data:image/jpeg;base64,' + data.image;
});

// socket.on('text', ...) removed to rely on HTTP response for better reliability

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
    if (running) {
        fetch('/stop')
            .then(response => response.json())
            .then(data => {
                console.log('App stopped:', data);
                alert('The application has been stopped.');
                controlButton.innerHTML = '<span>▶️ Resume</span>';
                running = false;
            })
            .catch((error) => {
                console.error('Error stopping the app:', error);
            });
    } else {
        fetch('/resume')
            .then(response => response.json())
            .then(data => {
                console.log('App resumed:', data);
                alert('The application has resumed.');
                controlButton.innerHTML = '<span>⏹ Stop</span>';
                running = true;
            })
            .catch((error) => {
                console.error('Error resuming the app:', error);
            });
    }
}

function analyze() {
    var analyzeButton = document.getElementById('analyze-button');
    analyzeButton.disabled = true;
    analyzeButton.innerHTML = '<span>⏳ Analyzing...</span>';

    // Add temporary thinking message
    var thinkingMsg = appendMessage('Thinking...', true);

    fetch('/analyze', {
        method: 'POST'
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
                appendMessage('Error: ' + data.message, true);
                alert('Analysis failed: ' + data.message);
            }
        })
        .catch(error => {
            thinkingMsg.remove();
            console.error('Error analyzing:', error);
            appendMessage('Error: ' + error, true);
            alert('Error analyzing: ' + error);
        })
        .finally(() => {
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = '<span>🔍 Analyze</span>';
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

    fetch('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            api_key: apiKey,
            model: model,
            prompt: prompt
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Settings saved successfully!');
                closeSettings();
            } else {
                alert('Error saving settings.');
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
