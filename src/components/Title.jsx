import { forwardRef } from 'react'

/* CLONE_SPEC 5 */
const Title = forwardRef(function Title(_, ref) {
  return (
    <section className="titleSection" ref={ref}>
      <div />
      <div className="title">
        <h1 className="text-headline1">
          Enabling the
          <br />
          Infrastructure
          <br />
          of Change
        </h1>
      </div>
      <div className="subtitle text-bodyL">
        <div className="circle" />
        <span>
          Made to endure, designed to adapt: we help organizations and places deliver sustainable, resilient and
          profitable impact.
        </span>
      </div>
      <div className="videoLayer">
        <video src="/bird_low.mp4" autoPlay muted loop playsInline />
      </div>
    </section>
  )
})

export default Title
