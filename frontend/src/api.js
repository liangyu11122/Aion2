/** Tiny fetch wrapper so views don't import fetch directly. */
async function http(url) {
  const r = await fetch(url)
  const text = await r.text()
  let json
  try { json = JSON.parse(text) } catch { json = { error: 'parse', body: text } }
  if (!r.ok) {
    const err = new Error(json.error || ('HTTP ' + r.status))
    err.status = r.status
    err.body = json
    throw err
  }
  return json
}

export const api = {
  searchChars: (params) => http('/api/search?' + new URLSearchParams(params)),
  getCharacter: (serverId, characterId, refresh = false) =>
    http(`/api/char?serverId=${serverId}&characterId=${encodeURIComponent(characterId)}` + (refresh ? '&refresh=1' : '')),
  // Server/class metadata still comes from the NC proxy
  getServers: () => http('/proxy/ncsoft/api/gameinfo/servers'),
  getClasses: () => http('/proxy/ncsoft/api/gameinfo/classes'),
}

export function profileImg(rel) {
  if (!rel) return ''
  const qs = rel.split('?')[1] || ''
  return '/proxy/profile-img?' + qs
}
