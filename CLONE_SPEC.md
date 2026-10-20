Source: https://equatorcompany.com/

# The Equator Company: Clone Build Spec

Recon date: 2026-10-20. I measured the live site with Playwright (Chromium) at 1440x900, 1280x800 and 390x844, and cross-checked against the shipped CSS bundles (`entry.DkmCBGCE.css`, `index.Bz9B3sVc.css`, `useSectionWatcher.DxYJ83pd.css`, `privacy-policy.DCQMMc0V.css`) and the JS chunks (`B2rxQMiQ.js` main bundle, `CxvaQVEJ.js` index page, `CrgkewiP.js` footer and composables, `tklmdvPw.js` privacy page). All px values below are computed values, not estimates. If a value comes from source CSS rather than a computed-style read, it says "(CSS)". Asset list and download URLs: `ASSET_MANIFEST.md` (same directory).

Original stack, for reference only: Nuxt 3 / Vue 3 SSR, **Locomotive Scroll v5** (wrapping **Lenis 1.1.9**), **@lottiefiles/dotlottie-web 0.54.1** (canvas Lottie players), **vue3-carousel**, **marquee3k** (vendored), VueUse (`useElementVisibility`, `useIntersectionObserver`, `useWindowSize`, `useElementSize`) and blurhash placeholders. It does **not** use GSAP, ScrollTrigger, WebGL or a custom cursor.

Suggested React equivalents: `lenis` (lerp 0.1), `@lottiefiles/dotlottie-react` (or `dotlottie-web`), a small custom carousel or `embla-carousel-react` (with the behaviour described below), and a custom rAF marquee. IntersectionObserver and scroll-progress hooks are custom.

---

## 0. Routes

| Route | Reached from | Notes |
|---|---|---|
| `/` | logo, home | Single long landing page. Every main-nav item is an **in-page anchor** on `/`. |
| `/#our-story`, `/#what-we-stand-for`, `/#capabilities`, `/#our-work`, `/#team` | main nav | Section ids on `/`. They are not separate routes. |
| `/privacy-policy` | footer "Privacy Policy" link | Second (and last) real route. The router table in `B2rxQMiQ.js` has only `index` and `privacy-policy`. See section 12. |
| `/Equator-PRR-Investimentos.pdf` | subfooter "Project sheet" (`target=_blank`, `download`) | Static PDF. |

External links: `mailto:info@equatorcompany.com`, LinkedIn company page, Mailchimp signup, Google Maps, partner sites, team LinkedIns, studio-cronica.com, recuperarportugal.gov.pt. All of them use `target="_blank"`, except mailto.

There is no language switch, no modal and no cookie banner. Analytics: umami (`umami.upclose.dev`) and Cloudflare RUM. Do not clone the analytics.

---

## 1. Global design tokens (from `entry.DkmCBGCE.css`, verified computed)

### 1.1 CSS custom properties (put these on `:root`)
```css
:root{
  --margin-page:50px;                       /* <=1180px: 30px ; <=768px: 20px */
  --font-size-headline1:6rem;  --font-line-headline1:.98; --font-spacing-headline1:-.03em; --font-weight-headline1:500;
  --font-size-headline2:4.5rem;--font-line-headline2:1.1; --font-spacing-headline2:-.04em; --font-weight-headline2:500;
  --font-size-headline3:3.75rem;--font-line-headline3:1;  --font-spacing-headline3:-.03em;
  --font-size-headline4:2.25rem;--font-line-headline4:1.1;--font-spacing-headline4:-.02em; --font-weight-headline4:500;
  --font-size-body-l:1.5rem;   --font-line-body-l:1.2;    --font-spacing-body-l:-.03em;
  --font-size-body-m:1.3125rem;--font-line-body-m:1.2;    --font-spacing-body-m:-.02em;
  --font-size-body-s:1.125rem; --font-line-body-s:1.2;    --font-spacing-body-s:-.02em;
  --font-size-caption:1rem;    --font-line-body-s:1.18;   --font-spacing-caption:-.03em;   /* sic: the original re-declares --font-line-body-s=1.18 here, so body-s line-height is effectively 1.18; --font-line-caption is never defined, so caption line-height = inherited/normal */
  --color-white:#fff; --color-oat:#fcf8f0; --color-lime:#c8fdab; --color-earth:#3e2002;
  --color-earth-light:rgba(62,32,2,.7); --color-coral:#ff9d69;
}
@media (max-width:1180px){:root{--margin-page:30px}}
@media (max-width:768px){:root{--margin-page:20px;--font-size-headline1:3.25rem;--font-size-headline2:2.25rem;--font-size-headline3:2rem;--font-size-headline4:1.5rem;--font-size-body-l:1.3125rem;--font-size-body-m:1rem}}
```
**Important quirk to replicate:** `--font-line-body-s` is declared twice. The second declaration wins, so textBodyS line-height = **1.18** (computed: 18px → 21.24px). Also, `--font-line-caption` is never defined, so `.textCaption` has `line-height: normal` unless an element overrides it.

### 1.2 Global resets
```css
html,body{font-family:National,Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased;color:var(--color-earth)}
*{margin:0;padding:0}
a{color:currentColor;text-decoration:none;-webkit-tap-highlight-color:transparent}
.noselect{user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}
```
Body background is transparent. Each section paints its own background.

### 1.3 Breakpoints in use
`1366` (footer grid), `1180` (margin 30, story indents, value lottie size, h2 size), `1024` (footer flex, story logos grid, indent 0), `920` (value text 1 col), `768` (mobile: tokens, header, most layouts), `620` (capabilities grid 1 col), `520` (values slide height, slide width, team active band, team padding). All are `max-width` except where noted.

### 1.4 Text role classes (computed at 1440 / 390)

| Class | Desktop size / line-height / letter-spacing / weight | Mobile (<=768) |
|---|---|---|
| `.textHeadline1` | 96px / 94.08px (0.98) / -2.88px (-0.03em) / 500 | 52px / 50.96px / -1.56px / 500 |
| `.textHeadline2` (story text) | 72px / 79.2px (1.1) / -2.88px (-0.04em) / **400** | 36px / 39.6px / -1.44px / 400 |
| `.textHeadline2Medium` | 72px / 79.2px / -2.88px / **500** | 36px / 39.6px / -1.44px / 500 |
| `.textHeadline3` (team names) | 60px / 60px (1) / -1.8px (-0.03em) / 400 | 32px / 32px / -0.96px / 400 |
| `.textHeadline4` | 36px / 39.6px (1.1) / -0.72px (-0.02em) / 500 | 24px / 26.4px / -0.48px / 500 |
| `.textBodyL` | 24px / 28.8px (1.2) / -0.72px (-0.03em) / 400 | 21px / 25.2px / -0.63px |
| `.textBodyM` | 21px / 25.2px (1.2) / -0.42px (-0.02em) / 400 | 16px / 19.2px / -0.32px |
| `.textBodyS` | 18px / 21.24px (1.18) / -0.36px (-0.02em) / 400 | same |
| `.textCaption` | 16px / normal (unless overridden) / -0.48px (-0.03em) / 400 | same |

There is no text-transform anywhere (`none`). Type sizes do not use clamp() or vw. Sizing is purely rem plus the 768 breakpoint. The only viewport-relative sizing is layout: `svh`/`vw` heights and widths, noted per section.

### 1.5 Fonts
- Family **"National"** (Klim Type Foundry, National 2). Self-hosted, `font-display: swap`:
  - weight 400: `https://equatorcompany.com/national-2-regular.woff2` (34,956 B). `src: local("National Regular"), local("National"), url(...) format(woff2)`
  - weight 500: `https://equatorcompany.com/national-2-medium.woff2` (37,072 B). `src: local("National Medium"), url(...)`
- Fallback stack: `National, Arial, Helvetica, sans-serif`.
- These font files are **not** in the saved folder, so download them (see manifest). They are commercial fonts. Check the licence before shipping.

### 1.6 Palette (computed)

| Token | Value | Used by |
|---|---|---|
| coral | `#ff9d69` / rgb(255,157,105) | splash, title section, team, mobile header/menu, dropdown open, pills on dropdowns, `<meta theme-color>` |
| coral-light (hard-coded) | `#feb891` | dropdown pills when open |
| oat | `#fcf8f0` / rgb(252,248,240) | story, capabilities, partners, CTA overlay (multiply), CTA buttons, LinkedIn tag, subfooter text, footer wordmark |
| lime | `#c8fdab` / rgb(200,253,171) | values section bg, slide pills, slide active layer, team role chip, LinkedIn tag hover |
| lime-dark (hard-coded) | `#c1f2a3` | slide pills when active |
| earth | `#3e2002` / rgb(62,32,2) | all text, footer bg, subfooter bg, bullets, nav underline |
| earth-light | rgba(62,32,2,.7) | section subtitles (capabilities, team) |
| white | `#fff` | dropdown cards, slide cards, portrait card, CTA section bg |
| footer text | `#9d8c79` / rgb(157,140,121) | footer text |
| footer credits | `#6d543c` / rgb(109,84,60) | credits row |
| carousel arrows | button color rgb(0,0,0), but the SVGs are filled `var(--color-earth)` | |

---

## 2. Page `/`: overall structure and stacking

Document height: **14,521px at 1440x900**, **13,660px at 1280x800**, **14,040px at 390x844**.

```
<main id="mainContent" style="position:relative">
  div.logoSmallZone          abs; top: calc(150svh + 34px); bottom:0; width:100%; pointer-events:none  (visibility sentinel)
  -- LandingHeader fragment --
  div.logoTrigger            abs; top:0; height: calc(50svh + 34px)   (scroll-progress sentinel)
  div.logoZone               abs; top:0; bottom:0; left:var(--margin-page); right:0; z-index:11; pointer-events:none
    div.logoTopScroll        sticky top:0; height: calc(100% - 50svh - 34px); padding-top: calc(50svh - 34px); box-sizing:border-box
      div.logoCont(.small)   sticky top:0; height:68px; display:flex; align-items:center
        a.textHeadline4 (href "/")   display:flex; align-items:flex-end; height: calc(36px*1.1)=39.6px; transform-origin:left center; transform: scale3d(s,s,1)
          svg wordmark 352x34
  div.mobileHeader           (mobile only, see 4.3)
  section.splash             100svh, coral
  div.headerCont             sticky top:0; z-index:10; pointer-events:none  -> header (68px) -> nav
  -- end header --
  section.titleSection       100svh coral   (no id)
  section#our-story.story    oat
  section#what-we-stand-for.values  lime
  section#capabilities.capabilities oat
  section#our-work.partners  oat
  section#team.team          coral
  section.ctaSection         100svh white (+ oat multiply overlay)
  footer                     earth
  div.subfooter              earth
</main>
```

