// 永恆蜂窩 (bnshive) Aion 2 backend client (edge runtime)
const API = 'https://aion-api.bnshive.com'
const PROFILE_IMG = 'https://aion-profile-img.bnshive.com'
const HEADERS = {
  'User-Agent': 'Mozilla/5.0',
  'Accept': 'application/json',
  'Accept-Language': 'zh-TW,zh;q=0.9',
  'Origin': 'https://aion2.bnshive.com',
  'Referer': 'https://aion2.bnshive.com/',
  'Content-Type': 'application/json',
}

async function bj (method, path, params, body) {
  const url = new URL(API + path)
  if (params) for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v)
  }
  const init = { method, headers: HEADERS }
  if (body !== undefined) init.body = JSON.stringify(body)
  const r = await fetch(url, init)
  const text = await r.text()
  if (!r.ok) throw new Error('bnshive ' + r.status + ' ' + text.slice(0, 200))
  try { return JSON.parse(text) } catch { return { raw: text } }
}

export async function bnshiveSearch ({ keyword, serverId, race, pcId, page = 1, size = 40 }) {
  // bnshive uses POST search
  return bj('POST', '/character/search', null, {
    keyword, serverId: serverId ? Number(serverId) : null,
    raceId: race ? Number(race) : null, pcId: pcId ? Number(pcId) : null,
    page: Number(page), size: Number(size),
  })
}

export async function bnshiveQueryCharacter (serverId, characterId, maxWaitMs = 25000) {
  const start = Date.now()
  let job = await bj('GET', '/character/query', { serverId, characterId })
  if (job?.status === 'done' && job.queryResult?.data) return [job, null]
  const jobId = job?.jobId
  if (!jobId) return [null, { error: 'no jobId', payload: job }]
  while (Date.now() - start < maxWaitMs) {
    await new Promise(r => setTimeout(r, 1000))
    const s = await bj('GET', '/character/query/status', { jobId })
    if (s?.status === 'done' && s.queryResult?.data) return [s, null]
    if (s?.status === 'failed') return [null, { error: 'job failed', payload: s }]
  }
  return [null, { error: 'timeout', payload: { jobId } }]
}

export async function bnshiveProfileImageRaw (queryString) {
  // queryString already starts with ?
  const r = await fetch(PROFILE_IMG + '/character/profileImage' + (queryString || ''), { headers: HEADERS })
  return { status: r.status, contentType: r.headers.get('content-type') || 'image/png', body: await r.arrayBuffer() }
}
