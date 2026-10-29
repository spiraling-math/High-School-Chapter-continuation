// PLAN B for backend/claudeClient.js  (no npm package needed)
// -----------------------------------------------------------------------------
// Use this ONLY if @anthropic-ai/sdk will not install or load in Wix.
// Paste this whole file over the content of backend/claudeClient.js.
// It calls the same Claude Messages API with Wix's built-in wix-fetch.
// -----------------------------------------------------------------------------
import { fetch } from 'wix-fetch';
import { isSpendLimitError } from 'backend/navBotCore';

const API_URL = 'https://api.anthropic.com/v1/messages';
const API_VERSION = '2026-10-21';
const DEFAULT_TIMEOUT_MS = 11000; // used only when the caller passes no timeout

function kindForStatus(status, apiError) {
  // A spend limit arrives as a 400 (a limit you set) or a 429 (the tier's monthly cap).
  if (isSpendLimitError(status, apiError)) return 'spend_limit';
  if (status === 401) return 'auth';
  if (status === 402) return 'billing'; // billing or payment problem
  if (status === 403) return 'permission';
  if (status === 404) return 'not_found';
  if (status === 400) return 'bad_request';
  if (status === 429) return 'rate_limited';
  if (status >= 500) return 'server'; // 500 / 529 overloaded
  return 'api';
}

export async function createMessage(apiKey, params, opts) {
  const timeoutMs = (opts && opts.timeoutMs) || DEFAULT_TIMEOUT_MS;
  // The SDK's `betas` field is really the anthropic-beta header.
  const body = Object.assign({}, params);
  const betas = body.betas;
  delete body.betas;

  const headers = {
    'content-type': 'application/json',
    'x-api-key': apiKey,
    'anthropic-version': API_VERSION,
  };
  if (Array.isArray(betas) && betas.length) headers['anthropic-beta'] = betas.join(',');

  let timer;
  const timeout = new Promise((_, rejectFn) => {
    timer = setTimeout(() => rejectFn({ kind: 'timeout', message: 'Claude API timed out' }), timeoutMs);
  });

  let res;
  try {
    res = await Promise.race([fetch(API_URL, { method: 'post', headers, body: JSON.stringify(body) }), timeout]);
  } catch (err) {
    if (err && err.kind) throw err;
    throw { kind: 'network', message: String((err && err.message) || err) };
  } finally {
    clearTimeout(timer);
  }

  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }
  if (!res.ok) {
    const apiError = (data && data.error) || {};
    throw {
      kind: kindForStatus(res.status, apiError),
      status: res.status,
      type: apiError.type,
      message: String(apiError.message || res.statusText || 'HTTP ' + res.status),
    };
  }
  return data;
}
