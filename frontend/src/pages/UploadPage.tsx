import { useCallback, useRef, useState } from 'react'
import { getImage, originalImageUrl, processedImageUrl, uploadImage } from '../api'
import { useAuth } from '../context/AuthContext'
import type { ImageDetail } from '../types'
import './UploadPage.css'

type Phase =
  | { kind: 'idle' }
  | { kind: 'uploading' }
  | { kind: 'processing'; data: ImageDetail; previewUrl: string }
  | { kind: 'done'; data: ImageDetail; previewUrl: string }
  | { kind: 'error'; message: string; previewUrl: string | null }

const POLL_MS = 1500
const TIMEOUT_MS = 5 * 60 * 1000

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms))
}

function pct(v: number) {
  return `${(v * 100).toFixed(1)} %`
}

export default function UploadPage() {
  const { token } = useAuth()
  const [phase, setPhase] = useState<Phase>({ kind: 'idle' })
  const inputRef = useRef<HTMLInputElement>(null)
  const previewRef = useRef<string | null>(null)
  const [dragOver, setDragOver] = useState(false)

  const revokePreview = useCallback(() => {
    if (previewRef.current) {
      URL.revokeObjectURL(previewRef.current)
      previewRef.current = null
    }
  }, [])

  const processFile = useCallback(
    async (file: File) => {
      if (!token) return
      revokePreview()
      const previewUrl = URL.createObjectURL(file)
      previewRef.current = previewUrl

      setPhase({ kind: 'uploading' })
      try {
        const created = await uploadImage(file, token)
        setPhase({ kind: 'processing', data: created, previewUrl })

        if (created.processing_complete) {
          setPhase({ kind: 'done', data: created, previewUrl })
          return
        }

        const deadline = Date.now() + TIMEOUT_MS
        let last = created
        while (Date.now() < deadline) {
          await sleep(POLL_MS)
          last = await getImage(created.id, token)
          setPhase({ kind: 'processing', data: last, previewUrl })
          if (last.processing_complete) {
            setPhase({ kind: 'done', data: last, previewUrl })
            return
          }
        }
        setPhase({
          kind: 'error',
          message:
            'Превышено время ожидания. Убедитесь, что Celery-воркер запущен.',
          previewUrl,
        })
      } catch (e) {
        const message = e instanceof Error ? e.message : String(e)
        setPhase({ kind: 'error', message, previewUrl })
      }
    },
    [token, revokePreview],
  )

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) void processFile(file)
    e.target.value = ''
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files?.[0]
    if (file && file.type.startsWith('image/')) void processFile(file)
  }

  const busy = phase.kind === 'uploading' || phase.kind === 'processing'

  return (
    <div className="upload-page">
      <h1 className="page-title">Загрузить изображение</h1>

      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''} ${busy ? 'disabled' : ''}`}
        onClick={() => !busy && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); if (!busy) setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && !busy && inputRef.current?.click()}
        aria-label="Зона загрузки"
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="sr-only"
          disabled={busy}
          onChange={onInputChange}
        />
        <div className="drop-icon">⬆</div>
        <p className="drop-label">
          {busy ? 'Обработка…' : 'Нажмите или перетащите файл сюда'}
        </p>
        <p className="drop-hint">PNG, JPG, WEBP</p>
      </div>

      {phase.kind === 'uploading' && (
        <p className="status-msg">Загрузка файла на сервер…</p>
      )}
      {phase.kind === 'processing' && (
        <p className="status-msg">
          Обработка YOLO… найдено объектов: {phase.data.detections.length}
        </p>
      )}
      {phase.kind === 'error' && (
        <p className="status-msg error" role="alert">
          {phase.message}
        </p>
      )}

      {(phase.kind === 'processing' ||
        phase.kind === 'done' ||
        phase.kind === 'error') &&
        phase.previewUrl != null && (
          <section className="result-section">
            <div className="images-grid">
              <div className="img-block">
                <h3>Оригинал</h3>
                <img
                  src={
                    phase.kind === 'done' && phase.data.original_filename
                      ? originalImageUrl(phase.data.original_filename)
                      : phase.previewUrl
                  }
                  alt="Оригинал"
                  className="result-img"
                />
              </div>

              {phase.kind === 'done' && phase.data.processed_filename && (
                <div className="img-block">
                  <h3>Результат обработки</h3>
                  <img
                    src={processedImageUrl(phase.data.processed_filename)}
                    alt="Обработанное изображение"
                    className="result-img"
                  />
                </div>
              )}

              {phase.kind === 'processing' && (
                <div className="img-block placeholder">
                  <h3>Результат обработки</h3>
                  <div className="processing-placeholder">
                    <span className="spinner" aria-label="Загрузка" />
                    <p>Обрабатывается…</p>
                  </div>
                </div>
              )}
            </div>

            {phase.kind === 'done' && phase.data.detections.length > 0 && (
              <div className="detections">
                <h3>Обнаруженные объекты ({phase.data.detections.length})</h3>
                <ul className="detection-list">
                  {phase.data.detections.map((d) => (
                    <li key={d.id} className="detection-card">
                      <span className="det-label">{d.label}</span>
                      <span className="det-conf">{pct(d.confidence)}</span>
                      <span className="det-bbox">
                        [{d.x_min.toFixed(1)}, {d.y_min.toFixed(1)}] —{' '}
                        [{d.x_max.toFixed(1)}, {d.y_max.toFixed(1)}]
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {phase.kind === 'done' && phase.data.detections.length === 0 && (
              <p className="no-detections">Объекты не обнаружены.</p>
            )}
          </section>
        )}

      {phase.kind !== 'idle' && (
        <button
          type="button"
          className="btn-reset"
          onClick={() => {
            revokePreview()
            setPhase({ kind: 'idle' })
          }}
        >
          Загрузить другое фото
        </button>
      )}
    </div>
  )
}
