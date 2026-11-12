import { useState, useEffect, useRef } from 'react'
import IndexSidebar from './components/IndexSidebar.jsx'
import IndexResultCard from './components/IndexResultCard.jsx'
import DocumentViewer from './components/DocumentViewer.jsx'
import { tagContent, toViewerDoc } from './services/api.js'

const SESSIONS_KEY = 'index_sessions'

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

function shorten(text, max) {
  return text.length > max ? text.slice(0, max) + '\u2026' : text
}

const GENERIC_CHAT_INPUTS = new Set([
  'hi', 'hello', 'hey', 'hola', 'hii', 'hiii', 'heyy', 'yo', 'sup',
  'how are you', 'how are u', 'how r u', 'how r you', 'how are you doing',
  'how are u doing', 'hows it going', 'how is it going', 'whats up',
  'good morning', 'good afternoon', 'good evening', 'greetings',
  'hi there', 'hello there', 'hey there', 'ok', 'okay', 'thanks', 'thank you'
])

function isGenericGreeting(text) {
  if (!text) return true
  const cleaned = text.trim().toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ')
  if (cleaned.length <= 2) return true
  if (GENERIC_CHAT_INPUTS.has(cleaned)) return true
  return /^(?:hi+|h[ea]y+|h[ea]llo+|hlo|hola|greetings?|yo+|sup|namaste)(?:\s+(?:there|index|agent|bot|all|team|friend|buddy))?$/.test(cleaned) ||
         /^(?:(?:hi+|h[ea]y+|h[ea]llo+|hlo)\s+)?(?:how|hw)\s+(?:r|are|re)\s+(?:u|you|yu)(?:\s+doing)?$/.test(cleaned) ||
         /^(?:hru|whats?\s+up|hows?\s+it\s+going|hows?\s+u)$/.test(cleaned)
}

function formatSmartTitle(text, fileName) {
  // 1. If user attached a file, clean file name
  if (fileName) {
    const base = fileName.replace(/\.[^/.]+$/, '').replace(/[-_]+/g, ' ').trim()
    if (base) {
      const formatted = base.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ')
      return shorten(formatted, 42)
    }
  }

  // 2. If user supplied text prompt, strip filler prefixes
  if (text && !isGenericGreeting(text)) {
    let clean = text.trim().replace(/\s+/g, ' ')
    clean = clean.replace(/^(?:can you|please|kindly|could you|would you|i want to|i need to|help me|can u|plz)\s+/i, '')
    clean = clean.replace(/^(?:extract|index|tag|metadata|classify|catalog|analyze|summarize|review)\s+(?:this|the|my|our)?\s*/i, '')
    clean = clean.replace(/^(?:document|metadata|file|data|record|content|text)\s+(?:for|on|about|regarding)?\s*/i, '')
    clean = clean.replace(/^[?:!.,-\s]+/, '')
    if (clean.length > 2) {
      const capitalized = clean.charAt(0).toUpperCase() + clean.slice(1)
      return shorten(capitalized, 42)
    }
  }

  return 'New conversation'
}

function loadSessions() {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY)
    const list = raw ? JSON.parse(raw) : []
    return list
      .filter(s => (s.messages || []).length > 0)
      .map(s => {
        let title = s.title || 'New conversation'
        // Filter out any corrupt HTML responses from earlier CloudFront 403 errors
        const messages = (s.messages || []).filter(m => {
          const str = typeof m.data === 'string' ? m.data : (typeof m.content === 'string' ? m.content : '')
          return !str.includes('<!doctype') && !str.includes('<html')
        })

        // Upgrade unlocked sessions: prefer AI metadata title, or smart-stripped prompt/filename
        if (!s.titleLocked) {
          const lastIndexMsg = [...messages].reverse().find(m => m.role === 'ai' && m.data?.basic?.title)
          const bt = lastIndexMsg ? shorten(lastIndexMsg.data.basic.title, 48) : null
          if (bt) {
            title = bt
          } else {
            const topicMsg = messages.find(m => m.role === 'user' && ((m.text && !isGenericGreeting(m.text)) || m.fileName))
            if (topicMsg) {
              title = formatSmartTitle(topicMsg.text, topicMsg.fileName)
            } else if (isGenericGreeting(title)) {
              title = 'New conversation'
            }
          }
        }

        return { ...s, title, messages }
      })
      .filter(s => (s.messages || []).length > 0)
  } catch {
    return []
  }
}

