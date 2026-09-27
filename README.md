# webookshows.com

Talent-booking showcase for **We Book Shows**: established hip-hop and West Coast acts for casinos, festivals, venues, hotel bars, hemp fests, cultural and business events, and official after-parties. It's a static site served from GitHub Pages (main branch, repo root) at https://webookshows.com.

## How it's built

- `_build/data.py`: the roster (bios, regions, signature songs, videos, verified official links, event fit). **Edit acts here.**
- `_build/build.py`: generates every page (home, roster, one profile per act, book form, artist-join form, about/contact, privacy, 404, sitemap).
- `js/config.js`: **the only place contact details live**: email, bookings phone, and form provider (FormSubmit / Formspree / mailto).
- `css/style.css` and `js/main.js`: styles, the forms, the click-to-load YouTube embeds, and the roster filters.
- `.github/workflows/build.yml`: rebuilds and commits the HTML whenever `_build/`, `js/config.js` or `img/` change on `main`.

To build locally, run `WBS_OUT=. python3 _build/build.py`.

## Photos

Artist photos go in `img/artists/<slug>.jpg`, using the photos from the tour one-sheet. If a photo is missing, the build shows a neutral name card instead. When you add photos, the site rebuilds automatically.

## Forms

Both forms post to FormSubmit (`https://formsubmit.co/ajax/<CONTACT_EMAIL>`). The **first submission sends an activation email** to the contact inbox. Click "Activate Form" once, and after that submissions arrive normally. If the service can't be reached, the form falls back to a pre-filled `mailto:`.

## Policy

- No prices or fee guides anywhere. Fees are quoted per date and availability is on request. The only money field is the optional budget range on the booking form.
- Only verifiable facts: no invented chart positions, awards, stats, testimonials or social handles.
- No claim of exclusive representation.
