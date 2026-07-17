# DEVELOPMENT —— 技术文档

个人同人创作站（文字 + 插画），[Hugo](https://gohugo.io/)（extended）自建主题，GitHub Pages 托管，Sveltia CMS 做网页后台，Waline 做评论/浏览量/点赞。

> 面向维护者。给创作者本人看的操作手册见 **[USAGE.md](./USAGE.md)**。

---

## 1. 整体架构

```
访客  ──https──►  Cloudflare（chusheng.uk 的 DNS + CDN/SSL）
                        │  回源
                        ▼
                  GitHub Pages（自定义域名 chusheng.uk）
                        ▲  部署 public/
                        │
        GitHub 仓库 chusheng716/chusheng716.github.io（main 分支）
              ▲  push 触发                    ▲  写入 main
              │                               │
       本地 hugo + git                 Sveltia CMS（/admin）
                                       经 Cloudflare Worker + GitHub OAuth 提交
                        │
                        ▼
        GitHub Actions（.github/workflows/hugo.yml）
        装 Hugo extended 0.164.0 → hugo --minify → 部署到 Pages

评论/浏览量/点赞：详情页前端直接调用独立的 Waline 后端（Vercel + Neon），与上面构建链路无关。
```

- **域名 `chusheng.uk`**：托管在 Cloudflare（DNS、CDN、SSL）。仓库根目录 `CNAME` 文件把 GitHub Pages 绑到这个域名（**勿删**）。
- **托管**：GitHub Pages，Source = GitHub Actions。
- **仓库**：`chusheng716/chusheng716.github.io`，部署分支 `main`。
- **两条写入路径**：① 本地改文件 + git 推送；② 网页后台 Sveltia CMS 直接提交到 `main`。两者都会触发 Actions 重新构建部署。

---

## 2. 环境要求 & 本地开发

- Hugo **extended** 版（本地与 CI 都锁 `v0.164.0`）。

```bash
brew install hugo
hugo version            # 确认输出里带 "extended"

hugo server -D          # 本地预览 http://localhost:1313/（-D 显示草稿）
hugo --gc --minify      # 一次性构建，产物在 public/（构建产物不入库）
```

> 本地预览时评论区、reaction、卡片浏览量需要连线上 Waline 后端，跨域下可能显示不全，属正常。

---

## 3. 内容结构

三类内容，全部在 `content/` 下。

### fandom（圈子）—— `content/fandoms/<slug>/`（Page Bundle）

首页大卡片的数据源。每个 fandom 一个文件夹：`index.md` + 封面图。

```yaml
# content/fandoms/qixiaoxia/index.md
---
title: "七小侠"        # fandom 名称，必须和文/图里 fandom 值完全一致
weight: 1              # 排序，数字越小越靠前
cover: "cover.png"     # 封面图文件名（同目录）
---
简介正文……
```

- 首页卡片链到聚合页 `/fandom/<title>/`。
- 这些页面 `render: never`（见 `content/fandoms/_index.md` 的 cascade），**不生成独立网址**，只作数据源；模板用 `where site.RegularPages "Section" "fandoms"` 取它们（`layouts/index.html`）。

### 同人文 —— `content/fiction/<slug>.md`（单文件）

```yaml
---
title: "标题"
date: 2026-07-17
draft: false
weight: 1              # 章节序号，同一 fandom 内按它升序翻章；单篇可省略
fandom: ["七小侠"]     # 可多个（crossover）
tags: ["甜文", "HE"]   # 自由标签，可多个
---
正文……
```

> 多章作品的 `weight` **从 1 起**（Hugo 把 `weight: 0` 当"未加权"排到最后，会打乱翻章顺序）。现有 `yeshanshen-1-00…05` 就是一篇拆成 6 小节，weight 1–6。

### 同人图 —— `content/art/<slug>/`（Page Bundle，支持多图）

```yaml
# content/art/crimefilm_au/index.md
---
title: "刑侦AU"
date: 2026-07-17
draft: false
cover: "01.jpg"        # 卡片缩略图；不写则取第一张
fandom: ["七小侠"]
tags: ["AU"]
images:                # 详情页按顺序纵向展示，每张可配说明；只有一张图时整段可省略
  - src: "01.jpg"
    caption: "第一张说明"
  - src: "02.jpg"
    caption: "第二张说明"
---
创作笔记（可选）
```

- 只有一张图：删掉 `images` 段，图片拷进文件夹即可，详情页自动展示目录里的图。
- 现有示例：`content/art/crimefilm_au/`（2 图）、`content/art/ancient_au/`（3 图）。

### fandom / tags 分类（taxonomy）

`hugo.toml` 的 `[taxonomies]`：`fandom = "fandom"`、`tag = "tags"`。

- **fandom** 驱动首页大卡片；聚合页 `/fandom/<名>/` 混排该圈子的文和图。
- **tags** 只在详情页和小卡片显示，聚合页 `/tags/<标签>/`。
- 前台 UI 文案统一用「fandom」，代码字段名 / URL（`/fandom/xxx/`）保持 `fandom` 不变。

---

## 4. 图片

- **放哪**：fandom 封面和画图作品的图都放进**各自的 Page Bundle 文件夹**，front matter 只写文件名（`cover.png`、`01.jpg`），不带路径。Page Bundle 里的图才会被 Hugo 处理；`static/` 下的图只原样拷贝。
- **命名规范**：**一律小写、用连字符、不留空格**（`crimefilm-au.jpg` ✅ / `Crime Film.JPG` ❌）。
  > ⚠️ **Linux 大小写敏感**：GitHub Actions 跑在 Linux 上，区分大小写；本地 macOS 不区分。所以 `Foo.PNG` 在你电脑上正常、线上却 404。统一小写彻底避免"本地好好的、线上裂图"。
- **构建时自动优化**（`layouts/partials/image.html`，原图保留在仓库、优化版缓存在 `resources/_gen/` 已被 gitignore）：

  | 位置 | 处理 |
  |---|---|
  | 卡片缩略图（画图 / fandom） | 宽 600px，转 WebP，质量 80 |
  | 详情页展示图 | 最大宽 1200px，WebP 质量 85；`<picture>` 以原图作 fallback；点击看原图 |

  所有图带 `loading="lazy"`。`.svg` 是矢量图，不处理、直接用原图。

---

## 5. 嵌入视频（B 站 / YouTube）

正文里用 `video` shortcode，响应式 16:9，不托管本地视频（`layouts/shortcodes/video.html`）：

```
{{</* video youtube="dQw4w9WgXcQ" */>}}     ← YouTube，参数是 v= 后面的视频 ID
{{</* video bilibili="BV1xx411c7mD" */>}}    ← B 站，参数是 BV 号
```

> CMS 富文本编辑器里插 shortcode 时，要确保这行作为纯文本存进正文（必要时切到源码/Markdown 模式），否则可能被转义。

---

## 6. docx → markdown 转换脚本

把 Word 稿转成 `content/fiction/` 下的 markdown（`scripts/docx_to_md.py`，依赖 `python-docx`）：

```bash
# 按文中「00.」「01.」小节拆成多篇（weight 自动 = 小节号+1）
python3 scripts/docx_to_md.py "drafts/某文.docx" --title "标题" --slug my-slug --split

# 整篇作一章
python3 scripts/docx_to_md.py "drafts/某文.docx" --title "标题" --weight 7 --slug my-slug
```

默认 `--fandom 七小侠`、`--date` 今天、`--out-dir content/fiction`。保留段落分隔、去掉 Word 格式。

---

## 7. 目录结构

```
hugo.toml                 站点配置（baseURL、taxonomies、菜单、Waline serverURL）
CNAME                     自定义域名 chusheng.uk（勿删）
.github/workflows/hugo.yml  GitHub Actions 构建部署
layouts/                  自建主题模板
  _default/baseof.html      骨架 + 两侧色带 + 导航高亮
  index.html                首页 fandom 大卡片（读 content/fandoms/）
  _default/list.html        section 列表页（/fiction/ /art/）
  _default/term.html        fandom / tags 聚合页
  _default/single.html      详情页 + 翻章 + Waline 评论/浏览量/点赞
  partials/card.html        小卡片（fandom + tags + 浏览量）
  partials/image.html       图片处理（缩放/WebP/lazy/点击看原图）
  partials/pageview.html    列表页拉取卡片浏览量（只读不计数）
  shortcodes/video.html     B 站 / YouTube 视频嵌入
static/css/main.css       全部样式（含 Waline 变量覆盖）
static/admin/             网页后台（Sveltia CMS）
  index.html                后台入口
  config.yml                collections / 字段配置
static/robots.txt         屏蔽所有搜索引擎爬虫
content/fandoms/          fandom（首页大卡片数据源，Page Bundle）
  _index.md                 render:never，只作数据源
  qixiaoxia/{index.md, cover.png}
  quanzier/{index.md, cover.svg}
content/fiction/          同人文（每篇一个 .md）
  _index.md, summer-rain.md, yeshanshen-1-00…05.md …
content/art/              同人图（每个作品一个文件夹 = Page Bundle）
  _index.md
  crimefilm_au/{index.md, 01.jpg, 02.jpg}
  ancient_au/{index.md, 01.jpg, 02.jpg, 03.png}
scripts/docx_to_md.py     docx → markdown 转换脚本
drafts/                   原始 docx 素材，已 gitignore，不发布
```

---

## 8. 发布

push 到 `main` → GitHub Actions 自动构建部署，约 1–2 分钟生效。

- 首次需在仓库 **Settings → Pages → Build and deployment → Source** 选 **"GitHub Actions"**。
- CMS 的每次保存 = 一次对 `main` 的提交，同样触发上面的流程。

---

## 9. 网页后台（Sveltia CMS）

不碰 git 也能发布：`https://chusheng.uk/admin/`，GitHub 账号登录，保存即写回 `main`、触发部署。

- **前端**：`static/admin/index.html`（从 CDN 加载 `@sveltia/cms`）。
- **配置**：`static/admin/config.yml`，三个 collection：**fandom / 同人文 / 同人图**，字段全中文。
- **登录授权链路**：
  1. `config.yml` 的 `backend.base_url` 指向 **Cloudflare Worker `sveltia-cms-auth.chusheng716.workers.dev`**。
  2. 该 Worker 用一个 **GitHub OAuth App** 完成授权：
     - Homepage URL：`https://chusheng.uk`
     - Authorization callback URL：`https://sveltia-cms-auth.chusheng716.workers.dev/callback`
  3. Worker 环境变量（**不含值**）：

     | 变量 | 作用 |
     |---|---|
     | `GITHUB_CLIENT_ID` | OAuth App 的 Client ID |
     | `GITHUB_CLIENT_SECRET` | OAuth App 的 Client Secret |
     | `ALLOWED_DOMAINS`（可选） | 限制哪些站点能用这个 auth（`chusheng.uk`） |

- **relation vs list 的取舍**（Sveltia 现状）：
  - fandom 用 `relation`（能搜索/补全已有的），但**不能在文/图编辑器里临时新建 fandom**——要用新 fandom，先去「fandom」collection 建好再回来选。
  - tags 用 `list`（能自由输入新 tag），但**不提示已有 tag**。两者兼得 Sveltia 目前做不到；若想改成"tags 也走 collection + relation（可自动补全，代价是新 tag 要先建）"，改 `config.yml` 即可。
- **文件夹名（slug）**：新建画图/fandom 时可在后台手动改 slug，建议小写英文（`crimefilm-au`），避免中文文件夹在 Linux 上的大小写/编码麻烦。
- **界面语言**：Sveltia 主要跟随浏览器语言；`config.yml` 里 `locale: zh-CN` 是尽力声明，浏览器为中文最稳。

---

## 10. 评论 / 浏览量 / 点赞（Waline）

独立后端，与站点构建无关，详情页前端直接调用。

- **后端**：部署在 **Vercel** —— `https://waline-lime-nine.vercel.app`，数据库用 **Neon（PostgreSQL）**。
- **serverURL 配置**：`hugo.toml` 的 `walineServerURL`（换后端只改这一行，模板自动引用）。
- **管理后台**：`https://waline-lime-nine.vercel.app/ui`。第一个访问 `/ui/register` 注册的账号 = 管理员；后台可删/审核评论、拉黑、看浏览量。
- **Vercel 环境变量清单（不含值）**：

  | 变量 | 作用 |
  |---|---|
  | Neon 连接（`PG_HOST`/`PG_DB`/`PG_USER`/`PG_PASSWORD`/`PG_PORT`，SSL 开启） | 评论数据存 Neon PostgreSQL |
  | `JWT_KEY` | 登录态签名密钥（随机串） |
  | `SECURE_DOMAINS` | 只允许 `chusheng.uk` 调用后端，防别站盗用 |
  | `DISABLE_IP` | 不记录评论者 IP（隐私） |
  | `DISABLE_USERAGENT` | 不记录评论者浏览器 UA（隐私） |
  | `AUTHOR_EMAIL`（可选） | 站长评论显示"博主"标记的邮箱 |

- **前端接法**：
  - 详情页 `single.html`：`init({ pageview:true, reaction:[...], meta:['nick'], requiredMeta:['nick'], dark:false, lang:'zh-CN' })`。标题下方显示阅读数，底部评论区 + 点赞。
  - reaction 只保留 4 个正面 emoji（❤️👍😊😘），用系统 emoji 包成 SVG data URI（Waline 只吃图片 URL 不吃 emoji 字符）。
  - 评论表单只要昵称（`meta/requiredMeta: ['nick']`），不要邮箱/网址。
  - 列表/聚合页小卡片浏览量由 `partials/pageview.html` 拉取（`update:false`，只读不 +1）；真正 +1 只在详情页。
  - 配色：`static/css/main.css` 的 `#waline { --waline-theme-color … }` 用站点淡紫/淡粉覆盖默认绿。
  - 客户端从 jsDelivr CDN 加载 `@waline/client@v3`，无需本地依赖。

---

## 11. 隐私措施（已做）

- **不记录访客身份**：Waline 设 `DISABLE_IP` + `DISABLE_USERAGENT`，评论不留 IP / User-Agent。
- **不被搜索引擎收录**：`static/robots.txt` = `User-agent: * / Disallow: /`，屏蔽所有爬虫（同人站不希望被搜到）。想被收录就删掉它。
- **CMS 统一署名**：后台只用**一个 GitHub 账号**（`chusheng716`）登录，所有提交在仓库历史里都是这单一署名，不会因多身份而暴露个人 git 身份/邮箱；站点前台署名统一为「初牲」。
- **评论只收昵称**：表单去掉邮箱/网址，减少留痕。

---

## 12. 常见问题排查

| 现象 | 多半是 |
|---|---|
| 后台登录弹窗关不掉 / 登录失败 | OAuth App 的 callback URL 写错，或 Worker 的 `GITHUB_CLIENT_ID/SECRET` 没配对；`ALLOWED_DOMAINS` 没包含 `chusheng.uk` |
| 保存后网站没更新 | 去 GitHub 仓库 **Actions** 页看构建是否失败；失败常见于图片文件名大小写、或 front matter 写坏 |
| 本地图片正常、线上 404 | 文件名大小写（Linux 敏感）——改成全小写 |
| 评论发不出去 | Waline 的 `SECURE_DOMAINS` 没含 `chusheng.uk`；或 Neon 免费层休眠，首访唤醒有几秒延迟，重试即可 |
| 评论区 / reaction 本地预览不全 | 跨域，需连线上后端才完整，属正常 |
| CMS 里插的视频不显示 | 视频那行要作为纯文本存进正文，富文本编辑器可能转义——切源码模式再粘 |
| 多章翻页顺序乱 | 章节序号（weight）要从 1 起，`0` 会被 Hugo 排到最后 |
| 首页少了 / 多了一张大卡片 | 看 `content/fandoms/` 下是否有对应文件夹；`title` 要和文/图里的 `fandom` 值完全一致 |
