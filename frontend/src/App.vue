<template>
  <header class="site-header">
    <h1>⚜ AION 2 · 材料成本 / 装备利润 / 卡牌强化</h1>
    <p>基于《材料成本计算表_模板.xlsm》自动转换 · 数据可直接编辑，浏览器本地保存</p>
  </header>
  <nav class="tabs">
    <router-link to="/calc">材料成本计算</router-link>
    <router-link to="/profit">装备拍卖利润</router-link>
    <router-link to="/cards">卡牌选择</router-link>
    <router-link to="/enhance">强化石消耗</router-link>
    <router-link to="/chars">角色查询 · 台服</router-link>
  </nav>
  <main>
    <router-view />
  </main>
  <footer>© 2026 Aion 2 工具站 · Vue 3 + Flask MVC</footer>
</template>
