Source: https://equatorcompany.com/

# Asset Manifest: The Equator Company clone

Status key:
- **PRESENT**: the file is in `The Equator Company_files/` and is being copied flat to `/Users/riyaghosh/V3/equator/public/assets/<same filename>`.
- **MISSING**: the file is not in the saved folder. Download it from the absolute URL given.

All MISSING URLs below returned HTTP 200 on 2026-10-20.

**Path mapping note:** the live site serves assets from several paths (`/`, `/team/`, `/logos/`, `/slides/`, `/lottie/`). The saved copies are flat. Either keep them flat under `/assets/` and reference `/assets/<file>`, or recreate the live folders. Download MISSING files into a matching layout, e.g. `public/assets/slides/slide1.jpg`, `public/assets/lottie/navbar.lottie`, `public/assets/fonts/national-2-regular.woff2`.

## 1. Fonts (MISSING, all of them)
| File | URL | Format | Size | Use |
|---|---|---|---|---|
| national-2-regular.woff2 | https://equatorcompany.com/national-2-regular.woff2 | woff2 | 34,956 B | `font-family: National; font-weight: 400` |
| national-2-medium.woff2 | https://equatorcompany.com/national-2-medium.woff2 | woff2 | 37,072 B | `font-family: National; font-weight: 500` |

`@font-face{font-display:swap;font-family:National;font-style:normal;font-weight:400;src:local("National Regular"),local("National"),url(...) format("woff2")}` and the same for 500 with `local("National Medium")`. National 2 is a commercial Klim typeface. Confirm the licence.

## 2. Video (MISSING)
| File | URL | Dimensions | Duration | Size | Use |
|---|---|---|---|---|---|
| bird_low.mp4 | https://equatorcompany.com/bird_low.mp4 | 1000x850 | 11.3s | 1,096,142 B | Title section, `mix-blend-mode:screen`, autoplay muted loop playsinline |
| cloud_low.mp4 | https://equatorcompany.com/cloud_low.mp4 | 1100x600 | 4.7s | 1,153,223 B | CTA section bg, with an oat multiply overlay |

## 3. Lottie animations (MISSING; dotLottie zip format, played with dotlottie-web 0.54.1)
| File | URL | Comp | fps | Frames | Playback |
|---|---|---|---|---|---|
| navbar.lottie | https://equatorcompany.com/lottie/navbar.lottie | 511x720 | 30 | 0–601 | Splash: play at +1000ms, then loop segment 270→end |
| sustainability.lottie | https://equatorcompany.com/lottie/sustainability.lottie | 253x253 | 30 | 300 | Value 1: play on visible, then loop 60→end |
| global.lottie | https://equatorcompany.com/lottie/global.lottie | 253x253 | 30 | 300 | Value 2 (same playback) |
| grounded.lottie | https://equatorcompany.com/lottie/grounded.lottie | 253x253 | 30 | 300 | Value 3 |
| curiosity.lottie | https://equatorcompany.com/lottie/curiosity.lottie | 253x253 | 30 | 150 | Value 4 |
| difference.lottie | https://equatorcompany.com/lottie/difference.lottie | 253x253 | 30 | 241 | Value 5 |
| footer.lottie | https://equatorcompany.com/lottie/footer.lottie | 350x400 | 30 | 242 | Footer: autoplay loop |

The runtime also loads the WASM renderer from `https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web@0.54.1/dist/dotlottie-player.wasm`. The npm package handles this. Do not vendor it unless you need to.

## 4. Images

### 4.1 Story merger logos (PRESENT; live path `/`)
| File | Natural size | Rendered width (desktop / mobile) | Live URL |
|---|---|---|---|
| logo_s317.png | 372x179 | 185 / 135 | https://equatorcompany.com/logo_s317.png |
| logo_sairdacasca.png | 167x186 | 83 / 60 | https://equatorcompany.com/logo_sairdacasca.png |
| logo_engidro.png | 353x146 | 176 / 128 | https://equatorcompany.com/logo_engidro.png |
| logo_factorsocial.png | 402x111 | 200 / 146 | https://equatorcompany.com/logo_factorsocial.png |

### 4.2 "Proud member of" marquee logos (PRESENT; live path `/logos/`)
`logo1.png` … `logo9.png`: each is 400x240 PNG, rendered 200x120 with `mix-blend-mode:multiply`. Live: `https://equatorcompany.com/logos/logo{1..9}.png`.

### 4.3 Team (live path `/team/`)
For each slug, the table lists 5 files:

| Variant | Status | Size | Used when |
|---|---|---|---|
| `<slug>.jpg` | PRESENT | 900x1120 | desktop `<img>` fallback |
| `<slug>-back.png` | PRESENT | 1700x2000 (halftone) | desktop left-half background when active |
| `<slug>.webp` | **MISSING** | 900x1120 | desktop `<source type=image/webp>` (what Chromium actually loads) |
| `<slug>_mobile.jpg` | **MISSING** | 500x622 | `<source media="(max-width:768px)">` |
| `<slug>_mobile.webp` | **MISSING** | 500x622 | `<source type=image/webp media="(max-width:768px)">` |

Slugs (15): filipe-de-morais-vasconcelos, miguel-feliz, nathalie-ballan, rui-marques, ana-goncalves, raquel-almeida, claudia-tapadas, dalila-antunes, marta-vian-santos, paulo-rosa, rita-campos, teresa-cordeiro, antonio-monteiro, joao-guimaraes, jose-palma.

