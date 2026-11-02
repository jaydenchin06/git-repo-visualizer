export const DEFAULT_WIDTH = 300
const MIN_WIDTH = 200
const MAX_WIDTH = 600

export function clampWidth(width) {
  return Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, width))
}

// The bar between the tree and the details panel. Drag it (or use the arrow keys)
// to make the tree wider or narrower, double-click to reset it
export default function ResizeHandle({ width, onChange }) {
  function handlePointerDown(event) {
    event.preventDefault()
    const startX = event.clientX
    const startWidth = width

    function handleMove(moveEvent) {
      onChange(clampWidth(startWidth + moveEvent.clientX - startX))
    }
    function handleUp() {
      window.removeEventListener('pointermove', handleMove)
      window.removeEventListener('pointerup', handleUp)
      document.body.classList.remove('resizing')
    }

    window.addEventListener('pointermove', handleMove)
    window.addEventListener('pointerup', handleUp)
    // Keeps the resize cursor and stops text getting selected while dragging
    document.body.classList.add('resizing')
  }

  function handleKeyDown(event) {
    if (event.key === 'ArrowLeft') {
      onChange(clampWidth(width - 20))
    } else if (event.key === 'ArrowRight') {
      onChange(clampWidth(width + 20))
    }
  }

  return (
    <div
      className="resize-handle"
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize the tree"
      aria-valuenow={width}
      aria-valuemin={MIN_WIDTH}
      aria-valuemax={MAX_WIDTH}
      tabIndex={0}
      onPointerDown={handlePointerDown}
      onKeyDown={handleKeyDown}
      onDoubleClick={() => onChange(DEFAULT_WIDTH)}
      title="Drag to resize, double-click to reset"
    />
  )
}