Section vertical map at 1440x900 (y = document top, height):

| Section | y | h | bg |
|---|---|---|---|
| splash | 0 | 900 | #ff9d69 |
| headerCont/header (sticky) | 900 | 68 (margin-bottom -68px, so it takes up no flow space) | transparent |
| titleSection | 900 | 900 | #ff9d69 |
| story #our-story | 1800 | 2115 | #fcf8f0 |
| values #what-we-stand-for | 3915 | 3900 | #c8fdab |
| capabilities | 7815 | 1354 | #fcf8f0 |
| partners #our-work | 9168 | 1391 | #fcf8f0 |
| team | 10560 | 2114 | #ff9d69 |
| ctaSection | 12673 | 900 | #fff |
| footer | 13573 | 731 | #3e2002 |
| subfooter | 14305 | 216 | #3e2002 |

At 1280x800: splash 0/800, title 800/800, story 1600/2115, values 3715/3400, capabilities 7115/1354, partners 8468/1331, team 9799/2114, cta 11913/800, footer 12713/731, subfooter 13444/216.
At 390x844: splash 0/844, title 844/844, story 1688/1218, values 2906/5730, capabilities 8636/1312, partners 9948/1016, team 10965/1537, cta 12502/617, footer 13118/762, subfooter 13881/159.

---

## 3. Smooth scroll and the scroll-progress engine

- **Locomotive Scroll v5** is instantiated with **no options** (`new LocomotiveScroll()`) on page mount and destroyed on unmount. Internally it creates **Lenis 1.1.9** with defaults: `lerp: 0.1`, `smoothWheel: true`, `syncTouch: false` (native touch scrolling), `wheelMultiplier: 1`, `touchMultiplier: 1`, `orientation: vertical`, `gestureOrientation: vertical`, wrapper = window. Sets `data-scroll-orientation="vertical"` on `<html>`. React: `new Lenis({ lerp: 0.1, smoothWheel: true })` driven by rAF.
- Locomotive is used only for **`data-scroll-event-progress`** elements. These dispatch `window` CustomEvents with `detail.progress` in [0, 1] every frame the progress changes. Progress formula (from source):
  - `data-scroll-position="A,B"` (default `"start,end"`). Let `vh` = innerHeight, `top` = element's document top, `h` = its height.
  - start: `A=start` → `top - vh`; `A=end` → `top - vh + h`. **If the element starts inside the first viewport (`top < vh`) the start is forced to 0 ("fold").**
  - end: `B=start` → `top`; `B=end` (default) → `top + h`. If end <= start, then end = start+1 (B=start) or start+h (B=end).
  - `progress = clamp((scrollY - start) / (end - start), 0, 1)`.
- Four sentinels use this. They are listed in each section below: `logoTrigger` (`logoTriggerProgress`), `lettersTrigger` (`lettersTriggerProgress`), `hide1..4Trigger` (`hide{n}Progress`).
- There are no data-scroll-speed parallax elements.

