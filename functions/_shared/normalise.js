// Map bnshive search hit shape -> NC-shaped row used by frontend
export function normaliseBnshive (results, pcIdFilter) {
  if (!Array.isArray(results)) return []
  let arr = results.map(r => ({
    name: r.characterName || r.name || '',
    characterId: r.characterId || r.charId || '',
    serverId: r.serverId,
    serverName: r.serverName || '',
    level: r.characterLevel ?? r.level ?? 0,
    race: r.raceId ?? r.race ?? 0,
    pcId: r.pcId ?? r.classId ?? 0,
    profileImageUrl: r.profileImageUrl || r.profileImage || '',
  }))
  if (pcIdFilter) arr = arr.filter(x => String(x.pcId) === String(pcIdFilter))
  return arr
}
