<template>
  <h2>角色查询（台服 · NCSoft 官方资料）</h2>
  <p class="small">
    搜索：NC 官方 → 失败 fallback 到永恆蜂窩。详情：本地 SQLite 缓存层（TTL 1 小时）。
  </p>

  <div class="card" style="margin-bottom:14px">
    <div class="search-bar">
      <input v-model="qName" class="cell text" placeholder="输入角色名（例如：风雅哥哥 / 满地王八我壳最绿[希塔]）"
             @keydown.enter="run" />
      <select v-model="qServer">
        <option value="">全部伺服器</option>
        <option v-for="s in servers" :key="s.serverId" :value="s.serverId">
          {{ s.serverName }} ({{ s.serverShortName }} · {{ RACE_MAP[s.raceId] || '' }})
        </option>
      </select>
      <select v-model="qRace">
        <option value="">全部种族</option>
        <option value="1">天族</option>
        <option value="2">魔族</option>
      </select>
      <select v-model="qClass">
        <option value="">全部职业</option>
        <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.text }}</option>
      </select>
      <button class="btn" :disabled="busy" @click="run"
              style="background:var(--gold);color:#111;border-color:var(--gold);font-weight:600">
        {{ busy ? '…' : '搜索' }}
      </button>
    </div>
    <p class="small" style="margin:8px 0 0">支持简/繁中文，按 Enter 搜索。带 [服] 后缀会自动识别伺服器。</p>
  </div>

  <div class="small status" :class="{ err: statusErr }">{{ status }}</div>

  <div class="results">
    <div v-for="c in results" :key="c.characterId + ':' + c.serverId" class="card"
         :style="{ borderLeft: '3px solid ' + (CLASS_COLOR[c.pcId] || 'var(--gold)') }">
      <div class="row-top">
        <img :src="profileImg(c.profileImageUrl)" @error="e => e.target.style.opacity = .2" />
        <div style="flex:1;min-width:0">
          <div class="name">{{ stripTag(c.name) }}</div>
          <div class="small pills">
            <span class="pill" :style="{ color: CLASS_COLOR[c.pcId], borderColor: CLASS_COLOR[c.pcId] }">
              {{ CLASS_MAP[c.pcId] || ('职业' + c.pcId) }}
            </span>
            <span class="pill">Lv.{{ c.level }}</span>
            <span class="pill">{{ RACE_MAP[c.race] || '' }}</span>
            <span class="pill">{{ c.serverName }}</span>
          </div>
          <div class="actions">
            <a class="btn"
               :href="`https://tw.ncsoft.com/aion2/characters/${c.serverId}/${encodeURIComponent(c.characterId)}`"
               target="_blank">官方资料 →</a>
            <button class="btn" @click="loadDetail(c)" :disabled="detail[key(c)]?.loading">
              {{ detail[key(c)]?.payload ? '✓ 已加载' : '查看详情' }}
            </button>
          </div>
        </div>
      </div>
      <CharacterDetail v-if="detail[key(c)]" :row="c"
                       :payload="detail[key(c)].payload"
                       :loading="detail[key(c)].loading"
                       :error="detail[key(c)].error"
                       @refresh="loadDetail(c, true)" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api, profileImg } from '../api.js'
import CharacterDetail from '../components/CharacterDetail.vue'

const CLASS_MAP = { 2: '劍星', 3: '守護星', 5: '殺星', 4: '弓星', 7: '魔道星', 6: '精靈星', 8: '治癒星', 9: '護法星' }
const RACE_MAP = { 1: '天族', 2: '魔族' }
const CLASS_COLOR = { 2: '#f59e0b', 3: '#fbbf24', 5: '#a78bfa', 4: '#34d399', 7: '#60a5fa', 6: '#22d3ee', 8: '#f472b6', 9: '#facc15' }

