/**
 * YogaMaty forms endpoint — one Cloudflare Worker for three forms (Specification §5.3, §6, §7).
 *
 *   POST /allies      allies application      -> emailed to ALLIES_TO,    nothing stored
 *   POST /wholesale   wholesale inquiry       -> emailed to WHOLESALE_TO, nothing stored
 *   POST /petition    petition signature      -> stored in D1 (deduped on lower-cased email)
 *   GET  /petition/count                      -> { visible, count? }; the count is withheld until PETITION_THRESHOLD
 *
 * Defenses: CORS locked to ALLOWED_ORIGINS, honeypot, minimum-fill-time check, Cloudflare Turnstile,
 * per-IP per-minute rate limit, and server-side validation. IP addresses are used transiently and never stored.
 */

const JSON_HEADERS = { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' };

const SKILLS = new Set([
  'Software engineering', 'Security / cryptography', 'Distributed ledgers', 'Product / UX design', 'Data and analytics',
  'Supply chain and logistics', 'Law and policy', 'Human rights / anti-trafficking', 'Partnerships and fundraising', 'Communications',
]);

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/* ----------------------------- helpers ----------------------------- */
function allowedOrigins(env) {
  return (env.ALLOWED_ORIGINS || '').split(',').map((s) => s.trim()).filter(Boolean);
}

function cors(request, env) {
  const origin = request.headers.get('Origin');
  const ok = origin && allowedOrigins(env).includes(origin);
  return {
    ok,
    headers: ok
      ? { 'Access-Control-Allow-Origin': origin, 'Vary': 'Origin', 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400' }
      : { 'Vary': 'Origin' },
  };
}

function respond(body, status, extra) {
  return new Response(JSON.stringify(body), { status, headers: { ...JSON_HEADERS, ...extra } });
}

const str = (v, max) => (typeof v === 'string' ? v.trim().replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').slice(0, max) : '');
const wordCount = (s) => (s.match(/\S+/g) || []).length;

function validUrl(s) {
  try { const u = new URL(s); return u.protocol === 'https:' || u.protocol === 'http:'; } catch { return false; }
}

/** Header-injection safe single-line value */
const oneLine = (s) => s.replace(/[\r\n]+/g, ' ');

/* ----------------------------- validation ----------------------------- */
function validateAllies(b) {
  const errors = {};
  const v = {
    first_name: str(b.first_name, 80), last_name: str(b.last_name, 80), email: str(b.email, 200), company: str(b.company, 160),
    statement: str(b.statement, 4000), link: str(b.link, 300), country: str(b.country, 120), skills_other: str(b.skills_other, 200),
    skills: Array.isArray(b.skills) ? b.skills.filter((s) => SKILLS.has(s)) : [],
  };
  for (const k of ['first_name', 'last_name', 'company', 'statement']) if (!v[k]) errors[k] = 'Required';
  if (!EMAIL_RE.test(v.email)) errors.email = 'Valid email required';
  if (v.statement && wordCount(v.statement) > 250) errors.statement = 'Maximum 250 words';
  if (v.link && !validUrl(v.link)) errors.link = 'Must be a web address';
  if (!v.skills.length && !v.skills_other) errors.skills = 'Choose a skill or add your own';
  if (b.consent !== true) errors.consent = 'Consent required';
  return { v, errors };
}

function validateWholesale(b) {
  const errors = {};
  const v = { name: str(b.name, 120), phone: str(b.phone, 40), email: str(b.email, 200), business: str(b.business, 160), note: str(b.note, 1500) };
  for (const k of ['name', 'business']) if (!v[k]) errors[k] = 'Required';
  if (v.phone.replace(/\D/g, '').length < 7) errors.phone = 'Valid phone number required';
  if (!EMAIL_RE.test(v.email)) errors.email = 'Valid email required';
  if (b.consent !== true) errors.consent = 'Consent required';
  return { v, errors };
}

function validatePetition(b) {
  const errors = {};
  const v = { name: str(b.name, 120), email: str(b.email, 200), location: str(b.location, 120) };
  for (const k of ['name', 'location']) if (!v[k]) errors[k] = 'Required';
  if (!EMAIL_RE.test(v.email)) errors.email = 'Valid email required';
  if (b.consent !== true) errors.consent = 'Consent required';
  return { v, errors };
}

/* ----------------------------- anti-abuse ----------------------------- */
async function verifyTurnstile(token, ip, env) {
  if (!env.TURNSTILE_SECRET) return true;            // not configured: skip (set the secret in production)
  if (!token) return false;
  const form = new FormData();
  form.append('secret', env.TURNSTILE_SECRET);
  form.append('response', token);
  if (ip) form.append('remoteip', ip);
  try {
    const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body: form });
    const j = await r.json();
    return j.success === true;
  } catch { return false; }
}

function looksAutomated(b, env) {
  if (b.website) return true;                          // honeypot field was filled
  const min = Number(env.MIN_FILL_SECONDS || 3) * 1000;
  const t = Number(b.t);
  if (!t || !Number.isFinite(t)) return true;
  const elapsed = Date.now() - t;
  return elapsed < min || elapsed > 1000 * 60 * 60 * 12;
}

/* ----------------------------- email ----------------------------- */
async function sendMail(env, { to, subject, text, replyTo }) {
  if (!env.RESEND_API_KEY || !to) throw new Error('mail not configured');
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: env.MAIL_FROM, to: [to], subject: oneLine(subject), text, reply_to: replyTo }),
  });
  if (!r.ok) throw new Error(`mail provider ${r.status}`);
}

