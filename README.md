# Aion 2 工具站

> 单页面 → 正经 MVC 架构。**Flask (Python)** 后端 + **Vue 3 (Vite)** 前端。

## 目录结构

```
Aion2/
├── backend/                     Flask MVC 后端
│   ├── app.py                   入口 + app factory
│   ├── requirements.txt
│   ├── controllers/             路由层（薄）
│   │   ├── search.py            GET /api/search
│   │   ├── character.py         GET /api/char
│   │   └── proxy.py             /proxy/ncsoft/* + /proxy/profile-img
│   ├── services/                业务层
│   │   ├── nc_client.py         NCSoft 官方 API 封装
│   │   ├── bnshive_client.py    永恆蜂窩 API 封装
│   │   └── search_service.py    NC → 蜂窩 fallback 编排
│   └── models/
│       └── character_cache.py   SQLite 缓存（TTL 1h）
│
├── frontend/                    Vue 3 SPA
│   ├── package.json
│   ├── vite.config.js           dev 时 /api、/proxy 反代到 :5180
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue              顶栏 + <router-view>
│       ├── router.js            5 个 tab 路由
│       ├── api.js               fetch 封装
│       ├── styles.css           全局主题（黑金色）
│       ├── data/                配方/利润/卡牌/强化数据
│       ├── views/               5 个 Tab 视图
│       └── components/          CharacterDetail / ItemTile / ScoreBox
│
├── legacy/                      原始单文件版本（备份）
│   ├── index.html
│   └── server.py
└── README.md
```

## 运行（开发）

两个终端：

```powershell
# Terminal 1 — 后端
cd backend
pip install -r requirements.txt
python app.py                    # http://127.0.0.1:5180

# Terminal 2 — 前端 (热更新)
cd frontend
npm install
npm run dev                      # http://127.0.0.1:5173 (代理 /api /proxy 到 5180)
```

## 运行（生产）

```powershell
cd frontend
npm install
npm run build                    # 产出 frontend/dist/
cd ..\backend
python app.py                    # 后端会自动 serve dist/index.html
```

→ 浏览器打开 `http://127.0.0.1:5180/`

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/search?keyword=&serverId=&race=&pcId=&page=&size=` | 角色搜索（NC → 蜂窝 fallback） |
| GET | `/api/char?serverId=&characterId=&refresh=0\|1` | 角色详情，本地 SQLite 缓存 |
| GET | `/proxy/ncsoft/<path>` | NC TW 透明代理（避 CORS） |
| GET | `/proxy/profile-img?gameServerKey=&charKey=` | 头像代理 |
