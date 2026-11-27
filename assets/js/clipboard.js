// Shared clipboard behavior. data-copy names an element ID; data-copy-text holds a literal command;
// data-copy-url copies the page's address (with the section it is at).
// Read the target on each click so citation tabs can change it. Buttons stay hidden without the API.
import { wireCopyButton } from './lib/copy.js';

document.querySelectorAll('[data-copy], [data-copy-text], [data-copy-url]').forEach(wireCopyButton);
