import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { useOperator } from '../hooks/useOperator'
import { Badge, Card, EmptyState, PageHeader } from '../components/ui'
import { fmt } from '../constants'

export default function Insights() {
  const operator = useOperator()
  const [forecast, setForecast] = useState(null)
  const [forecastError, setForecastError] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [askError, setAskError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!operator.hasKey) return undefined
    const controller = new AbortController()
    api.get('/api/intelligence/forecast?days=7', controller.signal).then(setForecast).catch((e) => {
      if (e.name !== 'AbortError') setForecastError(e.message)
    })
    return () => controller.abort()
  }, [operator.hasKey])

  async function ask(event) {
    event.preventDefault()
    setLoading(true); setAskError(''); setAnswer(null)
    try {
      setAnswer(await api.post('/api/intelligence/ask', { question }))
    } catch (e) {
      setAskError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return <>
    <PageHeader title="AI assistant and demand forecast" subtitle="Operator-only summaries grounded in ReliefSync records, with transparent assumptions." />
    {!operator.hasKey && <Card><EmptyState title="Team sign-in required">Sign in before viewing forecasts or asking questions about operational records. <a href="#/login">Go to sign in</a>.</EmptyState></Card>}
    {operator.hasKey && <div className="grid grid-2">
      <Card title="Resource demand forecast">
        {forecastError && <p className="form-error" role="alert">{forecastError}</p>}
        {!forecast && !forecastError && <p role="status">Loading forecast…</p>}
        {forecast && <>
          <p className="muted">Next {forecast.horizon_days} days, estimated from delivered allocations during the last 28 days.</p>
          {!forecast.items.length ? <EmptyState title="Not enough delivery history">Record delivered allocations to calculate a history-based projection.</EmptyState> : <div className="table-wrap"><table><caption className="sr-only">Projected resource demand by supply category</caption><thead><tr><th scope="col">Category</th><th scope="col">Projected need</th><th scope="col">Current stock</th><th scope="col">Potential gap</th><th scope="col">28-day change</th></tr></thead><tbody>{forecast.items.map((r) => <tr key={r.category}><th scope="row">{r.category}</th><td>{fmt(r.projected_demand)}</td><td>{fmt(r.current_stock)}</td><td><Badge tone={r.projected_gap ? 'amber' : 'green'}>{fmt(r.projected_gap)}</Badge></td><td>{r.trend_percent == null ? 'Baseline unavailable' : `${r.trend_percent > 0 ? '+' : ''}${r.trend_percent}%`}</td></tr>)}</tbody></table></div>}
          <details><summary>Method and limitations</summary><p className="sub">{forecast.method}</p><p className="sub">{forecast.limitations}</p></details>
        </>}
      </Card>
      <Card title="Ask about current operations">
        <p className="muted">Questions are answered from a bounded database snapshot. Contact details are excluded. If local Ollama is unavailable, the app returns a transparent totals summary.</p>
        <form onSubmit={ask}>
          <label htmlFor="ops-question">Your question</label>
          <textarea id="ops-question" value={question} onChange={(e) => setQuestion(e.target.value)} minLength={5} maxLength={500} required rows={4} placeholder="How many shelter places are available, and what inventory is recorded?" />
          <div className="row"><button type="submit" className="btn btn-primary" disabled={loading || question.trim().length < 5}>{loading ? 'Preparing answer…' : 'Ask operations assistant'}</button><span className="muted">{question.length}/500</span></div>
        </form>
        {askError && <p className="form-error" role="alert">{askError}</p>}
        {answer && <section className="subpanel" aria-live="polite"><strong>{answer.provider}</strong><p>{answer.answer}</p><small className="muted">{answer.data_basis}</small></section>}
      </Card>
    </div>}
  </>
}
