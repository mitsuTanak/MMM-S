// Obter todos os dropdowns do documento
const dropdowns = document.querySelectorAll('.dropdown');

// Percorrer todos os elementos dropdown
dropdowns.forEach(dropdown => {
    // Obter elementos internos de cada dropdown
    const select = dropdown.querySelector('.select');
    const caret = dropdown.querySelector('.caret');
    const menu = dropdown.querySelector('.menu');
    const options = dropdown.querySelectorAll('.menu li');
    const selected = dropdown.querySelector('.selected');
    const hiddenInput = document.getElementById('selected_role')

    // Adicionar um evento de clique ao elemento select
    select.addEventListener('click', () => {
        // Adicionar os estilos de clique ao elemento select
        select.classList.toggle('select-clicked');
        caret.classList.toggle('caret-rotate');
        // Adicionar os estilos de abertura ao elemento menu
        menu.classList.toggle('menu-open');
    });

    // Percorrer todos os elementos de opção
    options.forEach(option => {
        // Adicionar um evento de clique ao elemento de opção
        option.addEventListener('click', () => {
            // Alterar o texto interno de "selected" para o texto interno da opção clicada
            selected.innerText = option.innerText;
            // Atualiza o valor do campo oculto com o valor do dropdown
            hiddenInput.value = option.getAttribute('data-value')
            
            // Remover os estilos de clique do elemento select
            select.classList.remove('select-clicked');
            // Remover os estilos de rotação do elemento caret
            caret.classList.remove('caret-rotate');
            // Remover os estilos de abertura do elemento menu
            menu.classList.remove('menu-open');
            // Remover a classe ativa de todos os elementos de opção
            options.forEach(option => {
                option.classList.remove('active');
            });
            // Adicionar a classe ativa ao elemento de opção clicado
            option.classList.add('active');
        });
    });
});
