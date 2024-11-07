document.addEventListener("DOMContentLoaded", function() {
  const cardContainer = document.getElementById("card-container");
  const cards = [
      { title: "Fresadora CNC", category: "Fresadoras" },
      { title: "Torno Mecânico", category: "Tornos" },
      { title: "Furadeira de Bancada", category: "Furadeiras" },
      { title: "Retificadora Plana", category: "Retificadoras" },
      { title: "CNCs", category: "CNCs" },
      { title: "Especiais", category: "Especiais" },
      { title: "Prensas", category: "Prensas" },
      { title: "Serras", category: "Serras" },
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
});
