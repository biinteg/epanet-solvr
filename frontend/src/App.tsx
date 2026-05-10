import { useState, lazy, Suspense } from 'react'
import './App.css'

const SolverForm = lazy(() => import('./SolverForm'))

function App() {
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="app-container">
      <header className="glass top-nav">
        <div className="nav-content">
          <div className="logo">EPANET Solver</div>
          <nav>
            <a href="#" className="active">Home</a>
            <a href="#">Optimizer</a>
            <a href="#">Docs</a>
          </nav>
          <div className="nav-actions">
            <button className="btn-signin">Sign In</button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {!showForm ? (
          <section className="hero">
            <h1 className="display-text">EPANET Solver</h1>
            <p className="sub-text">
              High-precision hydraulic optimization. Upload your network and achieve aesthetic quietude in your engineering tasks.
            </p>
            <div className="cta-group">
              <button
                type="button"
                className="btn-primary"
                onClick={() => setShowForm(true)}
              >
                Run Solver
                <span className="material-symbols-outlined">arrow_forward</span>
              </button>
            </div>
          </section>
        ) : (
          <Suspense fallback={<div className="loading">Loading interface…</div>}>
            <SolverForm />
          </Suspense>
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-logo">EPANET Solver</div>
          <div className="footer-info">© 2024 EPANET Solver. Compliance: Permen PU Standards.</div>
          <nav className="footer-nav">
            <a href="#">Support</a>
            <a href="#">Privacy</a>
          </nav>
        </div>
      </footer>
    </div>
  )
}

export default App