MISSING team URLs (45):
```
https://equatorcompany.com/team/filipe-de-morais-vasconcelos.webp
https://equatorcompany.com/team/filipe-de-morais-vasconcelos_mobile.jpg
https://equatorcompany.com/team/filipe-de-morais-vasconcelos_mobile.webp
https://equatorcompany.com/team/miguel-feliz.webp
https://equatorcompany.com/team/miguel-feliz_mobile.jpg
https://equatorcompany.com/team/miguel-feliz_mobile.webp
https://equatorcompany.com/team/nathalie-ballan.webp
https://equatorcompany.com/team/nathalie-ballan_mobile.jpg
https://equatorcompany.com/team/nathalie-ballan_mobile.webp
https://equatorcompany.com/team/rui-marques.webp
https://equatorcompany.com/team/rui-marques_mobile.jpg
https://equatorcompany.com/team/rui-marques_mobile.webp
https://equatorcompany.com/team/ana-goncalves.webp
https://equatorcompany.com/team/ana-goncalves_mobile.jpg
https://equatorcompany.com/team/ana-goncalves_mobile.webp
https://equatorcompany.com/team/raquel-almeida.webp
https://equatorcompany.com/team/raquel-almeida_mobile.jpg
https://equatorcompany.com/team/raquel-almeida_mobile.webp
https://equatorcompany.com/team/claudia-tapadas.webp
https://equatorcompany.com/team/claudia-tapadas_mobile.jpg
https://equatorcompany.com/team/claudia-tapadas_mobile.webp
https://equatorcompany.com/team/dalila-antunes.webp
https://equatorcompany.com/team/dalila-antunes_mobile.jpg
https://equatorcompany.com/team/dalila-antunes_mobile.webp
https://equatorcompany.com/team/marta-vian-santos.webp
https://equatorcompany.com/team/marta-vian-santos_mobile.jpg
https://equatorcompany.com/team/marta-vian-santos_mobile.webp
https://equatorcompany.com/team/paulo-rosa.webp
https://equatorcompany.com/team/paulo-rosa_mobile.jpg
https://equatorcompany.com/team/paulo-rosa_mobile.webp
https://equatorcompany.com/team/rita-campos.webp
https://equatorcompany.com/team/rita-campos_mobile.jpg
https://equatorcompany.com/team/rita-campos_mobile.webp
https://equatorcompany.com/team/teresa-cordeiro.webp
https://equatorcompany.com/team/teresa-cordeiro_mobile.jpg
https://equatorcompany.com/team/teresa-cordeiro_mobile.webp
https://equatorcompany.com/team/antonio-monteiro.webp
https://equatorcompany.com/team/antonio-monteiro_mobile.jpg
https://equatorcompany.com/team/antonio-monteiro_mobile.webp
https://equatorcompany.com/team/joao-guimaraes.webp
https://equatorcompany.com/team/joao-guimaraes_mobile.jpg
https://equatorcompany.com/team/joao-guimaraes_mobile.webp
https://equatorcompany.com/team/jose-palma.webp
https://equatorcompany.com/team/jose-palma_mobile.jpg
https://equatorcompany.com/team/jose-palma_mobile.webp
```
If you need a minimal setup, the `.jpg` files already present are enough for desktop. The mobile variants (500x622, rendered 285x285 cover/top) are an optimisation.

### 4.4 "Our Work" slides (MISSING, all of them; live path `/slides/`)
| Slide | Desktop JPG | Desktop WebP | Mobile JPG | Mobile WebP | Dimensions (desktop / mobile) |
|---|---|---|---|---|---|
| 1 Forests, Carbon, and Natural Capital | https://equatorcompany.com/slides/slide1.jpg | https://equatorcompany.com/slides/slide1.webp | https://equatorcompany.com/slides/slide1_mobile.jpg | https://equatorcompany.com/slides/slide1_mobile.webp | 1200x800 / 600x400 |
| 2 Energy and Energy Efficiency | https://equatorcompany.com/slides/slide2.jpg | https://equatorcompany.com/slides/slide2.webp | https://equatorcompany.com/slides/slide2_mobile.jpg | https://equatorcompany.com/slides/slide2_mobile.webp | 1200x899 / (mobile not measured) |
| 3 Consumer Goods and Social Impact | https://equatorcompany.com/slides/slide3.jpg | https://equatorcompany.com/slides/slide3.webp | https://equatorcompany.com/slides/slide3_mobile.jpg | https://equatorcompany.com/slides/slide3_mobile.webp | 810x541 / (mobile not measured) |
| 4 Water, Sanitation, and Resilient Cities | https://equatorcompany.com/slides/slide4.jpg | https://equatorcompany.com/slides/slide4.webp | https://equatorcompany.com/slides/slide4_mobile.jpg | https://equatorcompany.com/slides/slide4_mobile.webp | 1200x900 / (mobile not measured) |
| 5 Resilience and Impact | https://equatorcompany.com/slides/slide5.jpg | https://equatorcompany.com/slides/slide5.webp | https://equatorcompany.com/slides/slide5_mobile.jpg | https://equatorcompany.com/slides/slide5_mobile.webp | 1200x800 / (mobile not measured) |

All slides render `object-fit:cover` inside a 66:50 card (630x477 at 1440). The blurhash placeholder CSS gradients are in CLONE_SPEC.md section 9.

### 4.5 Funding strip
| File | Status | Size | URL |
|---|---|---|---|
| mono.svg | PRESENT | 429x42 viewBox, 93,649 B (static, not animated) | https://equatorcompany.com/mono.svg |

