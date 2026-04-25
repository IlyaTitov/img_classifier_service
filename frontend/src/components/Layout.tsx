import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Layout.css'

export default function Layout() {
  const { userLogin, signOut } = useAuth()
  const navigate = useNavigate()

  function handleSignOut() {
    signOut()
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <span className="navbar-brand">ImageClassifier</span>
        <div className="navbar-links">
          <NavLink
            to="/upload"
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Загрузить
          </NavLink>
          <NavLink
            to="/archive"
            className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
          >
            Архив
          </NavLink>
        </div>
        <div className="navbar-user">
          <span className="username">{userLogin}</span>
          <button type="button" className="btn-ghost" onClick={handleSignOut}>
            Выйти
          </button>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
