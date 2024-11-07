// Função de filtro
function applyFilter() {
    const category = document.getElementById("category-filter").value;
    const searchQuery = document.getElementById("search-input").value.toLowerCase();
    filterCards(category, searchQuery);
}
  
// Função de filtro dos cards
function filterCards(category, searchQuery) {
    const cards = document.querySelectorAll(".card_mq");

    cards.forEach(card => {
      const cardCategory = card.getAttribute("data-category");
      const cardTitle = card.querySelector("h3").textContent.toLowerCase();

      const matchesCategory = category === "" || cardCategory === category;
      const matchesSearch = cardTitle.includes(searchQuery);

      if (matchesCategory && matchesSearch) {
        card.style.display = "block"; // Exibe o card
      } else {
        card.style.display = "none"; // Oculta o card
      }
    });
}

// Atualizar filtro ao alterar a categoria no dropdown
document.getElementById("category-filter").addEventListener("change", function() {
    applyFilter();
});

// Atualizar filtro ao digitar no campo de pesquisa
document.getElementById("search-input").addEventListener("input", function() {
    applyFilter();
});

// Função que cria os cards dinamicamente
document.addEventListener("DOMContentLoaded", function() {
    const cardContainer = document.getElementById("card-container");
    const cards = [
        { title: "Fresadora CNC", category: "Fresadoras" },
        { title: "Torno Mecânico", category: "Tornos" },
        { title: "Furadeira de Bancada", category: "Furadeiras" },
        { title: "Retificadora Plana", category: "Retificadoras" },
        // ... adicione os outros cards com as categorias desejadas
    ];

    cards.forEach(card => {
        const cardHtml = `
            <div class="card_mq" data-category="${card.category}">
                <div class="imBX"></div>
                <div class="content_card">
                    <span class="btn_mq">
                        <a href="" class="btn_A">Ver mais</a>
                    </span>
                    <h3>${card.title}</h3>
                </div>
            </div>
        `;
        cardContainer.insertAdjacentHTML("beforeend", cardHtml);
    });

    // Chama o filtro ao carregar a página
    applyFilter();
});