### 4.6 Favicons / PWA (MISSING)
| File | URL | Size |
|---|---|---|
| favicon.ico | https://equatorcompany.com/favicon.ico | 15,086 B |
| favicon.svg | https://equatorcompany.com/favicon.svg | 17,286 B |
| favicon-96x96.png | https://equatorcompany.com/favicon-96x96.png | 96x96 |
| apple-touch-icon.png | https://equatorcompany.com/apple-touch-icon.png | 180x180 |
| web-app-manifest-192x192.png | https://equatorcompany.com/web-app-manifest-192x192.png | 192x192 |
| web-app-manifest-512x512.png | https://equatorcompany.com/web-app-manifest-512x512.png | 512x512 |
| site.webmanifest | https://equatorcompany.com/site.webmanifest | JSON (contents in CLONE_SPEC section 13) |

## 5. Documents (MISSING)
| File | URL | Size |
|---|---|---|
| Equator-PRR-Investimentos.pdf | https://equatorcompany.com/Equator-PRR-Investimentos.pdf | 526,235 B ("Project sheet" link, `download`) |

## 6. Not needed by the clone (present in the saved folder)
`B2rxQMiQ.js` (Nuxt bundle), `entry.DkmCBGCE.css`, `index.Bz9B3sVc.css`, `useSectionWatcher.DxYJ83pd.css`, `default.DxKFSwaE.css` are reference only. `vce701823e78c4301a35b7e07294d87301792088814092` is the Cloudflare analytics beacon. Do not ship it.

## 7. Inline SVG icons
All icons are inline SVG in the original. There are no icon fonts and no sprite files. Their verbatim markup is in Appendix A below:
- `logoWordmark`: 352x34 "The Equator Company" wordmark, `fill=currentColor` (header logo; also used on /privacy-policy)
- `navEmail` / `navLinkedIn`: 24x24 header icons (earth)
- `plus`: 24x24 "+" used in dropdown and slide pills
- `carouselPrev` / `carouselNext`: 24x24 arrows
- `memberLinkedInLogo` (16x16) / `memberArrow` (13x13 ↗): team LinkedIn tag
- `ctaSignupArrow` (17x16) / `ctaLinkedinArrow` (13x12): CTA buttons, fill oat
- `footerWordmark`: 276x180 stacked wordmark, fill `var(--color-oat)`
- `footerPin` / `footerMail` / `footerLinkedIn`: 24x24 footer icons, `currentColor`

## Appendix A — Inline SVG markup (verbatim from live DOM, `data-v-*` attrs stripped)

