<template>
  <div class="score-box">
    <div class="small lbl">{{ label }}</div>
    <div class="val">{{ value }}</div>
    <div v-if="sub" class="small sub">{{ sub }}</div>
  </div>
</template>
<script setup>
defineProps({ label: String, value: [String, Number], sub: String })
</script>
<style scoped>
.score-box{background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:8px 10px}
.lbl{color:var(--muted);font-size:10px}
.val{font-size:18px;font-weight:600;color:var(--gold2);line-height:1.2}
.sub{color:var(--muted);font-size:10px;margin-top:2px}
</style>
