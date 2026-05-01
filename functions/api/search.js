const json = (obj, status = 200) => new Response(JSON.stringify(obj), {
  status, headers: { 'content-type': 'application/json; charset=utf-8' },
})
import { ncSearch } from '../_shared/nc.js'
import { bnshiveSearch } from '../_shared/bnshive.js'
import { normaliseBnshive } from '../_shared/normalise.js'

export async function onRequestGet ({ request }) {
  const u = new URL(request.url)
  const keyword = u.searchParams.get('keyword') || ''
  if (!keyword.trim()) return json({ error: 'missing keyword' }, 400)
  const params = {
    keyword: keyword.trim(),
    serverId: u.searchParams.get('serverId') || undefined,
    race: u.searchParams.get('race') || undefined,
    pcId: u.searchParams.get('pcId') || undefined,
    page: u.searchParams.get('page') || '1',
    size: u.searchParams.get('size') || '40',
  }

  let ncErr = null
  try {
    const data = await ncSearch(params)
    const list = data?.list || []
    if (list.length) {
      const total = data?.pagination?.total ?? list.length
      return json({ source: 'nc', list, total })
    }
    ncErr = 'empty'
  } catch (e) { ncErr = String(e.message || e) }

  // fallback bnshive
  try {
    const bn = await bnshiveSearch(params)
    const raw = bn?.results || []
    const list = normaliseBnshive(raw, params.pcId)
    return json({ source: 'bnshive', list, total: bn?.total ?? list.length, ncError: ncErr })
  } catch (e) {
    return json({ source: 'none', list: [], total: 0, ncError: ncErr, bnshiveError: String(e.message || e) }, 502)
  }
}