### logoWordmark
```html
<svg xmlns="http://www.w3.org/2000/svg" width="352" height="34" viewBox="0 0 352 34" fill="none"><path d="M21.2733 4.54455V0.457882H0V4.54455H8.26832V25.9753H13.005V4.54455H21.2733ZM23.6387 25.9753H28.262V15.2038C28.262 12.0327 29.7653 10.2774 32.3216 10.2774C34.3141 10.2774 35.4028 11.5386 35.4028 13.8305V25.9783H40.062V12.533C40.062 8.67366 37.7682 6.30594 34.162 6.30594C31.4566 6.30594 29.3149 7.6429 28.262 9.97424V0.457882H23.6387V25.9753ZM51.5994 22.8436C48.8553 22.8436 47.2028 20.7427 47.0894 17.1896H59.0415C59.2294 16.5772 59.4173 15.5464 59.4173 14.6309C59.4173 9.58922 56.4107 6.30291 51.5994 6.30291C48.8553 6.30291 46.6748 7.21847 45.0611 9.05262C43.4445 10.8868 42.657 13.3697 42.657 16.5014C42.657 22.7284 46.0007 26.4331 51.5636 26.4331C55.4711 26.4331 58.3286 24.5232 59.2324 21.1247L55.3995 19.8635C54.9103 21.8492 53.6695 22.8436 51.6024 22.8436H51.5994ZM51.5249 9.70139C53.6307 9.70139 55.0207 11.3051 55.0207 13.6365C55.0207 14.1337 55.0207 14.4005 54.9819 14.5915H47.164C47.4653 11.4961 49.0819 9.70139 51.5249 9.70139ZM74.3761 14.934H85.2394V11.1141H74.3761V4.54455H86.5906V0.457882H69.7885V25.9753H86.5906V21.8886H74.3761V14.9371V14.934ZM106.435 6.75766H102.79L102.226 9.88936C101.436 7.71263 99.2198 6.29988 96.4756 6.29988C91.5152 6.29988 88.4698 10.1956 88.4698 16.7288C88.4698 19.6695 89.1827 22.0402 90.5757 23.7956C92.0044 25.5539 93.8448 26.4301 96.1386 26.4301C98.9573 26.4301 100.911 25.1325 101.815 22.6496V33.5363H106.438V6.76069L106.435 6.75766ZM97.6031 22.7254C94.7844 22.7254 93.2065 20.5487 93.2065 16.6136C93.2065 12.2965 94.8232 9.85298 97.6807 9.85298C100.049 9.85298 101.815 11.6871 101.815 14.552V17.4564C101.815 20.7033 100.124 22.7284 97.6061 22.7284L97.6031 22.7254ZM126.503 6.75766H121.844V17.6079C121.844 20.8154 120.38 22.689 117.973 22.689C116.019 22.689 114.927 21.4278 114.927 19.1753V6.76069H110.304V20.2455C110.304 24.0654 112.672 26.4331 116.168 26.4331C119.175 26.4331 121.203 25.0203 122.068 22.3828L122.632 25.9723H126.503V6.76069V6.75766ZM137.591 6.29988C133.268 6.29988 130.375 8.51602 130.035 12.1449L134.396 12.8331C134.435 10.8837 135.449 9.8166 137.364 9.8166C139.279 9.8166 140.296 10.8868 140.296 12.7573V14.8976C139.693 14.8582 138.828 14.7824 138.229 14.7824C132.403 14.7824 129.17 17.035 129.17 20.8943C129.17 24.2564 131.5 26.3573 135.109 26.3573C137.704 26.3573 139.846 25.1719 140.558 23.2256C140.708 23.7228 140.86 24.1806 141.122 24.6384C141.835 25.7449 143.076 26.3573 144.618 26.3573C145.632 26.3573 146.685 26.0905 147.323 25.6327L147.135 22.4252C146.873 22.692 146.458 22.8072 146.047 22.8072C145.146 22.8072 144.731 22.3495 144.731 21.3187V12.4935C144.731 8.40688 142.288 6.30594 137.591 6.30594V6.29988ZM136.538 23.1468C134.772 23.1468 133.68 22.1524 133.68 20.5881C133.68 18.5629 135.41 17.4927 138.754 17.4927C138.942 17.4927 139.505 17.4927 140.296 17.6079V18.9449C140.296 21.5794 138.793 23.1468 136.538 23.1468ZM156.794 22.5738C155.177 22.5738 154.39 21.6946 154.39 19.9757V10.2713H159.69V6.75766H154.39V2.06163L149.731 2.67402V6.76069H147.174V10.2744H149.731V20.5517C149.731 24.3716 151.911 26.4331 155.932 26.4331C157.584 26.4331 159.24 25.9359 160.442 25.0567L159.803 21.5794C158.715 22.304 157.85 22.5738 156.797 22.5738H156.794ZM170.473 6.29988C167.729 6.29988 165.512 7.21544 163.896 9.01321C162.279 10.8079 161.492 13.2545 161.492 16.3468C161.492 19.4391 162.282 21.9614 163.896 23.7592C165.512 25.5539 167.729 26.4331 170.473 26.4331C176.036 26.4331 179.457 22.6132 179.457 16.3468C179.457 10.0804 176 6.29988 170.473 6.29988ZM170.473 22.9164C167.615 22.9164 166.151 20.6639 166.151 16.3468C166.151 12.0297 167.618 9.81357 170.473 9.81357C173.327 9.81357 174.834 12.0661 174.834 16.3468C174.834 20.6275 173.33 22.9164 170.473 22.9164ZM186.935 25.9723V16.6894C186.935 13.1757 188.775 10.9989 191.594 10.9989C192.232 10.9989 193.059 11.1141 193.512 11.2657L193.775 6.45146C193.36 6.33626 192.948 6.33626 192.534 6.33626C189.715 6.33626 187.499 8.32199 186.744 11.4173L186.219 6.75766H182.309V25.9723H186.932H186.935ZM213.243 26.4301C217.941 26.4301 221.249 24.1775 222.639 20.0515L218.466 18.0263C217.753 20.776 215.835 22.3828 213.243 22.3828C209.222 22.3828 206.89 18.9843 206.89 13.2151C206.89 7.44584 209.219 4.08374 213.243 4.08374C215.913 4.08374 217.753 5.6511 218.466 8.40082L222.639 6.33929C221.249 2.21321 217.941 -0.00292969 213.243 -0.00292969C209.822 -0.00292969 207.042 1.18245 204.975 3.58655C202.908 5.95427 201.894 9.16479 201.894 13.2121C201.894 17.2593 202.908 20.4698 204.975 22.877C207.042 25.2447 209.822 26.4301 213.243 26.4301ZM232.861 6.29685C230.117 6.29685 227.901 7.21241 226.284 9.01018C224.667 10.8049 223.88 13.2515 223.88 16.3437C223.88 19.436 224.67 21.9584 226.284 23.7561C227.901 25.5509 230.117 26.4301 232.861 26.4301C238.424 26.4301 241.845 22.6102 241.845 16.3437C241.845 10.0773 238.388 6.29685 232.861 6.29685ZM232.861 22.9133C230.004 22.9133 228.539 20.6608 228.539 16.3437C228.539 12.0267 230.004 9.81053 232.861 9.81053C235.719 9.81053 237.222 12.0631 237.222 16.3437C237.222 20.6244 235.719 22.9133 232.861 22.9133ZM254.847 6.29685C252.103 6.29685 249.923 7.86421 249.058 10.4593L248.494 6.75463H244.697V25.9693H249.32V15.1978C249.32 12.1025 250.749 10.2713 253.04 10.2713C255.032 10.2713 256.046 11.4567 256.046 13.785V25.9723H260.706V15.1614C260.706 12.0661 262.095 10.2713 264.389 10.2713C266.456 10.2713 267.435 11.4567 267.435 13.785V25.9723H272.058V12.3723C272.058 8.5524 269.842 6.29685 266.233 6.29685C263.527 6.29685 261.347 7.78539 260.333 10.3471C259.62 7.78842 257.589 6.29685 254.844 6.29685H254.847ZM275.93 33.5332H280.553V23.5257C281.418 25.3205 283.411 26.4301 285.815 26.4301C288.219 26.4301 290.211 25.5145 291.679 23.6409C293.146 21.7704 293.895 19.2875 293.895 16.2285C293.895 13.1696 293.182 10.8049 291.789 9.00715C290.399 7.21241 288.52 6.29382 286.113 6.29382C283.369 6.29382 281 8.01276 280.249 10.3441L279.724 6.75463H275.927V33.5332H275.93ZM284.687 10.0409C287.581 10.0409 289.158 12.2571 289.158 16.3832C289.158 20.5092 287.467 22.9164 284.61 22.9164C282.206 22.9164 280.55 21.0822 280.55 18.1809V15.3524C280.55 12.1055 282.28 10.044 284.684 10.044L284.687 10.0409ZM303.741 6.29685C299.419 6.29685 296.526 8.51299 296.186 12.1419L300.547 12.8301C300.586 10.8807 301.6 9.81357 303.515 9.81357C305.43 9.81357 306.447 10.8837 306.447 12.7543V14.8946C305.844 14.8552 304.982 14.7794 304.38 14.7794C298.554 14.7794 295.321 17.0319 295.321 20.8912C295.321 24.2533 297.65 26.3543 301.26 26.3543C303.852 26.3543 305.996 25.1689 306.709 23.2226C306.858 23.7198 307.01 24.1775 307.273 24.6353C307.986 25.7419 309.227 26.3543 310.769 26.3543C311.783 26.3543 312.836 26.0875 313.474 25.6297L313.286 22.4222C313.024 22.689 312.609 22.8042 312.198 22.8042C311.297 22.8042 310.882 22.3464 310.882 21.3157V12.4905C310.882 8.40385 308.439 6.30291 303.741 6.30291V6.29685ZM302.688 23.1437C300.923 23.1437 299.831 22.1494 299.831 20.585C299.831 18.5599 301.561 17.4897 304.905 17.4897C305.093 17.4897 305.656 17.4897 306.447 17.6049V18.9419C306.447 21.5764 304.943 23.1437 302.688 23.1437ZM315.467 25.9693H320.09V15.1978C320.09 12.0267 321.593 10.2713 324.15 10.2713C326.142 10.2713 327.231 11.5325 327.231 13.8244V25.9723H331.89V12.5269C331.89 8.6676 329.596 6.29988 325.99 6.29988C323.022 6.29988 320.767 7.82783 319.825 10.4623L319.261 6.75766H315.464V25.9723L315.467 25.9693ZM338.392 6.75463H333.507L340.421 26.6574C339.407 29.4466 338.691 30.2863 337.077 30.2863C336.287 30.2863 335.723 30.0953 334.861 29.4829L334.07 33.0724C334.971 33.6454 336.251 33.988 337.453 33.988C341.062 33.988 343.204 31.9265 345.044 26.7302L351.997 6.7516H347.487L342.902 21.3429H342.828L338.392 6.7516V6.75463Z" fill="currentColor"></path></svg>
```

