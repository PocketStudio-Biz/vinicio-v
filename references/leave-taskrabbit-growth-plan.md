# Vinicio V. — Launch & leave TaskRabbit

**Brand:** Vinicio V. (personal brand)  
**Strategy:** Soft transition with a hard-push focus — TaskRabbit stays as overflow discovery for ~3–6 months, but every week we move clients, reviews, and revenue onto the independent site.  
**Market:** Seattle metro · yard work, cleaning, moving help, car wash, estate cleanout, laundry  
**Baseline (live sync, Oct 2026):** ~286 tasks · 72 reviews · 5.0★ · site already mirrors rates, photos, and testimonials daily

---

## North star

Leave TaskRabbit when **direct work** reliably covers income without needing TR for new leads.

**Exit checklist (all must be true for 8+ weeks):**

| Metric | Target |
|--------|--------|
| Direct booked hours / week | ≥ 70% of total hours |
| Direct revenue / month | ≥ TR peak month |
| Repeat + referral clients | ≥ 40% of direct jobs |
| Google reviews on own profile | ≥ 25 (5.0 aim) |
| Quote → booked conversion | ≥ 30% |
| Response time to quote | &lt; 2 hours during work hours |

Until then: keep TR profile active, keep daily sync, but **stop promoting TR as the default CTA** once direct booking works.

---

## Phase 0 — Foundations (week 1)

Ship the minimum so a stranger can hire Vinicio **without** TaskRabbit.

### Business ops
1. **Domain** — buy something short that fits the personal brand (e.g. `viniciov.com` / `hirevinicio.com`). Point DNS to current host (Vercel/GitHub Pages).
2. **Google Business Profile** — create “Vinicio V. — Seattle Yard & Home Help”; categories: House Cleaning Service, Landscaper, Mover. Upload gallery photos from `public/gallery/`.
3. **Phone** — dedicated Google Voice / business line on the site (not only Formspree email).
4. **Insurance** — general liability that covers independent jobs (required before dropping TR protection narrative).
5. **Payments** — Stripe Payment Links or Invoice (deposit + balance). No custom app yet.
6. **Scheduling** — Calendly (or Google Calendar appointment slots) with buffers and 2-hour minimum rules.

### Site changes (this repo)
Flip the funnel from “Book on TaskRabbit” → “Book direct”:

| Today ([index.html](../index.html)) | Target |
|-------------------------------------|--------|
| Hero CTA → TaskRabbit | Hero CTA → `#book` / “Get a quote” or “Book a time” |
| Service cards → TaskRabbit | Service cards → quote form with service prefilled |
| “If it fits TaskRabbit” panel first | “Book direct” panel first; TR as “Also on TaskRabbit” secondary link |
| Form → Formspree email only | Form + phone + optional Calendly embed; auto-reply with next steps |
| Rates copy “from the TaskRabbit profile” | “Current rates” (still fed by sync) |
| Reviews sub “from his TaskRabbit profile” | “Client notes” + add Google review link when GBP is live |

Keep [monitor.py](../monitor.py) daily sync — social proof stays fresh while leaving.

### Lead handling
- Auto-reply: thanks + “I’ll confirm within 2 hours” + link to book a slot / send photos of the job.
- Simple CRM: Google Sheet or Airtable with columns `date | name | contact | service | source | status | $ | notes`.
- Tag every lead: `site` · `referral` · `google` · `tr-repeat` · `other`.

**Phase 0 done when:** someone can find the site, request a job, pay a deposit, and get on the calendar without opening TaskRabbit.

---

## Phase 1 — Launch hard (weeks 2–4)

Make direct the default path and fill the pipeline.

### Conversion on the site
1. Prefill quote form from service buttons (`?service=Cleaning`).
2. Add **service area** (Seattle neighborhoods / ZIP list) so junk leads drop.
3. Add **photo upload** (or “text me photos”) for yard/estate quotes.
4. Show **2–3 strongest testimonials** near the hero CTA (not only at bottom).
5. Add basic analytics (Plausible or GA4) — track CTA clicks, form submits, Calendly bookings.

