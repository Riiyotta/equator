/** @type {import('tailwindcss').Config} */
// Design tokens from CLONE_SPEC.md section 1 (entry.DkmCBGCE.css).
// Type sizes resolve through CSS custom properties declared on :root in src/index.css,
// because the original swaps them at the 768px breakpoint.
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        white: '#fff',
        oat: '#fcf8f0',
        lime: '#c8fdab',
        'lime-dark': '#c1f2a3', // slide pills when active (hard-coded in original)
        earth: '#3e2002',
        'earth-light': 'rgba(62,32,2,.7)',
        coral: '#ff9d69',
        'coral-light': '#feb891', // dropdown pills when open (hard-coded in original)
        'footer-text': '#9d8c79',
        'footer-credits': '#6d543c',
        'cta-bg': '#fff',
        'portrait-bg': '#fff',
        'nav-arrow': '#000', // vue3-carousel --vc-clr-primary
      },
      fontFamily: {
        national: ['National', 'Arial', 'Helvetica', 'sans-serif'],
      },
      fontSize: {
        headline1: ['var(--font-size-headline1)', { lineHeight: 'var(--font-line-headline1)', letterSpacing: 'var(--font-spacing-headline1)', fontWeight: 'var(--font-weight-headline1)' }],
        headline2: ['var(--font-size-headline2)', { lineHeight: 'var(--font-line-headline2)', letterSpacing: 'var(--font-spacing-headline2)' }],
        headline2Medium: ['var(--font-size-headline2)', { lineHeight: 'var(--font-line-headline2)', letterSpacing: 'var(--font-spacing-headline2)', fontWeight: 'var(--font-weight-headline2)' }],
        headline3: ['var(--font-size-headline3)', { lineHeight: 'var(--font-line-headline3)', letterSpacing: 'var(--font-spacing-headline3)' }],
        headline4: ['var(--font-size-headline4)', { lineHeight: 'var(--font-line-headline4)', letterSpacing: 'var(--font-spacing-headline4)', fontWeight: 'var(--font-weight-headline4)' }],
        bodyL: ['var(--font-size-body-l)', { lineHeight: 'var(--font-line-body-l)', letterSpacing: 'var(--font-spacing-body-l)' }],
        bodyM: ['var(--font-size-body-m)', { lineHeight: 'var(--font-line-body-m)', letterSpacing: 'var(--font-spacing-body-m)' }],
        bodyS: ['var(--font-size-body-s)', { lineHeight: 'var(--font-line-body-s)', letterSpacing: 'var(--font-spacing-body-s)' }],
        // --font-line-caption is never defined in the original (quirk kept on purpose).
        caption: ['var(--font-size-caption)', { lineHeight: 'var(--font-line-caption)', letterSpacing: 'var(--font-spacing-caption)' }],
        credits: ['.875rem', { lineHeight: '1' }],
      },
      spacing: {
        page: 'var(--margin-page)',
      },
      screens: {
        // all max-width, per CLONE_SPEC 1.3
        'max-1366': { max: '1366px' },
        'max-1180': { max: '1180px' },
        'max-1024': { max: '1024px' },
        'max-920': { max: '920px' },
        'max-768': { max: '768px' },
        'max-620': { max: '620px' },
        'max-520': { max: '520px' },
      },
    },
  },
  plugins: [],
}
