(function() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);

    window.addEventListener('DOMContentLoaded', () => {
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'theme-toggle';
        toggleBtn.innerHTML = theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode';
        document.body.appendChild(toggleBtn);

        toggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            toggleBtn.innerHTML = newTheme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode';
        });
    });
})();
