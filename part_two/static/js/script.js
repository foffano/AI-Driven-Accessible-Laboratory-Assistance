var socket = io();

socket.on('stream', function(data) {
    console.log('Received stream data');
    var img = document.getElementById('video');
    img.src = 'data:image/jpeg;base64,' + data.image;
});

socket.on('text', function(data) {
    console.log('Received text data:', data.message);
    var textContainer = document.getElementById('text-container');
    var newMessage = document.createElement('div');
    newMessage.classList.add('message');
    newMessage.textContent = data.message;
    textContainer.appendChild(newMessage);
    textContainer.scrollTop = textContainer.scrollHeight;
});

socket.on('current_settings', function(data) {
    console.log('Received settings:', data);
    document.getElementById('api-key-input').value = data.api_key || '';
    document.getElementById('model-input').value = data.model || '';
    document.getElementById('prompt-input').value = data.prompt || '';
});

function analyzeFrame() {
    console.log('Requesting analysis of the current frame.');
    socket.emit('analyze_frame');
}

document.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        // Avoid triggering analysis if the user is typing in the settings modal
        if (document.getElementById('settings-modal').style.display === 'none') {
            analyzeFrame();
        }
    }
});

function toggleSettingsModal() {
    var modal = document.getElementById('settings-modal');
    var isHidden = modal.style.display === 'none';
    if (isHidden) {
        // Request settings from backend when opening
        socket.emit('get_settings');
        modal.style.display = 'block';
    } else {
        modal.style.display = 'none';
    }
}

function saveSettings() {
    var apiKey = document.getElementById('api-key-input').value;
    var model = document.getElementById('model-input').value;
    var prompt = document.getElementById('prompt-input').value;

    fetch('/save_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ api_key: apiKey, model: model, prompt: prompt })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Settings saved successfully!');
            toggleSettingsModal();
        } else {
            alert('Failed to save settings: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
    });
}