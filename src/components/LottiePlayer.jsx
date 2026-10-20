import { useEffect, useRef } from 'react'
import { DotLottie } from '@lottiefiles/dotlottie-web'

/**
 * dotLottie canvas player, fit "contain", 100% x 100% (CLONE_SPEC 4.1 / 7.2 / 11.2).
 * `playerRef.current` receives { player, loaded } where `loaded` resolves once the
 * animation is ready, so callers can sequence play()/setSegment().
 * The WASM renderer is fetched from the package's default CDN, like the original.
 */
export default function LottiePlayer({ src, autoplay = false, loop = false, playerRef }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const player = new DotLottie({
      canvas: canvasRef.current,
      src,
      autoplay,
      loop,
      layout: { fit: 'contain', align: [0.5, 0.5] },
      // The original (dotlottie-web 0.54.1) measurably renders whole frames only: max 30
      // distinct canvas frames/s for these 30fps files. 0.81 interpolates to the rAF rate.
      useFrameInterpolation: false,
      renderConfig: { autoResize: true },
    })
    const loaded = new Promise((resolve) => {
      if (player.isLoaded) resolve()
      else player.addEventListener('load', () => resolve())
    })
    if (playerRef) playerRef.current = { player, loaded }
    return () => {
      if (playerRef) playerRef.current = null
      player.destroy()
    }
  }, [src, autoplay, loop, playerRef])

  return (
    <div className="lottieBox">
      <canvas ref={canvasRef} />
    </div>
  )
}

/**
 * Plays once from frame 0, then on the first `complete` loops segment
 * [loopFrom, totalFrames-1]. Used by the splash (270) and value lotties (60).
 */
export async function playThenLoop(handle, loopFrom) {
  if (!handle) return
  const { player, loaded } = handle
  await loaded
  let done = false
  const onComplete = () => {
    if (done) return
    done = true
    player.removeEventListener('complete', onComplete)
    player.setSegment(loopFrom, player.totalFrames - 1)
    player.setLoop(true)
    player.play()
  }
  player.addEventListener('complete', onComplete)
  player.play()
}
