document.querySelector('.menu-toggle').addEventListener('click', function() {
    var menu = document.querySelector('.nav-links');
    if (menu.classList.contains('active')) {
        menu.classList.remove('active');
        document.body.removeAttribute('style')
    } else {
        menu.classList.add('active');
        document.body.setAttribute('style', 'overflow: hidden;')
    }
});
