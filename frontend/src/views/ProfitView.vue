<template>
  <h2>装备拍卖利润</h2>
  <p class="small">利润 = 卖价 − 成本。绿色 = 赚，红色 = 亏。</p>
  <div v-for="(tbl, idx) in profitTables" :key="idx" class="card" style="margin-bottom:14px">
    <h3>{{ tbl.title }}</h3>
    <table>
      <thead>
        <tr><th v-for="c in tbl.cols" :key="c">{{ c }}</th><th>利润1</th><th>利润2</th></tr>
      </thead>
      <tbody>
        <tr v-for="(row, ri) in tbl.rows" :key="ri">
          <td>{{ row[0] }}</td>
          <td>{{ fmt(row[1]) }}</td>
          <td>{{ fmt(row[2]) }}</td>
          <td>{{ fmt(row[3]) }}</td>
          <td :class="profitClass(row[2], row[1])">{{ profit(row[2], row[1]) }}</td>
          <td :class="profitClass(row[3], row[1])">{{ profit(row[3], row[1]) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { profitTables } from '../data/profitTables.js'

function fmt (n) { return n == null ? '—' : Number(n).toLocaleString('en-US') }
function profit (sell, cost) {
  if (sell == null) return '—'
  const p = sell - cost
  return (p >= 0 ? '+' : '') + p.toLocaleString('en-US')
}
function profitClass (sell, cost) {
  if (sell == null) return 'neutral'
  return sell - cost >= 0 ? 'pos' : 'neg'
}
</script>
