// Example JavaScript code

// Example code to toggle a navigation menu on mobile devices
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');

navToggle.addEventListener('click', () => {
  navMenu.classList.toggle('active');
});

// Example code to show/hide additional details for articles
const articleDetails = document.querySelectorAll('.article-details');

articleDetails.forEach((details) => {
  const toggleButton = details.querySelector('.toggle-button');
  const content = details.querySelector('.content');

  toggleButton.addEventListener('click', () => {
    content.classList.toggle('hidden');
  });
});
