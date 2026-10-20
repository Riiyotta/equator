import { useEffect, useState } from 'react'
import { Hamburger, Header, useScrollLock } from '../components/Header'
import { Footer, Subfooter } from '../components/Footer'
import { LogoWordmark } from '../lib/icons'
import { useLenis } from '../lib/scroll'
import { navigate } from '../lib/router'
import privacyBody from '../lib/privacyBody'

/* CLONE_SPEC 12: no splash, no logo animation, no section watcher. */
function HomeLink() {
  return (
    <a
      href="/"
      className="text-headline4"
      aria-label="The Equator Company"
      onClick={(e) => {
        e.preventDefault()
        navigate('/')
      }}
    >
      <LogoWordmark />
    </a>
  )
}

export default function PrivacyPolicy() {
  useLenis()
  const [open, setOpen] = useState(false)
  useScrollLock(open)

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <main className="privacy">
      <div className="mobileHeader">
        <div className="logoSpace">
          <HomeLink />
        </div>
        <Hamburger open={open} onToggle={() => setOpen((o) => !o)} />
      </div>
      {/* nav links are plain "/#id" hrefs: full navigation back to the home page */}
      <Header open={open} logoSpace={<HomeLink />} />
      <article>
        <h1 className="text-headline1">Privacy Policy</h1>
        <div className="body text-bodyM" dangerouslySetInnerHTML={{ __html: privacyBody }} />
      </article>
      <Footer />
      <Subfooter />
    </main>
  )
}
