import { navigate } from '../lib/router'

// live: unknown routes render Nuxt's default 404 ("404", "Page not found: <path>", "Go back home").
export default function NotFound({ path }) {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-4 text-center px-4">
      <h1 className="text-[96px] leading-none font-medium">404</h1>
      <p className="text-[18px]">Page not found: {path}</p>
      <a
        href="/"
        className="underline"
        onClick={(e) => {
          e.preventDefault()
          navigate('/')
        }}
      >
        Go back home
      </a>
    </main>
  )
}
