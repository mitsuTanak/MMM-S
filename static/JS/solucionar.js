function salvar() {
    alert("Dados salvos com sucesso!");
}

function excluir() {
    if (confirm("Tem certeza que deseja excluir os dados?")) {
        document.getElementById("anomalyForm").reset();
        alert("Dados excluídos.");
    }
}

function fechar() {
    window.close();
}

function previewImage(inputId, imgId) {
    const input = document.getElementById(inputId);
    const img = document.getElementById(imgId);
    const reader = new FileReader();

    reader.onload = function(e) {
        img.src = e.target.result;
        img.style.display = 'block';
    };
    
    if (input.files[0]) {
        reader.readAsDataURL(input.files[0]);
    }
}

function updateFields() {
    const select = document.getElementById('machine-select');
    const selectedOption = select.options[select.selectedIndex];

    const setor = selectedOption.getAttribute('data-sector');
    const categoria = selectedOption.getAttribute('data-category');

    document.getElementById('setor').value = setor;
    document.getElementById('categoria').value = categoria;
}