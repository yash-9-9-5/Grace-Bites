document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Check for saved theme preference or default to light theme
    const savedTheme = localStorage.getItem('theme') || 'light-theme';
    body.className = savedTheme;

    // Update toggle button text
    updateToggleText();

    themeToggle.addEventListener('click', () => {
        // Toggle between light and dark theme
        if (body.classList.contains('light-theme')) {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark-theme');
        } else {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            localStorage.setItem('theme', 'light-theme');
        }
        
        updateToggleText();
    });

    function updateToggleText() {
        if (body.classList.contains('dark-theme')) {
            themeToggle.textContent = '☀️ Light Mode';
        } else {
            themeToggle.textContent = '🌙 Dark Mode';
        }
    }
}); 