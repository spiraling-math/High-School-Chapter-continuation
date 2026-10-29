// backend/claudeClient.js
// -----------------------------------------------------------------------------
// Calls the Claude Messages API with the official Anthropic SDK
// (@anthropic-ai/sdk, installed with the Wix editor's Package Manager).
//
// Exposes ONE function, createMessage(apiKey, params, {timeoutMs}), which
// resolves to the API response or throws a plain {kind, status, type, message}
// object (never the API key).
//
// PLAN B: if the SDK will not install or load in Wix, replace the WHOLE content
// of this file with ../alternatives/claudeClient.fetch.js (same function, uses
// Wix's built-in wix-fetch instead). Nothing else needs to change.
// -----------------------------------------------------------------------------
import Anthropic from '@anthropic-ai/sdk';
import { fetch as wixFetch } from 'wix-fetch';
import { isSpendLimitError } from 'backend/navBotCore';

// Wix documents no global fetch in backend code, so we hand the SDK Wix's own
// fetch. If the SDK misbehaves with it (see README troubleshooting), try false.
const USE_WIX_FETCH = true;
const DEFAULT_TIMEOUT_MS = 11000; // used only when the caller passes no timeout

let cached = null; // { apiKey, client } - one client per backend container

function getClient(apiKey) {
  if (!cached || cached.apiKey !== apiKey) {
    const options = {
      apiKey, // from the Wix Secrets Manager, never from frontend code
      timeout: DEFAULT_TIMEOUT_MS, // ms per attempt (SDK default is 10 minutes)
      maxRetries: 0, // SDK default is 2; Wix cuts the web method off at ~14 s, so no time to retry
    };
    if (USE_WIX_FETCH) options.fetch = wixFetch;
    cached = { apiKey, client: new Anthropic(options) };
  }
  return cached.client;
}

/** The `error` object of the API's error body: {type, message, details?}. */
function apiErrorOf(err) {
  const body = err && err.error;
  return body && typeof body === 'object' && body.error && typeof body.error === 'object' ? body.error : {};
}

/** Map SDK errors to a small plain object. Subclasses are checked before parents. */
function normaliseError(err) {
  const apiError = apiErrorOf(err);
  const status = err && err.status;
  const base = { status, type: (err && err.type) || apiError.type };
  const apiMessage = typeof apiError.message === 'string' ? apiError.message : String((err && err.message) || err);
  if (err instanceof Anthropic.APIConnectionTimeoutError) return Object.assign(base, { kind: 'timeout', message: 'Claude API timed out' });
  if (err instanceof Anthropic.APIConnectionError) return Object.assign(base, { kind: 'network', message: String(err.message) });
  // A spend limit arrives as a 400 (a limit you set) or a 429 (the tier's monthly cap).
  if (isSpendLimitError(status, apiError)) return Object.assign(base, { kind: 'spend_limit', message: apiMessage });
  if (err instanceof Anthropic.RateLimitError) return Object.assign(base, { kind: 'rate_limited', message: apiMessage });
  if (err instanceof Anthropic.AuthenticationError) return Object.assign(base, { kind: 'auth', message: 'ANTHROPIC_API_KEY secret is invalid or revoked (401)' });
  if (err instanceof Anthropic.PermissionDeniedError) return Object.assign(base, { kind: 'permission', message: apiMessage });
  if (err instanceof Anthropic.NotFoundError) return Object.assign(base, { kind: 'not_found', message: 'Model not found (404) - check MODEL in navBot.web.js' });
  if (err instanceof Anthropic.BadRequestError) return Object.assign(base, { kind: 'bad_request', message: apiMessage });
  if (err instanceof Anthropic.InternalServerError) return Object.assign(base, { kind: 'server', message: 'Anthropic server error / overloaded' });
  if (err instanceof Anthropic.APIError) {
    // 402 billing_error = billing or payment problem; 413 = request too large
    const kind = status === 402 ? 'billing' : 'api';
    return Object.assign(base, { kind, message: apiMessage });
  }
  return { kind: 'unexpected', message: String((err && err.message) || err) };
}

export async function createMessage(apiKey, params, opts) {
  const timeoutMs = (opts && opts.timeoutMs) || DEFAULT_TIMEOUT_MS;
  const client = getClient(apiKey);
  try {
    // `betas` in params becomes the anthropic-beta header (server-side refusal fallback)
    return await client.beta.messages.create(params, { timeout: timeoutMs });
  } catch (err) {
    throw normaliseError(err);
  }
}
