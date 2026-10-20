import { forwardRef, useEffect, useRef, useState } from 'react'
import { CAPABILITIES } from '../lib/content'
import { PlusIcon } from '../lib/icons'

/* ObjectDropdown - CLONE_SPEC 8 */
function Dropdown({ title, text, open, onToggle }) {
  const contentRef = useRef(null)
  const [contentH, setContentH] = useState(0)

  useEffect(() => {
    if (!open) return
    const measure = () => setContentH(contentRef.current.getBoundingClientRect().height)
    measure()
    window.addEventListener('resize', measure)
    return () => window.removeEventListener('resize', measure)
  }, [open])

  return (
    <div
      className={`dropdown noselect${open ? ' open' : ''}`}
      style={{ '--h': open ? `calc(${contentH}px + var(--min-height))` : 'var(--min-height)' }}
      onClick={onToggle}
    >
      <div className="dropdownHeader">
        <h3 className="text-headline4">{title}</h3>
      </div>
      <div className="dropdownContent" ref={contentRef}>
        <p className="text-bodyM">{text}</p>
      </div>
      <div className="plusPill">
        <PlusIcon />
      </div>
      <div className="otherPill" />
    </div>
  )
}

const Capabilities = forwardRef(function Capabilities(_, ref) {
  const [openIndex, setOpenIndex] = useState(-1)
  return (
    <section className="capabilities" id="capabilities" ref={ref}>
      <h2 className="text-headline2Medium">Your partner for a sustainable transition</h2>
      <p className="subtitle text-bodyL">
        With experience and expertise in a wide range of areas, we’re here to design and implement high-impact,
        long-lasting change with your organization. Whatever the scale, scope, service or challenge.
      </p>
      <div className="grid">
        {CAPABILITIES.map(([title, text], i) => (
          <Dropdown
            key={title}
            title={title}
            text={text}
            open={openIndex === i}
            onToggle={() => setOpenIndex((cur) => (cur === i ? -1 : i))}
          />
        ))}
      </div>
    </section>
  )
})

export default Capabilities
