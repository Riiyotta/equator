import { useEffect, useRef, useState } from 'react'
import Lenis from 'lenis'

/* ---------------------------------------------------------------------------
   Smooth scroll: Locomotive Scroll v5 defaults -> Lenis (CLONE_SPEC 3)
   --------------------------------------------------------------------------- */
export function useLenis() {
  useEffect(() => {
    const lenis = new Lenis({
      lerp: 0.1,
      smoothWheel: true,
      syncTouch: false,
      wheelMultiplier: 1,
      touchMultiplier: 1,
      orientation: 'vertical',
      gestureOrientation: 'vertical',
    })
    document.documentElement.setAttribute('data-scroll-orientation', 'vertical')
    let raf = 0
    const loop = (time) => {
      lenis.raf(time)
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)
    return () => {
      cancelAnimationFrame(raf)
      lenis.destroy()
      document.documentElement.removeAttribute('data-scroll-orientation')
    }
  }, [])
}

/* ---------------------------------------------------------------------------
   Locomotive `data-scroll-event-progress` formula (CLONE_SPEC 3)
   --------------------------------------------------------------------------- */
export function computeProgress(el, position = 'start,end') {
  const [A, B] = position.split(',')
  const vh = window.innerHeight
  const scrollY = window.scrollY
  const rect = el.getBoundingClientRect()
  const top = rect.top + scrollY
  const h = rect.height
  let start = A === 'end' ? top - vh + h : top - vh
  if (top < vh) start = 0 // "fold"
  let end = B === 'start' ? top : top + h
  if (end <= start) end = B === 'start' ? start + 1 : start + h
  const p = (scrollY - start) / (end - start)
  return Math.min(1, Math.max(0, p))
}

/**
 * Calls onProgress(progress) whenever the computed progress changes
 * (on scroll and resize). The callback is read from a ref so it can be inline.
 */
export function useScrollProgress(ref, position, onProgress) {
  const cb = useRef(onProgress)
  cb.current = onProgress
  useEffect(() => {
    let last = -1
    const update = () => {
      if (!ref.current) return
      const p = computeProgress(ref.current, position)
      if (p !== last) {
        last = p
        cb.current(p)
      }
    }
    update()
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [ref, position])
}

/* ---------------------------------------------------------------------------
   VueUse useElementVisibility equivalent (IO, threshold 0)
   --------------------------------------------------------------------------- */
export function useElementVisibility(ref, options) {
  const [visible, setVisible] = useState(false)
  const rootMargin = options?.rootMargin
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      (entries) => {
        const e = entries[entries.length - 1]
        setVisible(e.isIntersecting)
      },
      { threshold: 0, rootMargin },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [ref, rootMargin])
  return visible
}

/* ---------------------------------------------------------------------------
   scrollToY from the index chunk (CLONE_SPEC 3, "Nav / anchor scrolling")
   --------------------------------------------------------------------------- */
export function scrollToY(target) {
  const cur = window.scrollY
  let t = 0
  const dur = Math.max(0.1, Math.min(Math.abs(cur - target) / 2000, 0.8))
  function step() {
    t += 1 / 60
    const p = t / dur
    if (p < 1) {
      requestAnimationFrame(step)
      window.scrollTo(0, cur + (target - cur) * Math.sin((p * Math.PI) / 2))
    } else {
      window.scrollTo(0, target)
    }
  }
  step()
}

export function getYPosition(el) {
  return el.getBoundingClientRect().top + window.scrollY
}

export const isMobile = () => window.innerWidth <= 768
