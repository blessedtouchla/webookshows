import os, html, json, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from data import ACTS, EV

ROOT = os.environ.get('WBS_OUT') or os.path.join(os.path.dirname(__file__), '..', 'site')
SITE = 'https://webookshows.com'
BRAND = 'We Book Shows'
e = html.escape
import re as _re
_cfg = open(os.path.join(ROOT, 'js', 'config.js')).read()
EMAIL = (_re.search(r'CONTACT_EMAIL:\s*"([^"]*)"', _cfg) or [None, ''])[1]
PHONE = (_re.search(r'CONTACT_PHONE:\s*"([^"]*)"', _cfg) or [None, ''])[1]
TEL = (_re.search(r'CONTACT_PHONE_TEL:\s*"([^"]*)"', _cfg) or [None, ''])[1]
WHO = (_re.search(r'BOOKING_CONTACT_NAME:\s*"([^"]*)"', _cfg) or [None, ''])[1]
PHONE_HTML = (f'<span class="js-phone-who">Bookings: {html.escape(WHO)},</span> <a class="js-phone" href="tel:{TEL}">{html.escape(PHONE)}</a>') if PHONE else ''

def rel(depth): return '../' * depth

def page(path, title, desc, body, depth, og_image='img/og.jpg', active=''):
    r = rel(depth)
    canon = SITE + '/' + (path.replace('index.html', '') if path != 'index.html' else '')
    nav = [('', 'Home', 'home'), ('roster/', 'Roster', 'roster'), ('about/', 'About', 'about')]
    navhtml = ''.join(f'<a href="{r}{h}"{" aria-current=\"page\"" if k==active else ""}>{t}</a>' for h,t,k in nav)
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0b0a0f">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/{og_image}">
<meta property="og:image:alt" content="{BRAND}: booking established hip-hop and West Coast acts">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/{og_image}">
<link rel="icon" href="{r}img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}css/style.css">
<script src="{r}js/config.js" defer></script>
<script src="{r}js/main.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="logo" href="{r}" aria-label="{BRAND} home"><span class="logo-mark" aria-hidden="true">WB</span><span class="logo-text">We Book <b>Shows</b></span></a>
    <nav class="nav" aria-label="Main">{navhtml}<a class="btn btn-sm" href="{r}book/">Book a show</a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap foot">
    <div>
      <a class="logo" href="{r}"><span class="logo-mark" aria-hidden="true">WB</span><span class="logo-text">We Book <b>Shows</b></span></a>
      <p class="muted small">Talent booking for casinos, festivals, venues, hotel bars, hemp fests, cultural &amp; business events, and official after-parties.</p>
    </div>
    <nav class="foot-links" aria-label="Footer">
      <a href="{r}roster/">Roster</a>
      <a href="{r}book/">Book a show</a>
      <a href="{r}about/">About &amp; contact</a>
      <a href="{r}privacy/">Privacy</a>
    </nav>
    <div class="small">
      <p class="js-phone-row"{{PHONE_HIDDEN}}>{{PHONE_HTML}}</p>
      <p><a class="js-email" data-show href="{{MAILTO}}">{{EMAIL_TXT}}</a></p>
      <p class="muted"><a class="quiet" href="{r}join/">Artists: want to join the roster?</a></p>
    </div>
  </div>
  <div class="wrap small muted legal">&copy; <span class="js-year">2026</span> {BRAND}. Artist names, photos and videos belong to their respective owners. Fees quoted per date. Availability on request.</div>
