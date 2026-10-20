# https://equatorcompany.com/ — local React clone in this folder (src/App.jsx, src/pages/*, src/components/*), measured in CLONE_SPEC.md

Source: https://equatorcompany.com/ — local React clone in this folder (src/App.jsx, src/pages/*, src/components/*), measured in CLONE_SPEC.md
Status: **measured-from-clone**
3 routes · 3 templates · 16 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 3 templates (Home (single long page), Legal prose, 404 catch-all) account for 3 of 3 routes (100%). The remaining 0 routes span 0 templates.

| template | routes | share |
|---|---:|---:|
| Home (single long page) | 1 | 33% |
| Legal prose | 1 | 33% |
| 404 catch-all | 1 | 33% |

## Page chrome

**1 routes carry chrome = `animated`** — Home (single long page).

**1 routes carry chrome = `static`** — Legal prose.

**1 routes carry chrome = `none`** — 404 catch-all.

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `chrome.header-nav` | CHROME | 2 | 2 | `Header.jsx > Header` | Home and privacy policy. |
| `footer.main` | FOOTER | 2 | 2 | `Footer.jsx > Footer` | Home and privacy policy. |
| `footer.subfooter` | FOOTER | 2 | 2 | `Footer.jsx > Subfooter` | Home and privacy policy. |
| `chrome.logo-zone` | CHROME | 1 | 1 | `Header.jsx > LogoZone` | Home only. |
| `chrome.mobile-header` | CHROME | 1 | 1 | `Header.jsx > MobileHeader` | Home only (the privacy page builds its own bar, see chrome.static-logo-bar). |
| `chrome.static-logo-bar` | CHROME | 1 | 1 | `PrivacyPolicy.jsx > HomeLink + Hamburger` | Privacy policy only. |
| `intro.splash` | INTRO | 1 | 1 | `Splash.jsx` | Home only. |
| `intro.title` | INTRO | 1 | 1 | `Title.jsx` | Home only. |
| `content.story` | CONTENT | 1 | 1 | `Story.jsx` | Home only. |
| `content.values` | CONTENT | 1 | 1 | `Values.jsx` | Home only. |
| `content.capabilities` | CONTENT | 1 | 1 | `Capabilities.jsx` | Home only. |
| `content.our-work` | CONTENT | 1 | 1 | `OurWork.jsx` | Home only. |
| `content.team` | CONTENT | 1 | 1 | `Team.jsx` | Home only. |
| `conversion.cta` | CONVERSION | 1 | 1 | `Cta.jsx` | Home only. |
| `legal.privacy-article` | LEGAL | 1 | 1 | `PrivacyPolicy.jsx > article (lib/privacyBody.js)` | Privacy policy only. |
| `error.not-found` | ERROR | 1 | 1 | `pages/NotFound.jsx` | 404 catch-all only. |

**3 shared sections** appear in more than one template and belong in a component library.

**13 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

## Templates

### Home (single long page) — `template.home`

1 route · `/` · chrome: **animated**

| # | category | section | |
|---:|---|---|---|
| 1 | CHROME | `chrome.logo-zone` | page-local |
| 2 | CHROME | `chrome.mobile-header` | page-local |
| 3 | INTRO | `intro.splash` | page-local |
| 4 | CHROME | `chrome.header-nav` | shared ×2 |
| 5 | INTRO | `intro.title` | page-local |
| 6 | CONTENT | `content.story` | page-local |
| 7 | CONTENT | `content.values` | page-local |
| 8 | CONTENT | `content.capabilities` | page-local |
| 9 | CONTENT | `content.our-work` | page-local |
| 10 | CONTENT | `content.team` | page-local |
| 11 | CONVERSION | `conversion.cta` | page-local |
| 12 | FOOTER | `footer.main` | shared ×2 |
| 13 | FOOTER | `footer.subfooter` | shared ×2 |

### Legal prose — `template.legal`

1 route · `/privacy-policy` · chrome: **static**

| # | category | section | |
|---:|---|---|---|
| 1 | CHROME | `chrome.static-logo-bar` | page-local |
| 2 | CHROME | `chrome.header-nav` | shared ×2 |
| 3 | LEGAL | `legal.privacy-article` | page-local |
| 4 | FOOTER | `footer.main` | shared ×2 |
| 5 | FOOTER | `footer.subfooter` | shared ×2 |

