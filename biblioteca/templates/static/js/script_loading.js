const loadingText = document.getElementById('loading-text');
let toggle = true;

// Função para alternar mensagens
function alternateMessage() {
  if (toggle) {
    loadingText.textContent = 'Isso pode demorar um pouco';
  } else {
    loadingText.textContent = 'Processando Partitura';
  }
  toggle = !toggle;
}

// Alterna a cada 5 segundos (5000 ms)
setInterval(alternateMessage, 4000);