</footer>
</body>
</html>
'''
    doc = doc.replace('{PHONE_HTML}', PHONE_HTML).replace('{PHONE_HIDDEN}', '' if PHONE else ' hidden')
    doc = doc.replace('{MAILTO}', ('mailto:' + EMAIL) if EMAIL else r + 'about/#contact').replace('{EMAIL_TXT}', e(EMAIL) if EMAIL else 'Email coming soon')
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(doc)

def has_photo(a):
    return os.path.exists(os.path.join(ROOT, 'img', 'artists', a['photo'] + '.jpg'))

def namecard(a):
    initials = ''.join(w[0] for w in a['name'].replace("'", '').split() if w[0].isalnum())[:3].upper()
    return f'<div class="namecard" role="img" aria-label="{e(a["name"])}"><span class="nc-initials" aria-hidden="true">{e(initials)}</span><span class="nc-name" aria-hidden="true">{e(a["name"])}</span></div>'

def img_tag(a, r, cls='', eager=False, sizes=''):
    if not has_photo(a):
        return namecard(a)
    alt = f"{a['name']}" + (" promotional artwork" if a.get('photo_is_art') else " press photo")
    return f'<img class="{cls}" src="{r}img/artists/{a["photo"]}.jpg" alt="{e(alt)}" style="object-position:{a.get("pos","50% 30%")}" {"" if eager else "loading=\"lazy\" "}decoding="async">'

SHORT = {'afroman': 'Los Angeles & Palmdale, CA', 'kurupt': 'Hawthorne, CA', 'baby-bash': 'Vallejo, CA & Houston, TX', 'brockett-parsons': 'Los Angeles, CA', 'rappin-4-tay-x-suga-free': 'San Francisco & Pomona, CA', 'mr-capone-e-x-lil-rob': 'West Covina & San Diego, CA', 'rbl-posse': 'San Francisco, CA'}

def media(a, r, eager=False):
    if a.get('package'):
        return '<div class="duo">' + ''.join(img_tag(m, r, eager=eager) for m in a['members']) + '</div>'
    return img_tag(a, r, eager=eager)

def card(a, r):
    tags = ''.join(f'<li>{e(EV[g])}</li>' for g in a['good'][:3])
    kind = 'Double bill' if a.get('package') else (a.get('tagline') or a['genre'].split(',')[0])
    return f'''<li class="card" data-good="{' '.join(a['good'])}">
  <a href="{r}artists/{a['slug']}/" class="card-link">
    <div class="card-img">{media(a, r)}</div>
    <div class="card-body">
      <p class="eyebrow">{e(kind)}</p>
      <h3>{e(a['name'])}</h3>
      <p class="muted small">{e(SHORT.get(a['slug'], a['region']))}{(' · Since ' + e(a['since'][:4])) if a.get('since','')[:4].isdigit() else ''}</p>
      <ul class="chips">{tags}</ul>
    </div>
  </a>
</li>'''

def video_block(v, r):
    note = ''
    return f'''<div class="video">
  <button class="yt" type="button" data-yt="{v['id']}" aria-label="Play video: {e(v['title'])}">
    <img src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="Video thumbnail: {e(v['title'])}" loading="lazy" decoding="async" width="480" height="360">
    <span class="play" aria-hidden="true"></span>
  </button>
  <p class="small"><a href="https://www.youtube.com/watch?v={v['id']}" target="_blank" rel="noopener">Watch on YouTube: {e(v['title'])}</a></p>
  {note}
