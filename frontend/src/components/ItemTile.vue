<template>
  <div class="tile">
    <img v-if="item.icon" :src="item.icon" @error="hideImg" />
    <div v-else class="placeholder"></div>
    <div class="meta">
      <div class="small slot">
        {{ item.slotPosName }}
        <template v-if="grade">· {{ grade }}</template>
        <template v-if="lvl">· {{ lvl }}</template>
      </div>
      <div class="name" :title="item.name || ''">
        <span v-if="item.enchantLevel" class="enchant">+{{ item.enchantLevel }}</span>
        {{ item.name }}<template v-if="item.exceedLevel"> ({{ item.exceedLevel }})</template>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ item: Object, detail: Object })
const grade = computed(() => props.detail?.detail?.gradeName || props.item.grade || '')
const lvl = computed(() => {
  const lv = props.detail?.detail?.equipLevel
  return lv ? `Lv.${lv}` : ''
})
function hideImg (e) { e.target.style.opacity = .2 }
</script>
<style scoped>
.tile{display:flex;gap:6px;padding:5px;background:var(--bg);border:1px solid var(--border);border-radius:6px;align-items:center}
img,.placeholder{width:36px;height:36px;border-radius:4px;background:#000;flex-shrink:0}
.meta{flex:1;min-width:0}
.slot{color:var(--muted);font-size:10px}
.name{font-size:12px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.enchant{color:var(--gold)}
</style>
