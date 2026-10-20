import { useEffect, useState } from 'react'

// Tiny pathname router: "/" and "/privacy-policy" (CLONE_SPEC 0).
const EVT = 'app:navigate'

export function navigate(to) {
  if (to === window.location.pathname + window.location.hash) return
  window.history.pushState(null, '', to)
  window.dispatchEvent(new Event(EVT))
}

export function usePathname() {
  const [path, setPath] = useState(window.location.pathname)
  useEffect(() => {
    const sync = () => setPath(window.location.pathname)
    window.addEventListener('popstate', sync)
    window.addEventListener(EVT, sync)
    return () => {
      window.removeEventListener('popstate', sync)
      window.removeEventListener(EVT, sync)
    }
  }, [])
  return path.replace(/\/+$/, '') || '/'
}