const S2T = {
  '凯': '凱', '萨': '薩', '杰': '傑', '尔': '爾', '纳': '納', '达': '達', '弥': '彌', '验': '驗',
  '丽': '麗', '龙': '龍', '凤': '鳳', '门': '門', '馆': '館', '辽': '遼', '远': '遠', '点': '點',
  '后': '後', '间': '間', '问': '問', '变': '變', '边': '邊', '阶': '階', '随': '隨', '里': '裡',
  '为': '為', '们': '們',
}
const toTrad = s => [...(s || '')].map(c => S2T[c] || c).join('')

const qName = ref('')
const qServer = ref('')
const qRace = ref('')
const qClass = ref('')
const status = ref('')
const statusErr = ref(false)
const busy = ref(false)
const servers = ref([])
const classes = ref([])
const results = ref([])
const detail = reactive({})

onMounted(async () => {
  try {
    const sd = await api.getServers()
    servers.value = sd.serverList || []
  } catch (e) { console.warn('servers failed', e) }
  try {
    const cd = await api.getClasses()
    classes.value = cd.classList || []
  } catch (e) { console.warn('classes failed', e) }
})

const key = c => `${c.serverId}:${c.characterId}`
const stripTag = s => (s || '').replace(/<[^>]+>/g, '')

async function run () {
  let name = qName.value.trim()
  let sid = qServer.value
  if (!name) { status.value = '请输入角色名'; statusErr.value = true; return }
  statusErr.value = false

  // smart parse [服] suffix
  const m = name.match(/^(.+?)\s*[\[\u3010\s]([^\]\u3011\s]{1,6})[\]\u3011]?\s*$/)
  if (m) {
    const tail = m[2].trim(), tailT = toTrad(tail)
    const found = servers.value.find(s =>
      s.serverShortName === tailT || s.serverShortName === tail ||
      s.serverName.startsWith(tailT) || s.serverName.startsWith(tail) ||
      toTrad(s.serverShortName) === tailT)
    if (found) {
      name = m[1].trim(); sid = String(found.serverId)
      qServer.value = sid; qName.value = name
      status.value = `✓ 识别 [${tail}] -> ${found.serverName}。`
    }
  }

  busy.value = true
  status.value += (status.value ? ' ' : '') + '搜索中...'
  try {
    const params = { keyword: name, page: '1', size: '40' }
    if (sid) params.serverId = sid
    if (qRace.value) params.race = qRace.value
    if (qClass.value) params.pcId = qClass.value
    const data = await api.searchChars(params)
    const list = data.list || []
    const srcLabel = data.source === 'bnshive' ? ' (来源：永恆蜂窩)'
                    : data.source === 'nc' ? ' (来源：NC官方)' : ''
    status.value = `找到 ${data.total ?? list.length} 个角色${srcLabel}`
    results.value = list
    Object.keys(detail).forEach(k => delete detail[k])
  } catch (e) {
    status.value = '搜索失败：' + (e.message || e)
    statusErr.value = true
  } finally {
    busy.value = false
  }
}

async function loadDetail (c, refresh = false) {
  const k = key(c)
  if (!detail[k]) detail[k] = { loading: false, payload: null, error: null }
  detail[k].loading = true
  detail[k].error = null
  try {
    detail[k].payload = await api.getCharacter(c.serverId, c.characterId, refresh)
  } catch (e) {
    detail[k].error = e.message || String(e)
  } finally {
    detail[k].loading = false
  }
}
</script>

<style scoped>
.search-bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.search-bar input{flex:1 1 240px;border:1px solid var(--border);padding:10px 12px;font-size:14px}
.search-bar select{background:var(--panel2);color:var(--text);border:1px solid var(--border);padding:8px 10px;border-radius:6px}
.status{margin:6px 0 12px;color:var(--muted)}
.status.err{color:var(--bad)}
.results{display:flex;flex-direction:column;gap:10px}
.row-top{display:flex;gap:12px;align-items:center}
.row-top img{width:64px;height:64px;border-radius:8px;background:#000;object-fit:cover;border:1px solid var(--border);flex-shrink:0}
.name{font-size:15px;font-weight:600;color:var(--gold2);margin-bottom:4px}
.pills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}
.actions{display:flex;gap:6px;flex-wrap:wrap}
</style>
