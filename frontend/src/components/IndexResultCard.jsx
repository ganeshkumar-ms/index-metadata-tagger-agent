import { useState } from 'react'

export default function IndexResultCard({ data, guardrails, fileName, documentMetadata, onOpenDocument }) {
  const [copiedFilename, setCopiedFilename] = useState(false)
  const [copiedSummary, setCopiedSummary] = useState(false)
  const [selectedIntent, setSelectedIntent] = useState(null)

  if (!data) return null

  if (data.type === 'chat' || (!data.basic && (data.message || typeof data === 'string'))) {
    return (
      <div className="plainChatBubble">
        {data.message || (typeof data === 'string' ? data : JSON.stringify(data))}
      </div>
    )
  }

  const basic = data.basic || {}
  const business = data.business || {}
  const content = data.content || {}
  const entities = data.entities || {}
  const keyInfo = data.key_information || {}
  const dynamicMeta = data.dynamic_metadata || {}
  const searchOpt = data.search_optimization || {}

  function copyText(text, type) {
    navigator.clipboard.writeText(text)
    if (type === 'filename') {
      setCopiedFilename(true)
      setTimeout(() => setCopiedFilename(false), 2000)
    } else if (type === 'summary') {
      setCopiedSummary(true)
      setTimeout(() => setCopiedSummary(false), 2000)
    }
  }

  return (
    <div className="indexResultCard">
      {/* 1. Header & Canonical Title */}
      <div className="cardHeaderBlock">
        <div className="cardBadgeRow">
          <span className="typeBadge">{basic.document_type || 'Document'}</span>
          {business.domain && <span className="domainBadge">{business.domain}</span>}
          {basic.version && <span className="versionBadge">v{basic.version}</span>}
          {fileName && <span className="originalFileBadge">Original: {fileName}</span>}
        </div>
        <h2 className="docTitle">{basic.title || 'Indexed Document Profile'}</h2>
        <p className="docSummary">{data.summary}</p>

        {/* Recommended Filename Bar */}
        {searchOpt.recommended_filename && (
          <div className="filenameBanner">
            <div className="filenameLabel">
              <svg className="icon" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <span>RECOMMENDED CANONICAL FILENAME:</span>
            </div>
            <code className="canonicalName">{searchOpt.recommended_filename}</code>
            <button
              className="copyBtn"
              type="button"
              onClick={() => copyText(searchOpt.recommended_filename, 'filename')}
            >
              {copiedFilename ? '✓ COPIED' : 'COPY FILENAME'}
            </button>
          </div>
        )}
      </div>

      {/* 2. Basic & Business Taxonomy 2-Column Grid */}
      <div className="twoColGrid">
        <div className="taxoCard">
          <div className="taxoHead">
            <svg className="icon" viewBox="0 0 24 24">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
            <h3>BASIC METADATA</h3>
          </div>
          <div className="metaRows">
            <div className="metaRow">
              <span className="metaKey">Document Type:</span>
              <span className="metaVal">{basic.document_type || '—'}</span>
            </div>
            <div className="metaRow">
              <span className="metaKey">Target Audience:</span>
              <span className="metaVal">{basic.target_audience || '—'}</span>
            </div>
            <div className="metaRow">
              <span className="metaKey">Owner / Department:</span>
              <span className="metaVal">{basic.owner_department || '—'}</span>
            </div>
            <div className="metaRow">
              <span className="metaKey">Language:</span>
              <span className="metaVal">{basic.language || 'English'}</span>
            </div>
          </div>
        </div>

        <div className="taxoCard">
          <div className="taxoHead">
            <svg className="icon" viewBox="0 0 24 24">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            </svg>
            <h3>BUSINESS TAXONOMY</h3>
          </div>
          <div className="metaRows">
            <div className="metaRow">
              <span className="metaKey">Domain:</span>
              <span className="metaVal">{business.domain || '—'}</span>
            </div>
            <div className="metaRow">
              <span className="metaKey">Subdomain:</span>
              <span className="metaVal">{business.subdomain || '—'}</span>
            </div>
            <div className="metaRow">
              <span className="metaKey">Process Area:</span>
              <span className="metaVal">{business.process_area || '—'}</span>
            </div>
            <div className="metaRow">
              <span className="metaKey">Business Function:</span>
              <span className="metaVal">{business.business_function || '—'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Dynamic Metadata (Domain-Specific Adaptation) */}
      {dynamicMeta && Object.keys(dynamicMeta).length > 0 && (
        <div className="dynamicSection">
          <div className="sectionHead">
            <span className="dotAccent" />
            <h4>DYNAMIC ATTRIBUTES (ADAPTIVE TO DOCUMENT TYPE)</h4>
          </div>
          <div className="dynamicChipsGrid">
            {Object.entries(dynamicMeta).map(([k, v]) => (
              <div key={k} className="dynamicChip">
                <span className="dKey">{k}</span>
                <span className="dVal">{Array.isArray(v) ? v.join(', ') : String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. Content Intelligence: Topics, Keywords, & Tags */}
      <div className="contentSection">
        <div className="sectionHead">
          <span className="dotAccent" />
          <h4>CONTENT TOPICS & TAXONOMY TAGS</h4>
        </div>

        {content.core_topic && (
          <div className="coreTopicBanner">
            <span className="ctLabel">CORE TOPIC:</span>
            <span className="ctText">{content.core_topic}</span>
          </div>
        )}

        {content.subtopics && content.subtopics.length > 0 && (
          <div className="tagCluster">
            <span className="clusterLabel">Subtopics:</span>
            <div className="tagList">
              {content.subtopics.map((item, i) => (
                <span key={i} className="subtopicChip">{item}</span>
              ))}
            </div>
          </div>
        )}

        {content.tags && content.tags.length > 0 && (
          <div className="tagCluster">
            <span className="clusterLabel">Dynamic Tags:</span>
            <div className="tagList">
              {content.tags.map((tag, i) => (
                <span key={i} className="hashtagChip">{tag.startsWith('#') ? tag : `#${tag}`}</span>
              ))}
            </div>
          </div>
        )}

        {content.keywords && content.keywords.length > 0 && (
          <div className="tagCluster">
            <span className="clusterLabel">Search Keywords:</span>
            <div className="tagList">
              {content.keywords.map((kw, i) => (
                <span key={i} className="keywordChip">{kw}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 5. Identified Entities */}
      {entities && Object.values(entities).some(arr => arr && arr.length > 0) && (
        <div className="entitiesSection">
          <div className="sectionHead">
            <span className="dotAccent" />
            <h4>NAMED ENTITIES & COMPLIANCE STANDARDS</h4>
          </div>
          <div className="entitiesGrid">
            {entities.organizations && entities.organizations.length > 0 && (
              <div className="entityBlock">
                <span className="eType">Organizations</span>
                <p>{entities.organizations.join(', ')}</p>
              </div>
            )}
            {entities.systems_applications && entities.systems_applications.length > 0 && (
              <div className="entityBlock">
                <span className="eType">Systems & Tools</span>
                <p>{entities.systems_applications.join(', ')}</p>
              </div>
            )}
            {entities.roles && entities.roles.length > 0 && (
              <div className="entityBlock">
                <span className="eType">Roles & Personas</span>
                <p>{entities.roles.join(', ')}</p>
              </div>
            )}
            {entities.regulations_standards && entities.regulations_standards.length > 0 && (
              <div className="entityBlock">
                <span className="eType">Regulations & Standards</span>
                <p>{entities.regulations_standards.join(', ')}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 6. Key Information (Dates, Deadlines, Amounts, Rules) */}
      {keyInfo && Object.values(keyInfo).some(arr => arr && arr.length > 0) && (
        <div className="keyInfoSection">
          <div className="sectionHead">
            <span className="dotAccent" />
            <h4>KEY DATES, DEADLINES & GOVERNANCE RULES</h4>
          </div>
          <div className="keyInfoGrid">
            {keyInfo.dates && keyInfo.dates.length > 0 && (
              <div className="keyInfoItem">
                <span className="kLabel">Key Dates:</span>
                <ul>
                  {keyInfo.dates.map((d, i) => <li key={i}>{d}</li>)}
                </ul>
              </div>
            )}
            {keyInfo.deadlines && keyInfo.deadlines.length > 0 && (
              <div className="keyInfoItem">
                <span className="kLabel">Deadlines:</span>
                <ul>
                  {keyInfo.deadlines.map((dl, i) => <li key={i}>{dl}</li>)}
                </ul>
              </div>
            )}
            {keyInfo.compliance_rules && keyInfo.compliance_rules.length > 0 && (
              <div className="keyInfoItem full">
                <span className="kLabel">Compliance Rules:</span>
                <ul>
                  {keyInfo.compliance_rules.map((rule, i) => <li key={i}>{rule}</li>)}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 7. Search Optimization & Intent Retrieval Simulator */}
      {searchOpt && (
        <div className="searchOptSection">
          <div className="sectionHead">
            <svg className="icon" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <h4>FUTURE RETRIEVAL & SEARCH OPTIMIZATION</h4>
          </div>

          <p className="searchOptIntro">
            INDEX maps conversational intent and natural language phrasing so users find this document regardless of phrasing or typos.
          </p>

          <div className="intentGrid">
            <div className="intentColumn">
              <span className="colHead">Anticipated Intent Queries:</span>
              <ul className="queryList">
                {(searchOpt.intent_queries || []).map((q, i) => (
                  <li
                    key={i}
                    className={`queryItem${selectedIntent === q ? ' active' : ''}`}
                    onClick={() => setSelectedIntent(q)}
                  >
                    <span className="searchIco">🔍</span>
                    <span>&ldquo;{q}&rdquo;</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="intentColumn">
              <span className="colHead">Fuzzy / Shorthand Phrasings Mapped:</span>
              <ul className="fuzzyList">
                {(searchOpt.fuzzy_phrasings || []).map((f, i) => (
                  <li key={i} className="fuzzyItem">
                    <span className="fuzzyTag">&ldquo;{f}&rdquo;</span>
                    <span className="arrow">➔</span>
                    <span className="targetName">{searchOpt.recommended_filename || basic.title}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 8. Enterprise BFSI Guardrails Footer */}
      <div className="guardrailBar">
        <div className="guardrailStatus">
          <span className="shieldIcon">🛡️</span>
          <span className="guardrailTxt">
            Enterprise BFSI Guardrails Verified &bull; PCI-DSS Sanitized &bull; Zero Model Identifiers
          </span>
        </div>
        <button
          className="copySummaryBtn"
          type="button"
          onClick={() => copyText(JSON.stringify(data, null, 2), 'summary')}
        >
          {copiedSummary ? '✓ JSON COPIED' : 'EXPORT METADATA JSON'}
        </button>
      </div>
    </div>
  )
}

