import { useEffect, useRef, useState } from 'react'
import { Header, LogoZone, MobileHeader, useScrollLock } from '../components/Header'
import Splash from '../components/Splash'
import Title from '../components/Title'
import Story from '../components/Story'
import Values from '../components/Values'
import Capabilities from '../components/Capabilities'
import OurWork from '../components/OurWork'
import Team from '../components/Team'
import Cta from '../components/Cta'
import { Footer, Subfooter } from '../components/Footer'
import { getYPosition, isMobile, scrollToY, useElementVisibility, useLenis, useScrollProgress } from '../lib/scroll'

/* Section watcher (CLONE_SPEC 3): URL hash + active nav, debounced 500ms */
function useSectionWatcher(sectionRefs) {
  const [hash, setHash] = useState(() => window.location.hash)
  useEffect(() => {
    let raf = 0
    let timer = 0
    let pending = null
    const pick = () => {
      const mid = window.innerHeight / 2
      const els = sectionRefs.current.filter(Boolean)
      let found = els.find((el) => {
        const r = el.getBoundingClientRect()
        return r.top <= mid && r.bottom >= mid
      })
      if (!found) {
        const above = els.filter((el) => el.getBoundingClientRect().bottom < mid)
        found = above[above.length - 1]
      }
      if (!found) return
      const next = found.id ? `#${found.id}` : ''
      if (next === pending) return
      pending = next
      clearTimeout(timer)
      timer = setTimeout(() => {
        if (window.location.hash !== next) {
          window.history.replaceState(window.history.state, '', next || window.location.pathname)
        }
        setHash(next)
      }, 500)
    }
    const io = new IntersectionObserver(
      () => {
        cancelAnimationFrame(raf)
        raf = requestAnimationFrame(pick)
      },
      { rootMargin: '-49% 0px -49% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] },
    )
    sectionRefs.current.forEach((el) => el && io.observe(el))
    return () => {
      io.disconnect()
      cancelAnimationFrame(raf)
      clearTimeout(timer)
    }
  }, [sectionRefs])
  return hash
}

export default function Home() {
  useLenis()

  const logoTriggerRef = useRef(null)
  const logoZoneRef = useRef(null)
  const smallZoneRef = useRef(null)
  const titleRef = useRef(null)
  const sectionRefs = useRef([])
  const [open, setOpen] = useState(false)

  // logo scale: s = 1 - logoTriggerProgress * 0.3333 (scroll-scrubbed, no transition)
  useScrollProgress(logoTriggerRef, 'start,end', (p) => {
    const s = 1 - p * 0.3333
    logoZoneRef.current?.style.setProperty('--logo-transform', `scale3d(${s}, ${s}, 1)`)
  })

  // logo .small / mobileHeader .visible / splash caption hide
  const small = useElementVisibility(smallZoneRef)

  useScrollLock(open)

  const activeHash = useSectionWatcher(sectionRefs)

  // Arriving with a hash (e.g. from /privacy-policy "/#team"): jump to that section.
  useEffect(() => {
    const id = window.location.hash.slice(1)
    if (!id) return
    const el = document.getElementById(id)
    if (!el) return
    requestAnimationFrame(() => window.scrollTo(0, getYPosition(el)))
  }, [])

  const onNavigate = (id) => {
    const el = document.getElementById(id)
    if (!el) return
    if (isMobile()) {
      setOpen(false)
      setTimeout(() => scrollToY(getYPosition(el) - 40), 50)
    } else {
      scrollToY(getYPosition(el))
    }
  }

  const reg = (i) => (el) => (sectionRefs.current[i] = el)

  return (
    <main id="mainContent">
      <div className="logoSmallZone" ref={smallZoneRef} />
      <div className="logoTrigger" ref={logoTriggerRef} />
      <LogoZone ref={logoZoneRef} small={small} onClick={() => scrollToY(getYPosition(titleRef.current))} />
      <MobileHeader visible={small} open={open} onToggle={() => setOpen((o) => !o)} />
      <Splash logoSmall={small} />
      <Header open={open} activeHash={activeHash} onNavigate={onNavigate} />
      <Title
        ref={(el) => {
          titleRef.current = el
          sectionRefs.current[0] = el
        }}
      />
      <Story ref={reg(1)} />
      <Values ref={reg(2)} />
      <Capabilities ref={reg(3)} />
      <OurWork ref={reg(4)} />
      <Team ref={reg(5)} />
      <Cta ref={reg(6)} />
      <Footer ref={reg(7)} />
      <Subfooter />
    </main>
  )
}
