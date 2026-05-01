<template>
  <h2>强化石消耗</h2>
  <p class="small">每格 = 强化某等级所需的金/红色强化石平均数量。</p>

  <div class="card" style="margin-bottom:14px">
    <h3>普通装备 (金石 · 9 RMB/个)</h3>
    <table>
      <thead>
        <tr><th v-for="c in normalCols" :key="c">{{ c }}</th><th>金石 RMB</th></tr>
      </thead>
      <tbody>
        <tr v-for="(row, ri) in normalRows" :key="ri">
          <td>{{ row[0] }}</td>
          <td v-for="i in 4" :key="i">{{ fmt(row[i]) }}</td>
          <td>{{ fmtRMB(maxStone(row), 9) }}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h3>红色装备 (红石 · 35 RMB/个)</h3>
    <table>
      <thead>
        <tr><th v-for="c in redCols" :key="c">{{ c }}</th><th>红石 RMB</th></tr>
      </thead>
      <tbody>
        <tr v-for="(row, ri) in redRows" :key="ri">
          <td>{{ row[0] }}</td>
          <td v-for="i in 2" :key="i">{{ fmt(row[i]) }}</td>
          <td>{{ fmtRMB(maxStone(row), 35) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import {
  enhanceNormalCols as normalCols, enhanceNormalRows as normalRows,
  enhanceRedCols as redCols, enhanceRedRows as redRows,
} from '../data/enhance.js'

function fmt (n) { return n == null ? '—' : Number(n).toLocaleString('en-US') }
function maxStone (row) {
  let max = 0
  for (let i = 1; i < row.length; i++) {
    if (typeof row[i] === 'number' && row[i] > max) max = row[i]
  }
  return max
}
function fmtRMB (stones, price) {
  if (!stones) return '—'
  return '¥' + Math.round(stones * price).toLocaleString('en-US')
}
</script>
