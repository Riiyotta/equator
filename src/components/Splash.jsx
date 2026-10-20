import { useEffect, useRef, useState } from 'react'
import LottiePlayer, { playThenLoop } from './LottiePlayer'

/* CLONE_SPEC 4.1 */
export default function Splash({ logoSmall }) {
  const playerRef = useRef(null)
  const [introDone, setIntroDone] = useState(false)

  useEffect(() => {
    // not autoplay: play at +1000ms, then loop 270 -> end after the first complete
    const t = setTimeout(() => playThenLoop(playerRef.current, 270), 1000)
    // caption hidden for the first 2500ms
    const t2 = setTimeout(() => setIntroDone(true), 2500)
    return () => {
      clearTimeout(t)
      clearTimeout(t2)
    }
  }, [])

  const hide = !introDone || logoSmall

  return (
    <section className={`splash${hide ? ' hide' : ''}`}>
      <div className="lottieCont">
        <LottiePlayer src="/lottie/navbar.lottie" playerRef={playerRef} />
      </div>
      <div className="caption text-bodyS">Scroll to explore</div>
    </section>
  )
}
