# Forms Worker (api.yogamaty.com)

One Cloudflare Worker for the allies application, wholesale inquiry and petition. Free tier is far above this site's volume.

```
cd worker
npx wrangler d1 create yogamaty-petition            # copy the database_id into wrangler.toml
npx wrangler d1 execute yogamaty-petition --remote --file=schema.sql
npx wrangler secret put RESEND_API_KEY              # or adapt sendMail() for Postmark
npx wrangler secret put TURNSTILE_SECRET            # from Cloudflare dashboard → Turnstile (add site yogamaty.com)
npx wrangler deploy
```

Then add the custom domain `api.yogamaty.com` to the Worker (dashboard → Workers → Triggers), verify your sending domain in Resend, and put the Turnstile **site** key and `https://api.yogamaty.com` in `../src/site.json` (`turnstile_site_key`, `api_base`), rebuild and push.

| Route | Does |
|---|---|
| `POST /allies` | validates, emails `ALLIES_TO`, stores nothing (reply-to is the applicant) |
| `POST /wholesale` | validates, emails `WHOLESALE_TO`, stores nothing |
| `POST /petition` | validates, stores name/email/location/consent/timestamp in D1, dedupes on lower-cased email (`already_signed`) |
| `GET /petition/count` | `{visible:false}` until `PETITION_THRESHOLD` (500) is reached, then `{visible:true,count}` |

Protections: CORS locked to `ALLOWED_ORIGINS`, honeypot, minimum fill time, Turnstile, per-IP per-minute rate limit (IP never stored), server-side validation incl. the 250-word limit.

Export the petition: `npx wrangler d1 export yogamaty-petition --remote --output=petition-backup.sql` (or `d1 execute … "SELECT * FROM signatures"` for CSV-like output). Back it up regularly — a lost petition list cannot be reconstructed.

Tests: `node worker/test.mjs`.
