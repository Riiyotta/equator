import { forwardRef } from 'react'
import { LINKEDIN, MAIL } from '../lib/content'
import { FooterLinkedIn, FooterMail, FooterPin, FooterWordmark } from '../lib/icons'
import LottiePlayer from './LottiePlayer'
import { navigate } from '../lib/router'

/* CLONE_SPEC 11.2 */
export const Footer = forwardRef(function Footer(_, ref) {
  return (
    <footer ref={ref}>
      <div className="logoCont">
        <div className="lottieCont">
          <LottiePlayer src="/lottie/footer.lottie" autoplay loop />
        </div>
        <FooterWordmark />
      </div>
      <div className="infoCont">
        <p className="text-bodyM">
          Interdisciplinary sustainability consultancy with 45 years of experience. Designed to provide a structured
          full-service ESG offer for your organisation and community.
        </p>
        <ul className="text-bodyS">
          <li>
            <a href="https://maps.app.goo.gl/DhKJrr1GrcZ6ptwT7" target="_blank" rel="noopener noreferrer">
              <FooterPin />
              <span>Rua Laura Alves 12, 1050-138 Lisboa, Portugal</span>
            </a>
          </li>
          <li>
            <a href={MAIL}>
              <FooterMail />
              <span>info@equatorcompany.com</span>
            </a>
          </li>
        </ul>
        <ul className="text-bodyS">
          <li>
            <a href={LINKEDIN} target="_blank" rel="noopener noreferrer">
              <FooterLinkedIn />
              <span>Follow us on LinkedIn</span>
            </a>
          </li>
        </ul>
        <p className="text-bodyS">
          © {new Date().getFullYear()} The Equator Company.
          <br />
          All rights reserved.
        </p>
      </div>
      <div className="bottom">
        <div className="logoSpace" />
        <div className="credits text-credits">
          <a
            href="/privacy-policy"
            onClick={(e) => {
              e.preventDefault()
              navigate('/privacy-policy')
            }}
          >
            Privacy Policy
          </a>
          <span>
            Design by{' '}
            <a href="https://studio-cronica.com" target="_blank">
              Studio Cronica
            </a>
          </span>
        </div>
      </div>
    </footer>
  )
})

/* CLONE_SPEC 11.3 */
export function Subfooter() {
  return (
    <div className="subfooter">
      <a href="https://recuperarportugal.gov.pt/" target="_blank" rel="noopener noreferrer">
        <img src="/mono.svg" alt="" />
      </a>
      <a className="sheet text-caption" href="/Equator-PRR-Investimentos.pdf" target="_blank" download>
        Project sheet
      </a>
    </div>
  )
}
