// 永恆蜂窩 (bnshive) Aion 2 backend client. Mirrors backend/services/bnshive_client.py
const API = 'https://aion-api.bnshive.com'
const PROFILE_IMG = 'https://profileimg.plaync.com'
const HEADERS = {
  'User-Agent': 'Mozilla/5.0',
  'Accept': 'application/json',
  'Accept-Language': 'zh-TW,zh;q=0.9',
  'Origin': 'https://aion2.bnshive.com',
  'Referer': 'https://aion2.bnshive.com/',
}

async function bGet (path, params) {
  const url = new URL(API + path)
  if (params) for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v)
  }
  const r = await fetch(url, { headers: HEADERS })
  const text = await r.text()
  if (!r.ok) throw new Error('bnshive ' + r.status + ' ' + text.slice(0, 200))
  try { return JSON.parse(text) } catch { return {} }
}

export function bnshiveSearch ({ keyword, serverId, race, page = 1, size = 40 }) {
  return bGet('/character/search', { keyword, serverId, race, page, size })
}

export async function bnshiveQueryCharacter (serverId, characterId, maxWaitMs = 25000) {
  let init
  try {
    init = await bGet('/character/query', { serverId, characterId })
  } catch (e) { return [null, { error: 'bnshive_query_failed', detail: String(e.message || e) }] }
  const jobId = init?.jobId || `fetch:${serverId}:${characterId}`
  const start = Date.now()
  let last = init
  while (Date.now() - start < maxWaitMs) {
    if (last?.queryResult?.data) return [last, null]
    await new Promise(r => setTimeout(r, 1000))
    try { last = await bGet('/character/query/status', { jobId }) }
    catch (e) { return [null, { error: 'bnshive_poll_failed', detail: String(e.message || e) }] }
  }
  if (last?.queryResult?.data) return [last, null]
  return [null, { error: 'bnshive_timeout', last }]
}

export async function bnshiveProfileImageRaw (queryString) {
  const url = PROFILE_IMG + '/game_profile_images/aion2_tw/images' + (queryString || '')
  const r = await fetch(url, { headers: HEADERS })
  return { status: r.status, contentType: r.headers.get('content-type') || 'image/png', body: await r.arrayBuffer() }
}
