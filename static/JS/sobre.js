 // Função para verificar a visibilidade dos elementos
 function checkVisibility() {
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach(function(el) {
        if (el.getBoundingClientRect().top < window.innerHeight) {
            el.classList.add('visible'); // Adiciona a classe quando o elemento entrar na tela
        }
    });
}

// Verifica a visibilidade ao rolar a página
window.addEventListener('scroll', checkVisibility);

// Chama a função na carga da página para animar os elementos que já estão visíveis
document.addEventListener('DOMContentLoaded', checkVisibility);

// Configuração da animação quando a seção entrar na tela
document.addEventListener("DOMContentLoaded", function() {
    // Configuração do Intersection Observer
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Adiciona a classe de animação quando a seção entra na tela
                entry.target.classList.add('animate');
                observer.unobserve(entry.target); // Para de observar após a animação
            }
        });
    }, { threshold: 0.9 }); // Acionar quando 90% da seção estiver visível

    // Seletor para todas as seções que precisam ser observadas
    const sections = document.querySelectorAll('.section, .sobre-senai');

    // Começa a observar as seções
    sections.forEach(section => {
        observer.observe(section);
    });
});