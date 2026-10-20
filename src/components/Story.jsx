import { forwardRef, useRef, useState } from 'react'
import { STORY } from '../lib/content'
import { useScrollProgress } from '../lib/scroll'

const words = (s) => s.split(' ')

/* CLONE_SPEC 6: word-by-word reveal scrubbed by lettersTriggerProgress */
const Story = forwardRef(function Story(_, ref) {
  const triggerRef = useRef(null)
  const [reveal, setReveal] = useState(0) // progress * total

  useScrollProgress(triggerRef, 'start,end', (p) => setReveal(p * STORY.total))

  let k = 0 // 1-based global index across words and logos
  const word = (w, i, boldFrom) => {
    k += 1
    const cls = ['word', k <= reveal ? 'a' : '', boldFrom !== undefined && i >= boldFrom ? 'b' : '']
      .filter(Boolean)
      .join(' ')
    return (
      <span key={i} className={cls}>
        {w}
        {' '}
      </span>
    )
  }

  return (
    <section className="story" id="our-story" ref={ref}>
      <div className="lettersTrigger" ref={triggerRef} />
      <div className="introCont text-headline2">
        <p>{words(STORY.p1).map((w, i) => word(w, i))}</p>
        <div className="logos">
          {STORY.logos.map((l) => {
            k += 1
            return (
              <div key={l.src} className={`logo${k <= reveal ? ' a' : ''}`}>
                <a href={l.href} target="_blank">
                  <img src={l.src} width={l.w} height={l.h} alt={l.alt} />
                </a>
              </div>
            )
          })}
        </div>
        {STORY.rest.map((b) => (
          <p key={b.text} className={b.indent ? 'indent' : undefined}>
            {words(b.text).map((w, i) => word(w, i, b.boldFrom))}
          </p>
        ))}
      </div>
    </section>
  )
})

export default Story
