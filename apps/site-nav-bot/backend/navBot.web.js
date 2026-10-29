// backend/navBot.web.js
// -----------------------------------------------------------------------------
// Velo web module: the ONE backend function the website calls.
//   askNavBot({ message, history, lang })  ->  { answer, links: [{title, url}], noHistory? }
//                                          or  { answer, links: [], error: true }
// Callable by anyone who loads the site, so every input is checked here and
// nothing secret (API key, raw errors, stack traces) is ever returned.
// Details go to console.* -> visible in Wix Logs (Developer Tools).
// -----------------------------------------------------------------------------
import { Permissions, webMethod } from 'wix-web-module';
import { secrets } from 'wix-secrets-backend.v2';
import { elevate } from 'wix-auth';
import {
  buildSystemPrompt,
  buildOutputSchema,
  buildRequestParams,
  normaliseInput,
  interpretResponse,
  fallbackReply,
  errorReply,
  toPublicReply,
  createRateLimiter,
  indexSiteMap,
  missingRuleKeys,
  summariseUsage,
  remainingMs,
  TEXT,
} from 'backend/navBotCore';
import { SITE_MAP, SITE_FACTS, FALLBACK_LINK_KEYS } from 'backend/siteMap';
import { createMessage } from 'backend/claudeClient';

// ----- Settings you may change ------------------------------------------------
// Model. 'claude-haiku-5-5' ($0.10 / $0.50 per million tokens) is fast, cheap
// and a good fit for pure navigation. 'claude-opus-5-5' ($4 / $20) is ~40x
// dearer and more capable. Switching needs no other edit: the refusal-fallback
// option is sent to Opus only and dropped automatically for Haiku.
const MODEL = 'claude-haiku-5-5';
// Thinking is adaptive (on by default) on both models; 'low' effort = fast and cheap.
const EFFORT = 'low';
// Cap on output per attempt (thinking + JSON answer).
// Worst case: 2048 x $0.50 / 1M = ~$0.001 of output per question on Haiku 5.5
// (~$0.04 on Opus 5.5, where a refusal fallback can add a second attempt - see
// README "Model choice and cost").
const MAX_TOKENS = 2048;
// Wix stops a web method after ~14 s, so everything must finish sooner.
// The overall budget is counted from the start of the call.
const OVERALL_DEADLINE_MS = 12500;
const CLAUDE_TIMEOUT_MS = 11000; // longest single Claude call
const MIN_CLAUDE_BUDGET_MS = 5000; // less time than this left: don't start a (billed) call
// Light abuse limits (per backend container, reset on restart - see README).
// The per-visitor part is keyed on an id the browser chooses, so it stops
// casual over-use only; the Console spend limit is the hard cap.
const LIMITS = {
  perVisitorPerMinute: 6,
  perVisitorPerHour: 30,
  globalPerMinute: 40,
  globalPerDay: 600,
};
const SECRET_NAME = 'ANTHROPIC_API_KEY';
const SECRET_CACHE_MS = 10 * 60 * 1000; // re-read the key every 10 minutes (and after a key error)
// -----------------------------------------------------------------------------

const limiter = createRateLimiter(LIMITS);

// The prompt, schema and page index are built on first use, not at import, so a
// mistake in siteMap.js is logged as "SITE MAP ERROR" and visitors still get a
// friendly reply. Once built they are byte-identical every request, so prompt
// caching works.
let built = null;

function getBuilt() {
  if (built) return built;
  const index = indexSiteMap(SITE_MAP);
  const systemPrompt = buildSystemPrompt(SITE_MAP, SITE_FACTS);
  const schema = buildOutputSchema(SITE_MAP);
  const missing = missingRuleKeys(SITE_MAP, FALLBACK_LINK_KEYS);
  if (missing.length) {
    console.warn('navBot: siteMap.js has no page for key(s) the reply rules use: ' + missing.join(', '));
  }
  built = { index, systemPrompt, schema };
  return built;
}

const getSecretValueElevated = elevate(secrets.getSecretValue);
let keyCache = { value: null, at: 0 };