</div>'''

def facts(a):
    rows = [('Hometown / region', a['region']), ('Genre', a['genre'])]
    if a.get('since'):
        rows.append(('Career', a['since']) if not a['since'][:4].isdigit() else ('Active since', a['since']))
    if a.get('show'): rows.append(('Show', a['show']))
    rows.append(('Availability', 'On request'))
    return '<dl class="facts">' + ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in rows) + '</dl>'

def songs(a):
    if a.get('songs'):
        return '<h3>Signature songs</h3><ul class="songs">' + ''.join(f'<li>{e(s)}</li>' for s in a['songs']) + '</ul>'
    if a.get('known'):
        return '<h3>Known for</h3><ul class="songs">' + ''.join(f'<li>{e(s)}</li>' for s in a['known']) + '</ul>'
    return ''

def socials(a):
    if not a.get('socials'): return ''
    return '<h3>Official links</h3><ul class="socials">' + ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{e(n)}</a></li>' for n,u in a['socials']) + '</ul>'

def good(a):
    return '<h3>Good for</h3><ul class="chips chips-lg">' + ''.join(f'<li>{e(EV[g])}</li>' for g in a['good']) + '</ul>'

def profile(a):
    r = rel(2)
    book = f'{r}book/?artist={a["slug"]}'
    bio = ''.join(f'<p>{e(p)}</p>' for p in a['bio'])
    members = ''
    if a.get('package'):
        for m in a['members']:
            members += f'''<section class="member" id="{m['slug']}">
  <div class="wrap profile-grid">
    <div class="profile-photo">{img_tag(m, r)}</div>
    <div class="profile-info">
      <p class="eyebrow">Part of {e(a['name'])}</p>
      <h2>{e(m['name'])}</h2>
      {''.join(f'<p>{e(p)}</p>' for p in m['bio'])}
      {facts({**m, 'show': ''})}
      {songs(m)}
      {socials(m)}
      <p><a class="btn btn-ghost" href="{r}book/?artist={m['slug']}">Ask about {e(m['name'])} solo</a></p>
    </div>
    <div class="profile-video">{video_block(m['video'], r)}</div>
  </div>
</section>'''
    main_video = '' if a.get('package') else f'<div class="profile-video">{video_block(a["video"], r)}</div>'
    tagline = f'<p class="eyebrow">{e(a["tagline"])}</p>' if a.get('tagline') else ('<p class="eyebrow">Double bill · book the package or each artist</p>' if a.get('package') else '')
    body = f'''<section class="profile-hero">
  <div class="wrap">
    <p class="crumbs small"><a href="{r}roster/">Roster</a> / {e(a['name'])}</p>
  </div>
  <div class="wrap profile-grid">
    <div class="profile-photo{' is-duo' if a.get('package') else ''}">{media(a, r, eager=True)}</div>
    <div class="profile-info">
      {tagline}
      <h1>{e(a['name'])}</h1>
      {bio}
      {facts(a)}
      {'' if a.get('package') else songs(a)}
      {good(a)}
      {'' if a.get('package') else socials(a)}
      <p class="note small">Fees quoted per date. Availability on request.</p>
      <p class="cta-row"><a class="btn" href="{book}">Book {e(a['name'])}</a> <a class="btn btn-ghost" href="{r}roster/">Back to roster</a></p>
    </div>
    {main_video}
  </div>
</section>
{members}
<section class="band">
  <div class="wrap band-inner">
    <div><h2>Put {e(a['name'])} on your stage</h2><p class="muted">Send your date, city and venue details. Fees are quoted per date, and availability is on request.</p></div>
    <a class="btn" href="{book}">Start an inquiry</a>
  </div>
</section>'''
    desc = f"Book {a['name']} ({a['genre']}, {a['region']}) for casinos, festivals, venues and events through {BRAND}. Availability on request."
    page(f'artists/{a["slug"]}/index.html', f"{a['name']}: book for your event | {BRAND}", desc, body, 2, active='roster')

EVENT_BLURBS = [
 ('casinos','Headliners for showrooms, event centers and promo nights with name recognition across generations.'),
 ('festivals','Main-stage and support slots, from city festivals to multi-day lineups.'),
 ('venues','Club and theater bookings with routing-friendly packages and double bills.'),
 ('hotel','Polished sets and appearances for rooftops, pool parties and lounges.'),
 ('hemp','Artists with real credibility in cannabis culture for hemp fests and 420 events.'),
 ('cultural','Chicano rap, Bay Area and West Coast legends for heritage and community celebrations.'),
 ('business','Private, corporate and brand events, including talent that fits a more upscale room.'),
 ('after','Official after-parties for concerts, conventions, award shows and sporting events.'),
]

def home():
    r = ''
    feat = [a for a in ACTS if a.get('featured')]
    cards = ''.join(card(a, r) for a in feat)
    events = ''.join(f'<li><h3>{e(EV[k])}</h3><p class="muted small">{e(t)}</p></li>' for k,t in EVENT_BLURBS)
    names = ' · '.join(e(a['name']) for a in ACTS)
    body = f'''<section class="hero">
  <div class="wrap hero-inner">
    <p class="eyebrow">Talent booking · Hip-hop &amp; West Coast</p>
    <h1>Established hip-hop and West Coast acts, <span class="hl">booked for your stage.</span></h1>
    <p class="lead">We book recognizable artists for casinos, festivals, venues, hotel bars, hemp fests, cultural and business events, and official after-parties. Tell us the date and the room, and we'll handle the rest.</p>
    <p class="cta-row"><a class="btn" href="book/">Book a show</a> <a class="btn btn-ghost" href="roster/">See the roster</a></p>
    <p class="muted small hero-note">Fees quoted per date. Availability on request.</p>
  </div>
  <div class="marquee" aria-hidden="true"><div class="marquee-track"><span>{names}</span><span>{names}</span></div></div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Featured roster</h2><a href="roster/" class="more">Full roster &rarr;</a></div>
    <ul class="grid">{cards}</ul>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <div class="section-head"><h2>Who we book for</h2></div>
    <ul class="events">{events}</ul>
  </div>
