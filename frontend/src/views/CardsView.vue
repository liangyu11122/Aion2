<template>
  <h2>卡牌选择</h2>
  <p class="small">每个职业的 6 个卡槽推荐主卡（圣杯 / 羊皮纸 / 指南针 / 钟 / 镜子 / 天秤）。</p>
  <div v-for="cls in cardClasses" :key="cls.name" class="card" style="margin-bottom:14px">
    <h3>{{ cls.name }}</h3>
    <table>
      <thead>
        <tr>
          <th>主属性 \ 卡槽</th>
          <th v-for="s in slots" :key="s">{{ s }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(items, attr) in cls.cards" :key="attr">
          <td>
            <span class="tag" :class="tagClass(attr)">{{ attr }}</span>
          </td>
          <td v-for="(item, i) in slots" :key="i" class="card-cell small">
            {{ items[i] || '—' }}
          </td>
        </tr>
        <tr class="total-row">
          <td>推荐</td>
          <td v-for="(rec, i) in cls.recommend" :key="i" class="card-cell">{{ rec }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { cardClasses, cardSlots as slots } from '../data/cards.js'

function tagClass (attr) {
  if (attr.includes('活力')) return 'vit'
  if (attr.includes('纯血')) return 'pure'
  if (attr.includes('狂奔')) return 'rage'
  if (attr.includes('主推')) return 'either'
  return 'muted'
}
</script>
