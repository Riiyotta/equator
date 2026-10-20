import { forwardRef, useEffect, useRef, useState } from 'react'
import { VALUES } from '../lib/content'
import { computeProgress, useElementVisibility } from '../lib/scroll'
import LottiePlayer, { playThenLoop } from './LottiePlayer'

/* One stacked value panel (ObjectValue) - CLONE_SPEC 7.1 / 7.2 */
const Value = forwardRef(function Value({ value }, ref) {
  const triggerRef = useRef(null)
  const playerRef = useRef(null)
  const visible = useElementVisibility(triggerRef)
  const [mounted, setMounted] = useState(false)
  const played = useRef(false)

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 1000)
    return () => clearTimeout(t)
  }, [])

  useEffect(() => {
    if (!mounted || !visible || played.current) return
    played.current = true
    playThenLoop(playerRef.current, 60)
  }, [mounted, visible])

  return (
    <div className="scrollZone">
      <div className="value" ref={ref}>
        <div className="lottieTrigger" ref={triggerRef} />
        <div className="lottieCont">
          <LottiePlayer src={`/lottie/${value.lottie}.lottie`} playerRef={playerRef} />
        </div>
        <h2 className="text-headline1">
          {value.title[0]}
          <br />
          {value.title[1]}
        </h2>
        <div className="text text-bodyM">
          <p>{value.cols[0]}</p>
          <p>{value.cols[1]}</p>
        </div>
      </div>
    </div>
  )
})

const Values = forwardRef(function Values(_, ref) {
  const contRef = useRef(null)
  const hideRefs = useRef([])
  const stepRefs = useRef([])
  const [step, setStep] = useState(1)

  // hide{n}Progress ("end,start") -> value n opacity = 1 - progress, scrubbed, no transition.
  // Mirrors the original: the opacity CSS vars start at 0 (ref(0)) and Locomotive only emits
  // progress while the trigger intersects its RAF IntersectionObserver (rootMargin 100% on all
  // sides); on leaving that zone it emits a final progress snapped to the nearest of 0/1.
  useEffect(() => {
    const cont = contRef.current
    const state = hideRefs.current.map(() => ({ interactive: false, seen: false, last: null }))
    const emit = (i, p) => {
      if (p === state[i].last) return
      state[i].last = p
      cont.style.setProperty(`--hide${i + 1}-opacity`, String(1 - p))
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          const i = hideRefs.current.indexOf(e.target)
          if (i < 0) return
          const s = state[i]
          if (e.isIntersecting) {
            s.seen = true
            if (!s.interactive) {
              s.interactive = true
              emit(i, computeProgress(e.target, 'end,start'))
            }
          } else if (s.seen && s.interactive) {
            s.interactive = false
            if (s.last != null) emit(i, s.last <= 0.5 ? 0 : 1)
          }
        })
      },
      { rootMargin: '100% 100% 100% 100%' },
    )
    hideRefs.current.forEach((el) => el && io.observe(el))
    const update = () => {
      state.forEach((s, i) => {
        if (s.interactive) emit(i, computeProgress(hideRefs.current[i], 'end,start'))
      })
    }
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      io.disconnect()
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [])

  // N/5 counter: step triggers observed with rootMargin "50% 0% -100% 0%", never reset on exit.
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setStep(Number(e.target.dataset.step))
        })
      },
      { rootMargin: '50% 0% -100% 0%' },
    )
    stepRefs.current.forEach((el) => el && io.observe(el))
    return () => io.disconnect()
  }, [])

  return (
    <section className="values" id="what-we-stand-for" ref={ref}>
      <div className="numbersCont">
        <div className="number text-bodyL">{step}/5</div>
      </div>
      <div className="valuesCont" ref={contRef}>
        {VALUES.map((v) => (
          <Value key={v.lottie} value={v} />
        ))}
        {[1, 2, 3, 4].map((n) => (
          <div key={`h${n}`} className={`hideTrigger hide${n}Trigger`} ref={(el) => (hideRefs.current[n - 1] = el)} />
        ))}
        {[1, 2, 3, 4, 5].map((n) => (
          <div
            key={`s${n}`}
            id={`step${n}`}
            data-step={n}
            className={`stepTrigger step${n}Trigger`}
            ref={(el) => (stepRefs.current[n - 1] = el)}
          />
        ))}
      </div>
    </section>
  )
})

export default Values
