// The round button of what moves by itself (the hero's video, the drifting quotes, the grid of figures, a
// clip, the globe): it shows what a press does, the pause bars while it plays and the play triangle while it
// stands, and says so ("Pause the video", "Play the video"). what: the words after the verb.
const icons = {
  pause: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.5v9M11 3.5v9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  play: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.2v9.6L12.6 8z" fill="currentColor"/></svg>',
};
export const showPlayState = (button, playing, what) => {
  button.innerHTML = playing ? icons.pause : icons.play;
  button.setAttribute('aria-label', `${playing ? 'Pause' : 'Play'} ${what}`);
};
