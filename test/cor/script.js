document.getElementById('accessibilityBtn').addEventListener('click', function() {
    const menu = document.getElementById('accessibilityMenu');
    menu.classList.toggle('active');

    if (menu.classList.contains('active')) {
        menu.style.display = 'block'; // Mostra o menu
        setTimeout(() => {
            menu.style.opacity = '1'; // Faz a transição de opacidade
            menu.style.transform = 'translateY(0)'; // Reseta a transformação
        }, 10); // Atraso para garantir que a transição ocorra
    } else {
        menu.style.opacity = '0'; // Faz a transição de opacidade
        menu.style.transform = 'translateY(-20px)'; // Transforma para cima
        setTimeout(() => {
            menu.style.display = 'none'; // Oculta o menu após a transição
        }, 300); // Espera a duração da transição
    }
});

document.querySelectorAll('.themeBtn').forEach(button => {
    button.addEventListener('click', function() {
        document.body.className = ''; // Limpa as classes de tema
        const selectedTheme = button.getAttribute('data-theme');
        document.body.classList.add(selectedTheme + '-theme'); // Adiciona a classe ao body
        document.getElementById('accessibilityMenu').className = 'menu ' + selectedTheme + '-theme'; // Adiciona a classe ao menu
    });
});

document.getElementById('closeMenuBtn').addEventListener('click', function() {
    const menu = document.getElementById('accessibilityMenu');
    menu.classList.remove('active');
    menu.style.opacity = '0'; // Faz a transição de opacidade
    menu.style.transform = 'translateY(-20px)'; // Transforma para cima
    setTimeout(() => {
        menu.style.display = 'none'; // Oculta o menu após a transição
    }, 300); // Espera a duração da transição
});
