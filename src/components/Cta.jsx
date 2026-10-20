import { forwardRef } from 'react'
import { LINKEDIN } from '../lib/content'
import { CtaLinkedinArrow, CtaSignupArrow } from '../lib/icons'

/* CLONE_SPEC 11.1 */
const Cta = forwardRef(function Cta(_, ref) {
  return (
    <section className="ctaSection" ref={ref}>
      <div className="cloud">
        <video src="/cloud_low.mp4" autoPlay muted loop playsInline />
      </div>
      <div className="cloudOverlay" />
      <h2 className="text-headline2Medium">Let’s Build the Infrastructure of Change Together</h2>
      <div className="buttons">
        <a
          className="text-bodyS signup"
          href="https://mailchi.mp/960b9490730a/website-signup"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span>Sign up for updates</span>
          <CtaSignupArrow />
        </a>
        <a className="text-caption linkedin" href={LINKEDIN} target="_blank" rel="noopener noreferrer">
          <span>Follow us on LinkedIn</span>
          <CtaLinkedinArrow />
        </a>
      </div>
    </section>
  )
})

export default Cta
