import { useEffect } from 'react'
import Home from './pages/Home'
import PrivacyPolicy from './pages/PrivacyPolicy'
import NotFound from './pages/NotFound'
import { usePathname } from './lib/router'

export default function App() {
  const path = usePathname()

  useEffect(() => {
    // live: home has a title; /privacy-policy title is empty (UNSET) - we keep the brand title.
    document.title = 'The Equator Company'
  }, [path])

  if (path === '/') return <Home key="home" />
  if (path === '/privacy-policy') return <PrivacyPolicy key="privacy" />
  return <NotFound key="404" path={window.location.pathname} />
}
