document.addEventListener("DOMContentLoaded", function() {
    const cardContainer = document.getElementById("card-container");
    const numCards = 12;  // Número de cards que você quer gerar
  
    for (let i = 0; i < numCards; i++) {
      const cardHtml = `
        <div class="card_mq">
          <div class="imBX"></div>
          <div class="content_card">
            <span class="btn_mq">
              <a href="" class="btn_A">Ver mais</a>
            </span>
            <h3>Fresadora CNC</h3>
          </div>
        </div>
      `;
      cardContainer.insertAdjacentHTML("beforeend", cardHtml);
    }
  });
  