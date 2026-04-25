import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

const TOKEN_KEY = 'ic_token'
const LOGIN_KEY = 'ic_login'

type AuthContextValue = {
  token: string | null
  userLogin: string | null
  isAuthenticated: boolean
  signIn: (token: string, login: string) => void
  signOut: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_KEY),
  )
  const [userLogin, setUserLogin] = useState<string | null>(() =>
    localStorage.getItem(LOGIN_KEY),
  )

  const signIn = useCallback((t: string, login: string) => {
    localStorage.setItem(TOKEN_KEY, t)
    localStorage.setItem(LOGIN_KEY, login)
    setToken(t)
    setUserLogin(login)
  }, [])

  const signOut = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(LOGIN_KEY)
    setToken(null)
    setUserLogin(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ token, userLogin, isAuthenticated: token !== null, signIn, signOut }),
    [token, userLogin, signIn, signOut],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
