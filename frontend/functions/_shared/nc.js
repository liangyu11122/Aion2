// NC TW Aion 2 official API client (edge runtime)
const BASE = 'https://tw.ncsoft.com/aion2'
const HEADERS = {
  'User-Agent': 'Mozilla/5.0',
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-TW,zh;q=0.9',
  'Referer': 'https://tw.ncsoft.com/aion2/',
}

export async function ncGetJson (path, params) {
  const url = new URL(BASE + path)
  if (params) for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v)
  }
  const r = await fetch(url, { headers: HEADERS })
  if (!r.ok) throw new Error('NC ' + r.status + ' ' + (await r.text()).slice(0, 200))
  return r.json()
}

export async function ncGetRaw (path) {
  const r = await fetch(BASE + (path.startsWith('/') ? path : '/' + path), { headers: HEADERS })
  return { status: r.status, contentType: r.headers.get('content-type') || 'application/octet-stream', body: await r.arrayBuffer() }
}

export function ncSearch ({ keyword, serverId, race, pcId, page = 1, size = 40 }) {
  return ncGetJson('/api/character/search', { keyword, serverId, race, pcId, page, size })
}