</section>
<section class="section">
  <div class="wrap steps-wrap">
    <h2>How booking works</h2>
    <ol class="steps">
      <li><h3>Send an inquiry</h3><p class="muted">Date, city, venue, capacity and the artists you have in mind.</p></li>
      <li><h3>Get availability</h3><p class="muted">We check the date with the artist's team and come back with availability and a quote for that date.</p></li>
      <li><h3>Confirm the offer</h3><p class="muted">Terms, rider and logistics are confirmed in writing before anything is announced.</p></li>
    </ol>
  </div>
</section>
<section class="band">
  <div class="wrap band-inner">
    <div><h2>Have a date to fill?</h2><p class="muted">Send the details and we will follow up with availability.</p></div>
    <a class="btn" href="book/">Book a show</a>
  </div>
</section>'''
    page('index.html', f'{BRAND}: Book hip-hop & West Coast artists for casinos, festivals & events',
         'Book established hip-hop and West Coast acts, including Afroman, Paul Wall, Baby Bash, Kurupt, Digital Underground and more, for casinos, festivals, venues, hotel bars, hemp fests and after-parties.',
         body, 0, active='home')

def roster():
    r = rel(1)
    cards = ''.join(card(a, r) for a in ACTS)
    filters = '<button type="button" class="chip-btn" aria-pressed="true" data-filter="all">All</button>' + ''.join(f'<button type="button" class="chip-btn" aria-pressed="false" data-filter="{k}">{e(v)}</button>' for k,v in EV.items())
    body = f'''<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Roster</p>
    <h1>The roster</h1>
    <p class="lead">{len(ACTS)} acts, from Bay Area pioneers and Chicano rap favorites to Houston headliners and a Lady Gaga keyboardist. Tap an act for the bio, signature songs and video.</p>
    <div class="filters" role="group" aria-label="Filter by event type">{filters}</div>
  </div>
</section>
<section class="section pt0">
  <div class="wrap">
    <ul class="grid" id="roster-grid">{cards}</ul>
    <p class="muted small empty" hidden>No acts tagged for that event type yet. <a href="{r}book/">Ask us anyway</a>.</p>
    <p class="join-note small muted"><a class="quiet" href="{r}join/">Artists: want to join the roster?</a></p>
  </div>
</section>
<section class="band">
  <div class="wrap band-inner">
    <div><h2>Not sure who fits?</h2><p class="muted">Tell us about the room and the crowd. We'll suggest acts that fit.</p></div>
    <a class="btn" href="{r}book/">Book a show</a>
  </div>
