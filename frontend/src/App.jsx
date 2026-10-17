import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import ProtectedRoute from './components/ProtectedRoute'
import FeedPage from './pages/FeedPage'
import BookmarksPage from './pages/BookmarksPage'
import UploadPage from './pages/UploadPage'

import FlashcardsPage from './pages/FlashcardsPage'
import ChatPage from './pages/ChatPage'
import MyBooksPage from './pages/MyBooksPage'
import ProfilePage from './pages/ProfilePage'
import LandingPage from './pages/LandingPage'
import OnboardingPage from './pages/OnboardingPage'
import HelpPage from './pages/HelpPage'

function App() {
  return (
    <Routes>
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<FeedPage />} />
          <Route path="/bookmarks" element={<BookmarksPage />} />
          <Route path="/upload" element={<UploadPage />} />

          <Route path="/flashcards" element={<FlashcardsPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/books" element={<MyBooksPage />} />
          <Route path="/help" element={<HelpPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>
      <Route path="/welcome" element={<LandingPage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />
      {/* Login is disabled — guests get a session automatically */}
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="/signup" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
