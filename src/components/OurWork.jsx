import { forwardRef, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { SLIDES, MEMBER_LOGOS } from '../lib/content'
import { CarouselNext, CarouselPrev, PlusIcon } from '../lib/icons'
import LazyPicture from './LazyPicture'

const GAP = 20
const TRANSITION = 300
const DRAG_THRESHOLD = 0.08 // vue3-carousel default

const clamp = (val, min, max) => (max < min ? val : Math.min(Math.max(val, min), max))

function Slide({ slide, active, onClick }) {
  return (
    <div className={`slide${active ? ' active' : ''}`} onClick={onClick}>
      <h3 className="slideTitle text-headline4">{slide.title}</h3>
      <div className="photoLayer" />
      <LazyPicture base={slide.image} alt={slide.title} placeholder={slide.placeholder} draggable={false} />
      <div className="plusPill">
        <PlusIcon />
      </div>
      <div className="otherPill" />
      <div className="descriptionLayer" />
      <p className="description text-bodyM">{slide.text}</p>
    </div>
  )
}

/*
 * Carousel: vue3-carousel semantics ported from the shipped bundle.
 * itemsToShow:"auto", gap 20, snapAlign start, wrapAround false, mouse + touch drag.
 * Index range is 0..n-1; translate is clamped to (trackWidth - viewportWidth).
 * The 300ms ease-out transition is only applied while sliding (not while dragging).
 */
function Carousel() {
  const n = SLIDES.length
  const viewportRef = useRef(null)
  const slideRefs = useRef([])
  const [sizes, setSizes] = useState([])
  const [viewportW, setViewportW] = useState(0)
  const [current, setCurrent] = useState(0)
  const [sliding, setSliding] = useState(false)
  const [dragX, setDragX] = useState(0)
  const [dragging, setDragging] = useState(false)
  const [activeSlide, setActiveSlide] = useState(-1)
  const state = useRef({ current: 0, sliding: false, target: 0, timer: 0 })
  state.current.current = current
  state.current.sliding = sliding

  const measure = useCallback(() => {
    setSizes(slideRefs.current.map((el) => (el ? el.getBoundingClientRect().width : 0)))
    setViewportW(viewportRef.current ? viewportRef.current.getBoundingClientRect().width : 0)
  }, [])

  useLayoutEffect(() => {
    measure()
    const ro = new ResizeObserver(measure)
    if (viewportRef.current) ro.observe(viewportRef.current)
    return () => ro.disconnect()
  }, [measure])

  const slideTo = useCallback(
    (index, force = false) => {
      const s = state.current
      if (!force && s.sliding) return
      const target = clamp(index, 0, n - 1)
      if (s.current === target) return
      setSliding(true)
      setCurrent(target)
      clearTimeout(s.timer)
      s.timer = setTimeout(() => setSliding(false), TRANSITION)
    },
    [n],
  )

  useEffect(() => () => clearTimeout(state.current.timer), [])

  // translate for current index
  let translate = sizes.slice(0, current).reduce((a, w) => a + w + GAP, 0)
  const maxTranslate = sizes.reduce((a, w) => a + w + GAP, 0) - viewportW - GAP
  translate = clamp(translate, 0, maxTranslate)
  const avgSize = sizes.length ? sizes.reduce((a, w) => a + w, 0) / sizes.length : 0
  const effectiveSlideSize = avgSize + GAP

  // Drag handling (O8 / E8 in the original bundle)
  const onDragStart = (e) => {
    const isTouch = e.type === 'touchstart'
    if (state.current.sliding) return
    if (isTouch && e.touches.length > 1) return
    if (!isTouch) {
      e.preventDefault()
      if (e.button !== 0) return
    }
    const startX = isTouch ? e.touches[0].clientX : e.clientX
    const startY = isTouch ? e.touches[0].clientY : e.clientY
    let dx = 0
    let dy = 0
    let raf = 0
    let lastX = startX
    let lastY = startY
    state.current.target = state.current.current

    const move = (ev) => {
      if (isTouch && ev.touches.length > 1) return
      lastX = isTouch ? ev.touches[0].clientX : ev.clientX
      lastY = isTouch ? ev.touches[0].clientY : ev.clientY
      if (raf) return
      raf = requestAnimationFrame(() => {
        raf = 0
        dx = lastX - startX
        dy = lastY - startY
        setDragging(true)
        setDragX(dx)
        let delta = 0
        if (dx !== 0 && effectiveSlideSize > 0) {
          const a = dx / effectiveSlideSize
          const abs = Math.abs(a)
          if (abs >= DRAG_THRESHOLD) delta = -(abs < 1 ? Math.sign(a) : Math.round(a))
        }
        if (delta !== 0) state.current.target = clamp(state.current.current + delta, 0, n - 1)
      })
    }
    const end = () => {
      if (raf) cancelAnimationFrame(raf)
      if (!isTouch && Math.abs(dx) + Math.abs(dy) > 10) {
        window.addEventListener(
          'click',
          (ev) => {
            ev.preventDefault()
            ev.stopPropagation()
          },
          { once: true, capture: true },
        )
      }
      setDragX(0)
      setDragging(false)
      slideTo(state.current.target)
      document.removeEventListener(isTouch ? 'touchmove' : 'mousemove', move)
      document.removeEventListener(isTouch ? 'touchend' : 'mouseup', end)
    }
    document.addEventListener(isTouch ? 'touchmove' : 'mousemove', move, { passive: false })
    document.addEventListener(isTouch ? 'touchend' : 'mouseup', end, { passive: true })
  }

  const trackRef = useRef(null)
  useEffect(() => {
    // passive touchstart capture listener, like the original
    const el = trackRef.current
    const handler = (e) => onDragStart(e)
    el.addEventListener('touchstart', handler, { passive: true, capture: true })
    return () => el.removeEventListener('touchstart', handler, { capture: true })
  })

  const onSlideClick = (i) => {
    setActiveSlide((cur) => (cur === i ? -1 : i))
    if (window.innerWidth < 768) slideTo(i)
  }

  const prevDisabled = current <= 0
  const nextDisabled = current >= n - 1

  return (
    <section
      className={`carousel is-ltr is-effect-slide${dragging ? ' is-dragging' : ''}${sliding ? ' is-sliding' : ''}`}
      dir="ltr"
      aria-label="Gallery"
      tabIndex={0}
      style={sliding ? { '--vc-transition-duration': `${TRANSITION}ms` } : undefined}
    >
      <div className="carousel__viewport" ref={viewportRef}>
        <ol
          className="carousel__track"
          ref={trackRef}
          onMouseDownCapture={onDragStart}
          style={{ transform: `translateX(${-translate + dragX}px)` }}
        >
          {SLIDES.map((s, i) => (
            <li key={s.title} className="carousel__slide" ref={(el) => (slideRefs.current[i] = el)}>
              <Slide slide={s} active={activeSlide === i} onClick={() => onSlideClick(i)} />
            </li>
          ))}
        </ol>
      </div>
      <button
        type="button"
        className={`carousel__prev${prevDisabled ? ' carousel__prev--disabled' : ''}`}
        aria-label="Navigate to previous slide"
        disabled={prevDisabled}
        onClick={() => slideTo(current - 1)}
      >
        <CarouselPrev />
      </button>
      <button
        type="button"
        className={`carousel__next${nextDisabled ? ' carousel__next--disabled' : ''}`}
        aria-label="Navigate to next slide"
        disabled={nextDisabled}
        onClick={() => slideTo(current + 1)}
      >
        <CarouselNext />
      </button>
    </section>
  )
}

/* marquee3k port: 0.5px per animation frame, leftward, never pauses (CLONE_SPEC 9) */
function Marquee() {
  const rootRef = useRef(null)
  const wrapperRef = useRef(null)
  const copyRef = useRef(null)
  const [copies, setCopies] = useState(3)
  const offset = useRef(0)
  const contentW = useRef(0)

  useLayoutEffect(() => {
    const populate = () => {
      const cw = copyRef.current.offsetWidth
      const pw = rootRef.current.offsetWidth
      contentW.current = cw
      const clones = cw > pw ? 2 : Math.ceil((pw - cw) / cw) + 1
      setCopies(1 + clones)
    }
    populate()
    let t = 0
    const onResize = () => {
      clearTimeout(t)
      t = setTimeout(populate, 250)
    }
    window.addEventListener('resize', onResize)
    return () => {
      clearTimeout(t)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  useEffect(() => {
    let raf = 0
    const tick = () => {
      offset.current -= 0.5
      if (offset.current <= -contentW.current) offset.current = 0
      wrapperRef.current.style.transform = `translate(${offset.current}px, 0) translateZ(0)`
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  const logos = (
    <div className="logos">
      {MEMBER_LOGOS.map((src) => (
        <div className="logo" key={src}>
          <div className="logoCont">
            <img src={src} width="200" height="120" alt="" draggable={false} />
          </div>
        </div>
      ))}
    </div>
  )

  return (
    <div className="marquee3k" data-speed="0.5" ref={rootRef}>
      <div className="marquee3k__wrapper" ref={wrapperRef}>
        {Array.from({ length: copies }, (_, i) => (
          <div className="marquee3k__copy" key={i} ref={i === 0 ? copyRef : undefined} aria-hidden={i > 0 || undefined}>
            {logos}
          </div>
        ))}
      </div>
    </div>
  )
}

const OurWork = forwardRef(function OurWork(_, ref) {
  return (
    <section className="partners noselect" id="our-work" ref={ref}>
      <h2 className="text-headline2Medium">Trusted by those driving change</h2>
      <div className="navigationSpace" />
      <Carousel />
      <div className="logosCont">
        <div className="caption text-bodyL">Proud member of</div>
        <Marquee />
      </div>
    </section>
  )
})

export default OurWork