async function getApiKey() {
  const now = Date.now();
  if (keyCache.value && now - keyCache.at < SECRET_CACHE_MS) return keyCache.value;
  const r = await getSecretValueElevated(SECRET_NAME);
  // Velo examples return the string itself; the SDK schema documents { value }.
  const value = typeof r === 'string' ? r : r && typeof r.value === 'string' ? r.value : '';
  if (!value.trim()) throw { kind: 'secret', message: 'Secret ' + SECRET_NAME + ' is missing or empty' };
  keyCache = { value: value.trim(), at: now };
  return keyCache.value;
}

/** After a key error, read the secret again on the next question (a fixed key works at once). */
function forgetApiKey() {
  keyCache = { value: null, at: 0 };
}

/**
 * Per-visitor key for the rate limit: a random id that masterPage.js keeps in
 * the visitor's browser and sends with every question (already validated by
 * normaliseInput). null when absent: the global limits still apply.
 */
function visitorKeyOf(input) {
  return input.visitorId ? 'v:' + input.visitorId : null;
}

function withDeadline(promise, ms) {
  let timer;
  const deadline = new Promise((_, rejectFn) => {
    timer = setTimeout(() => rejectFn({ kind: 'deadline', message: 'overall deadline exceeded' }), ms);
  });
  return Promise.race([promise, deadline]).finally(() => clearTimeout(timer));
}

function logUsage(response, outcome, ms) {
  console.log('navBot', JSON.stringify(Object.assign({ outcome, ms }, summariseUsage(response, MODEL))));
}

function logError(err) {
  const e = err || {};
  const line = { kind: e.kind || 'unexpected', status: e.status, type: e.type, message: String(e.message || e) };
  if (e.kind === 'spend_limit') {
    console.error('navBot: SPEND LIMIT REACHED - raise the limit in the Claude Console, or wait for the monthly reset', line);
  } else if (e.kind === 'billing') {
    console.error('navBot: BILLING PROBLEM (402) - check credits and payment in the Claude Console', line);
  } else if (e.kind === 'auth' || e.kind === 'secret' || e.kind === 'permission') {
    console.error('navBot: API KEY PROBLEM', line);
  } else {
    console.error('navBot: error', line);
  }
}

function safeFallback() {
  try {
    return toPublicReply(fallbackReply(SITE_MAP, FALLBACK_LINK_KEYS));
  } catch (e) {
    return errorReply(TEXT.fallback);
  }
}

export const askNavBot = webMethod(Permissions.Anyone, async (payload) => {
  const started = Date.now();
  let stage = 'input';
  try {
    // 1. Cheap checks first: nothing below runs for a bad payload.
    const input = normaliseInput(payload);
    if (!input.ok) {
      console.warn('navBot: rejected input', input.code);
      return input.reply;
    }

    // 2. Prompt, schema and page index (built once).
    stage = 'sitemap';
    const b = getBuilt();
    stage = 'run';

    // 3. Light rate limit.
    const verdict = limiter.check(visitorKeyOf(input));
    if (!verdict.allowed) {
      console.warn('navBot: rate limited', verdict.reason);
      return errorReply(verdict.reason === 'global' ? TEXT.busy : TEXT.rateLimited);
    }

    // 4. Ask Claude within what is left of the overall time budget.
    const apiKey = await getApiKey();
    const left = remainingMs(started, Date.now(), OVERALL_DEADLINE_MS);
    if (left < MIN_CLAUDE_BUDGET_MS) {
      throw { kind: 'deadline', message: 'only ' + left + ' ms left before the Wix time limit; Claude not called' };
    }
    const params = buildRequestParams({
      model: MODEL,
      effort: EFFORT,
      maxTokens: MAX_TOKENS,
      systemPrompt: b.systemPrompt,
      schema: b.schema,
      messages: input.messages,
    });
    const response = await withDeadline(
      createMessage(apiKey, params, { timeoutMs: Math.min(CLAUDE_TIMEOUT_MS, left - 1500) }),
      left
    );

    // 5. Validate: only site-map links can come back.
    const result = interpretResponse(response, SITE_MAP, FALLBACK_LINK_KEYS, b.index);
    logUsage(response, result.outcome, Date.now() - started);
    return toPublicReply(result.reply);
  } catch (err) {
    if (stage === 'sitemap') {
      console.error(
        'navBot: SITE MAP ERROR - fix backend/siteMap.js; until then every visitor gets the fallback reply',
        String((err && err.message) || err)
      );
    } else {
      logError(err);
      if (err && (err.kind === 'auth' || err.kind === 'permission')) forgetApiKey();
    }
    return safeFallback();
  }
});
