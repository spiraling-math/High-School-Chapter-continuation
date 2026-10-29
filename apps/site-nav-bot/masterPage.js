// masterPage.js  (site repository: src/pages/masterPage.js; editor: Page Code > Global)
// -----------------------------------------------------------------------------
// Connects the chat widget (an Embed HTML element) to the backend, on every page.
//
//  Elements (set their IDs in the Properties & Events panel):
//    Desktop (pinned to the screen):
//      #navBotFrame          Embed HTML element holding widget.html   (required)
//      #navBotLauncher       a Wix Button that opens the chat          (optional)
//    Mobile (mobile-only elements in the page flow - mobile can't pin):
//      #navBotFrameMobile    mobile-only Embed HTML, "Collapsed on load"
//      #navBotLauncherMobile mobile-only Button
//  Without a launcher Button the widget draws its own round button inside the
//  Embed element. With one, the Embed element is shown only while chatting.
//
// The conversation is kept here (in the visitor's browser session), not in the
// iframe and not on the server. A random visitor id is kept in the browser's
// local storage and sent with each question, as the backend's rate-limit key.
//
// If this file already has code, paste the import lines at the top with the
// other imports and put the body of $w.onReady inside your existing onReady.
// -----------------------------------------------------------------------------
import { askNavBot } from 'backend/navBot.web';
import wixLocationFrontend from 'wix-location-frontend';
import wixWindowFrontend from 'wix-window-frontend';
import { local, session } from 'wix-storage-frontend';

// pinned: true  = pinned to the screen; shown/hidden with show()/hide().
// pinned: false = in the page flow; expand()/collapse() so a closed chat takes no space.
const PAIRS = [
  { frame: '#navBotFrame', launcher: '#navBotLauncher', pinned: true },
  { frame: '#navBotFrameMobile', launcher: '#navBotLauncherMobile', pinned: false },
];
const FROM_WIDGET = 'spi-navbot';
const TO_WIDGET = 'spi-navbot-host';
const STORE_KEY = 'spiNavBot.v1';
const VISITOR_KEY = 'spiNavBot.visitor';
const VISITOR_ID_RE = /^[A-Za-z0-9_-]{8,64}$/;
const MAX_MESSAGE_CHARS = 500;
const MAX_HISTORY = 6; // messages sent back to the server as context
const MAX_TRANSCRIPT = 30; // bubbles restored after moving to another page
const MIN_GAP_MS = 2000; // client-side pause between questions
const SITE_ORIGIN = 'https://www.spi-math.com';
const SITE_HOST_RE = /^(?:[a-z0-9-]+\.)?spi-math\.com$/i;
// Shown when the backend call itself fails (different from the chat window's
// own "could not connect" text, so the two problems can be told apart).
const SERVER_FAILED_TEXT = 'Sorry, the guide is not available right now. Please try again in a few minutes.';

let state = loadState();
let busy = false;
let lastAskAt = 0;
const handled = new Set(); // message ids already answered (guards against double wiring)

// ---------------------------------------------------------------- storage ---
function loadState() {
  const empty = { history: [], transcript: [], open: false };
  try {
    const raw = session.getItem(STORE_KEY);
    if (!raw) return empty;
    const s = JSON.parse(raw);
    return {
      history: Array.isArray(s.history) ? s.history.filter(isHistoryItem).slice(-MAX_HISTORY) : [],
      transcript: Array.isArray(s.transcript) ? s.transcript.filter(isTranscriptItem).slice(-MAX_TRANSCRIPT) : [],
      open: s.open === true,
    };
  } catch (e) {
    return empty;
  }
}

function saveState() {
  try {
    session.setItem(STORE_KEY, JSON.stringify(state));
  } catch (e) {
    /* storage full or blocked: the chat still works for this page */
  }
}

/** A random id for this browser (not personal data); the backend rate-limits per id. */
function visitorId() {
  try {
    let id = local.getItem(VISITOR_KEY);
    if (typeof id !== 'string' || !VISITOR_ID_RE.test(id)) {
      id = 'v' + Date.now().toString(36) + Math.random().toString(36).slice(2, 12);
      local.setItem(VISITOR_KEY, id);
    }
    return id;
  } catch (e) {
    return undefined; // storage blocked: the backend applies its global limits only
  }
}

function isHistoryItem(x) {
  return !!x && (x.role === 'user' || x.role === 'assistant') && typeof x.content === 'string';
}

function isTranscriptItem(x) {
  return !!x && (x.from === 'user' || x.from === 'bot') && typeof x.text === 'string' && Array.isArray(x.links);
}

