// Transparent passthrough to NCSoft TW. Path captured by [[path]] is the rest after /proxy/ncsoft/
import { ncGetRaw } from '../../_shared/nc.js'

export async function onRequestGet ({ request, params }) {
  const u = new URL(request.url)
  const tail = Array.isArray(params.path) ? params.path.join('/') : (params.path || '')
  const upstreamPath = '/' + tail + (u.search || '')
  try {
    const { status, contentType, body } = await ncGetRaw(upstreamPath)
    return new Response(body, { status, headers: { 'content-type': contentType, 'cache-control': 'public, max-age=300' } })
  } catch (e) {
    return new Response('proxy error: ' + (e.message || e), { status: 502 })
  }
}
