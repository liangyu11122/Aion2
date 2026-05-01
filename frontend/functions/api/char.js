import { bnshiveQueryCharacter } from '../_shared/bnshive.js'

const TTL_SEC = 3600
const json = (obj, status = 200) => new Response(JSON.stringify(obj), {
  status, headers: { 'content-type': 'application/json; charset=utf-8' },
})

function decodeRepeated (s, rounds = 3) {
  let cur = s
  for (let i = 0; i < rounds; i++) {
    try {
      const dec = decodeURIComponent(cur)
      if (dec === cur) break
      cur = dec
    } catch { break }
  }
  return cur
}

export async function onRequestGet ({ request, env }) {
  const u = new URL(request.url)
  const serverId = u.searchParams.get('serverId')
  const characterIdRaw = u.searchParams.get('characterId')
  const refresh = u.searchParams.get('refresh') === '1'
  if (!serverId || !characterIdRaw) return json({ error: 'missing serverId/characterId' }, 400)
  const characterId = decodeRepeated(characterIdRaw)
  const cacheKey = `char:${serverId}:${characterId}`

  // KV cache lookup (CHAR_CACHE binding optional)
  if (env.CHAR_CACHE && !refresh) {
    const hit = await env.CHAR_CACHE.get(cacheKey, { type: 'json' })
    if (hit) {
      const age = Math.floor(Date.now() / 1000) - hit.fetchedAt
      if (age < TTL_SEC) {
        return json({ ...hit.data, cached: true, ageSeconds: age, source: hit.source })
      }
    }
  }

  // Fetch fresh from bnshive
  try {
    const [payload, err] = await bnshiveQueryCharacter(serverId, characterId)
    if (err) {
      // serve stale on failure if cache exists
      if (env.CHAR_CACHE) {
        const stale = await env.CHAR_CACHE.get(cacheKey, { type: 'json' })
        if (stale) {
          const age = Math.floor(Date.now() / 1000) - stale.fetchedAt
          return json({ ...stale.data, cached: true, stale: true, ageSeconds: age, source: stale.source, upstreamError: err.error })
        }
      }
      return json({ error: 'upstream', detail: err }, 502)
    }
    if (env.CHAR_CACHE) {
      await env.CHAR_CACHE.put(cacheKey, JSON.stringify({
        fetchedAt: Math.floor(Date.now() / 1000), source: 'bnshive', data: payload,
      }), { expirationTtl: TTL_SEC * 24 }) // keep up to 24h, served as stale after TTL
    }
    return json({ ...payload, cached: false, source: 'bnshive' })
  } catch (e) {
    return json({ error: String(e.message || e) }, 502)
  }
}
