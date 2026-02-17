// Material Design inspired JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('menu-button');
    const drawer = document.getElementById('drawer');
    const scrim = document.getElementById('scrim');
    const darkModeToggle = document.getElementById('dark-mode-toggle');

    // Drawer toggle
    menuButton.addEventListener('click', function() {
        drawer.classList.toggle('open');
        scrim.classList.toggle('show');
    });

    scrim.addEventListener('click', function() {
        drawer.classList.remove('open');
        scrim.classList.remove('show');
    });

    // Dark mode toggle
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark');
        const icon = darkModeToggle.querySelector('i');
        if (document.body.classList.contains('dark')) {
            icon.textContent = 'brightness_5';
        } else {
            icon.textContent = 'brightness_6';
        }
    });

    console.log('Lecturer Management System loaded');
});