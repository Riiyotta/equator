# The Equator Company — local clone

React 18 + Vite 5 + Tailwind v3 replica of https://equatorcompany.com/, for local development only.

```bash
npm install
npm run dev      # http://localhost:5193
npm run build
```

The copy, team photos, logos, videos, Lottie files and the National 2 font (Klim Type Foundry, commercial licence) belong to their owners. Don't deploy this publicly without the rights to them.

## Information architecture

- `ia.json` is the only IA file to hand-edit.
- `IA.md` and `matrix.csv` are **generated** from it — don't edit them by hand.

After changing routes or sections, re-run:

```bash
node validate.mjs && node build.mjs
```

### What the data shows

- 3 routes, 3 templates, 16 sections; every route is a one-off page, with no patterned collections.
- Only 3 sections are shared across templates: the nav (`chrome.header-nav`), `footer.main` and `footer.subfooter`, used by home and privacy policy.
- The other 13 sections are single-use, and 10 of them live on the home page alone. The build effort, and all the scroll-linked motion, is concentrated in that one route.
- The three templates differ mainly in their chrome: the home page has the animated splash and shrinking logo, privacy policy uses a static logo bar, and the 404 page has no chrome at all.

## Other docs

- `CLONE_SPEC.md` — measured build spec from the live site.
- `ASSET_MANIFEST.md` — asset inventory and original URLs.
