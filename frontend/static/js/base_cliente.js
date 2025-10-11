document.addEventListener('DOMContentLoaded', function () {
    // --- Tema oscuro/claro ---
    const toggleBtn = document.getElementById('toggleTheme');
    if (toggleBtn) {
        const icon = toggleBtn.querySelector('i');
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
            icon.classList.remove('bi-moon');
            icon.classList.add('bi-sun');
        } else {
            document.body.classList.remove('dark-mode');
            icon.classList.remove('bi-sun');
            icon.classList.add('bi-moon');
        }
        toggleBtn.addEventListener('click', function () {
            document.body.classList.toggle('dark-mode');
            if (document.body.classList.contains('dark-mode')) {
                icon.classList.remove('bi-moon');
                icon.classList.add('bi-sun');
                localStorage.setItem('theme', 'dark');
            } else {
                icon.classList.remove('bi-sun');
                icon.classList.add('bi-moon');
                localStorage.setItem('theme', 'light');
            }
        });
    }

});