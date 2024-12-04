function toggleDropdown(id) {
    var element = document.getElementById(id);
    if (element.style.display === "block") {
        element.style.display = "none";
    } else {
        element.style.display = "block";
    }
}

function selectOption(event, tipo, valor) {
    event.preventDefault();
    alert('Selecionado ' + tipo + ': ' + valor);
    // Aqui você pode adicionar lógica para aplicar o filtro selecionado
}