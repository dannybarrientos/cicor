import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar      from './components/Navbar.jsx'
import Dashboard   from './components/Dashboard.jsx'
import Commercial  from './components/modules/Commercial.jsx'
import Inventory   from './components/modules/Inventory.jsx'
import Accounting  from './components/modules/Accounting.jsx'
import Operations  from './components/modules/Operations.jsx'
import RRHH        from './components/modules/RRHH.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#F0F4FC] flex flex-col">
        <Navbar />

        <main className="flex-1 pt-16">
          <Routes>
            <Route path="/"            element={<Dashboard />}  />
            <Route path="/commercial"  element={<Commercial />} />
            <Route path="/inventory"   element={<Inventory />}  />
            <Route path="/accounting"  element={<Accounting />} />
            <Route path="/operations"  element={<Operations />} />
            <Route path="/hr"          element={<RRHH />}       />
            {/* Fallback */}
            <Route path="*"            element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
