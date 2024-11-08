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

// Função para alternar a visibilidade das opções
function toggleOptions() {
    const options = document.querySelector('.options');
    options.classList.toggle('show-options');
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
    const cardImage = document.getElementById('card-image').files[0];  // Captura da imagem

    // Verifica se todos os campos foram preenchidos
    if (cardName && cardModel && cardYear && cardPrice && cardSector && cardCategory && cardStatus && cardImage) {
        const formData = new FormData();
        formData.append('name', cardName);
        formData.append('model', cardModel);
        formData.append('year', cardYear);
        formData.append('price', cardPrice);
        formData.append('sector', cardSector);
        formData.append('category', cardCategory);
        formData.append('status', cardStatus);
        formData.append('image', cardImage);  // Envia a imagem no formData

        // Envia os dados para o backend
        fetch('/save_card', {
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
                <div class="card_mq">
                    <div class="content_card">
                        <div class="imBX" style="background-image: url('${imageUrl}')">
                            <!-- A imagem de fundo é atribuída aqui -->
                        </div>
                        <h3>${cardName}</h3>
                        <p><strong>Modelo:</strong> ${cardModel}</p>
                        <p><strong>Ano:</strong> ${cardYear}</p>
                        <p><strong>Preço:</strong> R$ ${cardPrice}</p>
                        <p><strong>Setor:</strong> ${cardSector}</p>
                        <p><strong>Categoria:</strong> ${cardCategory}</p>
                        <p><strong>Status:</strong> ${cardStatus}</p>
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
    fetch('/load_cards')
      .then(response => response.json())
      .then(cards => {
        const cardContainer = document.getElementById('card-container');
        cardContainer.innerHTML = ''; // Limpar o conteúdo atual

        cards.forEach(card => {
          const cardHtml = `
          <div class="card_mq" data-category="${card.category}">
              <div class="imBX">
              <img src="${card.image_url}" alt="${card.name}" class="card-image"/>
              </div>
              <div class="content_card">
                  <span class="btn_mq">
                      <a href="" class="btn_A">Ver mais</a>
                  </span>
                  <h3>${card.name}</h3>
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