### navEmail
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M21.8002 5V19H2.2002V5M21.8002 5H2.2002M21.8002 5L12.0002 12L2.2002 5" stroke="var(--color-earth)" stroke-width="2" stroke-linecap="round"></path></svg>
```

### navLinkedIn
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M18.2222 4C18.6937 4 19.1459 4.1873 19.4793 4.5207C19.8127 4.8541 20 5.30628 20 5.77778V18.2222C20 18.6937 19.8127 19.1459 19.4793 19.4793C19.1459 19.8127 18.6937 20 18.2222 20H5.77778C5.30628 20 4.8541 19.8127 4.5207 19.4793C4.1873 19.1459 4 18.6937 4 18.2222V5.77778C4 5.30628 4.1873 4.8541 4.5207 4.5207C4.8541 4.1873 5.30628 4 5.77778 4H18.2222ZM17.7778 17.7778V13.0667C17.7778 12.2981 17.4725 11.5611 16.929 11.0176C16.3856 10.4742 15.6485 10.1689 14.88 10.1689C14.1244 10.1689 13.2444 10.6311 12.8178 11.3244V10.3378H10.3378V17.7778H12.8178V13.3956C12.8178 12.7111 13.3689 12.1511 14.0533 12.1511C14.3834 12.1511 14.6999 12.2822 14.9333 12.5156C15.1667 12.749 15.2978 13.0655 15.2978 13.3956V17.7778H17.7778ZM7.44889 8.94222C7.84495 8.94222 8.22478 8.78489 8.50484 8.50484C8.78489 8.22478 8.94222 7.84495 8.94222 7.44889C8.94222 6.62222 8.27556 5.94667 7.44889 5.94667C7.05047 5.94667 6.66838 6.10494 6.38666 6.38666C6.10494 6.66838 5.94667 7.05047 5.94667 7.44889C5.94667 8.27556 6.62222 8.94222 7.44889 8.94222ZM8.68444 17.7778V10.3378H6.22222V17.7778H8.68444Z" fill="var(--color-earth)"></path></svg>
```

### plus
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M11 13H5V11H11V5H13V11L19 11V13H13L13 19H11L11 13Z" fill="var(--color-earth)"></path></svg>
```

### carouselPrev
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M7.825 13L13.425 18.6L12 20L4 12L12 4L13.425 5.4L7.825 11L20 11V13L7.825 13Z" fill="var(--color-earth)"></path></svg>
```

