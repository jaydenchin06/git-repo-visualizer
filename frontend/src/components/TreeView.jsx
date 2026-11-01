import { useMemo, useState } from 'react'

const FOLDER_ICON = (
  <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
    <path fill="currentColor" d="M1.5 3A1.5 1.5 0 0 1 3 1.5h3.4l1.6 2H13A1.5 1.5 0 0 1 14.5 5v7.5A1.5 1.5 0 0 1 13 14H3a1.5 1.5 0 0 1-1.5-1.5z" />
  </svg>
)

const FILE_ICON = (
  <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
    <path fill="none" stroke="currentColor" strokeWidth="1.4" d="M4 1.5h5.5L13 5v9.5H4zM9.5 1.5V5H13M6 8.5h5M6 11h5" />
  </svg>
)

// Short badge shown next to each node so you can tell types apart at a glance
const TYPE_BADGES = {
  folder: { label: FOLDER_ICON, title: 'Folder' },
  file: { label: FILE_ICON, title: 'File' },
  class: { label: 'C', title: 'Class' },
  function: { label: 'ƒ', title: 'Function' },
  method: { label: 'm', title: 'Method' },
}

export function TypeBadge({ type }) {
  const badge = TYPE_BADGES[type]
  return (
    <span className={`type-badge type-${type}`} title={badge.title} role="img" aria-label={badge.title}>
      {badge.label}
    </span>
  )
}

// Returns a copy of the tree with only the nodes whose name matches the search
// (plus the folders/classes above them), or null if nothing matches
function filterTree(node, query) {
  const children = node.children
    .map((child) => filterTree(child, query))
    .filter(Boolean)
  if (children.length > 0 || node.name.toLowerCase().includes(query)) {
    // Keep the original so selecting a node still shows all of its contents
    return { ...node, children, original: node.original ?? node }
  }
  return null
}

function TreeNode({ node, depth, selectedId, onSelect, searching, onlyChild }) {
  // Start with the top level open so you can see something right away, and also
  // anything that's alone in its folder (like the one file when you paste code)
  const [open, setOpen] = useState(depth < 1 || onlyChild)
  const hasChildren = node.children.length > 0
  const isOpen = searching || open

  return (
    <li role="treeitem" aria-expanded={hasChildren ? isOpen : undefined} aria-selected={selectedId === node.id}>
      <div className={selectedId === node.id ? 'tree-row selected' : 'tree-row'} style={{ paddingLeft: depth * 14 + 4 }}>
        {hasChildren ? (
          <button
            type="button"
            className="chevron"
            onClick={() => setOpen(!open)}
            disabled={searching}
            aria-label={isOpen ? `Collapse ${node.name}` : `Expand ${node.name}`}
          >
            {isOpen ? '▾' : '▸'}
          </button>
        ) : (
          <span className="chevron" aria-hidden="true" />
        )}
        <button
          type="button"
          className="tree-label"
          onClick={() => {
            onSelect(node.original ?? node)
            setOpen(true)
          }}
        >
          <TypeBadge type={node.type} />
          <span className="tree-name">{node.name}</span>
          {node.error && <span className="error-dot" title={node.error}>!</span>}
        </button>
      </div>

      {hasChildren && isOpen && (
        <ul role="group">
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              depth={depth + 1}
              selectedId={selectedId}
              onSelect={onSelect}
              searching={searching}
              onlyChild={node.children.length === 1}
            />
          ))}
        </ul>
      )}
    </li>
  )
}

export default function TreeView({ tree, selectedId, onSelect }) {
  const [search, setSearch] = useState('')
  const query = search.trim().toLowerCase()

  const visibleTree = useMemo(
    () => (query ? filterTree(tree, query) : tree),
    [tree, query],
  )

  return (
    <div className="tree-view">
      <input
        type="search"
        className="text-input tree-search"
        placeholder="Search files, classes, functions…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        aria-label="Search the tree"
      />
      {visibleTree ? (
        <ul className="tree" role="tree">
          <TreeNode
            node={visibleTree}
            depth={0}
            selectedId={selectedId}
            onSelect={onSelect}
            searching={Boolean(query)}
          />
        </ul>
      ) : (
        <p className="muted tree-empty">Nothing matches “{search}”.</p>
      )}
    </div>
  )
}
