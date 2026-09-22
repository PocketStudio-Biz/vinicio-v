#!/usr/bin/env python3
"""Build a single self-contained, sendable static preview of the Vinicio V. site.

Everything (data + photos) is inlined as base64 data URIs so the file opens in
any browser with no server, no external requests, and no sibling folders.
"""

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def b64(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def small(path: Path, max_w=900, max_h=900) -> str:
    """Downscale large images so the single file stays small but crisp."""
    try:
        from PIL import Image
        import io
        im = Image.open(path)
        im.thumbnail((max_w, max_h))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=82, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return b64(path)


data = json.loads((ROOT / "data" / "profile-stats.json").read_text())

avatar = small(ROOT / "public" / "profile.jpg", 240, 240)
gallery = [small(ROOT / "public" / "gallery" / Path(g).name) for g in data["gallery"]]

services = data["services"]
reviews = [
    {"n": "Annabelle C.", "c": "Car Washing", "t": "Vinicio did an incredible job- quick and communicative."},
    {"n": "Anuj S.", "c": "Car Washing", "t": "Very kind, and attentive to detail. Thanks Vinicio. Highly recommend to others"},
    {"n": "Alexa C.", "c": "Car Washing", "t": "He was fantastic! On time, cleaned very well and throughly, and was so respectful! 10/10!"},
    {"n": "Juan N.", "c": "Car Washing", "t": "Five stars for Vinicio! He arrived exactly when he said he would and did a phenomenal job detailing my car's interior."},
    {"n": "Shoaa A.", "c": "Cleaning", "t": "Vinicio is a hard worker and did a thorough job cleaning our place. He went above and beyond."},
    {"n": "Dante M.", "c": "Cleaning", "t": "Vinicio was AMAZING! He DETAILED the place. Smells wonderful. Can't recommend him enough!"},
    {"n": "Prasanth D.", "c": "Cleaning", "t": "Vinicio was great at deep cleaning, very kind, courteous and respectful of time."},
    {"n": "Jordan W.", "c": "Cleaning", "t": "Highly highly recommend! Vinicio is multi-talented, efficient, and has a great eye for detail."},
    {"n": "Isabelle B.", "c": "Cleaning", "t": "Vinicio is an absolute lifesaver. His attention to detail was phenomenal — windows, kitchen, blinds, balcony."},
    {"n": "Alexandra R.", "c": "Cleaning", "t": "10/10 recommend! Vinicio cleaned our apartment after we moved out and the place was spotless."},
    {"n": "Farah B.", "c": "Errands", "t": "Vinicio was extremely professional, efficient, and helpful. A great problem solver."},
    {"n": "Nir S.", "c": "Help Moving", "t": "Great work"},
    {"n": "Sharon C.", "c": "Help Moving", "t": "Vinicio is a super star, absolutely exceptional! Showed up 10 mins early."},
    {"n": "Christine S.", "c": "Help Moving", "t": "Vinicio was amazing! Friendly, focused, a great communicator, and incredibly hardworking."},
    {"n": "Sinja M.", "c": "Help Moving", "t": "Vinci is simply the best. He even took an extra two hours just to help me move."},
    {"n": "Sarah S.", "c": "Landscaping Help", "t": "Vinicio did an AWESOME job cleaning up around my garden… would 10000% hire him again."},
    {"n": "Kerry M.", "c": "Laundry and Ironing", "t": "Vinicio turned a messy closet into a well-organized walk-in closet."},
    {"n": "Mack O.", "c": "Yard Work", "t": "10 stars! Our yard looks so much better!"},
    {"n": "Sid K.", "c": "Yard Work", "t": "Vini created a very nice design with grass and mulch and planted beautiful plants."},
    {"n": "Vinod S.", "c": "Yard Work", "t": "The backyard looks completely clean and tidy. Strongly recommend him."},
    {"n": "Syed A.", "c": "Truck Assisted Help Moving", "t": "Vinio will go above and beyond to make sure you get what you're hiring him for."},
    {"n": "Suzanne W.", "c": "Truck Assisted Help Moving", "t": "Got my items moved quickly and carefully. Definitely recommend."},
    {"n": "Arun C.", "c": "Truck Assisted Help Moving", "t": "Vini was outstanding. Handled a two-person job entirely on his own."},
    {"n": "Troy D.", "c": "Personal Assistant", "t": "Vinicio was kind and on top of it. Good communication."},
    {"n": "Elizabeth L.", "c": "Personal Assistant", "t": "Vinny completed my task quickly and professionally. Asked thoughtful questions."},
]

form_action = "https://formspree.io/f/mzblqjkd"

service_cards = "\n".join(
    f'''        <div class="service">
            <div class="service-price">{s['price']}</div>
            <h3>{s['name']}</h3>
            <div class="meta">{s['count']}+ jobs completed</div>
            <div class="blurb">{s.get('blurb','')}</div>
            <a href="{data['profile_url']}" class="btn btn-primary" target="_blank" rel="noopener">Book</a>
        </div>'''
    for s in services
)

gallery_imgs = "\n".join(
    f'            <img src="{g}" alt="Vinicio V. — recent job">'
    for g in gallery
)

testimonials = "\n".join(
    f'''        <div class="testimonial">
            <p>“{r['t']}”</p>
            <div class="testimonial-author">
                <div class="avatar">{''.join(w[0] for w in r['n'].split()[:2]).upper()[:2]}</div>
                <div class="author-meta"><strong>{r['n']}</strong><span>{r['c']} · Verified Client</span></div>
            </div>
        </div>'''
    for r in reviews
)

updated = data.get("last_updated", "")
try:
    from datetime import datetime
    updated = datetime.fromisoformat(updated).strftime("%B %d, %Y")
except Exception:
    pass

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vinicio V. — Seattle Professional Services</title>
<style>
:root {{ --bg:#fff; --surface:#fff; --text:#14110f; --muted:#5b5550; --red:#b5232f; --red-dark:#7d141d; --gold:#b8902f; --border:#ece7e2; --light:#f7f4f1; --shadow:0 10px 30px rgba(20,17,15,.06); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ font-family:'Inter',system-ui,-apple-system,sans-serif; line-height:1.65; color:var(--text); background:var(--bg); font-size:15.5px; -webkit-font-smoothing:antialiased; }}
h1,h2,h3 {{ font-family:'Playfair Display',Georgia,serif; font-weight:700; line-height:1.15; }}
header {{ background:rgba(255,255,255,.95); border-bottom:1px solid var(--border); padding:1rem 0; position:sticky; top:0; z-index:100; }}
.header-inner {{ max-width:1080px; margin:0 auto; padding:0 1.4rem; display:flex; align-items:center; justify-content:space-between; gap:1.5rem; }}
.logo {{ font-family:'Playfair Display',Georgia,serif; font-size:1.5rem; color:var(--text); text-decoration:none; letter-spacing:-.01em; }}
.logo span {{ color:var(--red); }}
.btn {{ display:inline-block; padding:.72rem 1.5rem; font-size:.88rem; font-weight:600; letter-spacing:.3px; text-decoration:none; border-radius:6px; transition:all .18s ease; cursor:pointer; border:1px solid transparent; text-align:center; }}
.btn-primary {{ background:var(--red); color:#fff; border-color:var(--red); }}
.btn-primary:hover {{ background:var(--red-dark); }}
.btn-secondary {{ background:transparent; color:var(--text); border-color:var(--border); }}
.btn-secondary:hover {{ background:var(--light); }}
.hero {{ background:radial-gradient(1200px 400px at 50% -120px, rgba(184,144,47,.10), transparent), var(--surface); border-bottom:1px solid var(--border); padding:4.5rem 1.4rem 4rem; }}
.hero-inner {{ max-width:1080px; margin:0 auto; text-align:center; }}
.hero-avatar {{ width:96px; height:96px; border-radius:50%; object-fit:cover; border:3px solid #fff; box-shadow:var(--shadow); margin-bottom:1.1rem; }}
.rating {{ color:var(--gold); font-size:1rem; letter-spacing:2px; margin-bottom:.5rem; }}
.rating .count {{ color:var(--muted); letter-spacing:0; font-size:.85rem; font-weight:500; }}
.hero h1 {{ font-size:clamp(2.1rem,5.5vw,3rem); margin-bottom:.55rem; }}
.hero p.lead {{ color:var(--muted); max-width:560px; margin:0 auto 1.6rem; font-size:1.02rem; }}
.hero-actions {{ display:flex; gap:.75rem; justify-content:center; flex-wrap:wrap; }}
.stats {{ max-width:1080px; margin:0 auto; padding:3rem 1.4rem 2.5rem; display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1.5rem; }}
.stat {{ text-align:center; padding:1rem .5rem; }}
.stat-num {{ font-family:'Playfair Display',Georgia,serif; font-size:2.1rem; color:var(--red); line-height:1; margin-bottom:.3rem; }}
.stat-label {{ font-size:.76rem; letter-spacing:1.2px; text-transform:uppercase; color:var(--muted); font-weight:500; }}
.section {{ max-width:1080px; margin:0 auto; padding:3rem 1.4rem; }}
.section-head {{ text-align:center; margin-bottom:2.1rem; }}
.section-head h2 {{ font-size:1.8rem; margin-bottom:.35rem; }}
.section-head p {{ color:var(--muted); font-size:.95rem; }}
.services-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:1.1rem; }}
.service {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:1.4rem 1.45rem; display:flex; flex-direction:column; }}
.service-price {{ font-family:'Playfair Display',Georgia,serif; font-size:1.4rem; color:var(--gold); margin-bottom:.15rem; }}
.service h3 {{ font-size:1.08rem; margin-bottom:.25rem; }}
.service .meta {{ font-size:.8rem; color:var(--muted); margin-bottom:.55rem; }}
.service .blurb {{ font-size:.88rem; color:var(--muted); margin-bottom:1rem; flex:1; }}
.service .btn {{ font-size:.8rem; padding:.55rem 1.1rem; align-self:flex-start; }}
.gallery-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:.8rem; }}
.gallery-grid img {{ width:100%; height:190px; object-fit:cover; border-radius:10px; border:1px solid var(--border); }}
.features {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1.3rem; }}
.feature {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:1.5rem 1.6rem; }}
.feature h3 {{ font-size:1.02rem; margin-bottom:.35rem; }}
.feature p {{ color:var(--muted); font-size:.9rem; }}
.quote-section {{ background:var(--light); border-top:1px solid var(--border); border-bottom:1px solid var(--border); }}
.quote-grid {{ max-width:1080px; margin:0 auto; padding:3rem 1.4rem; display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:2rem; }}
.panel {{ border:1px solid var(--border); border-radius:10px; background:#fff; padding:1.9rem 1.85rem; }}
.panel h3 {{ font-size:1.15rem; margin-bottom:.4rem; }}
.panel p {{ color:var(--muted); font-size:.92rem; margin-bottom:1.25rem; }}
.form-group {{ margin-bottom:1rem; }}
.form-group label {{ display:block; font-size:.78rem; letter-spacing:.5px; text-transform:uppercase; color:var(--muted); margin-bottom:.35rem; font-weight:500; }}
.form-group input, .form-group textarea {{ width:100%; padding:.72rem .9rem; border:1px solid var(--border); border-radius:6px; background:#fff; font-size:1rem; font-family:inherit; }}
.form-group input:focus, .form-group textarea:focus {{ outline:none; border-color:var(--red); }}
.form-group textarea {{ min-height:100px; resize:vertical; }}
.msg {{ margin-top:.8rem; font-size:.9rem; font-weight:500; }}
.msg.success {{ color:#166534; }}
.msg.error {{ color:#9f1239; }}
.testimonials {{ background:var(--light); }}
.testimonial-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:1.3rem; }}
.testimonial {{ background:#fff; border:1px solid var(--border); border-radius:10px; padding:1.55rem 1.6rem; display:flex; flex-direction:column; min-height:200px; }}
.testimonial p {{ font-style:italic; color:var(--text); flex:1; margin-bottom:1.1rem; font-size:.95rem; }}
.testimonial-author {{ display:flex; align-items:center; gap:.7rem; font-size:.9rem; }}
.avatar {{ width:36px; height:36px; border-radius:50%; background:var(--red); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:600; font-size:.78rem; flex-shrink:0; }}
.author-meta strong {{ display:block; font-weight:600; }}
.author-meta span {{ font-size:.75rem; color:var(--muted); }}
footer {{ background:var(--text); color:#d1d5db; padding:2.6rem 1.4rem; text-align:center; font-size:.9rem; }}
footer a {{ color:#fff; text-decoration:none; }}
footer a:hover {{ color:var(--gold); }}
.updated {{ margin-top:1rem; font-size:.74rem; opacity:.6; }}
</style>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="#" class="logo">Vinicio V<span>.</span></a>
    <a href="{data['profile_url']}" class="btn btn-primary" target="_blank" rel="noopener">Book on TaskRabbit</a>
  </div>
</header>

<section class="hero">
  <div class="hero-inner">
    <img class="hero-avatar" src="{avatar}" alt="Vinicio V.">
    <div class="rating">★★★★★ <span class="count">({data['reviews']} reviews)</span></div>
    <h1>Professional services.<br>Seattle.</h1>
    <p class="lead">{data['bio']}</p>
    <div class="hero-actions">
      <a href="{data['profile_url']}" class="btn btn-primary" target="_blank" rel="noopener">Book on TaskRabbit</a>
      <a href="#book" class="btn btn-secondary">Request a custom quote</a>
    </div>
  </div>
</section>

<section class="stats">
  <div class="stat"><div class="stat-num">{data['tasks']}+</div><div class="stat-label">Tasks Completed</div></div>
  <div class="stat"><div class="stat-num">{data['rating']}</div><div class="stat-label">Average Rating</div></div>
  <div class="stat"><div class="stat-num">{data['reviews']}</div><div class="stat-label">Reviews</div></div>
  <div class="stat"><div class="stat-num">{data['since']}</div><div class="stat-label">Tasker Since</div></div>
</section>

<section id="services" class="section">
  <div class="section-head"><h2>Services &amp; Rates</h2><p>Current rates from Vinicio's verified TaskRabbit profile</p></div>
  <div class="services-grid">
{service_cards}
  </div>
</section>

<section id="work" class="section">
  <div class="section-head"><h2>Recent work</h2><p>Real jobs, completed locally</p></div>
  <div class="gallery-grid">
{gallery_imgs}
  </div>
</section>

<section id="why" class="section">
  <div class="section-head"><h2>Why clients choose Vinicio</h2><p>Consistent, professional work every time.</p></div>
  <div class="features">
    <div class="feature"><h3>Attention to detail</h3><p>Every project receives careful, thorough work — nothing half-done.</p></div>
    <div class="feature"><h3>Reliable &amp; punctual</h3><p>Shows up on time and finishes what is promised.</p></div>
    <div class="feature"><h3>Clear communication</h3><p>Updates throughout the job and responsive to questions.</p></div>
    <div class="feature"><h3>Fully equipped</h3><p>Professional tools and supplies for every task.</p></div>
  </div>
</section>

<section id="book" class="quote-section">
  <div class="quote-grid">
    <div class="panel">
      <h3>Book directly</h3>
      <p>Standard services with fixed hourly rates and secure payment through TaskRabbit.</p>
      <a href="{data['profile_url']}" class="btn btn-primary" target="_blank" rel="noopener">Book on TaskRabbit</a>
    </div>
    <div class="panel">
      <h3>Request a custom quote</h3>
      <p>Need something outside standard services? Send details for a personalized quote.</p>
      <form id="leadForm" action="{form_action}" method="POST" novalidate>
        <input type="hidden" name="_subject" value="Quote request for Vinicio V.">
        <input type="text" name="_honey" tabindex="-1" autocomplete="off" style="display:none">
        <div class="form-group"><label for="name">Full name</label><input type="text" id="name" name="name" autocomplete="name"></div>
        <div class="form-group"><label for="email">Email</label><input type="text" id="email" name="email" inputmode="email" autocomplete="email"></div>
        <div class="form-group"><label for="phone">Phone</label><input type="text" id="phone" name="phone" inputmode="tel" autocomplete="tel"></div>
        <div class="form-group"><label for="project">Project details</label><textarea id="project" name="message"></textarea></div>
        <button type="submit" class="btn btn-primary" style="width:100%">Send request</button>
      </form>
      <p id="formSuccess" class="msg success" style="display:none;">Request sent. I'll contact you shortly.</p>
      <p id="formError" class="msg error" style="display:none;">Something went wrong. Please try again.</p>
    </div>
  </div>
</section>

<section id="reviews" class="section testimonials">
  <div class="section-head"><h2>Client feedback</h2><p>Real reviews from completed jobs</p></div>
  <div class="testimonial-grid">
{testimonials}
  </div>
</section>

<footer>
  <p><strong>Vinicio V.</strong> — Seattle professional services</p>
  <p style="margin-top:.4rem; opacity:.85;"><a href="{data['profile_url']}" target="_blank" rel="noopener">Book on TaskRabbit</a></p>
  <p class="updated">Profile stats synced {updated} via TaskRabbit</p>
  <p style="margin-top:1rem; font-size:.78rem; opacity:.65;">© 2026 Vinicio V. All rights reserved.</p>
</footer>

<script>
document.getElementById('leadForm').addEventListener('submit', async function(e){{
  e.preventDefault();
  var form=this, data=new FormData(form);
  if(data.get('_honey')) return;
  data.delete('_honey');
  var typed=String(data.get('email')||'').trim();
  data.delete('email');
  if(/[^\\s@]+@[^\\s@]+\\.[^\\s@]+/.test(typed)){{ data.set('email', typed); data.set('_replyto', typed); }}
  else if(typed) data.set('contact', typed);
  var btn=form.querySelector('button'); btn.disabled=true;
  try {{
    var res=await fetch(form.action,{{method:'POST',body:data,headers:{{Accept:'application/json'}}}});
    var body=await res.json().catch(function(){{return {{}};}});
    if(res.ok && body.ok!==false && String(body.success)!=='false'){{ form.style.display='none'; document.getElementById('formSuccess').style.display='block'; }}
    else throw new Error('bad');
  }} catch(err){{ document.getElementById('formError').style.display='block'; }}
  finally {{ btn.disabled=false; }}
}});
</script>
</body>
</html>'''

out = ROOT / "vinicio-v-preview.html"
out.write_text(html)
print(f"Wrote {out} ({len(html)/1024:.0f} KB)")