### 404 catch-all — `template.not-found`

1 route · `/*` · chrome: **none**

| # | category | section | |
|---:|---|---|---|
| 1 | ERROR | `error.not-found` | page-local |

## Section reference

### CHROME

_Site-wide header, logo and navigation furniture that frames page content_

**`chrome.logo-zone`** — Sticky oversized wordmark that scales from 1 to 0.6667 over the first half-screen of scroll, then locks small; clicking it scrolls to the title section.

· Home only. · appears on 1 routes · implemented by `Header.jsx > LogoZone`

**`chrome.mobile-header`** — Mobile (<=768px) top bar that appears once the logo is small, with the hamburger toggling the full-screen coral menu and scroll lock.

· Home only (the privacy page builds its own bar, see chrome.static-logo-bar). · appears on 1 routes · implemented by `Header.jsx > MobileHeader`

**`chrome.header-nav`** — Desktop nav with the five in-page anchor links (our story, what we stand for, capabilities, our work, team) plus contact icons; doubles as the mobile slide-down menu panel.

· Home and privacy policy. · appears on 2 routes · implemented by `Header.jsx > Header`

**`chrome.static-logo-bar`** — Non-animated wordmark link home plus hamburger, used where there is no splash or shrinking logo.

· Privacy policy only. · appears on 1 routes · implemented by `PrivacyPolicy.jsx > HomeLink + Hamburger`

### INTRO

_Full-viewport opening blocks at the top of the home page_

**`intro.splash`** — 100svh coral screen with a centred brand Lottie (starts 1s after mount, then loops from frame 270) and a delayed 'Scroll to explore' caption.

· Home only. · appears on 1 routes · implemented by `Splash.jsx`

**`intro.title`** — Three-line headline over a looping bird video in screen blend mode.

· Home only. · appears on 1 routes · implemented by `Title.jsx`

### CONTENT

_Anchored home-page content sections reachable from the main nav_

**`content.story`** — #our-story: paragraph revealed word by word as the reader scrolls, followed by the four merger-company logos.

· Home only. · appears on 1 routes · implemented by `Story.jsx`

**`content.values`** — #what-we-stand-for: five sticky stacked value panels on a lime background, each with its own Lottie, an N/5 counter and a scroll-scrubbed fade-out.

· Home only. · appears on 1 routes · implemented by `Values.jsx`

**`content.capabilities`** — #capabilities: nine accordion cards, one open at a time, with pill reveal on open.

· Home only. · appears on 1 routes · implemented by `Capabilities.jsx`

**`content.our-work`** — #our-work: draggable five-slide project carousel with arrows, followed by a continuously scrolling 'Proud member of' logo marquee.

· Home only. · appears on 1 routes · implemented by `OurWork.jsx`

**`content.team`** — #team: list of fifteen names; the name crossing mid-viewport activates a portrait card, halftone background and LinkedIn tag.

· Home only. · appears on 1 routes · implemented by `Team.jsx`

### CONVERSION

_Blocks whose job is to send the visitor to contact or social channels_

**`conversion.cta`** — Closing call to action over a cloud video with an oat multiply overlay; two buttons that widen and invert colour on hover.

· Home only. · appears on 1 routes · implemented by `Cta.jsx`

### LEGAL

_Long-form legal prose_

**`legal.privacy-article`** — Single long-form privacy policy article rendered from static HTML.

· Privacy policy only. · appears on 1 routes · implemented by `PrivacyPolicy.jsx > article (lib/privacyBody.js)`

### ERROR

_Error-state page bodies_

**`error.not-found`** — Minimal centred '404 / Page not found: <path> / Go back home' body with no site chrome.

· 404 catch-all only. · appears on 1 routes · implemented by `pages/NotFound.jsx`

### FOOTER

_Bottom-of-page contact, credit and funding blocks_

**`footer.main`** — Footer with looping brand Lottie, contact links, social links, privacy policy link and studio credit.

· Home and privacy policy. · appears on 2 routes · implemented by `Footer.jsx > Footer`

**`footer.subfooter`** — Funding strip with the co-funding logos (mono.svg) and the 'Project sheet' PDF link.

· Home and privacy policy. · appears on 2 routes · implemented by `Footer.jsx > Subfooter`
