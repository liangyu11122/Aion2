// Map bnshive search hit shape -> NC-shaped row used by frontend
export function normaliseBnshive (results, pcIdFilter) {
  if (!Array.isArray(results)) return []
  const out = []
  for (const r of results) {
    if (pcIdFilter && r.pcId && String(r.pcId) !== String(pcIdFilter)) continue
    let prof = r.profileImageUrl || ''
    // Strip absolute prefix so the SPA can hit /proxy/profile-img
    if (prof.startsWith('http') && prof.includes('/game_profile_images/')) {
      prof = '/' + prof.split('/').slice(3).join('/')
    }
    out.push({
      name: r.characterName || '',
      characterId: r.characterId,
      serverId: r.serverId,
      serverName: r.serverName || '',
      level: r.characterLevel,
      race: r.raceId,
      pcId: r.pcId,
      profileImageUrl: prof,
    })
  }
  return out
}
