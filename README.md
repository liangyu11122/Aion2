# Aion 2 工具站

单文件 HTML + 本地 Python 服务器（静态 + 反向代理 + SQLite 缓存）。

## 运行
```
python server.py            # http://127.0.0.1:5180
python server.py 8080       # 自定义端口
```

## 功能
- 材料成本计算器（3 个配方）
- 拍卖利润表
- 卡牌槽位推荐
- 强化石消耗表
- 角色查询（台服）：NC 官方搜索 → 失败时 fallback 到永恆蜂窩
- 角色详情：本地 SQLite 缓存层（TTL 1 小时），数据源 https://aion-api.bnshive.com

## 端点
- `GET /api/search?keyword=&serverId=&race=&pcId=` 角色搜索（NC → 蜂窝 fallback）
- `GET /api/char?serverId=&characterId=&refresh=0|1` 角色详情（缓存）
- `GET /proxy/ncsoft/<path>` NC 透明代理
- `GET /proxy/profile-img?...` 头像代理
