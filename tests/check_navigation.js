// Unit checks for the homepage's scroll-aware navigation, without browser dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const listeners = {};
const frames = [];
const profile = {};
const makeHeading = (top) => ({ top, getBoundingClientRect() { return { top: this.top }; } });
const headings = { aboutme: makeHeading(420), publications: makeHeading(900) };
const makeLink = (id) => ({
  hash: '#' + id,
  attrs: {},
  setAttribute(name, value) { this.attrs[name] = value; },
  removeAttribute(name) { delete this.attrs[name]; }
});
const links = [makeLink('aboutme'), makeLink('publications')];
let observer;
let observed;
let hasProfile = true;
const window = {
  pageYOffset: 0,
  innerHeight: 900,
  getComputedStyle() { return { scrollMarginTop: '105px' }; },
  requestAnimationFrame(callback) { frames.push(callback); },
  addEventListener(event, callback) { listeners[event] = callback; },
  ResizeObserver: class {
    constructor(callback) { observer = callback; }
    observe(element) { observed = element; }
  }
};
const document = {
  documentElement: { scrollHeight: 3000 },
  querySelector() { return hasProfile ? profile : null; },
  querySelectorAll() { return links; },
  getElementById(id) { return headings[id]; },
  addEventListener() {}
};
const context = vm.createContext({ window, document, ResizeObserver: window.ResizeObserver });
vm.runInContext(fs.readFileSync(path.join(__dirname, '../js/main.js'), 'utf8'), context);
context.main.initSectionNavigation();

const flush = () => { while (frames.length) frames.shift()(); };
const current = () => links.filter(link => link.attrs['aria-current'] === 'location').map(link => link.hash);
assert.deepEqual(current(), ['#aboutme']);
assert.equal(observed, profile);

headings.publications.top = 105;
listeners.scroll();
listeners.scroll();
assert.equal(frames.length, 1, 'Scroll updates should be coalesced');
flush();
assert.deepEqual(current(), ['#publications']);

headings.publications.top = 600;
listeners.hashchange();
flush();
assert.deepEqual(current(), ['#aboutme']);

headings.publications.top = 76;
window.getComputedStyle = () => ({ scrollMarginTop: '76px' });
listeners.resize();
flush();
assert.deepEqual(current(), ['#publications']);

headings.publications.top = 400;
observer();
flush();
assert.deepEqual(current(), ['#aboutme'], 'Expanded content changes the active section');

window.pageYOffset = 2100;
listeners.scroll();
flush();
assert.deepEqual(current(), ['#publications'], 'At the bottom, the last section is active');
window.pageYOffset = 0;
listeners.pageshow();
flush();
assert.deepEqual(current(), ['#aboutme']);

hasProfile = false;
assert.doesNotThrow(() => context.main.initSectionNavigation(), '404 pages have no profile');
console.log('PASS: active navigation, mobile offset, scroll batching, resize/disclosure changes, history, 404');
