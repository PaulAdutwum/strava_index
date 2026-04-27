export type LargestIndex = {
  index: string
  size_gb: number
  shards: number
}

export type ShardCountRow = {
  index: string
  shards: number
  size_gb: number
}

export type OffenderRow = {
  index: string
  size_gb: number
  shards: number
  ratio: number
  recommended_shards: number
  is_offender: boolean
}

export type ApiResponse<T> = {
  data: T
  warning?: string
}

const API_BASE = import.meta.env.VITE_API_BASE ?? ""

function buildPath(path: string, debug: boolean) {
  return `${API_BASE}${path}${debug ? "?debug=true" : ""}`
}

async function fetchData<T>(path: string, debug: boolean): Promise<ApiResponse<T>> {
  const response = await fetch(buildPath(path, debug))
  if (!response.ok) {
    const body = await response.text()
    throw new Error(body || response.statusText)
  }
  const payload = await response.json()
  return payload as ApiResponse<T>
}

export const fetchLargestIndexes = (debug: boolean) =>
  fetchData<LargestIndex[]>("/api/largest", debug)

export const fetchShardCounts = (debug: boolean) =>
  fetchData<ShardCountRow[]>("/api/shards", debug)

export const fetchOffenders = (debug: boolean) =>
  fetchData<OffenderRow[]>("/api/offenders", debug)