</section>'''
    page('roster/index.html', f'Roster: hip-hop & West Coast artists available to book | {BRAND}',
         'The We Book Shows roster: Afroman, Rappin\' 4-Tay x Suga Free, Mr. Capone-E x Lil Rob, Celly Cel, RBL Posse, Dru Down, Yukmouth, Brockett Parsons, Devin the Dude, Lil Eazy-E, Baby Bash, Bizarre, Spice 1, Kurupt, 2nd II None, Paul Wall and Digital Underground.',
         body, 1, active='roster')

def field(name, label, typ='text', req=False, opts=None, ph='', auto='', full=False, help=''):
    rq = ' required' if req else ''
    star = ' <span aria-hidden="true" class="req">*</span>' if req else ' <span class="muted small">(optional)</span>'
    cls = 'field full' if full else 'field'
    hid = f' aria-describedby="{name}-help"' if help else ''
    hl = f'<small id="{name}-help" class="muted">{e(help)}</small>' if help else ''
    if typ == 'select':
        o = '<option value="">Choose…</option>' + ''.join(f'<option>{e(x)}</option>' for x in opts)
        return f'<div class="{cls}"><label for="{name}">{label}{star}</label><select id="{name}" name="{name}"{rq}{hid}>{o}</select>{hl}</div>'
    if typ == 'textarea':
        return f'<div class="{cls}"><label for="{name}">{label}{star}</label><textarea id="{name}" name="{name}" rows="5" placeholder="{e(ph)}"{rq}{hid}></textarea>{hl}</div>'
    a = f' autocomplete="{auto}"' if auto else ''
    return f'<div class="{cls}"><label for="{name}">{label}{star}</label><input id="{name}" name="{name}" type="{typ}" placeholder="{e(ph)}"{a}{rq}{hid}>{hl}</div>'

def form_shell(kind, subject, inner, submit):
    return f'''<form class="form js-form" data-kind="{kind}" data-subject="{e(subject)}" novalidate>
  <div class="hp" aria-hidden="true"><label>Leave this empty <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>
  <div class="form-grid">{inner}</div>
  <p class="form-actions"><button class="btn" type="submit">{submit}</button></p>
  <p class="form-status" role="status" aria-live="polite"></p>
  <p class="muted small">By sending this form you agree to our <a href="../privacy/">privacy notice</a>. We only use your details to reply.</p>
</form>'''

def book():
    r = rel(1)
    artist_opts = []
    for a in ACTS:
        artist_opts.append((a['slug'], a['name']))
        for m in a.get('members', []):
            artist_opts.append((m['slug'], m['name'] + ' (solo)'))
    checks = ''.join(f'<label class="check"><input type="checkbox" name="artist_interest" value="{e(n)}" data-slug="{s}"> <span>{e(n)}</span></label>' for s,n in artist_opts)
    checks += '<label class="check"><input type="checkbox" name="artist_interest" value="Not sure, recommend acts" data-slug="recommend"> <span>Not sure, recommend acts</span></label>'
    inner = ''.join([
        field('name','Your name',req=True,auto='name'),
        field('company','Company or venue',req=True,auto='organization'),
        field('email','Email',typ='email',req=True,auto='email'),
        field('phone','Phone',typ='tel',auto='tel'),
        field('event_type','Event type','select',req=True,opts=list(EV.values())+['Other']),
        field('event_date','Event date',typ='date',req=True, help='Flexible? Pick your preferred date and mention alternatives below.'),
        field('city','City / state',req=True,auto='address-level2',ph='e.g. Las Vegas, NV'),
        field('budget','Budget range','select',opts=['Prefer to discuss','$10,000 – $25,000','$25,000 – $50,000','$50,000 – $100,000','$100,000+'], help='Optional. It helps us match acts and dates.'),
        f'<fieldset class="field full"><legend>Artist interest <span class="muted small">(choose any)</span></legend><div class="checks">{checks}</div></fieldset>',
        field('message','Message','textarea',full=True,ph='Venue capacity, set length, indoor/outdoor, other acts on the bill, anything else we should know.'),
    ])
    body = f'''<section class="page-head">
  <div class="wrap narrow">
    <p class="eyebrow">Book a show</p>
    <h1>Tell us about your event</h1>
    <p class="lead">Share the basics and we'll come back with availability and next steps. No commitment; an inquiry is not a booking.</p>
  </div>
