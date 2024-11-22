// Para escolher as opções
function toggleOptions() {
    const options = document.querySelector('.options');
    options.classList.toggle('show-options');
}
// Função para abrir o modal de cadastro de máquinas
function openCardModal() {
    document.getElementById('card-modal').style.display = 'block';
}

// Função para fechar o modal de cadastro de máquinas
function closeCardModal() {
    document.getElementById('card-modal').style.display = 'none';
}

// Fechar o modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('card-modal');
    if (event.target == modal) {
        closeCardModal();
    }
}

function saveCard() {
    const cardName = document.getElementById('card-name').value;
    const cardModel = document.getElementById('card-model').value;
    const cardYear = document.getElementById('card-year').value;
    const cardPrice = document.getElementById('card-price').value;
    const cardSector = document.getElementById('card-sector').value;
    const cardCategory = document.getElementById('card-category').value;
    const cardStatus = document.getElementById('card-status').value;
    const cardDescription = document.getElementById('card-description').value;
    const cardPdf = document.getElementById('card-pdf').files[0]; 
    const cardImage = document.getElementById('card-image').files[0];  // Captura da imagem

    // Verifica se todos os campos foram preenchidos
    if (cardName && cardModel && cardYear && cardPrice && cardSector && cardCategory && cardStatus && cardImage) {
        const formData = new FormData();
        formData.append('card-name', cardName);
        formData.append('card-model', cardModel);
        formData.append('card-year', cardYear);
        formData.append('card-price', cardPrice);
        formData.append('card-sector', cardSector);
        formData.append('card-category', cardCategory);
        formData.append('card-status', cardStatus);
        formData.append('card-description', cardDescription); // Adiciona a descrição no formData
        formData.append('image', cardImage);  // Envia a imagem no formData
        if (cardPdf) {
            formData.append('pdf', cardPdf); // Adiciona o PDF ao FormData
        }

        // Envia os dados para o backend
        fetch('/save_machine', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Card salvo com sucesso', data);
            closeCardModal();

            // Caminho da imagem que foi carregada no servidor
            const imageUrl = data.image_url;

            // Adicionando o card na página
            const cardContainer = document.getElementById('card-container');
            const newCardHtml = `
            <div class="card_mq" data-category="${cardCategory}">
                <div class="imBX">
                    <img src="${imageUrl}" alt="${cardName}" class="card-image"/>
                </div>
                <div class="content_card">
                    <span class="btn_mq">
                        <a href="/machine_details/${data.id}" class="btn_A">Ver mais</a>
                    </span>
                    <h3>${cardName}</h3>
                </div>
            </div>
            `;

            cardContainer.insertAdjacentHTML("beforeend", newCardHtml);

            // Resetando o formulário após salvar
            document.getElementById('card-form').reset();
        })
        .catch(error => console.error('Erro ao salvar o card:', error));
    } else {
        alert("Preencha todos os campos e adicione uma imagem.");
    }
}

// Função para carregar os cards ao iniciar a página
function loadCards() {
    fetch('/load_machines')
      .then(response => response.json())
      .then(cards => {
        console.log("Máquinas carregadas:", cards);  // Verificando os dados recebidos

        const cardContainer = document.getElementById('card-container');
        cardContainer.innerHTML = ''; // Limpar o conteúdo atual

        cards.forEach(card => {
            const cardHtml = `
            <div class="card_mq" data-category="${card.category}">
                <div class="imBX">
                    <img src="${card.image_path}" alt="${card.machine_name}" class="card-image"/>
                </div>
                <div class="content_card">
                    <span class="btn_mq">
                        <a href="/detalhamento/${card.id}" class="btn_A">Ver mais</a>
                    </span>
                    <h3>${card.machine_name}</h3> 
                </div>
            </div>
            `;
            cardContainer.insertAdjacentHTML("beforeend", cardHtml);
        });
      })
      .catch(error => console.error('Erro ao carregar os cards:', error));
}
 
// Chamar a função de loadCards ao carregar a página
document.addEventListener('DOMContentLoaded', loadCards);

// Ajustar o botão "Cadastrar Máquinas" para abrir o modal
document.getElementById('add-card-button').onclick = openCardModal;