// The news rail follows the reading position; stories remain visible and stationary.
document.querySelectorAll('.news-timeline').forEach((timeline) => {
  const stories = [...timeline.querySelectorAll('.news-story')];
  if (!stories.length) return;
  let queued = false;
  const update = () => {
    queued = false;
    const navHeight = document.querySelector('.nav')?.getBoundingClientRect().bottom || 0;
    const readingLine = navHeight + Math.min(180, (innerHeight - navHeight) * .25);
    const boxes = stories.map(story => story.getBoundingClientRect());
    const top = boxes[0].top + 9;
    const length = Math.max(1, boxes[boxes.length - 1].top - boxes[0].top);
    const progress = Math.max(0, Math.min(1, (readingLine - top) / length));
    timeline.style.setProperty('--rail-top', `${top - timeline.getBoundingClientRect().top}px`);
    timeline.style.setProperty('--rail-length', `${length}px`);
    timeline.style.setProperty('--rail-progress', progress.toFixed(5));
    let current = 0;
    boxes.forEach((box, i) => { if (box.top + 9 <= readingLine) current = i; });
    stories.forEach((story, i) => {
      story.classList.toggle('is-current', i === current);
      story.classList.toggle('is-passed', i < current);
    });
    timeline.classList.add('is-tracked');
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  new ResizeObserver(queue).observe(timeline);
  update();
});
