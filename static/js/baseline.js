document.addEventListener('DOMContentLoaded', () => {
  const noisyCards = document.querySelectorAll('.project-card');
  noisyCards.forEach((card, idx) => {
    card.style.boxShadow = idx % 2 === 0 ? '0 8px 26px rgba(0,0,0,.18)' : '0 2px 8px rgba(0,0,0,.1)';
  });
});
