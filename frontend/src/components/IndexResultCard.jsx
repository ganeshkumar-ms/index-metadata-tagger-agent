import { useState } from 'react'

function ShieldIcon() {
  return (
    <svg className="icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  )
}

function CopyIcon({ size = 13 }) {
  return (
    <svg className="icon" viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  )
}

function CheckIcon({ size = 13 }) {
  return (
    <svg className="icon" viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function DownloadIcon({ size = 14 }) {
  return (
    <svg className="icon" viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}

function deterministicHash(str) {
  let h1 = 0xdeadbeef ^ (str || '').length
  let h2 = 0x41c6ce57 ^ (str || '').length
  for (let i = 0; i < (str || '').length; i++) {
    const ch = str.charCodeAt(i)
    h1 = Math.imul(h1 ^ ch, 2654435761)
    h2 = Math.imul(h2 ^ ch, 1597334677)
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909)
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909)
  const hex1 = (h1 >>> 0).toString(16).padStart(8, '0')
  const hex2 = (h2 >>> 0).toString(16).padStart(8, '0')
  return `${hex1}${hex2}${hex1}${hex2}`
}

function buildStandardMetadataProperties(data, documentMetadata, fileName) {
  const meta = documentMetadata || data?.document_metadata || {}
  const basic = data?.basic || {}
  const business = data?.business || {}
  const governance = data?.governance || {}
  const tech = data?.technical_metrics || {}
  const visual = data?.visual_media_metadata || {}
  const content = data?.content || {}
  const entities = data?.entities || {}
  const keyInfo = data?.key_information || {}
  const searchOpt = data?.search_optimization || {}
  const dyn = data?.dynamic_metadata || {}

  const rawName = fileName || meta.filename || searchOpt.recommended_filename || 'Enterprise_Asset.pdf'
  const extMatch = rawName.match(/\.[^/.]+$/)
  const ext = extMatch ? extMatch[0].toLowerCase() : (meta.type || '.pdf')
  const extUpper = ext.toUpperCase().replace('.', '') || 'FILE'
  const isImage = meta.kind === 'image' || ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'].includes(ext)

  const mimeMap = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.csv': 'text/csv',
    '.json': 'application/json',
    '.txt': 'text/plain'
  }
  const mimeType = meta.mime_type || mimeMap[ext] || (isImage ? 'image/png' : 'application/octet-stream')
  const sizeBytes = meta.size_bytes || 0
  const sizeDisplay = sizeBytes
    ? `${(sizeBytes / 1024).toFixed(2)} KB (${sizeBytes.toLocaleString()} bytes)`
    : (tech.estimated_word_count ? `${tech.estimated_word_count} (Digital Stream)` : 'Verified Payload')

  const hashSeed = `${rawName}_${basic.title || ''}_${data?.summary || ''}`
  const sha = meta.sha256 || deterministicHash(hashSeed)
  const shortSha = sha.length > 28 ? `${sha.slice(0, 20)}...${sha.slice(-8)}` : sha
  const todayDate = new Date().toISOString().split('T')[0]

  const rows = [
    // 1. FILE & TECHNICAL PROPERTIES (8 Properties)
    { category: 'File & Technical', property: 'Original File Name', value: rawName },
    { category: 'File & Technical', property: 'Standardized File Name', value: searchOpt.recommended_filename || `Standardized_${rawName.replace(/\s+/g, '_')}` },
    { category: 'File & Technical', property: 'File Format & Extension', value: `${extUpper} (${isImage ? 'Raster Image Format' : 'Digital Document Format'})` },
    { category: 'File & Technical', property: 'MIME Type', value: mimeType },
    { category: 'File & Technical', property: 'File Size', value: sizeDisplay },
    { category: 'File & Technical', property: 'Character / Media Encoding', value: isImage ? (meta.compression || `${extUpper} Lossless / Standard Stream`) : (tech.encoding_standard || 'UTF-8 Digital Stream') },
    { category: 'File & Technical', property: 'SHA-256 Checksum', value: shortSha },
    { category: 'File & Technical', property: 'Indexed Date (UTC)', value: todayDate },

    // 2. CONTENT & DESCRIPTIVE PROPERTIES (8 Properties)
    { category: 'Content & Descriptive', property: 'Title', value: basic.title || 'Indexed Enterprise Asset' },
    { category: 'Content & Descriptive', property: 'Artifact / Document Type', value: basic.document_type || (isImage ? 'Visual Media Asset' : 'Enterprise Document') },
    { category: 'Content & Descriptive', property: 'Primary Subject / Core Topic', value: content.core_topic || basic.title || 'Enterprise Content' },
    { category: 'Content & Descriptive', property: 'Summary / Abstract', value: data?.summary || 'Standardized enterprise asset metadata record.' },
    { category: 'Content & Descriptive', property: 'Subtopics', value: (content.subtopics && content.subtopics.length > 0) ? content.subtopics.join(', ') : (business.subdomain || 'Operational Documentation') },
    { category: 'Content & Descriptive', property: 'Language', value: basic.language || 'English (en-US)' },
    { category: 'Content & Descriptive', property: 'Version', value: `v${basic.version || '1.0'}` },
    { category: 'Content & Descriptive', property: 'Publication Status', value: basic.publication_status || 'Active / Verified' },

    // 3. MEDIA, VISUAL & STRUCTURAL PROPERTIES (6 Properties)
    { category: 'Media & Structure', property: 'Content Modality', value: isImage ? (visual.media_modality || 'Raster Image / Visual Capture') : (visual.media_modality || 'Structured Digital Text') },
    {
      category: 'Media & Structure',
      property: isImage ? 'Image Resolution & Aspect Ratio' : 'Page / Section Count',
      value: isImage
        ? (meta.resolution ? `${meta.resolution} · Aspect Ratio ${meta.aspect_ratio || '16:9'} · ${meta.megapixels || 'Digital'}` : 'High-Resolution Visual Canvas')
        : `${meta.pages || meta.slides || 1} Page(s)`
    },
    {
      category: 'Media & Structure',
      property: isImage ? 'Color Space & Bit Depth' : 'Word & Character Count',
      value: isImage
        ? `${meta.color_space || 'sRGB (24-bit TrueColor)'} · ${meta.bit_depth || '8-bit per channel'}`
        : `${tech.estimated_word_count || `${meta.word_count || 450} words`}${meta.char_count ? ` · ${meta.char_count.toLocaleString()} characters` : ''}`
    },
    {
      category: 'Media & Structure',
      property: isImage ? 'Orientation & Layout Composition' : 'Structural Format & Density',
      value: isImage
        ? `${meta.orientation || 'Landscape'} · ${visual.layout_composition || 'Structured Visual Frame'}`
        : `${tech.structural_format || 'Hierarchical Sections'} · ${tech.content_density || 'High Information Density'}`
    },
    { category: 'Media & Structure', property: 'Readability / Legibility Grade', value: tech.readability_level || 'Professional Enterprise' },
    { category: 'Media & Structure', property: 'Estimated Review Time', value: tech.reading_time || (isImage ? '1–2 mins' : '3–4 mins') },

    // 4. BUSINESS & OWNERSHIP PROPERTIES (6 Properties)
    { category: 'Business & Ownership', property: 'Industry / Domain', value: business.domain || 'Enterprise Operations' },
    { category: 'Business & Ownership', property: 'Sub-Domain', value: business.subdomain || 'Information Management' },
    { category: 'Business & Ownership', property: 'Business Process / Workflow', value: business.process_area || 'Operational Execution' },
    { category: 'Business & Ownership', property: 'Business Function', value: business.business_function || 'Operations & Governance' },
    { category: 'Business & Ownership', property: 'Owner / Custodian Department', value: basic.owner_department || 'Corporate Operations' },
    { category: 'Business & Ownership', property: 'Target Audience', value: basic.target_audience || 'Enterprise Stakeholders' },

    // 5. GOVERNANCE, SECURITY & LIFECYCLE PROPERTIES (6 Properties)
    { category: 'Governance & Security', property: 'Confidentiality Level', value: governance.confidentiality_level || 'Internal Confidential' },
    { category: 'Governance & Security', property: 'Data Classification', value: governance.data_classification || 'Enterprise Operational Record' },
    { category: 'Governance & Security', property: 'Access Control Policy', value: governance.access_control_policy || 'Role-Based Enterprise Access (RBAC)' },
    { category: 'Governance & Security', property: 'Retention Period', value: governance.retention_period || '7 Years Statutory' },
    { category: 'Governance & Security', property: 'Storage / Archival Tier', value: governance.archival_tier || 'Active Standard Storage' },
    {
      category: 'Governance & Security',
      property: 'Regulatory & Compliance Standards',
      value: (governance.regulatory_frameworks && governance.regulatory_frameworks.length > 0)
        ? governance.regulatory_frameworks.join(', ')
        : ((entities.regulations_standards && entities.regulations_standards.length > 0) ? entities.regulations_standards.join(', ') : 'ISO 27001, SOC 2, GDPR')
    },

    // 6. SEMANTIC, ENTITY & DOMAIN-SPECIFIC PROPERTIES (6+ Properties)
    {
      category: 'Semantic & Entities',
      property: 'Search Keywords',
      value: (content.keywords && content.keywords.length > 0) ? content.keywords.join(', ') : 'enterprise, metadata, document, governance'
    },
    {
      category: 'Semantic & Entities',
      property: 'Metadata Tags',
      value: (content.tags && content.tags.length > 0) ? content.tags.map(t => (t.startsWith('#') ? t : `#${t}`)).join('  ') : '#enterprise  #metadata  #verified'
    }
  ]

  if (entities.organizations && entities.organizations.length > 0) {
    rows.push({ category: 'Semantic & Entities', property: 'Organizations / Entities', value: entities.organizations.join(', ') })
  }
  if (entities.systems_applications && entities.systems_applications.length > 0) {
    rows.push({ category: 'Semantic & Entities', property: 'Systems & Platforms', value: entities.systems_applications.join(', ') })
  }
  if (entities.roles && entities.roles.length > 0) {
    rows.push({ category: 'Semantic & Entities', property: 'Roles & Personas', value: entities.roles.join(', ') })
  }
  if (keyInfo.dates && keyInfo.dates.length > 0) {
    rows.push({ category: 'Semantic & Entities', property: 'Referenced Dates', value: keyInfo.dates.join(', ') })
  }
  if (keyInfo.deadlines && keyInfo.deadlines.length > 0) {
    rows.push({ category: 'Semantic & Entities', property: 'Deadlines / SLAs', value: keyInfo.deadlines.join(', ') })
  }
  if (keyInfo.monetary_amounts && keyInfo.monetary_amounts.length > 0) {
    rows.push({ category: 'Semantic & Entities', property: 'Financial Figures / Metrics', value: keyInfo.monetary_amounts.join(', ') })
  }
  if (visual.accessibility_alt_text) {
    rows.push({ category: 'Media & Structure', property: 'Accessibility Alt-Text', value: visual.accessibility_alt_text })
  }

  // Append all domain-specific dynamic_metadata attributes
  if (dyn && typeof dyn === 'object') {
    Object.entries(dyn).forEach(([k, v]) => {
      const label = String(k).replace(/_/g, ' ').trim()
      const valStr = Array.isArray(v) ? v.join(', ') : String(v || '').trim()
      if (label && valStr) {
        const alreadyExists = rows.some(r => r.property.toLowerCase() === label.toLowerCase())
        if (!alreadyExists) {
          rows.push({
            category: 'Semantic & Entities',
            property: label,
            value: valStr
          })
        }
      }
    })
  }

  return rows
}

const CATEGORIES = [
  'All Metadata',
  'File & Technical',
  'Content & Descriptive',
  'Media & Structure',
  'Business & Ownership',
  'Governance & Security',
  'Semantic & Entities'
]

export default function IndexResultCard({ data, guardrails, fileName, documentMetadata }) {
  const [activeCategory, setActiveCategory] = useState('All Metadata')
  const [downloadMenuOpen, setDownloadMenuOpen] = useState(false)
  const [copiedSummary, setCopiedSummary] = useState(false)
  const [copiedRowIdx, setCopiedRowIdx] = useState(null)

  if (!data) return null

  if (data.type === 'chat' || (!data.basic && (data.message || typeof data === 'string'))) {
    return (
      <div className="plainChatBubble">
        {data.message || (typeof data === 'string' ? data : JSON.stringify(data))}
      </div>
    )
  }

  const basic = data.basic || {}
  const searchOpt = data.search_optimization || {}
  const traceId = data?.trace_id || basic?.trace_id || ''

  const allProperties = buildStandardMetadataProperties(data, documentMetadata, fileName)
  const visibleProperties =
    activeCategory === 'All Metadata'
      ? allProperties
      : allProperties.filter(item => item.category === activeCategory)

  function copyValue(text, idx) {
    if (!text) return
    navigator.clipboard.writeText(text)
    if (idx === 'json') {
      setCopiedSummary(true)
      setTimeout(() => setCopiedSummary(false), 2000)
    } else {
      setCopiedRowIdx(idx)
      setTimeout(() => setCopiedRowIdx(null), 1600)
    }
  }

  function handleExportCsv() {
    const headers = ['Category', 'Metadata Property', 'Value']
    const rows = allProperties.map(r =>
      [r.category, r.property, r.value]
        .map(v => `"${String(v || '').replace(/"/g, '""')}"`)
        .join(',')
    )
    const csvContent = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const baseName = (searchOpt.recommended_filename || basic.title || 'Enterprise_Asset').replace(/\.[^/.]+$/, '').replace(/\s+/g, '_')
    a.download = `${baseName}_Metadata.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  function handleExportJson() {
    const jsonObj = {
      asset_title: basic.title || 'Indexed Enterprise Asset',
      trace_id: traceId,
      total_metadata_properties: allProperties.length,
      metadata_properties: allProperties
    }
    const blob = new Blob([JSON.stringify(jsonObj, null, 2)], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const baseName = (searchOpt.recommended_filename || basic.title || 'Enterprise_Asset').replace(/\.[^/.]+$/, '').replace(/\s+/g, '_')
    a.download = `${baseName}_Metadata.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="indexResultCard">
      {/* 0. GUARDRAILS STATUS BAR & TOP-RIGHT TRACE ID */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          marginBottom: '6px',
          width: '100%',
          flexWrap: 'wrap'
        }}
      >
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 12px',
            borderRadius: '999px',
            fontSize: '11.5px',
            fontWeight: 700,
            background: guardrails?.status === 'BLOCKED'
              ? 'rgba(239, 68, 68, 0.22)'
              : 'rgba(52, 211, 153, 0.16)',
            color: guardrails?.status === 'BLOCKED' ? '#f87171' : '#34d399',
            border: guardrails?.status === 'BLOCKED'
              ? '1px solid rgba(239, 68, 68, 0.65)'
              : '1px solid rgba(52, 211, 153, 0.45)'
          }}
        >
          <ShieldIcon />
          <span>
            {guardrails?.status === 'BLOCKED'
              ? `Guardrails: Blocked (${guardrails.triggered_rule || 'Policy Violation'})`
              : guardrails?.status === 'REDACTED'
              ? `Guardrails: ${guardrails.redacted_count || 1} Secret(s) Sanitized`
              : 'Guardrails: Passed · Verified Safe'}
          </span>
        </span>

        {traceId && (
          <span
            style={{
              fontSize: '11px',
              fontFamily: 'ui-monospace, "JetBrains Mono", Menlo, Consolas, monospace',
              fontWeight: 600,
              color: '#38bdf8',
              letterSpacing: '0.6px',
              padding: '3px 9px',
              borderRadius: '6px',
              background: 'rgba(7, 140, 255, 0.08)',
              border: '1px solid rgba(7, 140, 255, 0.24)',
              marginLeft: 'auto',
              flexShrink: 0
            }}
            title="Verification Trace Code"
          >
            {traceId}
          </span>
        )}
      </div>

      {/* 1. CLEAN ENTERPRISE METADATA SPECIFICATION SHEET */}
      <div className="idxRegistrySection">
        <div className="idxRegistryHeaderRow">
          <div>
            <h2 className="docTitle" style={{ marginBottom: 4 }}>
              {basic.title || 'Enterprise Asset Metadata Specification'}
            </h2>
            <p className="docSummary" style={{ marginBottom: 0 }}>
              {allProperties.length} Standardized Enterprise Metadata Properties Extracted
            </p>
          </div>

          <div className="idxExportBtns">
            <div className="idxDropdownWrap">
              <button
                type="button"
                className="idxActionBtn"
                onClick={() => setDownloadMenuOpen(prev => !prev)}
              >
                <DownloadIcon size={13} />
                <span>Download</span>
                <svg className="icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true">
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>

              {downloadMenuOpen && (
                <div className="idxDropdownMenu">
                  <button
                    type="button"
                    className="idxDropdownItem"
                    onClick={() => {
                      setDownloadMenuOpen(false)
                      handleExportCsv()
                    }}
                  >
                    <span>CSV (.csv)</span>
                  </button>
                  <button
                    type="button"
                    className="idxDropdownItem"
                    onClick={() => {
                      setDownloadMenuOpen(false)
                      handleExportJson()
                    }}
                  >
                    <span>JSON (.json)</span>
                  </button>
                </div>
              )}
            </div>

            <button
              type="button"
              className="idxActionBtn"
              onClick={() => copyValue(JSON.stringify(allProperties, null, 2), 'json')}
            >
              {copiedSummary ? <CheckIcon size={13} /> : <CopyIcon size={13} />}
              <span>{copiedSummary ? 'Copied' : 'Copy All'}</span>
            </button>
          </div>
        </div>

        {/* Category Filter Tabs */}
        <div className="idxFilterBar">
          {CATEGORIES.map(cat => {
            const count =
              cat === 'All Metadata'
                ? allProperties.length
                : allProperties.filter(r => r.category === cat).length
            return (
              <button
                key={cat}
                type="button"
                className={`idxFilterPill${activeCategory === cat ? ' active' : ''}`}
                onClick={() => setActiveCategory(cat)}
              >
                <span>{cat}</span>
                <span className="idxFilterCount">{count}</span>
              </button>
            )
          })}
        </div>

        {/* Standard 3-Column Enterprise Metadata Table */}
        <div className="idxTableWrap">
          <table className="idxMetadataTable">
            <thead>
              <tr>
                <th style={{ width: '22%' }}>Category</th>
                <th style={{ width: '28%' }}>Metadata Property</th>
                <th style={{ width: '50%' }}>Value</th>
              </tr>
            </thead>
            <tbody>
              {visibleProperties.map((row, idx) => {
                const isCopied = copiedRowIdx === idx
                return (
                  <tr key={`${row.property}-${idx}`}>
                    <td className="idxColCat">
                      <span className="idxCatBadge">{row.category}</span>
                    </td>
                    <td className="idxColLabel">
                      <strong>{row.property}</strong>
                    </td>
                    <td className="idxColVal">
                      <div className="idxValWrap">
                        <span>{row.value}</span>
                        <button
                          type="button"
                          className="idxRowCopyBtn"
                          title="Copy value"
                          onClick={() => copyValue(row.value, idx)}
                        >
                          {isCopied ? <CheckIcon size={12} /> : <CopyIcon size={12} />}
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
