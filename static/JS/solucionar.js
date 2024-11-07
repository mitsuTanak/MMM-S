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
