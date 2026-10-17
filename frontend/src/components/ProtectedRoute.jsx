import { useEffect, useState } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import useStore from '../store/useStore'
import { guestLogin } from '../api'

export default function ProtectedRoute() {
  const token = useStore((s) => s.token)
  const onboarded = useStore((s) => s.onboarded)
  const loadBookmarks = useStore((s) => s.loadBookmarks)
  const loadLikes = useStore((s) => s.loadLikes)
  const setAuth = useStore((s) => s.setAuth)
  const [guestError, setGuestError] = useState(false)

  // No login screen: start a private guest session automatically
  useEffect(() => {
    if (token) return
    guestLogin()
      .then((data) => setAuth(data.user, data.token, data.refresh_token))
      .catch(() => setGuestError(true))
  }, [token])

  useEffect(() => {
    if (token) {
      loadBookmarks()
      loadLikes()
    }
  }, [token])

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center text-text-muted">
        {guestError ? 'Could not start a session. Please refresh the page.' : 'Loading...'}
      </div>
    )
  }
  if (!onboarded) return <Navigate to="/onboarding" replace />
  return <Outlet />
}