const alliesText = (v) => [
  `New allies application`,
  ``,
  `Name:      ${oneLine(v.first_name)} ${oneLine(v.last_name)}`,
  `Email:     ${v.email}`,
  `Company / title: ${oneLine(v.company)}`,
  `Skills:    ${[...v.skills, v.skills_other].filter(Boolean).join('; ')}`,
  `Link:      ${v.link || '—'}`,
  `Country / time zone: ${oneLine(v.country) || '—'}`,
  ``,
  `Statement (${wordCount(v.statement)} words):`,
  v.statement,
  ``,
  `— Sent from yogamaty.com. Consent to the privacy policy was given. Reply to this email to answer the applicant`,
  `   (request a résumé, or send a kind decline). Nothing is stored on the website.`,
].join('\n');

const wholesaleText = (v) => [
  `New wholesale / studio inquiry`,
  ``,
  `Name:     ${oneLine(v.name)}`,
  `Business: ${oneLine(v.business)}`,
  `Phone:    ${oneLine(v.phone)}`,
  `Email:    ${v.email}`,
  ``,
  `Note:`,
  v.note || '—',
  ``,
  `— Sent from yogamaty.com. Consent to the privacy policy was given. Nothing is stored on the website.`,
].join('\n');

/* ----------------------------- routes ----------------------------- */
async function readBody(request) {
  const len = Number(request.headers.get('Content-Length') || 0);
  if (len > 20000) return null;
  try { const b = await request.json(); return b && typeof b === 'object' ? b : null; } catch { return null; }
}

async function handleForm(kind, request, env, ctx, c) {
  const ip = request.headers.get('CF-Connecting-IP') || '';
  if (env.RL) {
    const { success } = await env.RL.limit({ key: ip || 'unknown' });
    if (!success) return respond({ ok: false, error: 'rate_limited' }, 429, c.headers);
  }
  const body = await readBody(request);
  if (!body) return respond({ ok: false, error: 'bad_request' }, 400, c.headers);

  if (looksAutomated(body, env)) {
    // Pretend success to a honeypot hit, so bots learn nothing; a too-fast human gets a retry message.
    if (body.website) return respond({ ok: true }, 200, c.headers);
    return respond({ ok: false, error: 'too_fast' }, 403, c.headers);
  }
  if (!(await verifyTurnstile(str(body.turnstile, 4096), ip, env))) return respond({ ok: false, error: 'turnstile' }, 403, c.headers);

  if (kind === 'allies') {
    const { v, errors } = validateAllies(body);
    if (Object.keys(errors).length) return respond({ ok: false, errors }, 422, c.headers);
    try {
      await sendMail(env, { to: env.ALLIES_TO, subject: `Allies application — ${v.first_name} ${v.last_name}`, text: alliesText(v), replyTo: v.email });
    } catch { return respond({ ok: false, error: 'mail_failed' }, 502, c.headers); }
    return respond({ ok: true }, 200, c.headers);
  }

  if (kind === 'wholesale') {
    const { v, errors } = validateWholesale(body);
    if (Object.keys(errors).length) return respond({ ok: false, errors }, 422, c.headers);
    try {
      await sendMail(env, { to: env.WHOLESALE_TO, subject: `Wholesale inquiry — ${v.business}`, text: wholesaleText(v), replyTo: v.email });
    } catch { return respond({ ok: false, error: 'mail_failed' }, 502, c.headers); }
    return respond({ ok: true }, 200, c.headers);
  }

  // petition
  const { v, errors } = validatePetition(body);
  if (Object.keys(errors).length) return respond({ ok: false, errors }, 422, c.headers);
  const emailLc = v.email.toLowerCase();
  const res = await env.DB.prepare(
    'INSERT OR IGNORE INTO signatures (name, email, email_lc, location, consent, created_at) VALUES (?1, ?2, ?3, ?4, 1, ?5)'
  ).bind(v.name, v.email, emailLc, v.location, new Date().toISOString()).run();
  const inserted = (res.meta && res.meta.changes) > 0;
  return respond({ ok: true, status: inserted ? 'signed' : 'already_signed' }, 200, c.headers);
}

async function handleCount(env, c) {
  const threshold = Number(env.PETITION_THRESHOLD || 500);
  const row = await env.DB.prepare('SELECT COUNT(*) AS n FROM signatures').first();
  const n = row ? row.n : 0;
  const body = n >= threshold ? { visible: true, count: n } : { visible: false };
  return respond(body, 200, { ...c.headers, 'Cache-Control': 'public, max-age=300' });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const c = cors(request, env);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: c.ok ? 204 : 403, headers: c.headers });
    }
    // Browsers always send Origin on cross-origin POSTs; reject anything not from our own pages.
    if (request.method === 'POST' && !c.ok) return respond({ ok: false, error: 'forbidden' }, 403, c.headers);

    try {
      if (request.method === 'GET' && url.pathname === '/petition/count') return await handleCount(env, c);
      if (request.method === 'POST') {
        const kind = { '/allies': 'allies', '/wholesale': 'wholesale', '/petition': 'petition' }[url.pathname];
        if (kind) return await handleForm(kind, request, env, ctx, c);
      }
      if (request.method === 'GET' && url.pathname === '/') return respond({ ok: true, service: 'yogamaty-api' }, 200, c.headers);
      return respond({ ok: false, error: 'not_found' }, 404, c.headers);
    } catch (e) {
      return respond({ ok: false, error: 'server_error' }, 500, c.headers);
    }
  },
};
