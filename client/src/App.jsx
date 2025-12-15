import { useState, useEffect } from 'react'

function App() {
  const [question, setQuestion] = useState("Who had the most triple-doubles in 2016?")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleQuery = async () => {
    if (!question.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      if (!response.ok) {
        throw new Error('Failed to execute query')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Handle Enter key
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleQuery()
  }

  const [showDetails, setShowDetails] = useState(false)

  return (
    <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      <header style={{ marginBottom: '3rem', borderBottom: '1px solid #334155', paddingBottom: '1rem' }}>
        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          🏀 Deep Stat AI <span style={{ fontSize: '0.8rem', background: '#334155', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>AGENTIC ANALYST</span>
        </div>
      </header>

      {/* Query Section */}
      <section style={{ marginBottom: '3rem' }}>
        <div className="card" style={{ padding: '2rem' }}>
          <label className="metric-label" style={{ marginBottom: '1rem', display: 'block' }}>
            Ask a complex NBA question (e.g., "Compare Lebron and Curry in 2016 finals")
          </label>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your question..."
              style={{
                flex: 1,
                padding: '1rem',
                fontSize: '1.1rem',
                background: '#0F172A',
                border: '1px solid #334155',
                color: 'white',
                borderRadius: '8px'
              }}
            />
            <button
              onClick={handleQuery}
              disabled={loading}
              style={{
                width: '150px',
                fontSize: '1rem',
                background: loading ? '#334155' : 'var(--primary)',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Thinking...' : 'Run Analysis'}
            </button>
          </div>
          {error && <div style={{ color: 'var(--error)', marginTop: '1rem' }}>{error}</div>}
        </div>
      </section>

      {/* Results Section */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

          {/* Main Answer (Narrative) */}
          <div className="card" style={{ padding: '2rem', borderColor: result.success ? '#334155' : 'var(--error)' }}>
            <h3 style={{ marginTop: 0, color: '#38BDF8', borderBottom: '1px solid #334155', paddingBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {result.success ? '🎙️ Deep Stat Insight' : '❌ Runtime Error'}
            </h3>
            <div style={{
              fontSize: '1.2rem',
              lineHeight: '1.6',
              color: result.success ? '#F8FAFC' : '#F87171',
              marginTop: '1rem',
              whiteSpace: 'pre-wrap'
            }}>
              {result.narrative || result.result}
            </div>
          </div>

          {/* Raw Data (If Narrative exists and wasn't shown as main) */}
          {result.narrative && result.success && (
            <div className="card" style={{ opacity: 0.9 }}>
              <h3 style={{ marginTop: 0, color: '#94A3B8', fontSize: '1rem' }}>🔢 Raw Data Source</h3>
              <pre style={{ background: '#0F172A', padding: '1rem', borderRadius: '8px', fontSize: '0.9rem', color: '#CBD5E1', overflowX: 'auto' }}>
                {result.result}
              </pre>
            </div>
          )}

          {/* Collapsible Details */}
          <div>
            <button
              onClick={() => setShowDetails(!showDetails)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#64748B',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '1rem',
                padding: 0
              }}
            >
              <span style={{ transform: showDetails ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}>▶</span>
              {showDetails ? 'Hide Logic Trace' : 'Show Architect Plan & Generated Code'}
            </button>

            {showDetails && (
              <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1rem' }}>
                {/* Plan */}
                <div className="card">
                  <h3 style={{ marginTop: 0, color: '#94A3B8' }}>🧠 Architect's Plan</h3>
                  <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.9rem', lineHeight: '1.5' }}>
                    {result.plan}
                  </div>
                </div>

                {/* Code */}
                <div className="card">
                  <h3 style={{ marginTop: 0, color: '#94A3B8' }}>🐍 Generated Code</h3>
                  <pre style={{
                    background: '#0F172A',
                    padding: '1rem',
                    borderRadius: '8px',
                    overflowX: 'auto',
                    fontSize: '0.85rem'
                  }}>
                    <code>{result.code}</code>
                  </pre>
                </div>
              </div>
            )}
          </div>

        </div>
      )}

      {/* Empty State */}
      {!result && !loading && (
        <div style={{ textAlign: 'center', color: '#64748B', marginTop: '4rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</div>
          <p>I am ready to write code for you.</p>
        </div>
      )}

      {loading && (
        <div style={{ textAlign: 'center', color: '#64748B', marginTop: '4rem' }}>
          <div className="loader" style={{ margin: '0 auto 1rem auto' }}></div>
          <p>Architecting Solution...</p>
        </div>
      )}
    </div>
  )
}

export default App
