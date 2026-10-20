import { forwardRef, useEffect } from 'react'
import { NAV, MAIL, LINKEDIN } from '../lib/content'
import { LogoWordmark, NavEmail, NavLinkedIn } from '../lib/icons'

/* Hamburger, "squeeze" variant (CLONE_SPEC 4.3) */
export function Hamburger({ open, onToggle }) {
  return (
    <button
      className={`hamburger hamburger--squeeze${open ? ' is-active' : ''}`}
      type="button"
      aria-label="Menu"
      onClick={onToggle}
    >
      <span className="hamburger-box">
        <span className="hamburger-inner" />
      </span>
    </button>
  )
}

/* v-scroll-lock equivalent: body overflow hidden while the mobile menu is open */
export function useScrollLock(locked) {
  useEffect(() => {
    if (!locked) return
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = ''
    }
  }, [locked])
}

/*
 * Desktop header / mobile menu overlay (CLONE_SPEC 4.2, 4.3, 12).
 * home: links are in-page anchors handled by onNavigate(id).
 * privacy: links are plain "/#id" hrefs (full navigation back to home).
 */
export function Header({ open, activeHash = '', onNavigate, logoSpace = null }) {
  return (
    <div className="headerCont noselect">
      <header className={open ? 'open' : ''}>
        <div className="logoSpace">{logoSpace}</div>
        <nav className="text-bodyS">
          {NAV.map(({ id, label }) => (
            <a
              key={id}
              href={`/#${id}`}
              className={`navlink${activeHash === `#${id}` ? ' active' : ''}`}
              onClick={
                onNavigate
                  ? (e) => {
                      e.preventDefault()
                      onNavigate(id)
                    }
                  : undefined
              }
            >
              {label}
            </a>
          ))}
          <div className="icons text-bodyS">
            <a href={MAIL}>
              <NavEmail />
              <span>Email us</span>
            </a>
            <a href={LINKEDIN} target="_blank" rel="noopener noreferrer">
              <NavLinkedIn />
              <span>LinkedIn</span>
            </a>
          </div>
        </nav>
      </header>
    </div>
  )
}

/* Home-page mobile bar (fixed, fades in with the small-logo condition) */
export function MobileHeader({ visible, open, onToggle }) {
  return (
    <div className={`mobileHeader${visible ? ' visible' : ''}`}>
      <Hamburger open={open} onToggle={onToggle} />
    </div>
  )
}

/* Home-page logo zone: sticky, scroll-scaled wordmark (CLONE_SPEC 4.2) */
export const LogoZone = forwardRef(function LogoZone({ small, onClick }, ref) {
  return (
    <div className="logoZone" ref={ref}>
      <div className="logoTopScroll">
        <div className={`logoCont${small ? ' small' : ''}`}>
          <a
            href="/"
            className="text-headline4"
            aria-label="The Equator Company"
            onClick={(e) => {
              e.preventDefault()
              onClick()
            }}
          >
            <LogoWordmark />
          </a>
        </div>
      </div>
    </div>
  )
})
