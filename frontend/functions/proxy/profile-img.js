import { bnshiveProfileImageRaw } from '../_shared/bnshive.js'

export async function onRequestGet ({ request }) {
  const u = new URL(request.url)
  try {
    const { status, contentType, body } = await bnshiveProfileImageRaw(u.search)
    return new Response(body, { status, headers: { 'content-type': contentType, 'cache-control': 'public, max-age=86400' } })
  } catch (e) {
    return new Response('img proxy error: ' + (e.message || e), { status: 502 })
  }
}
