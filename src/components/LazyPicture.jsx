import { useEffect, useRef, useState } from 'react'

/*
 * Original `Image` component (data-v-c9f645bb): <source>/<img> URLs are only assigned on the
 * first intersection (VueUse useIntersectionObserver, default options) and the <img> carries
 * `.lazy` (opacity 0) until its load event, then fades in via `transition: opacity .16s`.
 * Used for the Our Work slides and the team portraits.
 */
export default function LazyPicture({ base, alt, placeholder, imgClass = 'cover', draggable, ...rest }) {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        setInView(true)
        io.disconnect()
      }
    })
    io.observe(ref.current)
    return () => io.disconnect()
  }, [])

  return (
    <picture className="responsivePicture" ref={ref} style={placeholder ? { backgroundImage: placeholder } : undefined} {...rest}>
      {inView && <source srcSet={`${base}_mobile.jpg`} media="(max-width: 768px)" />}
      {inView && <source srcSet={`${base}_mobile.webp`} type="image/webp" media="(max-width: 768px)" />}
      {inView && <source srcSet={`${base}.webp`} type="image/webp" />}
      <img
        className={`${loaded ? '' : 'lazy '}${imgClass}`}
        src={inView ? `${base}.jpg` : undefined}
        alt={alt}
        onLoad={() => setLoaded(true)}
        draggable={draggable}
      />
    </picture>
  )
}
