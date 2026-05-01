<template>
  <div class="detail-panel">
    <div v-if="loading" class="small" style="color:var(--muted)">
      正在向本地缓存请求…（首次需 3-15 秒）
    </div>
    <div v-else-if="error" :style="{color:'var(--bad)'}">
      详情失败：{{ error }}
    </div>
    <template v-else-if="payload">
      <div class="detail-header">
        <div class="small" style="color:var(--muted)">
          <strong style="color:var(--gold2)">{{ profile.characterName || row.name }}</strong>
          · {{ profile.serverName }} · {{ profile.raceName }} · {{ profile.className }}
          <span v-if="profile.titleName">· 稱號「{{ profile.titleName }}」</span>
        </div>
        <div class="small" style="color:var(--muted);display:flex;gap:6px;align-items:center">
          <span>{{ ageStr }}{{ payload.stale ? ' (stale)' : '' }}</span>
          <button class="btn" style="padding:2px 8px;font-size:11px" @click="refresh">刷新</button>
        </div>
      </div>

      <div class="score-row">
        <ScoreBox label="PVE 評分"
                  :value="ratingScore != null ? Number(ratingScore).toFixed(2) : '—'"
                  :sub="ratingPctStr || ratingSrvStr" />
        <ScoreBox label="戰鬥力"
                  :value="fmt(profile.combatPower)"
                  :sub="cpStr" />
        <ScoreBox label="道具等級" :value="fmt(itemLevel)" />
        <ScoreBox label="角色等級"
                  :value="'Lv.' + (profile.characterLevel ?? '—')"
                  :sub="profile.regionName ? '軍團 ' + profile.regionName : ''" />
      </div>

      <div v-if="gearSlots.length">
        <div class="section-title">裝備 ({{ gearSlots.length }})</div>
        <div class="item-grid">
          <ItemTile v-for="e in gearSlots" :key="e.slotPos" :item="e" :detail="itemBySlot[e.slotPos]" />
        </div>
      </div>

      <div v-if="cardSlots.length">
        <div class="section-title">卡牌 / 古文石 ({{ cardSlots.length }})</div>
        <div class="item-grid">
          <ItemTile v-for="e in cardSlots" :key="e.slotPos" :item="e" :detail="itemBySlot[e.slotPos]" />
        </div>
      </div>

      <div v-if="statList.length">
        <div class="section-title">主要屬性</div>
        <div class="stat-grid">
          <div v-for="(s, i) in statList.slice(0,16)" :key="i" class="small stat-cell">
            <span style="color:var(--muted)">{{ s.name || s.statName }}</span>
            <span>{{ s.value ?? s.statValue }}</span>
          </div>
        </div>
      </div>

      <div class="small" style="margin-top:8px;color:var(--muted);font-size:11px">
        数据源：本地 SQLite 缓存 ←
        <a :href="`https://aion2.bnshive.com/character/${row.serverId}/${encodeURIComponent(row.characterId)}`"
           target="_blank" style="color:var(--gold)">永恆蜂窩</a>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ScoreBox from './ScoreBox.vue'
import ItemTile from './ItemTile.vue'

const props = defineProps({
  row: { type: Object, required: true },
  payload: Object,
  loading: Boolean,
  error: String,
})
const emit = defineEmits(['refresh'])

const data = computed(() => (props.payload?.queryResult?.data) || {})
const profile = computed(() => data.value.profile || {})
const equipment = computed(() => data.value.equipment?.equipmentList || [])
const itemDetails = computed(() => data.value.itemDetails || [])
const itemBySlot = computed(() => Object.fromEntries(itemDetails.value.map(it => [it.slotPos, it])))
const gearSlots = computed(() => equipment.value.filter(e => e.slotPos >= 1 && e.slotPos <= 19))
const cardSlots = computed(() => equipment.value.filter(e => e.slotPos >= 20))
const statList = computed(() => data.value.stat?.statList || [])

const rating = computed(() => props.payload?.rating || {})
const ratingScore = computed(() => rating.value?.scores?.score ?? null)
const ratingPctStr = computed(() => {
  const p = rating.value?.percentile?.allDataPercentile
  return p != null ? `全體前 ${p.toFixed(2)}%` : ''
})
const ratingSrvStr = computed(() => {
  const p = rating.value?.percentile?.serverPercentile
  return p != null ? `本服前 ${p.toFixed(2)}%` : ''
})
const cpStr = computed(() => {
  const p = props.payload?.combatPowerPercentile?.allDataPercentile
  return p != null ? `全體前 ${p.toFixed(2)}%` : ''
})
const itemLevel = computed(() => {
  const h = props.payload?.itemLevelHistory || []
  return h.length ? h[h.length - 1].itemLevel : null
})
const ageStr = computed(() => {
  const age = props.payload?.ageSeconds || 0
  if (!props.payload?.cached) return '刚刚抓取'
  const m = Math.round(age / 60)
  return `本地缓存 · ${m < 1 ? '刚刚' : m + ' 分钟前'}`
})

function fmt (n) { return n == null || isNaN(n) ? '—' : Number(n).toLocaleString('en-US') }
function refresh () { emit('refresh') }
</script>

<style scoped>
.detail-panel{width:100%;margin-top:12px;padding:14px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;box-sizing:border-box}
.detail-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;gap:8px;flex-wrap:wrap}
.score-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px;margin-bottom:12px}
.section-title{margin:8px 0 6px;font-weight:600;color:var(--gold2)}
.item-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:6px}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:4px}
.stat-cell{display:flex;justify-content:space-between;padding:3px 6px;background:var(--bg);border-radius:4px}
</style>
