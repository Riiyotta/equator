#!/usr/bin/env node
/**
 * Re-measure section heights of the BUILT clone at 1440px (optional tool; verify_all.py never runs it).
 *
 *   npm ci && npx vite build --outDir <scratch-dir>
 *   npx vite preview --outDir <scratch-dir> --port <port>
 *   NODE_PATH="$(npm root -g)" EQUATOR_BASE_URL=http://localhost:<port> node design-repo/extraction/measure_sections.mjs > heights.json
 *
 * Playwright is resolved through NODE_PATH (a global install); no machine path is stored here.
 * Output: { viewport, templates: { <template id>: { route, pageHeight, sections: [{ section, index, top, height, inFlow }] } } }
 * One route per template. Section boundaries come from the rendered DOM:
 *   - home: the children of <main> (the absolutely-positioned logo zones and the fixed mobile header take no
 *     page height and are not sections);
 *   - legal: the <article> is split at its real heading boundaries (h1 -> legal-header; every bold-paragraph or
 *     h2 heading inside .body starts one content.legal-section that runs to the next heading / article end);
 *   - not-found: <main> is the single section.
 * The sticky header bar has margin-bottom:-68px, so it is recorded with inFlow:false (it adds no page height).
 */
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const BASE = process.env.EQUATOR_BASE_URL || 'http://localhost:4173';
const VIEWPORT = 1440;

export const ROUTES = {
  'template.home': '/',
  'template.legal-prose': '/privacy-policy',
  'template.not-found': '/this-route-does-not-exist',
};

function resolveSections(template) {
  const R = (el) => {
    const r = el.getBoundingClientRect();
    return { top: r.top + window.scrollY, bottom: r.bottom + window.scrollY };
  };
  const out = [];
  const push = (section, box, inFlow = true) => out.push({ section, top: box ? box.top : null, bottom: box ? box.bottom : null, inFlow });
  const main = document.querySelector('#root > main');
  if (template === 'template.home') {
    const map = [
      ['section.splash', 'chrome.splash'],
      ['div.headerCont', 'chrome.header', false],
      ['section.titleSection', 'hero.title'],
      ['section#our-story', 'narrative.story-reveal'],
      ['section#what-we-stand-for', 'values.sticky-stack'],
      ['section#capabilities', 'capabilities.accordion'],
      ['section#our-work', 'work.carousel-marquee'],
      ['section#team', 'team.roster'],
      ['section.ctaSection', 'conversion.cta-video'],
      ['footer', 'chrome.footer'],
      ['div.subfooter', 'chrome.subfooter'],
    ];
    for (const [sel, id, inFlow] of map) {
      const el = main.querySelector(':scope > ' + sel);
      push(id, el ? R(el) : null, inFlow !== false);
    }
  } else if (template === 'template.legal-prose') {
    const hc = main.querySelector(':scope > div.headerCont');
    push('chrome.header', hc ? R(hc) : null, false);
    const art = main.querySelector(':scope > article');
    const a = R(art);
    const body = art.querySelector('.body');
    const isHeading = (el) => el.tagName === 'H2' || (el.tagName === 'P' && el.children.length === 1 && el.firstElementChild.tagName === 'STRONG' && el.textContent.trim() === el.firstElementChild.textContent.trim());
    const heads = [...body.children].filter(isHeading);
    const tops = heads.map((h) => R(h).top);
    push('content.legal-header', { top: a.top, bottom: tops[0] ?? a.bottom });
    tops.forEach((t, i) => push('content.legal-section', { top: t, bottom: i + 1 < tops.length ? tops[i + 1] : a.bottom }));
    push('chrome.footer', R(main.querySelector(':scope > footer')));
    push('chrome.subfooter', R(main.querySelector(':scope > div.subfooter')));
  } else if (template === 'template.not-found') {
    push('content.not-found', R(main));
  }
  return out;
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: VIEWPORT, height: 900 } });
const result = { viewport: VIEWPORT, viewportHeight: 900, templates: {} };
for (const [template, route] of Object.entries(ROUTES)) {
  await page.goto(BASE + route, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  const rows = await page.evaluate(resolveSections, template);
  const pageHeight = await page.evaluate(() => document.documentElement.scrollHeight);
  result.templates[template] = {
    route,
    pageHeight,
    sections: rows.map((r, index) => ({
      section: r.section,
      index,
      top: r.top === null ? null : Math.round(r.top * 10) / 10,
      height: r.top === null ? null : Math.round((r.bottom - r.top) * 10) / 10,
      inFlow: r.inFlow,
    })),
  };
}
await browser.close();
process.stdout.write(JSON.stringify(result, null, 1) + '\n');
