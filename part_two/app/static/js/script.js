var socket = io();
var running = true;

socket.on('stream', function (data) {
    var img = document.getElementById('video');
    img.src = 'data:image/jpeg;base64,' + data.image;
});

socket.on('text', function (data) {
    var textContainer = document.getElementById('text-container');
    var newMessage = document.createElement('div');
    newMessage.classList.add('message');
    newMessage.textContent = data.message;
    textContainer.appendChild(newMessage);
    textContainer.scrollTop = textContainer.scrollHeight;
});

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
                controlButton.innerHTML = '<span>⏹ Parar</span>';
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
    analyzeButton.innerHTML = '<span>⏳ Analisando...</span>';

    fetch('/analyze', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Analysis success:', data.message);
            } else {
                console.error('Analysis failed:', data.message);
                alert('Analysis failed: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error analyzing:', error);
            alert('Error analyzing: ' + error);
        })
        .finally(() => {
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = '<span>🔍 Analisar</span>';
        });
}
