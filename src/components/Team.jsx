import { forwardRef, useEffect, useRef, useState } from 'react'
import { TEAM } from '../lib/content'
import { MemberArrow, MemberLinkedInLogo } from '../lib/icons'
import { getYPosition, scrollToY } from '../lib/scroll'
import LazyPicture from './LazyPicture'

/* ObjectMember - CLONE_SPEC 10 */
function Member({ member }) {
  const rowRef = useRef(null)
  const nameRef = useRef(null)
  const [active, setActive] = useState(false)
  const [activeMobile, setActiveMobile] = useState(false)

  useEffect(() => {
    const el = rowRef.current
    // desktop: 1%-tall band at viewport centre
    const io = new IntersectionObserver((es) => setActive(es[es.length - 1].isIntersecting), {
      rootMargin: '-49.5% 0% -49.5% 0%',
    })
    // <=520: band at 25% from the top
    const ioMobile = new IntersectionObserver((es) => setActiveMobile(es[es.length - 1].isIntersecting), {
      rootMargin: '-24.5% 0% -74.5% 0%',
    })
    io.observe(el)
    ioMobile.observe(el)
    return () => {
      io.disconnect()
      ioMobile.disconnect()
    }
  }, [])

  const onNameClick = () => {
    const el = nameRef.current
    const top = getYPosition(el)
    const h = el.getBoundingClientRect().height
    const vh = window.innerHeight
    scrollToY(window.innerWidth < 520 ? top - vh / 4 + h / 2 : top - vh / 2 + h / 2)
  }

  const { name, slug, role, linkedin } = member
  return (
    <div ref={rowRef}>
      <div className={`teamMember${active ? ' isActive' : ''}${activeMobile ? ' isActiveMobile' : ''}`}>
        <div className="name text-headline3" ref={nameRef} onClick={onNameClick}>
          {name}
        </div>
        <div className="overlayCont">
          <div className="backgroundCont">
            <img src={`/team/${slug}-back.png`} width="1700" height="2000" alt="" />
          </div>
          <div className="portraitCont">
            <LazyPicture base={`/team/${slug}`} alt={name} width="900" height="1120" />
            <div className="role text-caption" dangerouslySetInnerHTML={{ __html: role }} />
            <a href={linkedin} className="linkedin text-caption" target="_blank">
              <span>Linkedin</span>
              <MemberLinkedInLogo />
              <MemberArrow />
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

const Team = forwardRef(function Team(_, ref) {
  return (
    <section className="team" id="team" ref={ref}>
      <div className="intro">
        <h2 className="text-headline2Medium">Over 45 years experience delivering impact</h2>
        <p className="subtitle text-bodyL">
          Our executive team brings decades of experience in diverse areas such as infrastructure, strategy, social
          innovation, and policy - ensuring sustainable transitions are not only possible, but practical.
        </p>
      </div>
      <div className="list">
        {TEAM.map((m) => (
          <Member key={m.slug} member={m} />
        ))}
      </div>
    </section>
  )
})

export default Team