### carouselNext
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M16.175 11L10.575 5.4L12 4L20 12L12 20L10.575 18.6L16.175 13L4 13L4 11L16.175 11Z" fill="var(--color-earth)"></path></svg>
```

### memberLinkedInLogo
```html
<svg class="logo" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M14.2222 0C14.6937 0 15.1459 0.187301 15.4793 0.520699C15.8127 0.854097 16 1.30628 16 1.77778V14.2222C16 14.6937 15.8127 15.1459 15.4793 15.4793C15.1459 15.8127 14.6937 16 14.2222 16H1.77778C1.30628 16 0.854097 15.8127 0.520699 15.4793C0.187301 15.1459 0 14.6937 0 14.2222V1.77778C0 1.30628 0.187301 0.854097 0.520699 0.520699C0.854097 0.187301 1.30628 0 1.77778 0H14.2222ZM13.7778 13.7778V9.06667C13.7778 8.29813 13.4725 7.56107 12.929 7.01763C12.3856 6.47419 11.6485 6.16889 10.88 6.16889C10.1244 6.16889 9.24444 6.63111 8.81778 7.32444V6.33778H6.33778V13.7778H8.81778V9.39556C8.81778 8.71111 9.36889 8.15111 10.0533 8.15111C10.3834 8.15111 10.6999 8.28222 10.9333 8.5156C11.1667 8.74898 11.2978 9.06551 11.2978 9.39556V13.7778H13.7778ZM3.44889 4.94222C3.84495 4.94222 4.22478 4.78489 4.50484 4.50484C4.78489 4.22478 4.94222 3.84495 4.94222 3.44889C4.94222 2.62222 4.27556 1.94667 3.44889 1.94667C3.05047 1.94667 2.66838 2.10494 2.38666 2.38666C2.10494 2.66838 1.94667 3.05047 1.94667 3.44889C1.94667 4.27556 2.62222 4.94222 3.44889 4.94222ZM4.68444 13.7778V6.33778H2.22222V13.7778H4.68444Z" fill="var(--color-earth)"></path></svg>
```

### memberArrow
```html
<svg class="arrow" xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M1 0V2H9.59L0 11.59L1.41 13L11 3.41V12H13V0H1Z" fill="var(--color-earth)"></path></svg>
```

### ctaSignupArrow
```html
<svg xmlns="http://www.w3.org/2000/svg" width="17" height="16" viewBox="0 0 17 16" fill="none"><path d="M12.175 7L6.575 1.4L8 -6.99382e-07L16 8L8 16L6.575 14.6L12.175 9L6.11959e-07 9L7.86805e-07 7L12.175 7Z" fill="var(--color-oat)"></path></svg>
```

### ctaLinkedinArrow
```html
<svg xmlns="http://www.w3.org/2000/svg" width="13" height="12" viewBox="0 0 13 12" fill="none"><path d="M9.13125 5.25L4.93125 1.05L6 -5.24537e-07L12 6L6 12L4.93125 10.95L9.13125 6.75L4.5897e-07 6.75L5.90104e-07 5.25L9.13125 5.25Z" fill="var(--color-oat)"></path></svg>
```

### footerWordmark
```html
<svg width="276" height="180" viewBox="0 0 276 180" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M38.92 7.36V0H0V7.36H15.13V45.94H23.79V7.36H38.92Z" fill="var(--color-oat)"></path><path d="M43.2598 45.94H51.7198V26.55C51.7198 20.84 54.4698 17.68 59.1498 17.68C62.7898 17.68 64.7898 19.95 64.7898 24.08V45.95H73.3198V21.74C73.3198 14.79 69.1198 10.53 62.5198 10.53C57.5698 10.53 53.6498 12.94 51.7198 17.13V0H43.2598V45.94Z" fill="var(--color-oat)"></path><path d="M94.4298 40.2995C89.4098 40.2995 86.3798 36.5195 86.1798 30.1195H108.05C108.39 29.0195 108.74 27.1595 108.74 25.5095C108.74 16.4295 103.24 10.5195 94.4398 10.5195C89.4198 10.5195 85.4298 12.1695 82.4698 15.4695C79.5098 18.7695 78.0698 23.2395 78.0698 28.8795C78.0698 40.0895 84.1898 46.7595 94.3698 46.7595C101.52 46.7595 106.75 43.3195 108.4 37.1995L101.39 34.9295C100.5 38.5095 98.2298 40.2895 94.4398 40.2895L94.4298 40.2995ZM94.2898 16.6395C98.1398 16.6395 100.69 19.5295 100.69 23.7195C100.69 24.6095 100.69 25.0995 100.62 25.4395H86.3198C86.8698 19.8695 89.8298 16.6395 94.2998 16.6395H94.2898Z" fill="var(--color-oat)"></path><path d="M11.8299 85.6696H31.6999V78.7896H11.8299V66.9596H34.1799V59.5996H3.43994V105.54H34.1799V98.1796H11.8299V85.6696Z" fill="var(--color-oat)"></path><path d="M63.8201 70.9509L62.7901 76.5909C61.3501 72.6709 57.2901 70.1309 52.2701 70.1309C43.1901 70.1309 37.6201 77.1409 37.6201 88.9009C37.6201 94.1909 38.9301 98.4609 41.4701 101.621C44.0801 104.781 47.4501 106.371 51.6501 106.371C56.8101 106.371 60.3801 104.031 62.0301 99.5609V119.161H70.4901V70.9509H63.8201ZM62.0301 90.2109C62.0301 96.0609 58.9401 99.7009 54.3301 99.7009C49.1701 99.7009 46.2801 95.7809 46.2801 88.7009C46.2801 80.9309 49.2401 76.5309 54.4601 76.5309C58.7901 76.5309 62.0201 79.8309 62.0201 84.9909V90.2209L62.0301 90.2109Z" fill="var(--color-oat)"></path><path d="M107.22 70.9492H98.6901V90.4792C98.6901 96.2592 96.0101 99.6292 91.6101 99.6292C88.0301 99.6292 86.0401 97.3592 86.0401 93.2992V70.9492H77.5801V95.2292C77.5801 102.109 81.9101 106.369 88.3101 106.369C93.8101 106.369 97.5201 103.829 99.1101 99.0792L100.14 105.539H107.22V70.9492Z" fill="var(--color-oat)"></path><path d="M144.97 99.1509C144.49 99.6309 143.73 99.8409 142.98 99.8409C141.33 99.8409 140.57 99.0109 140.57 97.1609V81.2709C140.57 73.9109 136.1 70.1309 127.5 70.1309C119.59 70.1309 114.3 74.1209 113.68 80.6509L121.66 81.8909C121.73 78.3809 123.59 76.4609 127.09 76.4609C130.59 76.4609 132.45 78.3809 132.45 81.7509V85.6009C131.35 85.5309 129.77 85.3909 128.67 85.3909C118.01 85.3909 112.1 89.4509 112.1 96.3909C112.1 102.441 116.36 106.221 122.97 106.221C127.72 106.221 131.64 104.091 132.94 100.581C133.22 101.471 133.49 102.301 133.97 103.121C135.28 105.111 137.55 106.211 140.37 106.211C142.23 106.211 144.15 105.731 145.32 104.901L144.98 99.1209L144.97 99.1509ZM132.45 92.8909C132.45 97.6409 129.7 100.461 125.57 100.461C122.34 100.461 120.34 98.6709 120.34 95.8509C120.34 92.2009 123.5 90.2809 129.62 90.2809C129.96 90.2809 131 90.2809 132.44 90.4909V92.9009L132.45 92.8909Z" fill="var(--color-oat)"></path><path d="M162.65 99.4205C159.69 99.4205 158.25 97.8405 158.25 94.7405V77.2705H167.95V70.9405H158.25V62.4805L149.72 63.5805V70.9405H145.04V77.2705H149.72V95.7705C149.72 102.65 153.71 106.36 161.07 106.36C164.1 106.36 167.12 105.47 169.32 103.88L168.15 97.6205C166.15 98.9305 164.57 99.4105 162.65 99.4105V99.4205Z" fill="var(--color-oat)"></path><path d="M187.68 70.1294C182.66 70.1294 178.6 71.7794 175.64 75.0094C172.68 78.2394 171.24 82.6394 171.24 88.2094C171.24 93.7794 172.68 98.3194 175.64 101.549C178.6 104.779 182.65 106.359 187.68 106.359C197.86 106.359 204.12 99.4794 204.12 88.1994C204.12 76.9194 197.79 70.1094 187.68 70.1094V70.1294ZM187.68 100.049C182.45 100.049 179.77 95.9894 179.77 88.2194C179.77 80.4494 182.45 76.4594 187.68 76.4594C192.91 76.4594 195.66 80.5194 195.66 88.2194C195.66 95.9194 192.91 100.049 187.68 100.049Z" fill="var(--color-oat)"></path><path d="M217.8 105.54V88.8297C217.8 82.4997 221.17 78.5797 226.33 78.5797C227.5 78.5797 229.01 78.7897 229.84 79.0597L230.32 70.3897C229.56 70.1797 228.81 70.1797 228.05 70.1797C222.89 70.1797 218.83 73.7597 217.46 79.3297L216.5 70.9397H209.35V105.53H217.81L217.8 105.54Z" fill="var(--color-oat)"></path><path d="M21.5298 165.971C30.1298 165.971 36.1798 161.911 38.7198 154.491L31.0898 150.841C29.7798 155.791 26.2798 158.681 21.5298 158.681C14.1698 158.681 9.90977 152.561 9.90977 142.181C9.90977 131.801 14.1698 125.741 21.5298 125.741C26.4098 125.741 29.7798 128.561 31.0898 133.511L38.7198 129.801C36.1798 122.371 30.1198 118.381 21.5298 118.381C15.2698 118.381 10.1798 120.511 6.39977 124.841C2.61977 129.101 0.759766 134.881 0.759766 142.171C0.759766 149.461 2.61977 155.241 6.39977 159.571C10.1798 163.831 15.2698 165.971 21.5298 165.971Z" fill="var(--color-oat)"></path><path d="M57.42 129.731C52.4 129.731 48.34 131.381 45.38 134.611C42.42 137.841 40.98 142.241 40.98 147.811C40.98 153.381 42.42 157.921 45.38 161.151C48.34 164.381 52.39 165.961 57.42 165.961C67.6 165.961 73.86 159.081 73.86 147.801C73.86 136.521 67.53 129.711 57.42 129.711V129.731ZM57.42 159.651C52.19 159.651 49.51 155.591 49.51 147.821C49.51 140.051 52.19 136.061 57.42 136.061C62.65 136.061 65.4 140.121 65.4 147.821C65.4 155.521 62.65 159.651 57.42 159.651Z" fill="var(--color-oat)"></path><path d="M97.6599 129.73C92.6399 129.73 88.6498 132.55 87.0698 137.23L86.0398 130.56H79.0898V165.15H87.5499V145.76C87.5499 140.19 90.1598 136.89 94.3598 136.89C97.9998 136.89 99.8598 139.02 99.8598 143.22V165.16H108.39V145.7C108.39 140.13 110.93 136.9 115.13 136.9C118.91 136.9 120.7 139.03 120.7 143.23V165.17H129.16V140.69C129.16 133.81 125.1 129.76 118.5 129.76C113.55 129.76 109.56 132.44 107.7 137.05C106.39 132.44 102.68 129.76 97.6599 129.76V129.73Z" fill="var(--color-oat)"></path><path d="M165.26 134.61C162.72 131.38 159.28 129.73 154.88 129.73C149.86 129.73 145.53 132.82 144.15 137.02L143.19 130.56H136.24V178.77H144.7V160.75C146.28 163.98 149.93 165.98 154.33 165.98C158.73 165.98 162.38 164.33 165.06 160.96C167.74 157.59 169.12 153.12 169.12 147.62C169.12 142.12 167.81 137.86 165.27 134.62L165.26 134.61ZM152.13 159.64C147.73 159.64 144.7 156.34 144.7 151.11V146.02C144.7 140.17 147.86 136.46 152.27 136.46C157.56 136.46 160.45 140.45 160.45 147.88C160.45 155.31 157.36 159.64 152.13 159.64Z" fill="var(--color-oat)"></path><path d="M204.6 158.75C204.12 159.23 203.36 159.44 202.61 159.44C200.96 159.44 200.2 158.61 200.2 156.76V140.87C200.2 133.51 195.73 129.73 187.13 129.73C179.22 129.73 173.93 133.72 173.31 140.25L181.29 141.49C181.36 137.98 183.22 136.06 186.72 136.06C190.22 136.06 192.08 137.98 192.08 141.35V145.2C190.98 145.13 189.4 144.99 188.3 144.99C177.64 144.99 171.73 149.05 171.73 155.99C171.73 162.04 175.99 165.82 182.6 165.82C187.35 165.82 191.27 163.69 192.57 160.18C192.85 161.07 193.12 161.9 193.6 162.72C194.91 164.71 197.18 165.81 200 165.81C201.86 165.81 203.78 165.33 204.95 164.5L204.61 158.72L204.6 158.75ZM192.08 152.49C192.08 157.24 189.33 160.06 185.2 160.06C181.97 160.06 179.97 158.27 179.97 155.45C179.97 151.8 183.13 149.88 189.25 149.88C189.59 149.88 190.63 149.88 192.07 150.09V152.5L192.08 152.49Z" fill="var(--color-oat)"></path><path d="M208.59 165.15H217.05V145.76C217.05 140.05 219.8 136.89 224.48 136.89C228.12 136.89 230.12 139.16 230.12 143.29V165.16H238.65V140.95C238.65 134 234.45 129.74 227.85 129.74C222.42 129.74 218.29 132.49 216.57 137.24L215.54 130.57H208.59V165.16V165.15Z" fill="var(--color-oat)"></path><path d="M250.54 130.561H241.6L254.25 166.391C252.39 171.411 251.09 172.921 248.13 172.921C246.69 172.921 245.65 172.581 244.07 171.481L242.63 177.941C244.28 178.971 246.62 179.591 248.82 179.591C255.42 179.591 259.34 175.881 262.71 166.521L275.43 130.551H267.18L258.79 156.821H258.65L250.53 130.551L250.54 130.561Z" fill="var(--color-oat)"></path></svg>
```

### footerPin
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2C16.6199 2 20.7996 5.5418 20.7998 11.0195C20.7998 14.6715 17.863 18.995 12 24C6.13708 18.995 3.2002 14.6715 3.2002 11.0195C3.20043 5.54188 7.38021 2.0001 12 2ZM12 4.2002C8.31524 4.2003 5.40062 7.02685 5.40039 11.0195C5.40039 13.5935 7.545 17.0042 12 21.0742C16.455 17.0042 18.6006 13.5935 18.6006 11.0195C18.6004 7.02678 15.6849 4.2002 12 4.2002ZM12 8.33301C13.3671 8.33301 14.4755 9.44156 14.4756 10.8086C14.4756 12.1757 13.3671 13.2842 12 13.2842C10.633 13.2841 9.52441 12.1756 9.52441 10.8086C9.52452 9.44163 10.633 8.33311 12 8.33301Z" fill="currentColor"></path></svg>
```

