// Navbar responsive hamburguesa para home
document.addEventListener('DOMContentLoaded', function () {
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function () {
            if (navLinks.style.display === 'flex') {
                navLinks.style.display = '';
            } else {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'column';
                navLinks.style.background = '#fff';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '72px';
                navLinks.style.right = '18px';
                navLinks.style.boxShadow = '0 6px 18px rgba(10,15,30,0.08)';
                navLinks.style.zIndex = '2000';
                navLinks.style.borderRadius = '12px';
                navLinks.style.padding = '12px 0';
            }
        });
        // Cierra el menú al hacer click fuera
        document.addEventListener('click', function (e) {
            if (!navLinks.contains(e.target) && !mobileToggle.contains(e.target)) {
                navLinks.style.display = '';
            }
        });
    }
});