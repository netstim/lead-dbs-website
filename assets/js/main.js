// Rotate slideshow images and testimonials, like the old Enfold sliders.
function rotate(container, selector, interval) {
  const items = Array.from(container.querySelectorAll(selector));
  if (items.length < 2) return;
  let i = 0;
  items.forEach((el, n) => el.classList.toggle('active', n === 0));
  let timer = setInterval(next, interval);
  function next() {
    items[i].classList.remove('active');
    i = (i + 1) % items.length;
    items[i].classList.add('active');
  }
  container.addEventListener('mouseenter', () => clearInterval(timer));
  container.addEventListener('mouseleave', () => { timer = setInterval(next, interval); });
}
document.querySelectorAll('.slideshow').forEach((el) => rotate(el, 'img', 5000));
document.querySelectorAll('.testimonials').forEach((el) => rotate(el, 'blockquote', 8000));
