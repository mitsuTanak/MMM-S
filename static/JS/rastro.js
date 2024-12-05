const canvas = document.getElementById('canvas1');
const ctx = canvas.getContext('2d');

// Obtém o tamanho da imagem da equipe
const teamPhoto = document.querySelector('.team-photo img');

canvas.width = teamPhoto.offsetWidth;
canvas.height = teamPhoto.offsetHeight;

// Redimensiona o canvas ao ajustar a janela
window.addEventListener('resize', () => {
    canvas.width = teamPhoto.offsetWidth;
    canvas.height = teamPhoto.offsetHeight;
});

const particlesArray = [];
let hue = 0;

// Objeto para coordenadas do mouse
const mouse = {
    x: undefined,
    y: undefined,
};

// Captura eventos de clique no canvas
canvas.addEventListener('click', (event) => {
    mouse.x = event.x;
    mouse.y = event.y;
    hue += 10; // Altera a tonalidade
    for (let i = 0; i < 10; i++) {
        particlesArray.push(new Particle());
    }
});

// Captura o movimento do mouse
canvas.addEventListener('mousemove', (event) => {
    mouse.x = event.x;
    mouse.y = event.y;
    hue += 2; // Altera a tonalidade
    for (let i = 0; i < 3; i++) {
        particlesArray.push(new Particle());
    }
});

// Classe para criar partículas
class Particle {
    constructor() {
        this.x = mouse.x;
        this.y = mouse.y;
        this.size = Math.random() * 10 + 1; // Tamanho entre 1 e 10
        this.speedX = Math.random() * 3 - 1.5; // Velocidade horizontal
        this.speedY = Math.random() * 3 - 1.5; // Velocidade vertical
        this.color = 'rgba(255, 0, 0, 0.8)'; // Cor vermelha com opacidade 0.8
    }

    // Atualiza posição e tamanho da partícula
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        if (this.size > 0.2) this.size -= 0.1;
    }

    // Desenha a partícula
    draw() {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Gerencia partículas
function handleParticles() {
    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
        particlesArray[i].draw();

        // Conecta partículas próximas
        for (let j = i; j < particlesArray.length; j++) {
            const dx = particlesArray[i].x - particlesArray[j].x;
            const dy = particlesArray[i].y - particlesArray[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 100) {
                ctx.beginPath();
                ctx.strokeStyle = particlesArray[i].color;
                ctx.lineWidth = 0.1;
                ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                ctx.stroke();
                ctx.closePath();
            }
        }

        // Remove partículas muito pequenas
        if (particlesArray[i].size <= 0.3) {
            particlesArray.splice(i, 1);
            i--;
        }
    }
}

// Anima as partículas
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpa a tela
    handleParticles();
    requestAnimationFrame(animate); // Chama o próximo frame
}
animate();