### Nav / anchor scrolling (custom, not Lenis `scrollTo`)
`scrollToY(targetY)` from the index chunk:
```js
// duration (s) = clamp(|target - current| / 2000, 0.1, 0.8); easing easeOutSine = sin(t*PI/2)
let t=0; const dur=Math.max(.1,Math.min(Math.abs(cur-target)/2000,.8));
function step(){ t+=1/60; const p=t/dur; if(p<1){ requestAnimationFrame(step); window.scrollTo(0, cur+(target-cur)*Math.sin(p*Math.PI/2)); } else window.scrollTo(0,target); }
```
- Desktop (>768): nav item scrolls to `getYPosition(#id)` (section's document top). The logo scrolls to `section.titleSection` top (= 1 viewport height). The router hash is not set on click. The section watcher sets it later.
- Mobile (<=768): close the menu first, then after `setTimeout 50ms` scroll to `top - 40`.
- Clicking a team name scrolls so that name is centred. Desktop: `nameTop - vh/2 + nameH/2`. Width < 520: `nameTop - vh/4 + nameH/2`.

### Section watcher (URL hash + active nav)
- An IntersectionObserver over all section components, with `rootMargin "-49% 0px -49% 0px"` and `threshold [0,.25,.5,.75,1]`. On change, a rAF picks the section whose rect spans `innerHeight/2`. With none, it falls back to the last one above.
- If that section has an `id`, call `router.replace({hash:'#id'})`. Sections with no id (title, CTA, footer) clear the hash. The update is **debounced 500ms**.
- Nav links get class `.active` when `route.hash === '#id'`, which shows a permanent underline (see 4.2).
- Verified at 1440 (500ms after each jump): y=1800 → `#our-story`; y=4000 → `#what-we-stand-for`; y=11400 → `#team`; y=13621 (footer) → hash cleared. A reading at y=11180 still showed `#capabilities` because the 500ms debounce had not flushed yet.

---

## 4. Header, logo, splash and mobile menu (LandingHeader)

### 4.1 Splash (`section.splash`)
- `height:100svh; background:#ff9d69; display:flex; align-items:flex-end; justify-content:center; padding:var(--margin-page); position:relative; box-sizing:border-box`.
- `.lottieCont`: `position:absolute; left:50%; top:50%; transform:translate3d(-50%,-50%,0); aspect-ratio:335/394; width:calc(100vw - var(--margin-page)*2); max-width:calc(85.02538svh - 127.53807px)`.
  - Measured: 1440x900 → x401 y75, 638x750. 1280x800 → x364 y75, 553x650. 390x844 → x20 y216, 350x412.
  - Contains a dotLottie canvas player: `src="/lottie/navbar.lottie"`, `layout:{fit:"contain"}`, 100% x 100%. Animation: 511x720 comp, 30fps, frames 0–601. **The canvas artwork itself is UNMEASURABLE via DOM** (canvas-rendered). Use the .lottie file.
  - Playback: **not autoplay**. After `setTimeout(1000)` call `play()` from frame 0. On the first `complete` event, call `setSegment(270, totalFrames-1)`, `setLoop(true)` and `play()`. That is: an intro of 0→600 (about 20s), then loop frames 270→600 (about 11s).
- `.textBodyS` caption "Scroll to explore" (18px/21.24px, -0.36px). It is centred at the bottom: at 1440 it sits at x657 y829, 126x21 (bottom edge = 900 - 50 padding). Mobile: x132 y803.
  - It contains a `<span>` showing the live logo progress number. The span is `opacity:0; position:absolute; width:0; pointer-events:none`, so it is invisible. Render the span empty or omit it.
  - `transition: opacity .2s ease-in-out`. The splash gets class `.hide` (caption `opacity:0`) when **(a)** for the first **2500ms** after mount, or **(b)** logo-small zone is visible (scrollY > 0.5vh+34). So the caption fades in at 2.5s and fades out once you scroll past about 484px (900vh).

### 4.2 Desktop header (>768)
- `div.headerCont`: `position:sticky; top:0; width:100%; z-index:10; pointer-events:none`. It sits in flow right after the splash, so at load the nav sits at y=900 (below the fold). It scrolls up with the page and sticks at top:0 from scrollY >= 900.
- `header`: `display:flex; justify-content:space-between; align-items:center; height:68px; margin-bottom:-68px; padding:0 var(--margin-page); position:relative; box-sizing:border-box; width:100%`. **Background: transparent.** The nav floats over content.
  - child 1: `div.logoSpace` (empty, 0x0).
  - child 2: `nav.textBodyS`: `display:flex; align-items:center; gap:20px; pointer-events:auto`. At 1440 it sits at x815, 575x24, vertically centred (link text top y = header top + 23).
    - Links (`a.navlink`, inline-block, relative): "Our Story" (73px wide) → `/#our-story`, "What we stand for" (139) → `/#what-we-stand-for`, "Capabilities" (90) → `/#capabilities`, "Our Work" (72) → `/#our-work`, "Team" (42) → `/#team`. Text 18px/21.24px, -0.36px, earth.
    - Underline: `a.navlink:after{content:"";position:absolute;left:0;bottom:-1px;width:100%;height:.06em;background:var(--color-earth);transform:scaleX(0);transform-origin:bottom right;transition:transform .12s ease-out}`. On hover (hover:hover) and `.active`: `transform:scaleX(1);transform-origin:bottom left`.
    - `div.icons`: `display:flex; align-items:center; gap:10px`. Two 24x24 icon links: mail (`mailto:info@equatorcompany.com`, stroke icon) and LinkedIn (`https://www.linkedin.com/company/the-equator-company/`, `target=_blank rel="noopener noreferrer"`). Each has a `<span>` label ("Email us", "LinkedIn") with `display:none` on desktop. SVGs are in Appendix A of the manifest.
- **Logo** (`.logoZone`, z-index 11, above header):
  - The left edge sits at `--margin-page`. At load the logo is vertically centred in the splash: the logoCont box is at y=416 (= 50vh - 34) and the link is at y430, 352x40 (svg 352x34 at y436).
  - `.logoTopScroll` is sticky with padding-top `calc(50svh - 34px)`, so the logoCont reaches top:0 when scrollY ≈ 416 and then stays pinned at top:0 (68px row, vertically centred, aligned with the nav row) for the rest of the page. Its sticky parent ends 50svh+34px before the page bottom.
  - Scale: `transform: scale3d(s, s, 1)` with `transform-origin:left center`, where `s = 1 - progress*0.3333`. `progress` = `logoTriggerProgress`, the logoTrigger sentinel at top 0 with height `50svh+34px` in the fold, so `progress = clamp(scrollY / (0.5*vh + 34))`. Measured at 1440x900: y0 → 1.0, y100 → 0.9311, y242 → 0.83335, y484 → 0.6666. No CSS transition (scroll-linked; smoothness comes from Lenis).
  - Class `.small` (`transform:scale3d(.6666,.6666,1)`) is added whenever `div.logoSmallZone` (top `150svh+34px` to page bottom) is in the viewport, i.e. scrollY > 0.5vh+34. It holds the logo at 0.6666 for the rest of the page. Small-logo rendered width = 352*0.6666 ≈ 235px.
  - Click: prevent default and scrollToY(titleSection top).
- The SVG wordmark "The Equator Company" (352x34, `fill="currentColor"`) is in manifest Appendix A as `logoWordmark`.

### 4.3 Mobile header and menu (<=768)
- `.logoZone .logoTopScroll` becomes `position:fixed; padding-top:0`. `.logoCont` keeps 68px height with `align-items:flex-end`. The link is `height:34px; margin-bottom:14px; align-items:flex-start`. The logo sits at x20 y20 (352x34 at scale 1) and is **always fixed at the top**. It scales with the same progress formula: y200 → 0.8538, y456 → 0.6666 (at 844vh). Logo font-size context is 24px, but the SVG is fixed 352x34 regardless. (Source CSS has `transform:left top` on mobile, which is an invalid declaration and is ignored; the inline scale var still applies.)
- `div.mobileHeader`: `display:flex; position:fixed; top:0; width:100%; height:68px; margin-bottom:-68px; padding:0 var(--margin-page); justify-content:flex-end; align-items:center; background:#ff9d69; z-index:10; opacity:0; pointer-events:none; transition:opacity .2s ease-in-out`. With `.visible` (same condition as logo `.small`): `opacity:1; pointer-events:auto`. It contains the hamburger button at x346 y18, 24x32.
- Hamburger ("squeeze" variant, from hamburgers.css):
  ```css
  .hamburger{--pad-x:3px;--pad-y:6px;--w:18px;--h:2px;--sp:4px;padding:6px 3px;background:transparent;border:0;cursor:pointer;display:inline-block;pointer-events:auto;transition:opacity .15s linear, filter .15s linear}
  .hamburger-box{display:inline-block;position:relative;width:18px;height:calc(2px*3 + 4px*2) /*14px*/}
  .hamburger-inner,.hamburger-inner:before,.hamburger-inner:after{position:absolute;width:18px;height:2px;background:var(--color-earth);transition:transform .15s ease}
  .hamburger-inner{display:block;top:50%;margin-top:-1px}
  .hamburger-inner:before,.hamburger-inner:after{content:"";display:block}
  .hamburger-inner:before{top:-6px} .hamburger-inner:after{bottom:-6px}
  .hamburger--squeeze .hamburger-inner{transition-duration:75ms;transition-timing-function:cubic-bezier(.55,.055,.675,.19)}
  .hamburger--squeeze .hamburger-inner:before{transition:top 75ms ease .12s,opacity 75ms ease}
  .hamburger--squeeze .hamburger-inner:after{transition:bottom 75ms ease .12s,transform 75ms cubic-bezier(.55,.055,.675,.19)}
  .hamburger--squeeze.is-active .hamburger-inner{transform:rotate(45deg);transition-delay:.12s;transition-timing-function:cubic-bezier(.215,.61,.355,1)}
  .hamburger--squeeze.is-active .hamburger-inner:before{top:0;opacity:0;transition:top 75ms ease,opacity 75ms ease .12s}
  .hamburger--squeeze.is-active .hamburger-inner:after{bottom:0;transform:rotate(-90deg);transition:bottom 75ms ease,transform 75ms cubic-bezier(.215,.61,.355,1) .12s}
  ```
  `type="button" aria-label="Menu"`. Click toggles `open`.
- Menu = the same `header` restyled. `.headerCont` becomes `position:fixed; inset:0; z-index:9`. `header` becomes `flex-direction:column; align-items:flex-start; justify-content:space-between; height:100%; background:#ff9d69; transform:translate3d(0,-100%,0); transition:transform .2s ease-in`. With `.open`: `transform:translateZ(0); transition:transform .2s ease-in-out`.
  - `nav`: `flex-direction:column; align-items:flex-start; gap:12px; padding-bottom:70px`. The nav stack sits at the bottom of the screen. Links use headline2 sizes: 36px / 39.6px / -1.44px. Measured open at 390x844: "Our Story" x20 y462 140x40; "What we stand for" y514 266x40; "Capabilities" y565 172x40; "Our Work" y617 138x40; "Team" y668 81x40. Underline `:after` hidden on mobile.
  - `.icons`: `gap:50px; margin-top:30px`. Each `a` is `display:flex; align-items:center; gap:6px` with its label span shown: "Email us" (x20 y750 95x24) and "LinkedIn" (x165 y750 96x24), 18px.
  - While open, a `v-scroll-lock` directive sets `body{overflow:hidden}`, verified as inline `style="overflow: hidden;"` on body.
  - The logo (z 11) remains visible above the open menu (z 9) and above mobileHeader (z 10). The hamburger animates to an X.
  - Link click: close the menu, wait 50ms, then scrollToY(section top - 40).
- Quirk: before the mobileHeader becomes visible (scrollY < 0.5vh+34) the hamburger is invisible (parent opacity 0) but `pointer-events:auto` on the button means it is still clickable. Replicate or ignore.

---

## 5. Title section (`section.titleSection`, LandingTitle)

- `height:100svh; background:#ff9d69; padding:var(--margin-page); box-sizing:border-box; position:relative; overflow:hidden; display:grid; grid-template-rows:120px 1fr 120px; align-items:center`. Mobile: `grid-template-rows:160px 1fr min-content`.
- Children:
  1. empty `div` (row 1).
  2. `div.title`: `display:flex; align-items:center; height:100%`. At 1440: x50 y1070, 1340x560. Mobile: `align-items:flex-start`, x20 y1024 350x543.
     - `h1.textHeadline1`: **"Enabling the<br>Infrastructure<br>of Change"**. 96px/94.08px, -2.88px, 500, earth. Box at 1440: x50 y1209, 574x282. Mobile: 52px, x20 y1024, 311x153.
  3. `div.subtitle.textBodyL`: `display:grid; grid-template-columns:20px 1fr; gap:8px`. At 1440: x50 y1661 1340x58. Mobile: x20 y1567, 350x101, 21px.
     - `div.circle`: 20x20, `border-radius:50%`, bg earth, `margin-top:4px`.
     - `span` (`max-width:630px; text-wrap:balance`): **"Made to endure, designed to adapt: we help organizations and places deliver sustainable, resilient and profitable impact."** 24px/28.8px, -0.72px.
  4. `div.videoLayer`: `position:absolute; bottom:0; left:50%; transform:translate(-50%); height:calc(100% - 64px); aspect-ratio:150/85; mix-blend-mode:screen`. Mobile: `height:calc(100% - 110px)`. Measured: 1440 → x-18 y964 1475x836; 1280 → x-9 y864 1299x736; 390 → x-453 y954 1295x734 (it overflows and is clipped by section overflow:hidden).
     - `<video src="/bird_low.mp4" autoplay muted loop playsinline>` with `width:100%; height:100%; object-fit:contain; object-position:bottom center`. Video is 1000x850, 11.3s. **Blend `screen` over coral is essential.** (The video likely has a dark background that disappears under screen.)
- No entrance animation on the title text. It is static.

---

## 6. Story (`section#our-story.story`, LandingStory)

- `background:#fcf8f0; position:relative`.
- `div.lettersTrigger`: `position:absolute; top:50svh; bottom:100svh` (no left/right, so 0 width). It has `data-scroll data-scroll-position="start,end" data-scroll-event-progress="lettersTriggerProgress"`. That gives progress 0 at `scrollY = storyTop - 0.5vh` and 1 at `scrollY = storyBottom - vh`. At 1440x900: 1350 → 3015. At 390x844: 1266 → 2062.
- `div.introCont.textHeadline2`: `display:flex; flex-direction:column; gap:50px; max-width:1100px; margin:0 auto; padding:250px var(--margin-page) 350px; box-sizing:border-box; width:100%; text-wrap:balance; transform:translateZ(0)`. Text is 72px/79.2px, -2.88px, **weight 400**. Mobile: `gap:30px; padding:75px var(--margin-page) 100px`, 36px/39.6px.
  - At 1440: container x170 1100 wide, content x220 1000 wide. At 1280: container x90, content x140.
- Content blocks in order (copy is exact; every word is a separate `<span class="word">` followed by a trailing space inside the span):
  1. `p`: "Born from the merger of four companies with different skill sets, but the same shared values, expertise and decades of experience:" (21 words). At 1440: y2050, 1000x396 (5 lines).
  2. `div.logos`: `display:flex; align-items:center; gap:72px; margin-left:160px; padding:25px 0`. Margin-left is 80px at <=1180. At <=1024 it becomes `display:grid; grid-template-columns:min-content 1fr; gap:36px; margin-left:0`. Each `div.logo` has bg oat and contains `a[target=_blank] > img` with `height:auto; mix-blend-mode:multiply`:
     - `/logo_s317.png` (372x179, alt "S317") → https://s317consulting.com/ , width **185px** (mobile 135)
     - `/logo_sairdacasca.png` (167x186, alt "Sair da Casca") → https://www.sairdacasca.com/ , width **83px** (mobile 60)
     - `/logo_engidro.png` (353x146; the img attribute says 356x146, alt "Engidro") → https://engidro.pt/ , width **176px** (mobile 128)
     - `/logo_factorsocial.png` (402x111, alt "Factor Social") → https://factorsocial.pt/ , width **200px** (mobile 146)
     - At 1440 the row is at x380 y2496, 840x156. Images: x380/637/792/1040, centred vertically. Mobile 2x2 grid: (20,2056) (191,2056) (20,2165) (191,2172).
  3. `p`: "What emerged isn't just bigger. It is different." (8 words)
  4. `p.indent` (margin-left 160 / 80 at <=1180 / 0 at <=1024): "It is designed to provide a structured full-service ESG offer." (10 words)
  5. `p`: "It is a unique partner for organizations seeking change." (9 words)
  6. `p.indent`: "And it is here: meet **The Equator Company**". The last 3 words have class `.b` (`font-weight:500`). This is the word index >= 5 within the sentence.
- **Word-by-word reveal (scroll-scrubbed):**
  - The CSS is `.introCont p span{display:inline-block;opacity:0;transition:opacity .25s ease-in-out}` and `span.a{opacity:1}`. The logo images follow the same rule: `.logo img{opacity:0;transition:opacity .25s ease-in-out}` and `.logo.a img{opacity:1}`.
  - Counting runs across all blocks with the 4 logos counted as 4 "words" (positions 22–25). Total `c = 60`. An item with 1-based global index `k` gets class `a` when `k <= progress * 60`. It is reversible: scrolling up removes the class.
  - Measured at 1440: y1500 → 5/56 words; y1800 → 16; y2000 → 21 words + 2 logos; y2400 → 33 + 4 logos; y2800 → 48; y3200 → 56/56.
  - Initial state at load is all hidden (opacity 0).

---

## 7. Values (`section#what-we-stand-for.values`, LandingValues + ObjectValue x5)

### 7.1 Geometry
- `.values{--slide-height:100svh; --slide-spacing:170px; background:#c8fdab; position:relative; height:calc(80px + var(--slide-height)*5 - var(--slide-spacing)*4)}`. At <=520: `--slide-height:150svh`. Heights: 3900 @900vh, 3400 @800vh, 5730 @844vh mobile.
- `.numbersCont`: `position:absolute; top:80px; bottom:50px; left:50px; z-index:2`. Mobile: `left:auto; right:var(--margin-page)`.
  - `.number.textBodyL`: `position:sticky; top:0; height:calc(100svh - 50px); display:flex; align-items:flex-end`. The text **"N/5"** therefore sits pinned near the bottom-left of the viewport (text bottom ≈ vh - 50px; at 1440 text x50, 29x29). Mobile: `top:86px; height:auto; align-items:flex-start`, so it is pinned top-right at x345, 25x25, 21px.
- `.valuesCont`: `position:relative; height:100%; width:100%; padding:250px 0 350px; box-sizing:border-box`.
- Five `.scrollZone`: `position:absolute; left:var(--margin-page); right:var(--margin-page); bottom:350px`, with `top` of: #1 `80px`; #n `calc(80px + var(--slide-height)*(n-1) - var(--slide-spacing)*(n-1))`. At 900vh the tops are 80, 810, 1540, 2270, 3000 relative to the section (document y 3995, 4725, 5455, 6185, 6915).
  - `.value`: `position:sticky; top:0; min-height:400px; padding-top:170px; display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); grid-template-rows:min-content min-content; gap:60px 20px`. Measured box is 1340x570. Mobile: `display:flex; flex-direction:column; gap:20px; padding-top:250px` (350x650).
    - `.lottieTrigger`: `position:absolute; left:0; right:0; top:50svh` (0-height visibility sentinel).
    - `.lottieCont`: `position:absolute; left:0; top:135px; width:253px; height:255px`. <=1180: 190x190, top 153. <=768: 140x140, top 90. It holds a dotLottie canvas (`/lottie/<name>.lottie`, fit contain).
    - `h2.textHeadline1`: `grid-column:4 / span 9`. 96px/94.08px, -2.88px, 500. At 1440: x390 y(+170), 1000x188 (2 lines). At 1280: x350, 880 wide. 769–1180: headline2 sizes (72/79.2/-0.04em). Mobile: 52px, 350x153.
    - `.text.textBodyM`: `grid-column:4 / span 8; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:20px`. <=920: 1 column, gap 10px. At 1440: x390, 887 wide; each `p` is 433 wide (380 at 1280); 21px/25.2px. Mobile 16px/19.2px.
- Copy (titles contain `<br>`):
  1. lottie `sustainability`. **"Sustainability,<br />made to endure"**. Col 1: "We embed sustainability in the foundations of economies and communities - rooted in systems, strategies, and infrastructure that endure." Col 2: "From energy, water and wastewater infrastructure to multiyear sustainability strategies."
  2. lottie `global`. **"Local legitimacy,<br />global reach"**. Col 1: "Born from a merger of different organizations, we combine the independence of each to create a more dynamic structure for all." Col 2: "Our trusted network of local partnerships across the globe aligns diverse interests, ensures delivery on the ground and delivers systemic change."
  3. lottie `grounded`. **"Vision grounded<br />in reality"**. Col 1: "Bridging ambition and execution to make transitions work, moving institutions from objectives to results. We stay close to our clients to understand their long-term vision, and deliver it:" Col 2: "from inclusive 360º waste management blueprint to decarbonization roadmaps."
  4. lottie `curiosity`. **"We blend curiosity <br />with courage"**. Col 1: "Engaging every challenge with curiosity and openness, bringing in fresh ideas and perspectives to discover real-world solutions." Col 2: "That’s how we’ve been helping turn sanitation data into better services and shaping journeys toward sustainability."
  5. lottie `difference`. **"Making a difference<br />and making it last"**. Col 1: "Our work doesn’t end at strategy handover or ribbon-cutting. We are committed to real-world impact: we design it, we implement it, and we monitor it." Col 2: "45+ years of experience on and off the field have shown our transformations to be not only possible but practical."

### 7.2 Motion: stacked sticky "slides" with a cross-fade
- Each `.value` pins at the top. The next scrollZone starts `slide-height - 170px` lower, so the next value scrolls up into place while the previous one is still pinned. Because there is no background on `.value`, the previous value must disappear first. Four `hideNTrigger` sentinels handle that:
  - `.hideNTrigger{position:absolute; height:85svh; top:calc(-320px + var(--slide-height)*N - var(--slide-spacing)*N)}` (relative to valuesCont), with `data-scroll-position="end,start"`. That gives progress 0→1 between `scrollY = T - 0.15vh` and `scrollY = T`, where `T` = trigger document top (= valuesTop - 320 + N*(slideH - 170)).
  - Value N's opacity = `1 - hideNProgress` (inline CSS var on the section; value 5 never hides). It is **scroll-scrubbed with no CSS transition**: a linear fade over 0.15vh (135px at 900vh).
  - Measured at 1440: value1 opacity 1 at y4189, 0.962 at y4195, 0 at y4600; value2 0.406 at y5000. Hide1 range 4190→4325, hide2 4920→5055, hide3 5650→5785, hide4 6380→6515.
  - Note: the original's refs initialise to 0, so values 1–4 are opacity 0 until their sentinel first reports. They are offscreen at that point. **Initialise to 1** for the same visual result.
- **Counter "N/5"**: five 1px `stepNTrigger` divs (`top` = same as scrollZone N tops, `left:0; right:0`, ids `step1..5`) are observed with IntersectionObserver `rootMargin: "50% 0% -100% 0%"`. That observation zone is the band from 0.5vh **above** the viewport top to the viewport top. When step N intersects (i.e. it has just scrolled past the top, within half a viewport), set N. The value is never reset on exit. It is a text swap with no animation. Verified: y4600 → 1/5, y5000 → 2/5, y5800 → 3/5.
- **Value lotties**: each `.lottieCont` player is not autoplay. It plays the first time `.lottieTrigger` becomes visible (`useElementVisibility`, threshold 0), or after a 1000ms mount timeout if already visible. On its first `complete`: `setSegment(60, totalFrames-1)`, loop, play. Lottie specs: all 253x253 @30fps. Frames: sustainability 300, global 300, grounded 300, curiosity 150, difference 241. **Lottie artwork/colours UNMEASURED (canvas)**. Use the .lottie files.

---

## 8. Capabilities (`section#capabilities.capabilities`, LandingCapabilities + ObjectDropdown x9)

- `background:#fcf8f0; display:flex; flex-direction:column; gap:40px; padding:150px var(--margin-page)`. Mobile: `gap:30px; padding:75px var(--margin-page)`.
- `h2.textHeadline2Medium` (`max-width:700px; text-wrap:balance`): **"Your partner for a sustainable transition"**. At 1440: x50 y7965, 700x158 (2 lines). Mobile 350x79.
- `p.subtitle.textBodyL` (`max-width:570px; color:rgba(62,32,2,.7)`): **"With experience and expertise in a wide range of areas, we’re here to design and implement high-impact, long-lasting change with your organization. Whatever the scale, scope, service or challenge."** 570x115.
- `div.grid`: `display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:20px; margin-top:20px`. Mobile gap 12px; <=620 one column. At 1440 it sits at x50 y8338 1340x680 and cards are 660 wide (580 at 1280; 350 at 390).
- **Dropdown card** (`div.dropdown.noselect`, click toggles; accordion with only one open at a time, and clicking the open card closes it):
  ```css
  .dropdown{--min-height:120px;position:relative;overflow:hidden;cursor:pointer;background:#fff;border-radius:5px;height:var(--h);transition:height .12s ease-in-out,background-color .12s ease-in-out}
  /* --h = open ? calc(<contentHeight>px + var(--min-height)) : var(--min-height) ; mobile --min-height:84px */
  .dropdownHeader{padding:20px}                         /* mobile 16px */
  .dropdownHeader h3{max-width:400px;text-wrap:balance} /* .textHeadline4 36/39.6/-0.72/500; 769–1180: font-size 1.875rem; mobile max-width:calc(100% - 40px) */
  .dropdownContent{opacity:0;transition:opacity .12s ease-in-out}
  .dropdownContent p{padding:0 170px 20px 20px}          /* .textBodyM ; 769–1180 uses body-s sizes; mobile padding:0 60px 16px 16px */
  .plusPill{position:absolute;right:10px;bottom:0;width:120px;height:60px;border-radius:60px 60px 0 0;background:#ff9d69;z-index:3;transform:translate3d(0,100%,0);transition:transform .12s ease-in}
  .plusPill svg{position:absolute;bottom:14px;left:calc(50% - 12px);transition:opacity 60ms ease-in-out 60ms}
  .otherPill{position:absolute;right:10px;bottom:-60px;width:120px;height:60px;border-radius:60px 60px 0 0;background:#ff9d69;z-index:3;transform:translateZ(0);transition:transform .12s ease-in}
  @media (max-width:768px){.plusPill{border-radius:30px 30px 0 0;height:30px;width:60px;right:16px;transform:translateZ(0)} .plusPill svg{bottom:2px} .otherPill{border-radius:30px 30px 0 0;height:30px;width:60px;right:16px;bottom:-30px}}
  .dropdown.open{background:#ff9d69}
  .dropdown.open .plusPill,.dropdown.open .otherPill{background:#feb891;transform:translate3d(0,-100%,0);transition:transform .12s ease-out}
  .dropdown.open .plusPill svg{opacity:0;transition:opacity 60ms ease-in-out}
  .dropdown.open .dropdownContent{opacity:1;transition:opacity .12s ease-in-out 60ms}
  @media (hover:hover){.dropdown:hover:not(.open) .plusPill{transform:translateZ(0);transition:transform .12s ease-out}}
  ```
  - Behaviour summary. **Desktop:** the pill is hidden below the card edge and **slides up into view on hover** (a 120x60 coral half-capsule with a "+" icon, 24x24 earth). When open, the card turns coral, the height animates to header + content, both pills slide up by 100% and turn #feb891, the "+" fades out, and the text fades in. **Mobile:** the 60x30 pill is always visible.
  - Measured open (card #2 at 1440): height 266 = 145.97 content + 120. Bg rgb(255,157,105). Pills rgb(254,184,145), translateY(-60px).
  - Card heights closed: 120 (84 mobile). The h3 is 40px tall for 1-line titles and 79px for 2-line ones ("Energy, Carbon & Biodiversity", "Crisis & Communications Management", "Waste & Circular Economy").
- Copy (title, then description), in grid order (left/right alternating):
  1. **Sustainability Strategy**: "We design ESG strategies, implement financially sustainable action plans, ensure transparency and compliance, and mobilize stakeholders — driving sustainable growth, resilience, and measurable value for your business."
  2. **Energy, Carbon & Biodiversity**: "We help you lead the energy transition. We design sustainable solutions, networks and hybrid systems, structure finance mechanisms, conduct environmental audits and support carbon credits certification."
  3. **Impact & Risks**: "Integrate sustainability into your risk management and investment decisions. We assess impacts, compliance, and risk mitigation to strengthen your organizational resilience."
  4. **Water & Sanitation**: "We promote sustainable investment in resilient infrastructure. We provide technical assistance, apply Nature-Based Solutions and ensure efficiency, safety and resilience in water and wastewater systems."
  5. **Crisis & Communications Management**: "Prepare. Respond. Recover. We manage crises, reputation and communications to safeguard trust, continuity and institutional credibility."
  6. **Capacity Building**: "Turn knowledge into performance: we train teams, build skills and inspire leadership for a tangible application of sustainability and the green and digital transition."
  7. **Social & Communities**: "We create human impact. We help engage communities, promote inclusion and manage sustainable and social investments that generate lasting shared value."
  8. **Waste & Circular Economy**: "We embed circularity into core business processes and operations. We help organisations shift from linear to circular thinking — implementing circular models, reducing waste, accelerating industrial renewal and driving long-term resilience."
  9. **Sustainable Finance**: "Beyond buzzwords, we use the EU Taxonomy, hard-number financial modeling, blended finance and ESCO models to make your business sustainable and profitable."

---

## 9. Partners / Our Work (`section#our-work.partners.noselect`, LandingPartners)

- `background:#fcf8f0; box-sizing:border-box; width:100%; overflow:hidden; padding:150px var(--margin-page) 200px`. Mobile: `75px var(--margin-page) 100px`.
- `h2.textHeadline2Medium` (`max-width:700px; text-wrap:balance`): **"Trusted by those driving change"**. At 1440: x50 y9318 700x158.
- `div.navigationSpace`: height 100px (mobile 80px). The carousel arrows render inside this space.
- **Carousel** (vue3-carousel: `itemsToShow:"auto"`, `gap:20`, `snapAlign:"start"`, transition 300ms ease-out on the track transform, `mouseDrag:true`, `touchDrag:true`, `wrapAround:false`). The viewport is `overflow:visible`, so slides bleed off the right edge of the page. The section's `overflow:hidden` clips them.
  - Track: `display:flex; gap:20px; transform:translateX(-index*(slideW+20)px)`. Measured after "next": translateX(-650px) at 1440.
  - Arrows: `button.carousel__prev` at `left:-6px; top:-35px` and `button.carousel__next` at `left:24px; right:auto; top:-35px` (relative to the carousel). Each is 30x30, transparent, no border, `transition:opacity .12s ease-in-out`. Disabled state: `opacity:.2` (prev is disabled at index 0, next at the last index). At 1440: prev x44 y9527, next x74 y9527. Icons are 24x24 earth arrows (Appendix A).
  - Slides: `li.carousel__slide` (`display:flex; align-items:center; justify-content:center; flex-shrink:0`). Each contains a `div.slide`:
  ```css
  .slide{position:relative;width:calc(50vw - 90px);aspect-ratio:66/50;background:#fff;border-radius:5px;clip-path:inset(0 0 0 0 round 5px);cursor:pointer}
  @media (min-width:769px) and (max-width:1180px){.slide{aspect-ratio:46/44}}
  @media (max-width:768px){.slide{aspect-ratio:31/38;width:310px}}
  @media (max-width:520px){.slide{width:calc(100vw - 80px)}}
  .slideTitle{position:absolute;top:20px;left:20px;right:20px;z-index:10;color:#fcf8f0;text-wrap:balance;transition:color .12s ease-in-out} /* .textHeadline4; mobile 16px insets */
  .photoLayer{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(0,0,0,.7),transparent 46.78%)}
  picture.responsivePicture{display:block;width:100%;height:100%} /* bg = blurhash radial gradients (below) */
  picture img.cover{position:absolute;width:100%;height:100%;object-fit:cover;object-position:center;z-index:0;transition:opacity .16s ease-in-out} img.lazy{opacity:0}
  .plusPill{position:absolute;right:10px;bottom:0;width:120px;height:60px;border-radius:60px 60px 0 0;background:#c8fdab;z-index:3;transform:translate3d(0,100%,0);transition:transform .12s ease-in}
  .plusPill svg{position:absolute;bottom:14px;left:calc(50% - 12px);transition:opacity 60ms ease-in-out 60ms}
  .otherPill{position:absolute;right:10px;bottom:-60px;width:120px;height:60px;border-radius:60px 60px 0 0;background:#c8fdab;z-index:3;transition:transform .12s ease-in}
  .descriptionLayer{position:absolute;inset:0;z-index:2;background:#c8fdab;opacity:0;transition:opacity .12s ease-in-out}
  .description{position:absolute;left:20px;right:150px;bottom:20px;z-index:4;color:#3e2002;opacity:0;transform:translate3d(0,120px,0);transition:opacity .12s ease-in-out,transform .12s ease-in-out} /* .textBodyM; 769–1180 body-s sizes; mobile left/right/bottom 16px */
  .slide.active .slideTitle{color:#3e2002}
  .slide.active .plusPill,.slide.active .otherPill{background:#c1f2a3;transform:translate3d(0,-100%,0);transition:transform .12s ease-out}
  .slide.active .plusPill svg{opacity:0;transition:opacity 60ms ease-in-out}
  .slide.active .descriptionLayer{opacity:1}
  .slide.active .description{opacity:1;transform:translateZ(0);transition:opacity .12s ease-in-out 60ms,transform .12s ease-in-out 60ms}
  @media (hover:hover){.slide:hover:not(.active) .plusPill{transform:translateZ(0);transition:transform .12s ease-out}}
  /* mobile pills: 60x30, radius 30px 30px 0 0, right 16px, always visible (translateZ(0)); otherPill bottom:-30px; svg bottom:2px */
  ```
  - Sizes: 1440 → 630x477 (step 650); 1280 → 550x417, title 510 wide; 390 → 310x380, title 278 wide, 24px.
  - Click toggles `.active` (only one at a time; clicking again closes). Below 768px wide it also calls `slideTo(index)`.
  - Active state: lime layer covers the photo, the title turns earth, and the description rises 120px and fades in.
  - Images are lazy (IntersectionObserver on the `<picture>`, and srcset is assigned on the first intersection). `<source media="(max-width:768px)" srcset="/slides/slideN_mobile.jpg">`, `<source type="image/webp" media="(max-width:768px)" srcset="/slides/slideN_mobile.webp">`, `<source type="image/webp" srcset="/slides/slideN.webp">`, `<img class="cover" src="/slides/slideN.jpg" alt="<title>">`. The image fades from opacity 0 → 1 (.16s) on load. The picture background shows a blurhash placeholder meanwhile.
- Slides (title / description / image / placeholder):
  1. **Forests, Carbon, and Natural Capital**: "We support governments and companies in reforestation and conservation programs, such as the 550,000-hectare project in Malawi developed with Mamaland (Mota-Engil), which generates high-quality carbon credits. We work with E-Redes on natural capital assessment and biodiversity impact optimization, transforming ecosystems into strategic assets for a regenerative economy." / `slides/slide1` (1200x800; mobile 600x400) / placeholder:
     `radial-gradient(at 0 0,#7e6d69,#00000000 50%),radial-gradient(at 33% 0,#7f8381,#00000000 50%),radial-gradient(at 67% 0,#866f66,#00000000 50%),radial-gradient(at 100% 0,#83716c,#00000000 50%),radial-gradient(at 0 50%,#807470,#00000000 50%),radial-gradient(at 33% 50%,#768181,#00000000 50%),radial-gradient(at 67% 50%,#806a65,#00000000 50%),radial-gradient(at 100% 50%,#7f7471,#00000000 50%),radial-gradient(at 0 100%,#5d5d60,#00000000 50%),radial-gradient(at 33% 100%,#6c797a,#00000000 50%),radial-gradient(at 67% 100%,#7c706d,#00000000 50%),radial-gradient(at 100% 100%,#767171,#00000000 50%)`
  2. **Energy and Energy Efficiency**: "We support EDP in developing and implementing renewable generation solutions including solar, wind and hydro, integrated with energy efficiency and e-mobility. Through the Effizency platform, we help utilities deliver more competitive and scalable products for both B2C and B2B markets. We also work on designing and implementing energy infrastructure for cities, industry and government, covering project management, carbon services, financing, marketing and market intelligence." / `slides/slide2` (1200x899) / placeholder:
     `radial-gradient(at 0 0,#d6dadb,#00000000 50%),radial-gradient(at 33% 0,#dfdfdc,#00000000 50%),radial-gradient(at 67% 0,#e3e4e0,#00000000 50%),radial-gradient(at 100% 0,#e8e8e0,#00000000 50%),radial-gradient(at 0 50%,#959fa3,#00000000 50%),radial-gradient(at 33% 50%,#9ea9b1,#00000000 50%),radial-gradient(at 67% 50%,#a2acb1,#00000000 50%),radial-gradient(at 100% 50%,#9aa6ac,#00000000 50%),radial-gradient(at 0 100%,#454500,#00000000 50%),radial-gradient(at 33% 100%,#3d4626,#00000000 50%),radial-gradient(at 67% 100%,#50542e,#00000000 50%),radial-gradient(at 100% 100%,#636834,#00000000 50%)`
  3. **Consumer Goods and Social Impact**: "We support leading retailers and consumer brands in creating social and environmental value. With SONAE MC, we developed the Missão Continente programme, which supports 900,000 people and was recognised with the 2023 European Excellence Award. We also work with major foundations and international organisations to design and implement social responsibility and circular economy policies across Europe, Asia and Africa." / `slides/slide3` (810x541) / placeholder:
     `radial-gradient(at 0 0,#6e6f7e,#00000000 50%),radial-gradient(at 33% 0,#697183,#00000000 50%),radial-gradient(at 67% 0,#6a7085,#00000000 50%),radial-gradient(at 100% 0,#7e7f8e,#00000000 50%),radial-gradient(at 0 50%,#686c7d,#00000000 50%),radial-gradient(at 33% 50%,#667284,#00000000 50%),radial-gradient(at 67% 50%,#637087,#00000000 50%),radial-gradient(at 100% 50%,#787d8c,#00000000 50%),radial-gradient(at 0 100%,#67707e,#00000000 50%),radial-gradient(at 33% 100%,#647485,#00000000 50%),radial-gradient(at 67% 100%,#647486,#00000000 50%),radial-gradient(at 100% 100%,#6a7787,#00000000 50%)`
  4. **Water, Sanitation, and Resilient Cities**: "We develop climate-resilient plans and infrastructure, including the Lisbon General Drainage Plan and the Luanda Water Master Plan (2025–2045). In Portugal, we support frontier innovation in water systems. In countries such as Brazil, Angola, Mozambique, Ethiopia, Cape Verde, Malawi, Nigeria and Tanzania, we promote universal access to water and sanitation, sustainable urban drainage and integrated water resource management." / `slides/slide4` (1200x900) / placeholder:
     `radial-gradient(at 0 0,#bc6e63,#00000000 50%),radial-gradient(at 33% 0,#b8193f,#00000000 50%),radial-gradient(at 67% 0,#c75766,#00000000 50%),radial-gradient(at 100% 0,#b74557,#00000000 50%),radial-gradient(at 0 50%,#bb7148,#00000000 50%),radial-gradient(at 33% 50%,#b57d76,#00000000 50%),radial-gradient(at 67% 50%,#cc9c99,#00000000 50%),radial-gradient(at 100% 50%,#ae827e,#00000000 50%),radial-gradient(at 0 100%,#a97346,#00000000 50%),radial-gradient(at 33% 100%,#ad7e79,#00000000 50%),radial-gradient(at 67% 100%,#c3838d,#00000000 50%),radial-gradient(at 100% 100%,#a87470,#00000000 50%)`
  5. **Resilience and Impact**: "We assess the resilience and impact of infrastructure projects across multiple sectors, analyzing climate, economic and social risks. We develop methodologies that integrate territorial vulnerability and operational continuity, guiding investment and planning decisions. For example, we have carried out climate risk assessments for critical assets such as roads, airports and ports — including the Dallas Airport — strengthening the adaptability and safety of essential infrastructure." / `slides/slide5` (1200x800) / placeholder:
     `radial-gradient(at 0 0,#adb0a5,#00000000 50%),radial-gradient(at 33% 0,#adafa1,#00000000 50%),radial-gradient(at 67% 0,#a4b0a0,#00000000 50%),radial-gradient(at 100% 0,#94a197,#00000000 50%),radial-gradient(at 0 50%,#aba69f,#00000000 50%),radial-gradient(at 33% 50%,#a5a2a0,#00000000 50%),radial-gradient(at 67% 50%,#9ea6a7,#00000000 50%),radial-gradient(at 100% 50%,#7a8c93,#00000000 50%),radial-gradient(at 0 100%,#aea398,#00000000 50%),radial-gradient(at 33% 100%,#9e938f,#00000000 50%),radial-gradient(at 67% 100%,#979797,#00000000 50%),radial-gradient(at 100% 100%,#7d808d,#00000000 50%)`
- **"Proud member of" marquee** (`div.logosCont`: `display:flex; flex-direction:column; gap:30px; margin-top:123px`). At 1440: y10177, 1340x183.
  - `div.textBodyL` "Proud member of", `text-align:center` (24px).
  - `div.marquee3k[data-speed="0.5"]` (`overflow:visible; width:100%`; the section clips it). Inner `div.logos` is `display:flex; gap:10px`, with 9x `div.logo > div.logoCont(bg oat) > img[src=/logos/logoN.png width=200 height=120 alt=""]` and `mix-blend-mode:multiply`. Images are 400x240 natural, rendered 200x120, and each logo box is 200x124 because of the inline img baseline gap. Mobile: `.logoCont{margin-left:-15%; margin-right:-15%}`, which makes neighbours overlap (measured logo box 260x124 on 390).
  - Marquee algorithm (marquee3k, vendored): the wrapper `div.marquee3k__wrapper{white-space:nowrap}` holds the content copy (`display:inline-block`, width = 9*200+8*10 = **1880px**) plus clones. Clone count = `contentWidth > parentWidth ? 2 : ceil((parentWidth - contentWidth)/contentWidth)+1`. With 3 copies total at desktop, each frame (rAF) runs `offset -= 0.5`, and when `offset <= -contentWidth` it resets to 0. Apply `transform: translate(${offset}px,0) translateZ(0)`. Speed is **0.5px per animation frame** (30px/s at 60Hz), leftward, never pauses (not pausable) and has no hover effect. Re-populate on resize (250ms debounce).

---

## 10. Team (`section#team.team`, LandingTeam + ObjectMember x15)

- `background:#ff9d69; padding:150px var(--margin-page) 350px`. Mobile: `75px var(--margin-page) 200px`. <=520: bottom padding `45svh`.
- `.intro`: `display:flex; flex-direction:column; gap:40px` (mobile 30).
  - `h2.textHeadline2Medium` (`max-width:940px`): **"Over 45 years experience delivering impact"**. At 1440: 940x158.
  - `p.subtitle.textBodyL` (`max-width:570px; color:rgba(62,32,2,.7)`): **"Our executive team brings decades of experience in diverse areas such as infrastructure, strategy, social innovation, and policy - ensuring sustainable transitions are not only possible, but practical."**
- `.list`: `display:flex; flex-direction:column; gap:15px; margin-top:130px` (mobile 60). At 1440: y11153, 1340x1170.
- Each row: `div > div.teamMember{display:flex; justify-content:flex-end; position:relative}`.
  - `div.textHeadline3` (name): `max-width:500px; text-align:right; text-wrap:balance; opacity:.4; cursor:pointer; transform:translateZ(0); transition:opacity .24s ease-in-out .12s`. Hover (hover:hover): `opacity:1; transition:opacity .12s ease-in-out`. 60px/60px, -1.8px, 400. Names are right-aligned to x=1390 at 1440. Mobile: `max-width:350px`, 32px. Row heights are 60px, except "Filipe de Morais Vasconcelos", which wraps to 2 lines (120px) on desktop.
  - `div.overlayCont`: `position:fixed; inset:0; z-index:5; display:flex; align-items:center; justify-content:center; pointer-events:none` (mobile `justify-content:flex-start`). It stays mounted for every member at opacity 0.
    - `div.backgroundCont`: `position:absolute; inset:0 50% 0 0; opacity:0; transition:opacity .24s ease-in-out` (left half of the viewport, 720x900 at 1440). It contains `img src=/team/<slug>-back.png` (1700x2000 PNG, dotted halftone portrait) with `width:100%; height:100%; object-fit:contain; object-position:bottom left`. Hidden on mobile (<=768).
    - `div.portraitCont`: `position:relative; z-index:1; width:450px; aspect-ratio:45/56; background:#fff; border-radius:5px; overflow:hidden; opacity:0; transform:translateZ(0); transition:opacity .24s ease-in-out .12s`. It is centred in the viewport (x495 y170 450x560 at 1440x900). Mobile: 285x285 (aspect 1/1) at x0, vertically centred.
      - Responsive picture (`width=900 height=1120`, transparent placeholder): `<source media="(max-width:768px)" srcset="/team/<slug>_mobile.jpg">`, `<source type=image/webp media=(max-width:768px) srcset="/team/<slug>_mobile.webp">`, `<source type=image/webp srcset="/team/<slug>.webp">`, `<img class=cover src="/team/<slug>.jpg">`, with `object-fit:cover; object-position:top center`. Desktop JPG 900x1120; mobile JPG 500x622.
      - `div.role.textCaption` (HTML, may contain `<br/>`): `position:absolute; left:8px; bottom:8px; background:#c8fdab; border-radius:5px; padding:4px 6px 6px 26px; min-height:26px; box-sizing:border-box; line-height:1; letter-spacing:-.03em` (16px). `:before` is a 14x14 earth circle (`border-radius:7px`) at left 6px, top 6px. Mobile: `bottom:37px; min-height:22px; padding:2px 6px 4px 22px`, and the dot is 12x12 at top 5px.
      - `a.linkedin.textCaption` (`target=_blank`): `position:absolute; right:8px; bottom:8px; width:86px; height:26px; background:#fcf8f0; color:#3e2002; border-radius:5px; cursor:pointer; transform:translateZ(0); transition:background-color .12s ease-in-out, width .12s ease-in-out .12s`.
        - `span` "Linkedin": `position:absolute; left:6px; top:4px; line-height:1; letter-spacing:-.03em`.
        - `svg.logo` (16x16 LinkedIn glyph): `position:absolute; right:25px; top:50%; transform:translate3d(0,-50%,0); opacity:0; transition:opacity .12s`.
        - `svg.arrow` (13x13 ↗): `position:absolute; right:6px; top:50%; width:13px; height:13px; transform:scale3d(.7,.7,.7) translate3d(0,-50%,0); transform-origin:top right; transition:transform .12s ease-in-out .12s`.
        - Hover: `width:111px; background:#c8fdab` (width transition without delay). The logo fades in after .12s and the arrow scales to 1.
        - Mobile: `left:8px; right:0; height:22px` and span `top:2px`. It sits below the role chip.
  - **Active trigger (desktop >=521px):** an IntersectionObserver on each row wrapper with `rootMargin:"-49.5% 0% -49.5% 0%"` (a 1%-tall band at viewport centre). While a name's row intersects the band, `.isActive` applies:
    ```css
    .teamMember.isActive .overlayCont .backgroundCont{opacity:1;transition:opacity .24s ease-in-out .48s}
    .teamMember.isActive .overlayCont .portraitCont{opacity:1;pointer-events:auto;transition:opacity .24s ease-in-out 0s}
    .teamMember.isActive .textHeadline3{opacity:1;transition:opacity .24s ease-in-out 0s}
    ```
    That is: the portrait card fades in centred, and the halftone background fades in on the left half after 0.48s. On exit, the portrait fades out after a .12s delay and the background with no delay.
  - **Mobile (<=520):** a second observer with `rootMargin:"-24.5% 0% -74.5% 0%"` (a band at 25% from the top) sets `.isActiveMobile`, using the same rules (background hidden by the 768 rule).
  - Clicking a name scrolls it to the active band (see section 3).
- Members (name | slug | role HTML | LinkedIn):
  1. Filipe de Morais Vasconcelos | filipe-de-morais-vasconcelos | Management Team | https://www.linkedin.com/in/filipemoraisvasconcelos/
  2. Miguel Feliz | miguel-feliz | Management Team | https://www.linkedin.com/in/miguelfeliz/
  3. Nathalie Ballan | nathalie-ballan | Board Member&lt;br/&gt;Business Development Division | https://www.linkedin.com/in/nathalieballan/
  4. Rui Marques | rui-marques | Board Member&lt;br/&gt;Commercial Division | https://www.linkedin.com/in/rui-quintas-marques-20091813/
  5. Ana Gonçalves | ana-goncalves | Operations Division | https://www.linkedin.com/in/anahgoncalves/
  6. Raquel Almeida | raquel-almeida | Energy, Carbon &amp; Biodiversity | https://www.linkedin.com/in/raquelfaalmeida/
  7. Cláudia Tapadas | claudia-tapadas | Sustainability Strategy | https://www.linkedin.com/in/claudiatapadas/
  8. Dalila Antunes | dalila-antunes | Impact &amp; Risks | https://www.linkedin.com/in/dalila-antunes-5960321/
  9. Marta Vian Santos | marta-vian-santos | Social &amp; Communities | https://www.linkedin.com/in/martaviansantos/
  10. Paulo Rosa | paulo-rosa | Water &amp; Sanitation | https://www.linkedin.com/in/paulo-rosa-9201b15/
  11. Rita Campos | rita-campos | Innovation | https://www.linkedin.com/in/rita-campos-pt/
  12. Teresa Cordeiro | teresa-cordeiro | Partnerships | https://www.linkedin.com/in/teresa-menezes-cordeiro-34a0095a/
  13. António Monteiro | antonio-monteiro | Industry Expert Water &amp; Sanitation | https://www.linkedin.com/in/ant%C3%B3nio-jorge-monteiro-78045428/
  14. João Guimarães | joao-guimaraes | Industry Expert Water &amp; Sanitation | https://www.linkedin.com/in/jo%C3%A3o-guimar%C3%A3es-60a14131/
  15. José Palma | jose-palma | Industry Expert Circular Economy | https://www.linkedin.com/in/jmpalmao/
- Name x positions at 1440 (right-aligned at 1390): Filipe x890 (500 wide, 2 lines), Miguel x1096, Nathalie x1008, Rui x1078, Ana x1019, Raquel x993, Cláudia x979, Dalila x1025, Marta x933, Paulo x1111, Rita x1071, Teresa x998, António x953, João x986, José x1102. Rows are spaced 75px apart (60 + 15 gap).

---

## 11. CTA, footer and subfooter

### 11.1 CTA (`section.ctaSection`, no id)
- `height:100svh; background:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:50px; padding:var(--margin-page); box-sizing:border-box; overflow:hidden; position:relative`. Mobile: `height:auto; gap:100px; padding:75px var(--margin-page) 150px` (617px tall at 390).
- `div.cloud`: `position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); width:1100px; height:600px`. It contains `<video src="/cloud_low.mp4" autoplay muted loop playsinline>` (1100x600, 4.7s, default sizing that fills the box).
- `div.cloudOverlay`: `position:absolute; inset:0; z-index:1; background:#fcf8f0; mix-blend-mode:multiply` (tints the white bg and video to oat).
- `h2.textHeadline2Medium` (`max-width:800px; position:relative; z-index:2; text-align:center; text-wrap:balance`): **"Let’s Build the Infrastructure of Change Together"**. At 1440: x320 y12960, 800x238 (3 lines). Mobile: headline1 sizes (52px/50.96px, -0.03em, 500), 350x204.
- `div.buttons`: `display:flex; gap:8px; position:relative; z-index:2`. Mobile: `flex-direction:column; align-items:center`. At 1440: x544 y13247, 353x40.
  - Shared: `a{display:block;height:40px;line-height:40px;overflow:hidden;position:relative;text-align:center;background:#fcf8f0;color:#3e2002;transition:background-color .12s ease-in-out,color .12s ease-in-out,width .12s ease-in-out}` with `span{position:absolute;left:12px}` and `svg{position:absolute;top:50%;transform:translate3d(0,-50%,0)}`. The SVG is hidden on mobile. **No border-radius** (square).
  - `a.textBodyS.signup` → https://mailchi.mp/960b9490730a/website-signup (`_blank`): **"Sign up for updates"**, `font-weight:500; width:177px`, svg (17x16 arrow, fill oat) at `left:173px`. Hover (>=769 & hover:hover): `background:#3e2002; color:#fcf8f0; width:202px`, which reveals the arrow. Mobile: always earth bg with oat text.
  - `a.textCaption.linkedin` → https://www.linkedin.com/company/the-equator-company/ (`_blank`): **"Follow us on LinkedIn"**, `width:168px` (16px text), svg (13x12 arrow, fill oat) at `left:164px`. Hover: earth bg, oat text, `width:189px`.

### 11.2 Footer (`footer`)
- `background:#3e2002; color:#9d8c79; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:180px 20px; padding:60px var(--margin-page) 40px`.
  - <=1366: `grid-template-columns:repeat(3,minmax(0,1fr))`, with infoCont and bottom at `grid-column:2/span 2`.
  - <=1024: `display:flex; flex-direction:column; gap:30px; padding:var(--margin-page) var(--margin-page) 30px`.
  - Height 731 at 1440 and 1280, 762 at 390.
- `div.logoCont` (`grid-column:1; grid-row:span 2; display:flex; align-items:flex-end; position:relative`). At 1440: x50 y13633 660x631. At 1280: 380 wide.
  - `div.lottieCont`: `aspect-ratio:345/394; max-width:345px; width:100%`, rendered 345x394. It holds a dotLottie `src=/lottie/footer.lottie` with **autoplay + loop** and fit contain (350x400 comp, 30fps, 242 frames). Artwork UNMEASURED (canvas).
  - Inline SVG wordmark (276x180, stacked "The / Equator / Company", fill `var(--color-oat)`): `position:absolute; right:0; transform:translate3d(calc(100% + 20px),15px,0)`. It sits just right of the column, bottom-aligned, at x730 y14100 at 1440 (x450 y13239 at 1280).
  - <=1024: `display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:20px; order:2; padding-top:110px`, and the SVG becomes `position:relative; width:100%; height:auto; transform:translate3d(0,8%,0)`. Mobile: lottie 165x188 at x20, SVG 165x108 at x205.
- `div.infoCont` (`display:flex; flex-direction:column; gap:25px`; <=1024 `order:1`). At 1440: x730 y13633 660x271.
  - `p.textBodyM` (max-width 570, text-wrap:balance): "Interdisciplinary sustainability consultancy with 45 years of experience. Designed to provide a structured full-service ESG offer for your organisation and community." 21px/25.2px.
  - `ul.textBodyS` (`list-style:none; display:flex; flex-direction:column; gap:6px`). Each `li a` is `display:flex; align-items:center; gap:10px` (<=1024 align flex-start) with a 24x24 icon (`fill/stroke currentColor`):
    - pin icon + "Rua Laura Alves 12, 1050-138 Lisboa, Portugal" → https://maps.app.goo.gl/DhKJrr1GrcZ6ptwT7 (`_blank`)
    - mail icon + "info@equatorcompany.com" → mailto:info@equatorcompany.com. On the live site Cloudflare email obfuscation rewrites this; ignore that.
  - `ul.textBodyS`: LinkedIn icon + "Follow us on LinkedIn" → company page (`_blank`).
  - `p.textBodyS`: "© {currentYear} The Equator Company.<br>All rights reserved." (live: 2026). The year is computed at runtime: `new Date().getFullYear()`.
  - No hover styles on footer links (none in CSS).
- `div.bottom` (`grid-column:2; display:flex; justify-content:space-between; align-items:flex-end`; <=1366 `grid-column:2/span 2`; <=1024 `align-items:flex-start; order:3`).
  - `div.logoSpace` height 180px (hidden <=1024).
  - `div.credits` (`display:flex; gap:12px; font-size:.875rem (14px); line-height:1; text-align:right; color:#6d543c`): `<a href="/privacy-policy">Privacy Policy</a>` (router link) and `<span>Design by <a href="https://studio-cronica.com" target="_blank">Studio Cronica</a></span>`. At 1440 it is at x1136 y14251, 254x14.

### 11.3 Subfooter (`div.subfooter`)
- `background:#3e2002; color:#fcf8f0; display:flex; align-items:center; justify-content:center; gap:20px; padding:130px var(--margin-page) 40px`. <=1024: `flex-direction:column; align-items:flex-start; padding:40px var(--margin-page)`. Height 216 desktop, 159 at 390.
  - `a[href=https://recuperarportugal.gov.pt/ target=_blank rel="noopener noreferrer"] > img[src=/mono.svg alt=""]`: `height:42px; width:auto` (429x42). This is the PRR / República Portuguesa / EU funding strip. <=1024: `width:100%; max-width:429px; height:auto` (350x34 at 390).
  - `a.sheet.textCaption[href=/Equator-PRR-Investimentos.pdf target=_blank download]` "Project sheet": `margin-bottom:.5em` (16px, oat). <=1024: `font-size:.875rem; line-height:1`.

---

## 12. Route `/privacy-policy`

- Same tokens. `main{background:#fcf8f0; position:relative}`. Document height 4423 at 1440x900. `<title>` is empty on the live page (UNSET). Use "The Equator Company" or leave empty.
- **No splash, no lottie logo animation, no section watcher hash.** Locomotive/Lenis is still instantiated.
- Header (desktop): `div.headerCont` (sticky top 0, z 10, pointer-events none) → `header` (68px, `margin-bottom:-68px`, flex space-between, padding 0 margin-page, transparent).
  - `div.logoSpace > a` (to `/`): `display:block; margin-top:9px; pointer-events:auto; transform:scale3d(.6666,.6666,1); transform-origin:left center`. Wordmark at x50 y25, 235x27 rendered.
  - `nav` is identical to home, but links are `external` hrefs `/#our-story` and so on (full navigation back to home). It sits at x815 y22.
- Mobile header: `div.mobileHeader` is `position:sticky` (not fixed) and always visible, coral, 68px. It contains `.logoSpace` (abs left margin-page; link scaled .6666, `margin-top:6px`, height 34) and the hamburger. The menu overlay is the same as home.
- `article`: `display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:50px 20px; padding:400px var(--margin-page) 200px`. Mobile: `display:flex; flex-direction:column; gap:40px; padding:190px var(--margin-page) 120px`.
  - `h1.textHeadline1` "Privacy Policy" (`grid-column:span 12`): x50 y400, 96px.
  - `div.body.textBodyM` (`grid-column:1/span 7; display:flex; flex-direction:column; gap:10px`): 773 wide at 1440, 21px/25.2px. `strong{font-weight:500}`. `a{text-decoration:underline; text-decoration-thickness:.06em; text-underline-offset:.1em}`. `h2.textHeadline4` "Data Treatment".
  - Full article markup: see the appendix at the end of this file.
- Then the same footer and subfooter as home (footer at y3476).

---

## 13. Head / meta (home)
```html
<title>The Equator Company</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#FF9D69">
<meta name="apple-mobile-web-app-title" content="Equator">
<meta name="pinterest" content="nopin">
<meta property="og:title" content="The Equator Company"><meta name="twitter:title" content="The Equator Company">
<meta name="description" content="Interdisciplinary sustainability consultancy with 45 years of experience. Designed to provide a structured full-service ESG offer for your organisation and community."> (+ og:description, twitter:description identical)
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="shortcut icon" href="/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="canonical" href="http://equatorcompany.com">
```
`site.webmanifest`: name "The Equator Company", short_name "Equator", icons `/web-app-manifest-192x192.png` and `/web-app-manifest-512x512.png` (maskable), theme_color and background_color `#FF9D69`, display standalone.
A hidden skip link `<a id="skip" href="#mainContent">Skip content</a>` has `display:none`.

---

## 14. Motion inventory (summary table)

| # | Element | Trigger | Property | Duration / easing / delay | Notes |
|---|---|---|---|---|---|
| 1 | Page scroll | wheel | Lenis smoothing | lerp 0.1 | touch native |
| 2 | Splash lottie | mount + 1000ms | play 0→600, then loop 270→600 | 30fps | navbar.lottie |
| 3 | Splash caption | 2500ms after mount; hides when scrollY > 0.5vh+34 | opacity | .2s ease-in-out | |
| 4 | Logo scale | scroll 0 → 0.5vh+34 | scale 1 → 0.6667 (origin left center) | scrubbed | then `.small` lock |
| 5 | Logo position | sticky | — | — | centred in splash, pins at top:0 |
| 6 | Header nav | sticky after splash | — | — | |
| 7 | Nav underline | hover / active hash | scaleX 0→1 (origin right→left) | .12s ease-out | |
| 8 | Mobile header bar | scrollY > 0.5vh+34 | opacity 0→1 | .2s ease-in-out | |
| 9 | Mobile menu | hamburger | translateY(-100%)→0 | open .2s ease-in-out / close .2s ease-in | body overflow hidden |
| 10 | Hamburger → X | toggle | squeeze | 75ms + .12s delays | see 4.3 |
| 11 | Bird video | autoplay loop | — | 11.3s | mix-blend screen |
| 12 | Story words + logos | scroll (storyTop-0.5vh → storyBottom-vh) | opacity 0→1 per word, k ≤ p*60 | .25s ease-in-out each | reversible |
| 13 | Values stack | sticky | — | — | 5 pinned panels |
| 14 | Values fade-out | scroll over 0.15vh before next panel arrives | opacity 1→0 | scrubbed | values 1–4 |
| 15 | Values counter | IO step band | text "N/5" | instant | |
| 16 | Value lotties | first visible | play, then loop from frame 60 | 30fps | |
| 17 | Dropdown | click | height, bg, pills, content opacity | .12s; content delay 60ms | accordion |
| 18 | Dropdown pill | hover | translateY 100%→0 | .12s ease-out (in), ease-in (out) | desktop |
| 19 | Carousel | arrows / drag | translateX | 300ms ease-out | no loop |
| 20 | Slide | hover | pill up | .12s | |
| 21 | Slide | click | lime layer, title colour, description rise 120px | .12s, 60ms delay on desc | single active |
| 22 | Lazy images | load | opacity 0→1 | .16s ease-in-out | blurhash bg |
| 23 | Marquee | rAF | translateX -0.5px/frame | continuous | |
| 24 | Team name | hover | opacity .4→1 | .12s | |
| 25 | Team active | IO centre band 1% (desktop) / 25% band (<=520) | portrait opacity; bg opacity; name opacity | .24s; bg delay .48s; exit portrait delay .12s | |
| 26 | Team LinkedIn tag | hover | width 86→111, bg oat→lime, logo fade, arrow scale | .12s; staged .12s delays | |
| 27 | CTA buttons | hover (>=769) | bg/colour invert, width +25px (arrow reveal) | .12s ease-in-out | |
| 28 | Cloud video | autoplay loop | — | 4.7s | overlay multiply |
| 29 | Footer lottie | autoplay loop | — | 242f @30fps | |
| 30 | Anchor nav scroll | click | window.scrollTo | clamp(Δ/2000, .1, .8)s easeOutSine | |
| 31 | URL hash | section at viewport centre | router.replace | 500ms debounce | |

No load-time entrance animations exist for headings or paragraphs other than those listed. There are no cursor effects, no WebGL, and no SVG path animations. `mono.svg` is a static image. It is not animated.

## 15. UNMEASURED / caveats
- Lottie canvas artwork (splash, 5 values, footer) cannot be read from the DOM. Use the downloaded `.lottie` files directly.
- Video pixel content is not described. Use the downloaded MP4s.
- I did not test touch-drag inertia on the carousel or Lenis on a real device.
- At 120Hz the marquee runs faster (per-frame speed). The original behaves the same way.

## Appendix — /privacy-policy article markup (verbatim from route chunk tklmdvPw.js)
```html
<article><h1 class="textHeadline1">Privacy Policy</h1>
<div class="body textBodyM">
<p>This Privacy Policy presents the process of collecting and using personal data, as well as the safeguard and security measures adopted in the treatment of such data. S317 Consulting recognises the importance of privacy and we ask you to carefully read this Privacy Policy to know how your Personal Information will be handled when using our website. The website www.theequatorcompany.com is owned by S317 Consulting, LDA. with headquarters at Rua Laura Alves nº12, 6º andar, 1050-041 Lisboa, Portugal.</p>
<p> </p>
<p><strong>1. Data collection</strong></p>
<p>Whenever it is necessary to collect personal information, the use of this information will be carried out in compliance with the applicable legislation in force for the Data Protection Policy imposed by the National Data Protection Commission (CNPD), to ensure the confidentiality and security of personal data provided.</p>
<p>The collection of personal data (name, email address, telephone contact), is applicable in commercial consultations and/or service agreements. The entity responsible for the collection and processing of personal data is S317 Consulting.</p>
<p> </p>
<p><strong>2. Use of the information collected</strong></p>
<p>S317 Consulting undertakes to comply with the rules of personal data processing in force in Portugal.</p>
<p>The data collected data is exclusively for the use of S317 Consulting, being guaranteed the privacy and protection of the data of the users.</p>
<p> </p>
<p><strong>3. Right of Access, Rectification, Cancellation, and Opposition</strong></p>
<p>In accordance with the provisions of the law in force, any person may request access to their personal data, its content, as well as require its rectification, update or request its destruction, by written request addressed to S317 Consulting to the email address: <a href="mailto:info@s317consulting.com">info@s317consulting.com</a>.</p>
<p> </p>
<p><strong>4. Security and Data Protection</strong></p>
<p>S317 Consulting undertakes to treat your Personal Information with the utmost privacy, confidentiality, and security and undertakes to adopt the necessary security measures to ensure the safeguarding of the personal data of users against their possible misuse or against access not authorised.</p>
<p>Notwithstanding, and since the Internet is not 100% secure, S317 Consulting cannot guarantee the security of any information it disseminates online, nor be liable for any loss or damage caused to the user as a consequence of the loss of confidentiality of the information.</p>
<p> </p>
<p><strong>5. Responsibility</strong></p>
<p>On this web page, users will be able to find links that take them to other web pages outside the domain of S317 Consulting servers that may themselves collect data or request personal information. This Privacy Policy does not apply to third-party sites, so you should read the Privacy Policy of the third-party sites you visit, and we are not responsible for the content and information on those same sites.</p>
<p> </p>
<p><strong>5. Privacy Policy Agreement</strong></p>
<p>It is understood that the user accepts the conditions of this privacy policy when entering their data.</p>
<p>We assume that the user consents to the automated processing and use of the data in accordance with the privacy conditions described in this document wData Trehen filling out the forms. If you do not accept the terms and conditions of this Privacy Policy, we ask you not to provide any personal information to S317 Consulting through this site.</p>
<p> </p>
<p><strong>5. Changes to the Privacy Policy</strong></p>
<p>S317 Consulting reserves the right at any time to update or revise this Privacy Policy in order to adjust it to any legislative changes and/or other constraints. Any changes made will be published in this space, so the user should visit this area frequently to keep informed about the Privacy Policy in force.</p>
<p> </p>
<h2 class="textHeadline4">Data Treatment</h2><p>The Management determines that data processing must be subject to the following principles (data protection policy):</p>
<p>a) determination, before data collection, of the purposes for their use, as well as their conservation and elimination;</p>
<p>b) identification of data subjects (personal and non-personal) and determination of their interests and rights;</p>
<p>c) provision of information to the holders of personal data on the specific purposes for the use, limitation, and interruption of use, rectification and conservation, deletion of data and right of opposition, when the holders are not aware of the information;</p>
<p>d) obtaining authorisation from the holder of personal data for their use, especially when they are or may be used for the purpose of offering goods and services, even if free of charge, or for analysing and controlling their behaviour;</p>
<p>e) interruption of the processing of data that no longer meet the purposes for which they were collected or when requested by their holders;</p>
<p>f) deletion of data when they are not used or at the request of their holders, subject to the applicable legal/fiscal permissions.</p>
<p>g) data protection through logical, physical, and other security measures.</p>
<p>These principles apply to data collected directly (personal and phone contacts) or indirectly (postal correspondence, own internet sites, and social networks), either in verbal and/or written forms (registration/information forms; postal mail, advertising, emails, posts, and others).</p>
<p>The Management determines that all data held and kept by the organisation must be treated lawfully, loyally, and transparently, within the principles of security and responsibility referred to above in this section and in the “Information Assets”.</p>
<p>The data collected from its holders and kept by the organisation is structured accordingly to “Mapping the Value Network: Transactions”.</p>
<p>The company does not appoint any Data Protection Officer, as there is no need for regular and systematic control of the data based on their nature, scope, and purpose, as well as the small scale of the data collected and stored.</p>
<p>This policy was approved by the Managing Partners of S317 Consulting on March 17, 2021.</p>
</div></article>
```
