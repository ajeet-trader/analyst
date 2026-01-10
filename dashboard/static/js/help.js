// Help Page JavaScript - Accordion functionality
document.addEventListener('DOMContentLoaded', () => {
    initAccordion();
});

function initAccordion() {
    const headers = document.querySelectorAll('.accordion-header');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const isActive = header.classList.contains('active');

            // Close all other accordions
            headers.forEach(h => {
                h.classList.remove('active');
                h.querySelector('.accordion-arrow').textContent = '▶';
                h.nextElementSibling.style.display = 'none';
            });

            // Toggle current accordion
            if (!isActive) {
                header.classList.add('active');
                header.querySelector('.accordion-arrow').textContent = '▼';
                header.nextElementSibling.style.display = 'block';
            }
        });
    });
}