// ------------------------------------------------------------- validation ---
function isPlainObject(v) {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

/**
 * Same-site path for wixLocationFrontend.to(), or null. Only https pages on
 * spi-math.com; a path starting with "//" (which a browser reads as another
 * site) and any backslash are refused.
 */
function toSitePath(url) {
  if (typeof url !== 'string' || url.length > 600 || /[\\\s]/.test(url)) return null;
  let u;
  try {
    u = new URL(url, SITE_ORIGIN);
  } catch (e) {
    return null;
  }
  if (u.protocol !== 'https:' || u.username || u.password || !SITE_HOST_RE.test(u.hostname)) return null;
  const path = u.pathname || '/';
  if (path.charAt(0) !== '/' || path.charAt(1) === '/') return null;
  // Relative path keeps the visitor on the current domain / language version.
  return path + u.search + u.hash;
}

function cleanLinks(links) {
  if (!Array.isArray(links)) return [];
  return links
    .filter((l) => isPlainObject(l) && typeof l.title === 'string' && toSitePath(l.url))
    .slice(0, 3)
    .map((l) => ({ title: l.title.slice(0, 120), url: l.url }));
}

/** Returns a cleaned message from the widget, or null to ignore it. */
function parseWidgetMessage(data) {
  if (!isPlainObject(data) || data.source !== FROM_WIDGET || typeof data.type !== 'string') return null;
  switch (data.type) {
    case 'ready':
    case 'close':
    case 'reset':
      return { type: data.type };
    case 'state':
      return typeof data.open === 'boolean' ? { type: 'state', open: data.open } : null;
    case 'ask':
      if (typeof data.id !== 'string' || !/^[A-Za-z0-9_-]{1,40}$/.test(data.id)) return null;
      if (typeof data.text !== 'string') return null;
      if (!data.text.trim() || data.text.length > MAX_MESSAGE_CHARS) return null;
      return { type: 'ask', id: data.id, text: data.text.trim() };
    case 'navigate': {
      const path = toSitePath(data.url);
      return path ? { type: 'navigate', path } : null;
    }
    default:
      return null;
  }
}

// --------------------------------------------------------------- elements ---
/** $w element if it exists on this page, else null. */
function getElement(selector) {
  try {
    const el = $w(selector);
    return el && typeof el.type === 'string' && el.type ? el : null;
  } catch (e) {
    return null;
  }
}

function currentLanguage() {
  try {
    const lang = wixWindowFrontend.multilingual && wixWindowFrontend.multilingual.currentLanguage;
    return typeof lang === 'string' ? lang : undefined;
  } catch (e) {
    return undefined;
  }
}

/** Mobile phones get the mobile pair; desktops and tablets the pinned pair. */
function pairsForDevice() {
  let formFactor;
  try {
    formFactor = wixWindowFrontend.formFactor;
  } catch (e) {
    formFactor = undefined;
  }
  if (formFactor === 'Mobile') return PAIRS.filter((p) => !p.pinned);
  if (formFactor === 'Desktop' || formFactor === 'Tablet') return PAIRS.filter((p) => p.pinned);
  return PAIRS;
}

/** Runs a Velo element call that may return a Promise; never throws. */
function quietly(fn) {
  try {
    return Promise.resolve(fn()).catch(() => undefined);
  } catch (e) {
    return Promise.resolve();
  }
}

// ------------------------------------------------------------------ wiring ---
const wired = [];

function postTo(frame, msg) {
  try {
    frame.postMessage(Object.assign({ source: TO_WIDGET }, msg));
  } catch (e) {
    /* element not ready or removed */
  }
}

function broadcast(msg) {
  wired.forEach((w) => postTo(w.frame, msg));
}

/** Tell a pinned chat how tall the visible window is, so it stays on screen. */
function sendViewport(pair) {
  if (!pair.pinned) return;
  let p;
  try {
    p = wixWindowFrontend.getBoundingRect();
  } catch (e) {
    return;
  }
  Promise.resolve(p)
    .then((r) => {
      const h = r && r.window && r.window.height;
      if (typeof h === 'number' && h > 0) postTo(pair.frame, { type: 'viewport', height: Math.round(h) });
    })
    .catch(() => undefined);
}

function showEl(el, pinned) {
  return quietly(() => (pinned ? el.show() : el.expand()));
}

function hideEl(el, pinned) {
  return quietly(() => (pinned ? el.hide() : el.collapse()));
}

/**
 * Open or close the chat. With a launcher Button the Embed element is shown
 * only while open; opts.focus moves keyboard focus into the chat (after a
 * click on the Button), opts.focusLauncher returns it to the Button.
 */
async function setOpen(pair, open, opts) {
  const o = opts || {};
  state.open = open;
  saveState();
  if (!pair.launcher) return; // the widget draws its own launcher
  if (open) {
    await Promise.all([showEl(pair.frame, pair.pinned), hideEl(pair.launcher, pair.pinned)]);
    if (!pair.pinned) await quietly(() => pair.frame.scrollTo()); // bring the chat into view
    sendViewport(pair);
    if (o.focus) postTo(pair.frame, { type: 'focus' });
  } else {
    await Promise.all([hideEl(pair.frame, pair.pinned), showEl(pair.launcher, pair.pinned)]);
    if (o.focusLauncher) quietly(() => pair.launcher.focus());
  }
}

async function ask(pair, id, text) {
  if (handled.has(id)) return;
  handled.add(id);
  const now = Date.now();
  if (busy || now - lastAskAt < MIN_GAP_MS) {
    postTo(pair.frame, { type: 'reply', id, answer: 'Please wait a moment before sending another question.', links: [], error: true });
    return;
  }
  busy = true;
  lastAskAt = now;
  state.transcript.push({ from: 'user', text, links: [] });

  let res;
  try {
    res = await askNavBot({
      message: text,
      history: state.history.slice(-MAX_HISTORY),
      lang: currentLanguage(),
      visitorId: visitorId(),
    });
  } catch (err) {
    // The backend call failed: network problem, Wix timeout (504) / throttling (429),
    // or the backend code could not load (see Wix Logs).
    console.error('navBot call failed', err);
    res = { answer: SERVER_FAILED_TEXT, links: [], error: true };
  }
  busy = false;

  const answer = isPlainObject(res) && typeof res.answer === 'string' ? res.answer : 'Sorry, something went wrong.';
  const error = !isPlainObject(res) || res.error === true;
  const links = error ? [] : cleanLinks(res.links);

  if (error) {
    state.transcript.pop(); // keep failed questions out of the restored chat
  } else {
    // noHistory: a canned or declined reply. Shown, but not sent back as context
    // with later questions (a declined question would be declined again).
    if (res.noHistory !== true) {
      state.history.push({ role: 'user', content: text }, { role: 'assistant', content: answer });
      state.history = state.history.slice(-MAX_HISTORY);
    }
    state.transcript.push({ from: 'bot', text: answer, links });
    state.transcript = state.transcript.slice(-MAX_TRANSCRIPT);
  }
  saveState();
  postTo(pair.frame, { type: 'reply', id, answer, links, error });
}

function wire(cfg) {
  const frame = getElement(cfg.frame);
  if (!frame || typeof frame.onMessage !== 'function') return;
  const launcherEl = getElement(cfg.launcher);
  const launcher = launcherEl && typeof launcherEl.onClick === 'function' ? launcherEl : null;
  const pair = { frame, launcher, pinned: cfg.pinned };
  wired.push(pair);

  if (launcher) {
    // Two-element mode: the Button opens the chat, the Embed element shows only when open.
    if (state.open) {
      showEl(frame, pair.pinned);
      hideEl(launcher, pair.pinned);
    } else {
      hideEl(frame, pair.pinned);
      showEl(launcher, pair.pinned);
    }
    launcher.onClick(() => setOpen(pair, true, { focus: true }));
  }

  frame.onMessage((event) => {
    const msg = parseWidgetMessage(event && event.data);
    if (!msg) return; // ignore anything we don't recognise
    switch (msg.type) {
      case 'ready':
        postTo(frame, {
          type: 'init',
          externalLauncher: !!launcher,
          open: launcher ? true : state.open,
          pinned: pair.pinned,
          transcript: state.transcript,
          maxChars: MAX_MESSAGE_CHARS,
        });
        sendViewport(pair);
        break;
      case 'state':
        state.open = msg.open;
        saveState();
        if (msg.open) sendViewport(pair);
        break;
      case 'close':
        setOpen(pair, false, { focusLauncher: true });
        break;
      case 'reset':
        state = { history: [], transcript: [], open: state.open };
        saveState();
        broadcast({ type: 'reset' });
        break;
      case 'ask':
        sendViewport(pair);
        ask(pair, msg.id, msg.text);
        break;
      case 'navigate':
        setOpen(pair, false); // let the visitor see the page
        // Does nothing in Preview: test link buttons on the published site.
        wixLocationFrontend.to(msg.path);
        break;
      default:
        break;
    }
  });
}

$w.onReady(() => {
  pairsForDevice().forEach(wire);
});
