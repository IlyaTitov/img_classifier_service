import { useCallback, useEffect, useState } from "react";
import { getArchive, originalImageUrl, processedImageUrl } from "../api";
import { useAuth } from "../context/AuthContext";
import type { ArchiveItem, SortBy, SortOrder } from "../types";
import "./ArchivePage.css";

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatFileSize(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}

export default function ArchivePage() {
  const { token } = useAuth();
  const [items, setItems] = useState<ArchiveItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortBy, setSortBy] = useState<SortBy>("created_at");
  const [order, setOrder] = useState<SortOrder>("desc");
  const [expanded, setExpanded] = useState<number | null>(null);

  const fetchItems = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getArchive(token, {
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        sort_by: sortBy,
        order,
      });
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, [token, dateFrom, dateTo, sortBy, order]);

  useEffect(() => {
    void fetchItems();
  }, [fetchItems]);

  function toggleExpand(id: number) {
    setExpanded((prev) => (prev === id ? null : id));
  }

  return (
    <div className="archive-page">
      <h1 className="page-title">Архив фотографий</h1>

      <section className="filters">
        <div className="filter-row">
          <label className="filter-field">
            <span>С даты</span>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </label>
          <label className="filter-field">
            <span>По дату</span>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </label>
          <label className="filter-field">
            <span>Сортировка</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortBy)}
            >
              <option value="created_at">Время загрузки</option>
              <option value="detection_count">Кол-во объектов</option>
            </select>
          </label>
          <label className="filter-field">
            <span>Порядок</span>
            <select
              value={order}
              onChange={(e) => setOrder(e.target.value as SortOrder)}
            >
              <option value="desc">По убыванию</option>
              <option value="asc">По возрастанию</option>
            </select>
          </label>
          <button
            type="button"
            className="btn-clear"
            onClick={() => {
              setDateFrom("");
              setDateTo("");
            }}
          >
            Сбросить даты
          </button>
        </div>
      </section>

      {loading && <p className="arch-status">Загрузка…</p>}
      {error && <p className="arch-status error">{error}</p>}
      {!loading && !error && items.length === 0 && (
        <p className="arch-status">Нет изображений по заданным критериям.</p>
      )}

      <ul className="archive-list">
        {items.map((item) => (
          <li key={item.id} className="archive-card">
            <div
              className="archive-card-header"
              onClick={() => toggleExpand(item.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && toggleExpand(item.id)}
            >
              <div className="card-thumb">
                {item.processing_complete && item.processed_filename ? (
                  <img
                    src={processedImageUrl(item.processed_filename)}
                    alt={item.name}
                    className="thumb-img"
                    loading="lazy"
                  />
                ) : item.original_filename ? (
                  <img
                    src={originalImageUrl(item.original_filename)}
                    alt={item.name}
                    className="thumb-img"
                    loading="lazy"
                  />
                ) : (
                  <div className="thumb-placeholder">?</div>
                )}
              </div>
              <div className="card-info">
                <span className="card-name" title={item.name}>
                  {item.name}
                </span>
                <span className="card-date">
                  {formatDate(item.created_at)}
                  <span className="file-size-separator"> • </span>
                  {formatFileSize(item.file_size)} {/* Вывод размера */}
                </span>
                <span
                  className={`card-status ${item.processing_complete ? "done" : "pending"}`}
                >
                  {item.processing_complete ? "Обработано" : "В очереди…"}
                </span>
              </div>
              <div className="card-meta">
                <span className="det-badge">
                  {item.detection_count} объектов
                </span>
                <span className="expand-icon">
                  {expanded === item.id ? "▲" : "▼"}
                </span>
              </div>
            </div>

            {expanded === item.id && (
              <div className="archive-card-body">
                <div className="archive-images">
                  <div className="arch-img-block">
                    <p className="arch-img-label">Оригинал</p>
                    <img
                      src={originalImageUrl(item.original_filename)}
                      alt="Оригинал"
                      className="arch-img"
                    />
                  </div>
                  {item.processing_complete && item.processed_filename && (
                    <div className="arch-img-block">
                      <p className="arch-img-label">После обработки</p>
                      <img
                        src={processedImageUrl(item.processed_filename)}
                        alt="Обработанное"
                        className="arch-img"
                      />
                    </div>
                  )}
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
