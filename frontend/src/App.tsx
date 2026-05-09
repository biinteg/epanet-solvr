import { useState, lazy, Suspense } from 'react'

const SolverForm = lazy(() => import('./SolverForm')) // placeholder component

function App() {
  const [showForm, setShowForm] = useState(false)

  return (
    <>
      <section id="center">
        <h1>EPANET Solver</h1>
        <p>Upload an INP file and run the Auto Solver.</p>
        <button
          type="button"
          className="counter"
          onClick={() => setShowForm(true)}
        >
          Run Solver
        </button>
      </section>

      {showForm && (
        <Suspense fallback={<div>Loading…</div>}>
          <SolverForm />
        </Suspense>
      )}
    </>
  )
}

export default App