function saveSessions(sessions) {
  try {
    const valid = (sessions || []).filter(s => (s.messages || []).length > 0)
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(valid))
  } catch {
    // ignore
  }
}

function formatTimestamp(ts) {
  if (!ts) return 'TODAY'
  const d = new Date(ts)
  if (isNaN(d.getTime())) return String(ts)
  const now = new Date()
  const diffDays = Math.floor((now - d) / 86400000)
  if (diffDays === 0) {
    return `TODAY · ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  } else if (diffDays === 1) {
    return 'YESTERDAY'
  } else {
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }).toUpperCase()
  }
}

function getPreview(messages) {
  if (!messages || messages.length === 0) return 'Previous metadata extraction.'
  const lastAi = [...messages].reverse().find(m => m.role === 'ai')
  if (lastAi?.data?.summary) {
    return lastAi.data.summary.slice(0, 85) + (lastAi.data.summary.length > 85 ? '...' : '')
  }
  const fileMsg = messages.find(m => m.fileName || m.file?.name)
  if (fileMsg) {
    return `Attached document: ${fileMsg.fileName || fileMsg.file?.name}`
  }
  const firstUser = messages.find(m => m.role === 'user' && ((m.text && !isGenericGreeting(m.text)) || (m.content && typeof m.content === 'string' && !isGenericGreeting(m.content))))
  if (firstUser?.text) return firstUser.text.slice(0, 85)
  if (firstUser?.content && typeof firstUser.content === 'string') return firstUser.content.slice(0, 85)
  return 'Metadata intelligence & categorization preview.'
}

export default function App() {
  const [view, setView] = useState('home') // 'home' | 'chat'
  const [sessions, setSessions] = useState(loadSessions)
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [homeInputText, setHomeInputText] = useState('')
  const [attachedFile, setAttachedFile] = useState(null)
  const [isThinking, setIsThinking] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editingTitle, setEditingTitle] = useState(false)
  const [titleDraft, setTitleDraft] = useState('')
  const [viewerDoc, setViewerDoc] = useState(null)

  function openDocument(meta) {
    let target = meta || {}
    if (!target.view_url && !target.viewUrl && !target.url) {
      const aiWithDoc = messages.find(m => m.documentMetadata?.view_url || m.data?.document_metadata?.view_url)
      const found = aiWithDoc?.documentMetadata || aiWithDoc?.data?.document_metadata
      if (found) {
        target = { ...target, ...found }
      }
    }
    setViewerDoc(toViewerDoc(target))
  }

  useEffect(() => {
    setViewerDoc(null)
  }, [currentSessionId])

  const homeFileInputRef = useRef(null)
  const chatFileInputRef = useRef(null)
  const messagesContainerRef = useRef(null)
  const sessionsRef = useRef(sessions)
  const prevLastRoleRef = useRef(null)
  const sessionJustChangedRef = useRef(false)

  useEffect(() => {
    sessionsRef.current = sessions
    saveSessions(sessions)
  }, [sessions])

  // Scroll behavior:
  // 1. Session change -> top: 0
  // 2. New AI reply -> smoothly scroll container to top of AI card
  // 3. User message / thinking -> bottom
  useEffect(() => {
    const el = messagesContainerRef.current
    if (!el) return

    if (sessionJustChangedRef.current) {
      sessionJustChangedRef.current = false
      const timer = setTimeout(() => {
        const aiBubbles = el.querySelectorAll('.bubble.ai')
        const lastAi = aiBubbles[aiBubbles.length - 1]
        if (lastAi) {
          const elRect = el.getBoundingClientRect()
          const bubbleRect = lastAi.getBoundingClientRect()
          const targetTop = el.scrollTop + (bubbleRect.top - elRect.top) - 18
          el.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' })
        } else {
          el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
        }
      }, 50)
      prevLastRoleRef.current = messages[messages.length - 1]?.role
      return () => clearTimeout(timer)
    }

    const lastMsg = messages[messages.length - 1]
    const currentLastRole = lastMsg?.role
    const isNewAiReply = currentLastRole === 'ai' && (prevLastRoleRef.current === 'thinking' || lastMsg?.isNew)

    if (isNewAiReply) {
      const timer = setTimeout(() => {
        if (!el) return
        const aiBubbles = el.querySelectorAll('.bubble.ai')
        const lastAiBubble = aiBubbles[aiBubbles.length - 1]
        if (lastAiBubble) {
          const elRect = el.getBoundingClientRect()
          const bubbleRect = lastAiBubble.getBoundingClientRect()
          const targetTop = el.scrollTop + (bubbleRect.top - elRect.top) - 18
          el.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' })
        }
      }, 50)
      prevLastRoleRef.current = currentLastRole
      return () => clearTimeout(timer)
    } else if (currentLastRole === 'user' || isThinking) {
      el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
    }

    prevLastRoleRef.current = currentLastRole
  }, [messages, isThinking])

  const currentSession = sessions.find(s => s.id === currentSessionId)

  const openNewChat = (initialText = '', file = null) => {
    sessionJustChangedRef.current = true
    if (initialText || file) {
      const newId = generateId()
      const newSession = {
        id: newId,
        title: formatSmartTitle(initialText, file?.name),
        timestamp: new Date().toISOString(),
        date: 'TODAY',
        messages: []
      }
      setSessions(prev => [newSession, ...prev])
      setCurrentSessionId(newId)
      setMessages([])
      setView('chat')
      setDrawerOpen(false)
      setEditingTitle(false)
      handleSend(initialText, file, newId)
    } else {
      // Blank draft: NO empty session stored in history until user actually sends a message!
      setCurrentSessionId(null)
      setMessages([])
      setView('chat')
      setDrawerOpen(false)
      setEditingTitle(false)
    }
  }

  const selectSession = (sessionId) => {
    const s = sessions.find(item => item.id === sessionId)
    if (!s) return
    sessionJustChangedRef.current = true
    setCurrentSessionId(s.id)
    setMessages(s.messages || [])
    setView('chat')
    setDrawerOpen(false)
    setEditingTitle(false)
    setTimeout(() => {
      const el = messagesContainerRef.current
      if (el) {
        const aiBubbles = el.querySelectorAll('.bubble.ai')
        const lastAi = aiBubbles[aiBubbles.length - 1]
        if (lastAi) {
          const elRect = el.getBoundingClientRect()
          const bubbleRect = lastAi.getBoundingClientRect()
          const targetTop = el.scrollTop + (bubbleRect.top - elRect.top) - 18
          el.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' })
        } else {
          el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
        }
      }
    }, 60)
  }

  const renameSession = (id, newTitle) => {
    setSessions(prev => prev.map(s => s.id === id ? { ...s, title: newTitle, titleLocked: true } : s))
  }

  const deleteSession = (id) => {
    const next = sessionsRef.current.filter(s => s.id !== id)
    sessionsRef.current = next
    saveSessions(next)
    setSessions(next)

    if (id === currentSessionId) {
      setCurrentSessionId(null)
      setMessages([])
      setView('chat')
      setDrawerOpen(false)
      setEditingTitle(false)
    }
  }

  function commitTitle() {
    const v = titleDraft.trim()
    if (currentSessionId && v && v !== currentSession?.title) {
      renameSession(currentSessionId, v)
    }
    setEditingTitle(false)
  }

  const handleSend = async (textToSend, fileToSend, targetSessionId = currentSessionId) => {
    const content = (textToSend !== undefined ? textToSend : inputText).trim()
    const file = fileToSend !== undefined ? fileToSend : attachedFile

    if (!content && !file) return

    let activeId = targetSessionId
    if (!activeId) {
      const newSession = {
        id: generateId(),
        title: formatSmartTitle(content, file?.name),
        timestamp: new Date().toISOString(),
        date: 'TODAY',
        messages: []
      }
      activeId = newSession.id
      setSessions(prev => [newSession, ...prev])
      setCurrentSessionId(activeId)
    }

    const userMessage = {
      id: generateId(),
      role: 'user',
      text: content,
      fileName: file ? file.name : null,
      fileSize: file ? `${(file.size / 1024).toFixed(1)} KB` : null
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setAttachedFile(null)
    setIsThinking(true)

    // Build history for API
    const history = messages.map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.role === 'user' ? m.text : (m.data?.summary || 'Indexed document')
    }))

    try {
      const response = await tagContent({ file, text: content, conversationHistory: history })

      const docMeta = response.document_metadata
      const updatedUserMsg = docMeta && (userMessage.fileName || file)
        ? {
            ...userMessage,
            documentMetadata: docMeta,
            file: { name: userMessage.fileName, size: file?.size, ...docMeta }
          }
        : userMessage

      const aiMessage = {
        id: generateId(),
        role: 'ai',
        status: response.status,
        data: response.data || response,
        guardrails: response.guardrails,
        fileName: response.file_name || (file ? file.name : null),
        documentMetadata: docMeta,
        isNew: true
      }

      setMessages(prev => {
        const withUpdatedUser = prev.map(m => m.id === userMessage.id ? updatedUserMsg : m)
        const next = [...withUpdatedUser, aiMessage]
        setSessions(sPrev => sPrev.map(s => {
          if (s.id === activeId) {
            let updatedTitle = s.title
            if (!s.titleLocked) {
              if (response.data?.basic?.title) {
                updatedTitle = shorten(response.data.basic.title, 48)
              } else if (file) {
                updatedTitle = formatSmartTitle('', file.name)
              } else if (content && !isGenericGreeting(content)) {
                updatedTitle = formatSmartTitle(content)
              }
            }
            return {
              ...s,
              title: updatedTitle,
              messages: next
            }
          }
          return s
        }))
        return next
      })
    } catch (err) {
      const errorMsg = {
        id: generateId(),
        role: 'ai',
        status: 'error',
        data: {
          summary: `INDEX could not process this request: ${err.response?.data?.detail || err.message || 'Unknown error'}. Please verify connection and retry.`
        },
        isNew: true
      }
      setMessages(prev => {
        const next = [...prev, errorMsg]
        setSessions(sPrev => sPrev.map(s => s.id === activeId ? { ...s, messages: next } : s))
        return next
      })
    } finally {
      setIsThinking(false)
    }
  }

  return (
    <div className="app">
      <div className="aurora" />
      <div className="radialPattern" />

      {/* HOME LANDING VIEW */}
      {view === 'home' && (
        <section id="home">
          <header>
            <div className="word">INDEX</div>
            <button className="enter" onClick={() => openNewChat()} type="button">
              ENTER WORKSPACE ↗
            </button>
          </header>

          <main className="home">
            <div className="heroGroup">
              <div className="eyebrow">METADATA TAGGER</div>
              <h1>
                Know the content.<br />
                <span>Find it faster.</span>
              </h1>
              <p className="sub">
                A focused AI space for ideas, questions and conversations worth returning to.
              </p>

              {/* Big Home Prompt */}
              <div className="promptGlow">
                <div className="prompt">
                  <input
                    ref={homeFileInputRef}
                    type="file"
                    className="fileInput"
                    onChange={e => {
                      if (e.target.files && e.target.files[0]) {
                        setAttachedFile(e.target.files[0])
                      }
                    }}
                  />
                  <button
                    className="startAttach"
                    type="button"
                    aria-label="Add file"
                    title="Add file"
                    onClick={() => homeFileInputRef.current?.click()}
                  >
                    <svg className="icon" viewBox="0 0 24 24">
                      <path d="m21.4 11.6-8.9 8.9a6 6 0 0 1-8.5-8.5l9.3-9.3a4 4 0 0 1 5.7 5.7l-9.3 9.3a2 2 0 0 1-2.8-2.8l8.6-8.6" />
                    </svg>
                  </button>

                  <input
                    placeholder="Ask INDEX or attach a file to tag..."
                    value={homeInputText}
                    onChange={e => setHomeInputText(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        openNewChat(homeInputText, attachedFile)
                        setHomeInputText('')
                      }
                    }}
                  />

                  <button
                    className="send"
                    type="button"
                    aria-label="Send"
                    onClick={() => {
                      openNewChat(homeInputText, attachedFile)
                      setHomeInputText('')
                    }}
                  >
                    <svg className="icon" viewBox="0 0 24 24">
                      <path d="M5 12h13" />
                      <path d="m13 7 5 5-5 5" />
                    </svg>
                  </button>
                </div>
              </div>

              {attachedFile && (
                <div className="filePill show">
                  <span>📎 Attached: {attachedFile.name}</span>
                  <button
                    style={{ background: 'none', border: 0, color: '#fca5a5', cursor: 'pointer', marginLeft: 8 }}
                    onClick={() => setAttachedFile(null)}
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>

            {/* RECENT CONVERSATIONS (TAXORA STYLE: NO "Continue where you left off") */}
            <div className="recentGroup">
              <div className={`recentHead recentOnly${sessions.length === 0 ? ' recentEmpty' : ''}`}>
                <span>RECENT CONVERSATIONS</span>
              </div>

              <div className="cards">
                {sessions.length > 0 ? (
                  sessions.slice(0, 3).map(s => (
                    <button
                      key={s.id}
                      className="card"
                      type="button"
                      onClick={() => selectSession(s.id)}
                    >
                      <small>{formatTimestamp(s.timestamp || s.date)}</small>
                      <b>{s.title}</b>
                      <p>{getPreview(s.messages)}</p>
                    </button>
                  ))
                ) : (
                  <div className="card emptyCard">
                    <small>NOTHING YET</small>
                    <b>No conversations yet</b>
                    <p>Type a message or attach a file above to begin.</p>
                  </div>
                )}

                {sessions.length > 3 && (
                  <button
                    type="button"
                    className="seeMoreOnly"
                    onClick={() => { setDrawerOpen(true); setView('chat'); }}
                  >
                    SEE MORE <span>+</span>
                  </button>
                )}
              </div>
            </div>
          </main>
        </section>
      )}

      {/* CHAT / WORKSPACE VIEW */}
      {view === 'chat' && (
        <section className={`chatPage${drawerOpen ? ' drawerOpen' : ''}`}>
          {/* Scrim for Mobile Drawer */}
          <div
            className={`scrim${drawerOpen ? ' show' : ''}`}
            onClick={() => setDrawerOpen(false)}
          />

          <div className={`layout${viewerDoc ? ' withViewer' : ''}`}>
            <IndexSidebar
              sessions={sessions}
              currentSessionId={currentSessionId}
              isOpen={drawerOpen}
              onClose={() => setDrawerOpen(false)}
              onNew={() => openNewChat()}
              onLoad={selectSession}
              onRename={renameSession}
              onDelete={deleteSession}
            />

            <main className="chat">
              {/* Header: Title is directly editable on click (NO pencil icon) */}
              <div className="chatHead">
                <div>
                  <b>
                    {editingTitle ? (
                      <input
                        autoComplete="off"
                        autoFocus
                        className="titleInput"
                        value={titleDraft}
                        maxLength={60}
                        onChange={e => setTitleDraft(e.target.value)}
                        onBlur={commitTitle}
                        onKeyDown={e => {
                          if (e.key === 'Enter') commitTitle()
                          if (e.key === 'Escape') setEditingTitle(false)
                        }}
                      />
                    ) : (
                      <span
                        className="titleEditable"
                        title="Click to edit title"
                        onClick={() => {
                          setTitleDraft(currentSession?.title || 'New conversation')
                          setEditingTitle(true)
                        }}
                      >
                        {currentSession?.title || 'New conversation'}
                      </span>
                    )}
                  </b>
                  <small>METADATA INTELLIGENCE WORKSPACE</small>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <button
                    className="ghost mobileOnlyBtn"
                    type="button"
                    onClick={() => setDrawerOpen(prev => !prev)}
                  >
                    RECENT
                  </button>

                  <button
                    className="ghost"
                    type="button"
                    onClick={() => {
                      setDrawerOpen(false)
                      setView('home')
                    }}
                  >
                    <svg className="icon" viewBox="0 0 24 24" style={{ width: 14, height: 14, marginRight: 6 }}>
                      <path d="m3 10 9-7 9 7" />
                      <path d="M5 9v11h14V9" />
                    </svg>
                    <span>HOME</span>
                  </button>
                </div>
              </div>

              {/* Single Scrollable Messages Container */}
              <div className="messages" ref={messagesContainerRef}>
                {messages.length === 0 && !isThinking && (
                  <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--muted)', maxWidth: 440 }}>
                    <div style={{ fontSize: 32, marginBottom: 12 }}>🏷️</div>
                    <h3 style={{ color: '#fff', margin: '0 0 8px' }}>Metadata Tagger Workspace</h3>
                    <p style={{ fontSize: 14, lineHeight: 1.6 }}>
                      Upload any poorly named file (<code style={{ color: 'var(--cyan)' }}>DOC_48383_FINAL_V2.pdf</code>) or paste document content to extract multi-dimensional taxonomy, dynamic attributes, and retrieval queries.
                    </p>
                  </div>
                )}

                {messages.map(msg => {
                  if (msg.role === 'user') {
                    return (
                      <div key={msg.id} className="bubble user">
                        {msg.fileName && (
                          <button
                            type="button"
                            className="userFileCard"
                            onClick={() => openDocument(msg.documentMetadata || {
                              name: msg.fileName,
                              filename: msg.fileName,
                              size: msg.fileSize,
                              url: msg.documentMetadata?.url,
                              view_url: msg.documentMetadata?.view_url,
                              preview: msg.documentMetadata?.preview,
                              rawMeta: msg.documentMetadata
                            })}
                            title="Open document"
                          >
                            <div className="userFileHeader">
                              <div className="userFileLeft">
                                <span className="userFileIcon" aria-hidden="true">📄</span>
                                <div className="userFileInfo">
                                  <span className="userFileName" title={msg.fileName}>{msg.fileName}</span>
                                  <span className="userFileMeta">{msg.fileSize || 'DOCUMENT'}</span>
                                </div>
                              </div>
                              <span className="userFileViewBtn">Open ↗</span>
                            </div>
                          </button>
                        )}
                        {msg.text && !msg.text.startsWith('[Uploaded Document:') && !msg.text.startsWith('[File:') && (
                          <div style={{ marginTop: msg.fileName ? '8px' : '0' }}>{msg.text}</div>
                        )}
                      </div>
                    )
                  }

                  // AI Response Message
                  return (
                    <div key={msg.id} className="bubble ai">
                      <IndexResultCard
                        data={msg.data}
                        guardrails={msg.guardrails}
                        fileName={msg.fileName}
                        documentMetadata={msg.documentMetadata}
                        onOpenDocument={openDocument}
                      />
                    </div>
                  )
                })}

                {/* Thinking Indicator */}
                {isThinking && (
                  <div className="thinking">
                    <span className="thinkName">INDEX</span>
                    <span className="bars">
                      <i /><i /><i /><i />
                    </span>
                    <span style={{ fontSize: 13, color: 'var(--muted)' }}>
                      Analyzing document & generating multi-dimensional metadata...
                    </span>
                  </div>
                )}
              </div>

              {/* Composer */}
              <div className="composerArea">
                <div className="composer">
                  {attachedFile && (
                    <div className="composerAttachmentBar">
                      <span>📎 Attached: {attachedFile.name} ({(attachedFile.size / 1024).toFixed(1)} KB)</span>
                      <button type="button" onClick={() => setAttachedFile(null)}>✕</button>
                    </div>
                  )}

                  <form onSubmit={e => {
                    e.preventDefault()
                    handleSend()
                  }}>
                    <input
                      ref={chatFileInputRef}
                      type="file"
                      className="fileInput"
                      onChange={e => {
                        if (e.target.files && e.target.files[0]) {
                          setAttachedFile(e.target.files[0])
                        }
                      }}
                    />
                    <button
                      className="plus"
                      type="button"
                      aria-label="Add file"
                      title="Attach file"
                      onClick={() => chatFileInputRef.current?.click()}
                    >
                      <svg className="icon" viewBox="0 0 24 24">
                        <path d="m21.4 11.6-8.9 8.9a6 6 0 0 1-8.5-8.5l9.3-9.3a4 4 0 0 1 5.7 5.7l-9.3 9.3a2 2 0 0 1-2.8-2.8l8.6-8.6" />
                      </svg>
                    </button>

                    <input
                      placeholder="Message INDEX or attach a document to tag..."
                      value={inputText}
                      onChange={e => setInputText(e.target.value)}
                      disabled={isThinking}
                    />

                    <button
                      className="chatSend"
                      type="submit"
                      aria-label="Send"
                      disabled={isThinking || (!inputText.trim() && !attachedFile)}
                    >
                      <svg className="icon" viewBox="0 0 24 24">
                        <path d="M5 12h13" />
                        <path d="m13 7 5 5-5 5" />
                      </svg>
                    </button>
                  </form>
                </div>
                <div className="fine">
                  ENTERPRISE BFSI &bull; INDEX METADATA TAGGER &bull; SECURE &bull; SANITIZED
                </div>
              </div>
            </main>
            <DocumentViewer doc={viewerDoc} onClose={() => setViewerDoc(null)} />
          </div>
        </section>
      )}
    </div>
  )
}
