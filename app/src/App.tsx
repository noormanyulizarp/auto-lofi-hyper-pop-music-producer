import { Routes, Route } from 'react-router-dom'
import { Header } from './components/Layout/Header'
import { Sidebar } from './components/Layout/Sidebar'
import { HomePage } from './pages/HomePage'
import { GeneratePage } from './pages/GeneratePage'
import { LearnPage } from './pages/LearnPage'
import { DashboardPage } from './pages/DashboardPage'
import { ProviderDashboard } from './pages/ProviderDashboard'

export default function App() {
  return (
    <div className="h-screen flex flex-col bg-secondary-50">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/learn" element={<LearnPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/providers" element={<ProviderDashboard />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