</section>
<section class="section pt0">
  <div class="wrap narrow">
    {form_shell('booking','New booking inquiry: webookshows.com',inner,'Send inquiry')}
    <p class="muted small alt-contact">Prefer email? Write to <a class="js-email" data-show href="{{MAILTO}}">{{EMAIL_TXT}}</a>.</p>
  </div>
</section>'''
    page('book/index.html', f'Book a show: artist booking inquiry | {BRAND}',
         'Send a booking inquiry for hip-hop and West Coast artists: event type, date, city and artist interest. Casinos, festivals, venues, hotel bars, hemp fests and after-parties.',
         body, 1)

def join():
    inner = ''.join([
        field('name','Your name',req=True,auto='name'),
        field('act_name','Act / artist name',req=True),
        field('genre','Genre',req=True,ph='e.g. West Coast hip-hop'),
        field('city','City / region',req=True,auto='address-level2'),
        field('links','Links',typ='textarea',req=True,full=True,ph='YouTube, Spotify, Instagram, EPK: one per line'),
        field('notable','Notable shows, tours or press','textarea',full=True,ph='Festivals, tours, features, charting songs, press coverage.'),
        field('contact','Email or phone',req=True,auto='email'),
    ])
    body = f'''<section class="page-head">
  <div class="wrap narrow">
    <p class="eyebrow">For artists</p>
    <h1>Want to join the roster?</h1>
    <p class="lead">We're always listening. Send a few links and we'll reach out if it's a fit for the buyers we work with.</p>
  </div>
</section>
<section class="section pt0">
  <div class="wrap narrow">
    {form_shell('artist','Artist roster submission: webookshows.com',inner,'Send submission')}
  </div>
</section>'''
    page('join/index.html', f'Artists: join the roster | {BRAND}', 'Artists and managers: submit your act to be considered for the We Book Shows roster.', body, 1)

def about():
    r = rel(1)
    body = f'''<section class="page-head">
  <div class="wrap narrow">
    <p class="eyebrow">About</p>
    <h1>About {BRAND}</h1>
    <p class="lead">{BRAND} is a talent-booking service run by Victoria Imtanes. We connect event buyers with established hip-hop and West Coast artists.</p>
  </div>
</section>
<section class="section pt0">
  <div class="wrap narrow prose">
    <p>Buyers come to us for recognizable names that fit the room: casino showrooms, festival stages, clubs and theaters, hotel bars and pool parties, hemp and cannabis festivals, cultural celebrations, private and business events, and official after-parties.</p>
    <p>We work directly with artists and their teams to confirm availability, put together offers, and keep logistics clear from first email to show day. Offers and terms are confirmed in writing. Availability, fees and final approval always rest with each artist and their team.</p>
    <h2 id="contact">Contact</h2>
    <ul class="contact-list">
      <li><span class="muted">Email</span> <a class="js-email" data-show href="{{MAILTO}}">{{EMAIL_TXT}}</a></li>
      <li class="js-phone-row"{{PHONE_HIDDEN}}><span class="muted">Phone</span> <span>{{PHONE_HTML}}</span></li>
    </ul>
    <p class="cta-row"><a class="btn" href="{r}book/">Book a show</a> <a class="btn btn-ghost" href="{r}roster/">See the roster</a></p>
    <p class="small muted"><a class="quiet" href="{r}join/">Artists: want to join the roster?</a></p>
  </div>
</section>'''
    page('about/index.html', f'About & contact | {BRAND}', 'About We Book Shows, a talent-booking service for established hip-hop and West Coast artists, and how to get in touch.', body, 1, active='about')

def privacy():
    body = f'''<section class="page-head">
  <div class="wrap narrow">
    <p class="eyebrow">Privacy</p>
    <h1>Privacy notice</h1>
    <p class="muted">Last updated: September 2026</p>
  </div>
