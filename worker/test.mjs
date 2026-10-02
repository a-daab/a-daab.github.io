// Run: node worker/test.mjs   — exercises the Worker with a mock D1 and a mocked mail API (no network).
import worker from './src/index.js';
import assert from 'node:assert/strict';

const rows = new Map();
const DB = { prepare(sql) { return { _b: [], bind(...a) { this._b = a; return this; },
  async run() { const [name, email, lc] = this._b; if (rows.has(lc)) return { meta: { changes: 0 } }; rows.set(lc, { name, email }); return { meta: { changes: 1 } }; },
  async first() { return { n: rows.size }; } }; } };
const sent = [];
globalThis.fetch = async (url, init) => { if (String(url).includes('resend')) { sent.push(JSON.parse(init.body)); return new Response('{}', { status: 200 }); } return new Response('{"success":true}'); };
const env = { DB, ALLOWED_ORIGINS: 'https://www.yogamaty.com,https://yogamaty.com', ALLIES_TO: 'allies@example.org', WHOLESALE_TO: 'ws@example.org', MAIL_FROM: 'x@y.z', RESEND_API_KEY: 'k', PETITION_THRESHOLD: '3', MIN_FILL_SECONDS: '3' };
const ORIGIN = 'https://www.yogamaty.com';
const old = () => String(Date.now() - 10000);
const post = (path, body, origin = ORIGIN) => worker.fetch(new Request('https://api.yogamaty.com' + path, { method: 'POST', headers: { 'Content-Type': 'application/json', ...(origin ? { Origin: origin } : {}) }, body: JSON.stringify(body) }), env, {});
const j = async (r) => ({ s: r.status, ...(await r.json()) });

const pet = { name: 'A B', email: 'A@Example.com', location: 'New Haven, US', consent: true, t: old() };
let r = await j(await post('/petition', pet)); assert.equal(r.status, 'signed');
r = await j(await post('/petition', { ...pet, email: 'a@example.COM' })); assert.equal(r.status, 'already_signed', 'dedupe is case-insensitive');
assert.equal(rows.size, 1);
r = await j(await post('/petition', { ...pet, email: 'bad' })); assert.equal(r.s, 422); assert.ok(r.errors.email);
r = await j(await post('/petition', { ...pet, email: 'c@x.org', consent: false })); assert.equal(r.s, 422); assert.ok(r.errors.consent);
r = await j(await post('/petition', { ...pet, email: 'd@x.org', t: String(Date.now()) })); assert.equal(r.s, 403, 'too fast');
r = await j(await post('/petition', { ...pet, email: 'e@x.org', website: 'http://spam' })); assert.equal(r.s, 200); assert.equal(rows.size, 1, 'honeypot is not stored');
r = await j(await post('/petition', pet, 'https://evil.example')); assert.equal(r.s, 403, 'CORS locked');
r = await j(await post('/petition', pet, null)); assert.equal(r.s, 403, 'no Origin rejected');

let c = await j(await worker.fetch(new Request('https://api.yogamaty.com/petition/count', { headers: { Origin: ORIGIN } }), env, {}));
assert.equal(c.visible, false); assert.equal(c.count, undefined, 'count hidden below threshold');
await post('/petition', { ...pet, email: 'p2@x.org' }); await post('/petition', { ...pet, email: 'p3@x.org' });
c = await j(await worker.fetch(new Request('https://api.yogamaty.com/petition/count', { headers: { Origin: ORIGIN } }), env, {}));
assert.equal(c.visible, true); assert.equal(c.count, 3);

const words = (n) => Array(n).fill('w').join(' ');
const ally = { first_name: 'Ada', last_name: 'L', email: 'ada@x.org', company: 'Co', skills: ['Law and policy', 'Not a skill'], statement: words(250), consent: true, t: old() };
r = await j(await post('/allies', ally)); assert.equal(r.s, 200);
assert.equal(sent.length, 1); assert.equal(sent[0].to[0], 'allies@example.org'); assert.equal(sent[0].reply_to, 'ada@x.org');
assert.ok(!sent[0].text.includes('Not a skill'), 'unknown skills dropped');
r = await j(await post('/allies', { ...ally, statement: words(251) })); assert.equal(r.s, 422); assert.ok(r.errors.statement, '251 words rejected server-side');
r = await j(await post('/allies', { ...ally, skills: [], skills_other: '' })); assert.ok(r.errors.skills);
r = await j(await post('/allies', { ...ally, first_name: 'Ada\r\nBcc: x@evil', link: 'javascript:alert(1)' })); assert.ok(r.errors.link);

const ws = { name: 'N', phone: '203-555-0100', email: 'n@x.org', business: 'Studio', consent: true, t: old() };
r = await j(await post('/wholesale', ws)); assert.equal(r.s, 200); assert.equal(sent.at(-1).to[0], 'ws@example.org');
r = await j(await post('/wholesale', { ...ws, phone: '12' })); assert.ok(r.errors.phone);

const pre = await worker.fetch(new Request('https://api.yogamaty.com/petition', { method: 'OPTIONS', headers: { Origin: ORIGIN } }), env, {});
assert.equal(pre.status, 204); assert.equal(pre.headers.get('Access-Control-Allow-Origin'), ORIGIN);
assert.equal((await worker.fetch(new Request('https://api.yogamaty.com/petition', { method: 'OPTIONS', headers: { Origin: 'https://evil.example' } }), env, {})).status, 403);
console.log('worker: all checks passed');