### footerMail
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M21.8002 5V19H2.2002V5M21.8002 5H2.2002M21.8002 5L12.0002 12L2.2002 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path></svg>
```

### footerLinkedIn
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M19.3618 2.53516C19.9197 2.53516 20.4547 2.75676 20.8491 3.15121C21.2436 3.54566 21.4652 4.08065 21.4652 4.63849V19.3618C21.4652 19.9197 21.2436 20.4547 20.8491 20.8491C20.4547 21.2436 19.9197 21.4652 19.3618 21.4652H4.63849C4.08065 21.4652 3.54566 21.2436 3.15121 20.8491C2.75676 20.4547 2.53516 19.9197 2.53516 19.3618V4.63849C2.53516 4.08065 2.75676 3.54566 3.15121 3.15121C3.54566 2.75676 4.08065 2.53516 4.63849 2.53516H19.3618ZM18.836 18.836V13.2622C18.836 12.3529 18.4748 11.4808 17.8318 10.8379C17.1889 10.1949 16.3168 9.83372 15.4076 9.83372C14.5136 9.83372 13.4725 10.3806 12.9677 11.2009V10.0335H10.0335V18.836H12.9677V13.6513C12.9677 12.8415 13.6197 12.1789 14.4295 12.1789C14.82 12.1789 15.1945 12.3341 15.4706 12.6102C15.7467 12.8863 15.9018 13.2608 15.9018 13.6513V18.836H18.836ZM6.61562 8.38242C7.08421 8.38242 7.5336 8.19628 7.86494 7.86494C8.19628 7.5336 8.38242 7.08421 8.38242 6.61562C8.38242 5.63757 7.59367 4.83831 6.61562 4.83831C6.14425 4.83831 5.69218 5.02556 5.35887 5.35887C5.02556 5.69218 4.83831 6.14425 4.83831 6.61562C4.83831 7.59367 5.63757 8.38242 6.61562 8.38242ZM8.07744 18.836V10.0335H5.16432V18.836H8.07744Z" fill="currentColor"></path></svg>
```
