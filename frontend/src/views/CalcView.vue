<template>
  <h2>材料成本计算</h2>
  <p class="small">每行数据本地保存（localStorage）。点击表格直接编辑单价/数量。</p>
  <div class="grid two">
    <div v-for="(sheet, idx) in sheets" :key="idx" class="card">
      <h3>
        {{ sheet.title }}
        <span class="badge">合计 {{ fmt(total(sheet)) }}</span>
      </h3>
      <table>
        <thead>
          <tr><th>材料</th><th>单价</th><th>数量</th><th>小计</th></tr>
        </thead>
        <tbody>
          <tr v-for="(row, ri) in sheet.materials" :key="ri">
            <td>
              <input class="cell text" v-model="row[0]" @change="save" />
            </td>
            <td>
              <input class="cell" type="number" v-model.number="row[1]" @change="save" />
            </td>
            <td>
              <input class="cell" type="number" v-model.number="row[2]" @change="save" />
            </td>
            <td>{{ fmt(row[1] * row[2]) }}</td>
          </tr>
          <tr class="total-row">
            <td colspan="3">合计</td>
            <td>{{ fmt(total(sheet)) }}</td>
          </tr>
        </tbody>
      </table>
      <div class="toolbar" style="margin-top:10px">
        <button class="btn" @click="reset(idx)">重置本表</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { calcSheets } from '../data/recipes.js'

const sheets = ref(JSON.parse(JSON.stringify(calcSheets)))

onMounted(() => {
  sheets.value.forEach((s, i) => {
    const cached = localStorage.getItem('calc_' + i)
    if (cached) {
      try { s.materials = JSON.parse(cached) } catch {}
    }
  })
})

function save () {
  sheets.value.forEach((s, i) => localStorage.setItem('calc_' + i, JSON.stringify(s.materials)))
}
function reset (idx) {
  sheets.value[idx].materials = JSON.parse(JSON.stringify(calcSheets[idx].materials))
  localStorage.removeItem('calc_' + idx)
}
function total (sheet) {
  return sheet.materials.reduce((sum, r) => sum + (Number(r[1]) || 0) * (Number(r[2]) || 0), 0)
}
function fmt (n) {
  return Number(n || 0).toLocaleString('en-US')
}
</script>