### Demand generation (low cost, high fit)
1. **Every TR client** after a job: text/email “Next time book me direct — same work, no platform fee” + site link + QR card.
2. **Google Business Profile** — weekly posts (before/after from gallery), ask for Google reviews after each direct job.
3. **Nextdoor** — Seattle neighborhood posts / offers (yard cleanup, move-out clean).
4. **Referral offer** — e.g. $25 credit each way after first direct booking.
5. **Print** — simple leave-behind card at every job with QR → site `#book`.

### Pricing (independence buffer)
- Keep rates near live TR rates from sync.
- Direct booking: optional **small discount vs TR** *or* **same rate + better availability** — pick one message and stick to it.
- Always state 2-hour minimum and travel rules on the form confirmation.

**Phase 1 done when:** ≥ 8 direct jobs booked in a month and ≥ 10 Google reviews.

---

## Phase 2 — Grow & replace TR (months 2–3)

Push until direct is the majority of hours.

### Retention
- After every job: review ask (Google) + “save this link for next time.”
- Light nurture: monthly seasonal SMS/email (fall leaves, spring clean, holiday hosting clean) to past direct clients only.
- Offer **standing schedules** (biweekly clean / monthly yard) — these kill TR dependency fastest.

### SEO / local
- Own domain live; title/meta already exist — add LocalBusiness JSON-LD, `og:image`, sitemap, canonical.
- One landing intent per top service (or clear on-page sections): Yard Work Seattle, Move-out Cleaning Seattle, etc.
- Embed GBP map / service area list.

### Capacity
- Block TR “open for new clients” once direct calendar is ≥ 60% full.
- Use TR only for overflow or categories that won’t book direct yet.

**Phase 2 done when:** direct hours ≥ 70% for 4 consecutive weeks.

---

## Phase 3 — Leave (months 4–6)

1. Pause new TR discovery (profile “not accepting” / raise rates on TR above direct).
2. Final message to recent TR clients with direct booking link.
3. Keep daily sync **or** freeze last testimonials as owned copy once Google reviews cover social proof.
4. Update site: remove primary TR CTAs; keep a quiet footer link only if still useful for trust.
5. Reassess income for 8 weeks against exit checklist — then fully deactivate TR if stable.

---

## What we build in this repo (implementation order)

1. **CTA & copy flip** — direct booking first; TR secondary.
2. **Quote form upgrade** — service prefill, neighborhood/ZIP, phone required, auto-reply copy.
3. **Calendly + Stripe links** — embed or deep-link from success state.
4. **Analytics** — Plausible/GA4 events on CTAs and form.
5. **SEO pack** — domain-ready meta, JSON-LD, sitemap, robots.
6. **Review bridge** — Google review CTA once GBP URL exists.
7. **Optional later** — simple client portal; until then Sheet + Calendly + Stripe is enough.

Do **not** build a custom scheduler/payment app before Phase 1 proves demand.

---

## Weekly operating rhythm

| Day | Action |
|-----|--------|
| After every job | Ask for Google review; leave card; log in Sheet |
| Mon | Check quote inbox + calendar; fill open slots with Nextdoor/GBP post |
| Wed | Follow up unpaid quotes; send 3 referral asks |
| Fri | Review metrics: leads, booked, revenue direct vs TR |
| Ongoing | Daily GitHub sync keeps photos/reviews fresh |

---

## Risks & how we handle them

| Risk | Mitigation |
|------|------------|
| Lead volume drops when TR is de-emphasized | Soft transition: TR stays open until direct ≥ 70% |
| No-shows / payment risk off-platform | Stripe deposit before confirming slot |
| Review gap vs TR’s 70+ reviews | Aggressive Google review asks; keep synced TR quotes on site until GBP catches up |
| Insurance / damage claims | Bind liability before marketing “book direct” heavily |
| Time sink building software | Use Calendly + Stripe + Sheet; only customize the static site |

---

## Immediate next actions (this week)

1. Buy domain → point to current Vercel deploy.  
2. Open Google Business Profile + start review collection.  
3. Create Stripe Payment Link + Calendly with 2-hour minimum.  
4. PR on this repo: flip hero/service CTAs to direct quote; demote TaskRabbit.  
5. Add phone number + auto-reply on Formspree.  
6. Print QR cards for every job this week.

When those six are done, Phase 0 is complete and the hard push to leave TaskRabbit can start measuring against the exit checklist.
