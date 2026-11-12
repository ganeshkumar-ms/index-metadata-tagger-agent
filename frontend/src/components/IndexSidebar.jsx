import { useState } from 'react'

export default function IndexSidebar({
  sessions,
  currentSessionId,
  onNew,
  onLoad,
  onClose,
  isOpen,
  onRename,
  onDelete
}) {
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState('')
  const [confirmId, setConfirmId] = useState(null)

  function startRename(e, session) {
    e.stopPropagation()
    setConfirmId(null)
    setEditingId(session.id)
    setDraft(session.title)
  }

  function commitRename() {
    const t = draft.trim()
    if (editingId && t && onRename) {
      onRename(editingId, t)
    }
    setEditingId(null)
  }

  function askDelete(e, id) {
    e.stopPropagation()
    setEditingId(null)
    setConfirmId(id)
  }

  function confirmDelete(e, id) {
    e.stopPropagation()
    setConfirmId(null)
    if (onDelete) {
      onDelete(id)
    }
  }

  return (
    <aside className={`side${isOpen ? ' open' : ''}`}>
      <button
        className="drawerClose"
        type="button"
        aria-label="Close recent conversations"
        onClick={onClose}
      >
        <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 6l12 12M18 6 6 18" />
        </svg>
      </button>

      <span className="word">INDEX</span>

      <button
        className="new"
        onClick={() => { onNew(); onClose(); }}
        type="button"
      >
        <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 5v14M5 12h14" />
        </svg>
        <span>NEW CONVERSATION</span>
      </button>

      <div className="label">RECENT CONVERSATIONS</div>

      <div className="histList">
        {sessions.length === 0 && (
          <div className="histEmpty">No previous tagging sessions yet</div>
        )}

        {sessions.map(session => {
          const active = session.id === currentSessionId

          // 1. Inline Rename State
          if (editingId === session.id) {
            return (
              <div key={session.id} className="histRow editing">
                <input
                  autoComplete="off"
                  autoFocus
                  className="histInput"
                  value={draft}
                  maxLength={60}
                  onChange={e => setDraft(e.target.value)}
                  onBlur={commitRename}
                  onKeyDown={e => {
                    if (e.key === 'Enter') commitRename()
                    if (e.key === 'Escape') setEditingId(null)
                  }}
                />
              </div>
            )
          }

          // 2. Inline Delete Confirmation State
          if (confirmId === session.id) {
            return (
              <div key={session.id} className="histRow confirm">
                <span className="histConfirmTxt">Delete this chat?</span>
                <button
                  className="histBtn danger"
                  type="button"
                  onClick={e => confirmDelete(e, session.id)}
                >
                  Delete
                </button>
                <button
                  className="histBtn"
                  type="button"
                  onClick={e => { e.stopPropagation(); setConfirmId(null) }}
                >
                  Cancel
                </button>
              </div>
            )
          }

          // 3. Normal State with Hover Actions (Rename & Delete)
          return (
            <div key={session.id} className={`histRow${active ? ' on' : ''}`}>
              <button
                className={`hist${active ? ' on' : ''}`}
                title={session.title}
                type="button"
                onClick={() => { onLoad(session.id); onClose(); }}
              >
                {session.title}
              </button>

              <span className="histActions">
                <button
                  className="histIcon edit"
                  title="Rename"
                  aria-label="Rename conversation"
                  type="button"
                  onClick={e => startRename(e, session)}
                >
                  <svg className="icon" viewBox="0 0 24 24">
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
                  </svg>
                </button>
                <button
                  className="histIcon del"
                  title="Delete"
                  aria-label="Delete conversation"
                  type="button"
                  onClick={e => askDelete(e, session.id)}
                >
                  <svg className="icon" viewBox="0 0 24 24">
                    <path d="M3 6h18" />
                    <path d="M8 6V4h8v2" />
                    <path d="m6 6 1 14h10l1-14" />
                  </svg>
                </button>
              </span>
            </div>
          )
        })}
      </div>

      <div className="foot">ENTERPRISE INTELLIGENCE &middot; INDEX</div>
    </aside>
  )
}

