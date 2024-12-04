document.getElementById('phone').addEventListener('input', function (e) {
    let telefone = e.target.value;
    telefone = telefone.replace(/\D/g, ''); // Remove todos os caracteres que não são dígitos
    telefone = telefone.replace(/(\d{2})(\d)/, '($1) $2');
    telefone = telefone.replace(/(\d{5})(\d{1,4})$/, '$1-$2');
    e.target.value = telefone;
  });