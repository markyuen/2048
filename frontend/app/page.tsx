'use client'
import React, { useEffect, useState } from 'react'

type Board = number[][]
interface GameResponse {
  board: Board
  status?: 'WIN' | 'LOSE' | 'NOOP'
}

export default function Home(): React.JSX.Element {
  const [board, setBoard] = useState<Board>(Array(4).fill(Array(4).fill(0)))
  const [gameState, setGameState] = useState<'WIN' | 'LOSE' | 'NOOP' | null>(null)
  const [agentResponse, setAgentResponse] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  function setCell(r: number, c: number, val: string) {
    const nb = board.map(row => row.slice())
    nb[r][c] = Number(val) || 0
    setBoard(nb)
  }

  function tileColor(val: number) {
    if (val === 0) return '#eee4da59'
    if (val === 2) return '#eee4da'
    if (val === 4) return '#ede0c8'
    if (val === 8) return '#ecdaa587'
    if (val === 16) return '#f4e1a5ff'
    if (val === 32) return '#edcf76af'
    if (val === 64) return '#f4d885ff'
    if (val === 128) return '#f2b179'
    if (val === 256) return '#f59663ce'
    if (val === 512) return '#f67d5fbc'
    if (val === 1024) return '#f65d3bc5'
    return '#2fd84e6f'
  }

  function isTerminalState(): boolean {
    return gameState === 'WIN' || gameState === 'LOSE'
  }

  async function makeBackendCall(path: string, method: 'PATCH' | 'POST'): Promise<any> {
    setLoading(true)
    setError(null)
    setGameState(null)
    setAgentResponse(null)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}${path}`, { method: method })
      if (!res.ok) throw new Error(await res.text())
      return await res.json()
    } catch (e: any) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  async function restart() {
    if (loading) return
    setBoard(await makeBackendCall('/api/restart', 'PATCH').then((data: GameResponse) => data.board))
  }

  async function suggest() {
    if (loading || isTerminalState()) return
    setAgentResponse(await makeBackendCall('/api/suggest/2', 'POST'))
  }

  async function performMove(direction: 'LEFT' | 'RIGHT' | 'UP' | 'DOWN') {
    if (loading || isTerminalState()) return
    const data: GameResponse = await makeBackendCall(`/api/move/${direction}`, 'PATCH')
    setBoard(data.board)
    setGameState(data.status)
  }

  useEffect(() => { restart() }, [])
  useEffect(() => {
    function handler(e: KeyboardEvent) {
      if (e.key === 'ArrowLeft') {
        e.preventDefault()
        performMove('LEFT')
      } else if (e.key === 'ArrowRight') {
        e.preventDefault()
        performMove('RIGHT')
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        performMove('UP')
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        performMove('DOWN')
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [loading, board])

  return (
    <div className="container">
      <h1>2048 Game</h1>
      <div className="board">
        {board.map((row, r) => (
          <div className="row" key={r}>
            {row.map((cell, c) => (
              <input
                key={c}
                data-val={cell}
                className="cell tile"
                value={cell === 0 ? '' : String(cell)}
                onChange={e => setCell(r, c, e.target.value)}
                style={{
                  background: tileColor(cell),
                  color: '#776e65',
                  fontSize: '20px',
                  fontWeight: 700,
                  border: 'none',
                  borderRadius: 6,
                }}
              />
            ))}
          </div>
        ))}
      </div>

      <div className="controls">
        <button onClick={restart}>{'Restart'}</button>
        <button onClick={suggest}>{'Suggest Move'}</button>
      </div>

      {error && (
        <div className="error card">
          <div className="error-header"><strong>Something went wrong</strong></div>
          <div className="error-body">{error}</div>
        </div>
      )}
      {gameState && (
        <div className="state card">
          <div className="state-header">
            <div className="state-title"><strong>Game State</strong></div>
            <span className={`badge ${gameState === 'WIN' ? 'win' : gameState === 'LOSE' ? 'lose' : 'info'}`}>{gameState}</span>
          </div>
          <div className="state-body">
            {gameState === 'WIN' ? <p>Congratulations — you won!</p> : gameState === 'LOSE' ? <p>Game over — try again.</p> : <p>Invalid move - try a different move.</p>}
          </div>
        </div>
      )}
      {agentResponse && (
        <div className="agent-result card">
          <h3>Agent Suggestion</h3>
          <pre>{JSON.stringify(agentResponse, null, 2)}</pre>
        </div>
      )}

      <style>{`
        :root { --bg: #faf8ef; --board: #bbada0; --tile-empty: #eee4da59 }
        .container { max-width: 680px; margin: 24px auto; font-family: system-ui, -apple-system, 'Segoe UI', Roboto; color: #333 }
        h1 { text-align: center; margin-bottom: 12px; color: #776e65 }
        .board { display: grid; gap: 8px; margin: 0 auto 16px; background: var(--board); padding: 12px; border-radius: 10px; width: fit-content }
        .row { display: grid; grid-template-columns: repeat(4, 72px); gap: 8px }
        .cell { width: 72px; height: 72px; text-align: center; font-size: 20px; outline: none }
        .tile { display:flex; align-items:center; justify-content:center }
        .cell[data-val="0"] { background: var(--tile-empty); color: #776e65 }
        .controls { display:flex; gap:8px; margin: 12px 0; justify-content:center }
        .controls button { background:#8f7a66; color:#fff; border:none; padding:12px 18px; border-radius:10px; cursor:pointer; box-shadow: 0 3px 0 #00000014; font-size:16px; min-width:110px }
        .controls button[disabled] { opacity: 0.6; cursor: default }
        .controls button:hover:not([disabled]) { transform: translateY(-1px) }
        .card {
          display: block;
          width: 100%;
          max-width: 640px;
          margin: 10px auto;
          text-align: left;
          background: linear-gradient(180deg, #ffffff 0%, #fbfaf8 100%);
          border: 1px solid #0000000f;
          padding: 16px 18px;
          border-radius: 12px;
          box-shadow: 0 8px 22px #1818180f;
          color: #3b3a36;
          font-family: inherit;
          font-size: inherit;
          transition: transform 120ms ease, box-shadow 120ms ease;
        }
        .card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px #18181814 }
        .card h3 { margin: 0 0 8px 0; font-size: 18px; color: #6b5a4a }
        .agent-result pre { white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; max-width: 60ch; margin:8px 0 0 0; font-size: 15px; background:#fff; padding:12px; border-radius:8px }
        .state-header, .error-header { display:flex; align-items:center; justify-content:space-between; gap:12px }
        .state-body, .error-body { margin-top:8px; font-size:15px }
        .badge { display:inline-block; padding:6px 12px; border-radius:999px; font-weight:700; font-size:13px }
        .badge.win { background: #60b15a; color: white }
        .badge.lose { background: #d94a4a; color: white }
        .badge.info { background: #8f7a66; color: white }
        .error.card { color: #7a2a2a; background: linear-gradient(180deg, #fff6f6 0%, #fff1f1 100%); border: 1px solid #f3c2c2 }
      `}</style>
    </div>
  )
}