</section>
<section class="section pt0">
  <div class="wrap narrow prose">
    <h2>What we collect</h2>
    <p>We only collect what you choose to send us through our booking and artist-submission forms or by email: typically your name, company or venue, contact details, event details, and any links or notes you include.</p>
    <h2>How we use it</h2>
    <p>We use your details to reply to your inquiry, check artist availability, and prepare offers. We share event details with an artist's team only as needed to answer your inquiry. We don't sell your information or add you to marketing lists.</p>
    <h2>Form processing</h2>
    <p>Form submissions are delivered to our inbox by a third-party form service (FormSubmit), which processes the data only to deliver it. If the form service is unavailable, your email app opens with your message pre-filled instead.</p>
    <h2>Cookies, analytics and video</h2>
    <p>This site does not use analytics or advertising cookies. Artist videos are hosted on YouTube and load only when you press play, using YouTube's privacy-enhanced mode. At that point YouTube's own privacy policy applies.</p>
    <h2>Your choices</h2>
    <p>You can ask us to see, correct, or delete the information you've sent us at any time by emailing <a class="js-email" data-show href="{{MAILTO}}">{{EMAIL_TXT}}</a>.</p>
  </div>
</section>'''
    page('privacy/index.html', f'Privacy | {BRAND}', 'How We Book Shows handles information sent through its booking and artist forms.', body, 1)

def notfound():
    body = '''<section class="page-head"><div class="wrap narrow"><p class="eyebrow">404</p><h1>That page isn't on the bill.</h1><p class="lead">Try the <a href="/roster/">roster</a> or <a href="/book/">book a show</a>.</p></div></section>'''
    page('404.html', f'Page not found | {BRAND}', 'Page not found.', body, 0)
    # 404 must use root-absolute assets
    p = os.path.join(ROOT, '404.html'); s = open(p).read()
    s = s.replace('href="css/', 'href="/css/').replace('src="js/', 'src="/js/').replace('href="img/', 'href="/img/').replace('href=""', 'href="/"')
    for h in ['roster/','about/','book/','privacy/','join/']:
        s = s.replace(f'href="{h}"', f'href="/{h}"')
    open(p,'w').write(s)

def sitemap():
    urls = ['', 'roster/', 'book/', 'about/', 'join/', 'privacy/'] + [f'artists/{a["slug"]}/' for a in ACTS]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{SITE}/{u}</loc></url>\n' for u in urls) + '</urlset>\n'
    open(os.path.join(ROOT,'sitemap.xml'),'w').write(xml)
    open(os.path.join(ROOT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    open(os.path.join(ROOT,'CNAME'),'w').write('webookshows.com\n')
    open(os.path.join(ROOT,'.nojekyll'),'w').write('')

def og_fallback():
    p = os.path.join(ROOT, 'img', 'og.jpg')
    if os.path.exists(p): return
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), '#0b0a0f'); d = ImageDraw.Draw(im)
    def font(sz):
        for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
            if os.path.exists(f): return ImageFont.truetype(f, sz)
        return ImageFont.load_default()
    d.rectangle((0, 0, 14, H), fill='#f5b82e')
    d.text((80, 150), 'WE BOOK', font=font(110), fill='#f4f1ea')
    d.text((80, 270), 'SHOWS', font=font(110), fill='#f5b82e')
    d.text((80, 420), 'Established hip-hop & West Coast acts for casinos,', font=font(34), fill='#f4f1ea')
    d.text((80, 465), 'festivals, venues & official after-parties', font=font(34), fill='#cfc7da')
    d.text((80, 545), 'webookshows.com', font=font(30), fill='#f5b82e')
    os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p, 'JPEG', quality=85)

if __name__ == '__main__':
    og_fallback()
    home(); roster(); book(); join(); about(); privacy(); notfound(); sitemap()
    for a in ACTS: profile(a)
    print('built', len(ACTS), 'profiles')
