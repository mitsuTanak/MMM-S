// Para escolher as opções
function toggleOptions() {
  const options = document.querySelector('.options');
  options.classList.toggle('show-options');
}

// Função para abrir o formulário
function openCardForm() {
  document.getElementById('card-form').style.display = 'block';
}

// Função para fechar o formulário
function closeCardForm() {
  document.getElementById('card-form').style.display = 'none';
}

// Função para salvar o novo card
function saveCard() {
  const cardName = document.getElementById('card-name').value;
  const cardDescription = document.getElementById('card-description').value;

  if (cardName && cardDescription) {
      // Enviar os dados para o servidor para salvar no JSON
      fetch('/save_card', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name: cardName, description: cardDescription })
      })
      .then(response => response.json())
      .then(data => {
          console.log('Card salvo com sucesso', data);
          closeCardForm();
          loadCards(); // Atualiza os cards exibidos na página
      })
      .catch(error => {
          console.error('Erro ao salvar o card:', error);
      });
  } else {
      alert("Preencha todos os campos.");
  }
}

// Função para carregar os cards salvos
function loadCards() {
  fetch('/load_cards')
      .then(response => response.json())
      .then(cards => {
          const cardContainer = document.getElementById('card-container');
          cardContainer.innerHTML = ''; // Limpar o conteúdo atual

          // Criar um card para cada item no JSON
          cards.forEach(card => {
              const cardHtml = `
                  <div class="card_mq">
                      <div class="content_card">
                          <h3>${card.name}</h3>
                          <p>${card.description}</p>
                      </div>
                  </div>
              `;
              cardContainer.insertAdjacentHTML("beforeend", cardHtml);
          });
      })
      .catch(error => console.error('Erro ao carregar os cards:', error));
}

// Carregar os cards ao iniciar a página
document.addEventListener('DOMContentLoaded', loadCards);
