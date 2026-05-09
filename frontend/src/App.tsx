import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/context/AuthContext'
import { Layout } from '@/components/Layout'
import ProtectedRoute from '@/components/ProtectedRoute'
import Dashboard from '@/pages/Dashboard'
import CreateTicket from '@/pages/CreateTicket'
import TicketDetail from '@/pages/TicketDetail'
import Login from '@/pages/Login'
import Register from '@/pages/Register'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/tickets/new" element={<CreateTicket />} />
                      <Route path="/tickets/:id" element={<TicketDetail />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
