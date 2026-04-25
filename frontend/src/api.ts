import type { ArchiveItem, ImageDetail, SortBy, SortOrder, TokenResponse } from './types'

const BASE = '/v1'

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` }
}

async function checkResponse(res: Response): Promise<void> {
  if (!res.ok) {
    const text = await res.text()
    let detail = text
    try {
      const j = JSON.parse(text) as { detail?: unknown }
      if (typeof j.detail === 'string') detail = j.detail
      else if (j.detail != null) detail = JSON.stringify(j.detail)
    } catch {
      /* ignore */
    }
    throw new Error(detail || res.statusText)
  }
}

export async function login(loginVal: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login: loginVal, password }),
  })
  await checkResponse(res)
  return res.json() as Promise<TokenResponse>
}

export async function register(loginVal: string, password: string): Promise<void> {
  const res = await fetch(`${BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login: loginVal, password }),
  })
  await checkResponse(res)
}

export async function uploadImage(file: File, token: string): Promise<ImageDetail> {
  const body = new FormData()
  body.append('file', file)
  const res = await fetch(`${BASE}/image/upload`, {
    method: 'POST',
    headers: authHeaders(token),
    body,
  })
  await checkResponse(res)
  return res.json() as Promise<ImageDetail>
}

export async function getImage(imageId: number, token: string): Promise<ImageDetail> {
  const res = await fetch(`${BASE}/image/${imageId}`, {
    headers: authHeaders(token),
  })
  await checkResponse(res)
  return res.json() as Promise<ImageDetail>
}

export async function getArchive(
  token: string,
  params: {
    date_from?: string
    date_to?: string
    sort_by?: SortBy
    order?: SortOrder
  } = {},
): Promise<ArchiveItem[]> {
  const q = new URLSearchParams()
  if (params.date_from) q.set('date_from', params.date_from)
  if (params.date_to) q.set('date_to', params.date_to)
  if (params.sort_by) q.set('sort_by', params.sort_by)
  if (params.order) q.set('order', params.order)
  const res = await fetch(`${BASE}/image/?${q.toString()}`, {
    headers: authHeaders(token),
  })
  await checkResponse(res)
  return res.json() as Promise<ArchiveItem[]>
}

export function processedImageUrl(filename: string): string {
  return `/uploads/${filename}`
}

export function originalImageUrl(filename: string): string {
  return `/uploads/${filename}`
}
