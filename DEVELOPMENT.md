# 本地预览与发布说明

个人同人创作站（文字 + 插画），基于 [Hugo](https://gohugo.io/)（extended 版）自建主题。

## 环境要求

- Hugo **extended** 版（本地已用 `v0.164.0`；CI 也锁定这个版本）

macOS 安装：

```bash
brew install hugo
hugo version   # 确认输出里带 "extended"
```

## 本地预览

在项目根目录运行：

```bash
hugo server -D
```

- 打开 http://localhost:1313/
- `-D` 会显示草稿（front matter 里 `draft: true` 的内容）
- 保存文件后浏览器自动刷新

一次性构建（产物在 `public/`，无需手动提交）：

```bash
hugo --gc --minify
```

## 写新内容 —— 同人文

同人文是单个 markdown 文件，复制现有示例改即可：

**`content/fiction/我的新文.md`**
```yaml
---
title: "标题"
date: 2026-07-16
draft: false
fandom: ["七小侠"]        # 所属圈子，可多个（crossover）
tags: ["甜文", "HE"]       # 自由标签，可多个
---
正文……（首页/列表卡片自动截取开头做摘要）
```

## 写新内容 —— 同人图（一个卡片 = 一组图）

同人图用 **Page Bundle**：一个作品是一个**文件夹**，里面放一个 `index.md` + 若干图片，图片和文字放在一起。一张图或一组图都用同一套结构。

**发布一组图的完整流程：**

1. 新建文件夹 `content/art/作品名/`（文件夹名就是网址，用小写英文，如 `content/art/summer-set/`）。
2. 把图片拷进这个文件夹（和 `index.md` 同级），文件名一律小写，如 `01.jpg 02.jpg 03.jpg`。
3. 在里面写 `index.md`：

```yaml
---
title: "作品名"
date: 2026-07-16
draft: false
cover: "01.jpg"              # 卡片缩略图用哪张（不写则默认第一张）
caption: "整组作品的一句话说明"   # 显示在列表卡片上
fandom: ["七小侠"]
tags: ["AU"]
images:                       # 详情页按此顺序纵向展示，每张下面配说明
  - src: "01.jpg"
    caption: "第一张的说明文字"
  - src: "02.jpg"
    caption: "第二张的说明文字"
  - src: "03.jpg"
    caption: "第三张的说明文字"
---
整组作品的创作笔记（可选，显示在图片下方）
```

**只有一张图**：把 `images` 整段删掉、图片拷一张进文件夹即可——详情页会自动展示文件夹里的图片，行为和以前一样。想给这唯一一张配说明，就保留 `images` 写一条。

> 完整可参考现有示例：`content/art/dusk/`（单图）和 `content/art/sketchset/`（三图组图）。

## 圈子（fandom）与标签（tags）

两套 taxonomy，在 `hugo.toml` 的 `[taxonomies]` 里定义：

- **fandom（圈子）** — 驱动首页大卡片。每篇作品用 `fandom: [...]` 归入一个或多个圈子。
  圈子聚合页在 `/fandom/<圈子名>/`，混排该圈子下的文和图。
- **tags（自由标签）** — 只在详情页和列表小卡片显示，不进首页。可点击跳到 `/tags/<标签>/` 聚合页。

**圈子由 `content/fandoms/` 这个 collection 驱动**（首页大卡片从这里动态生成，不再写在 `hugo.toml`）。最省事的方式是用网页后台（见下方「网页后台」），也可以手动建文件夹：

```
content/fandoms/qixiaoxia/
  index.md      # title=圈子名, weight=排序, cover=封面文件名, 正文=简介
  cover.png     # 封面图，和 index.md 同目录
```

`index.md` 里的 `title` 要和文章 front matter 的 `fandom` 值完全一致（如「七小侠」），首页卡片会链到聚合页 `/fandom/七小侠/`。`weight` 小的排前面。这些页面本身不生成独立网址（`render: never`），只作数据源。

## 图片规范

- **放哪**：圈子封面和画图作品的图都放进**各自的 Page Bundle 文件夹**（圈子在 `content/fandoms/<圈子>/`，画图在 `content/art/<作品>/`），front matter 只写文件名。Page Bundle 里的图会被 Hugo 处理（压缩/转 WebP）；`static/` 下的图只原样拷贝、不处理。
- **格式**：`.png / .jpg / .jpeg / .webp` 会被处理；`.svg` 是矢量图，模板会原样使用（不转 WebP）。
- **文件名一律小写**，用连字符不用空格：`circle-qixiaoxia.png` ✅、`Circle_QiXiaoXia.PNG` ❌。
  > ⚠️ **大小写敏感**：GitHub Actions 跑在 Linux 上，文件系统区分大小写。本地 macOS 不区分，所以 `Foo.PNG` 在你电脑上能显示、推上去却 404。统一小写可彻底避免这类「本地好好的、线上裂图」。
- 大卡片和缩略图都用 `object-fit: cover`，不同尺寸的图会自动裁切填满，不会撑破布局。

### 图片自动优化（构建时）

原图原封不动留在仓库里，Hugo 在 **构建时** 生成优化版本（缓存在 `resources/_gen/`，已被 `.gitignore` 忽略）。逻辑在 `layouts/partials/image.html`：

| 位置 | 处理 |
|---|---|
| 卡片缩略图（画图/圈子） | 宽 600px，转 WebP，质量 80 |
| 详情页展示图 | 最大宽 1200px，WebP 质量 85；`<picture>` 里以原图作 fallback；点击看原图 |

图片都带 `loading="lazy"`，多图不会一次性全部加载。SVG 因是矢量图不做这些处理、直接用原图。

## 嵌入视频（B 站 / YouTube）

正文里用 `video` shortcode，自动响应式 16:9，不托管本地视频：

```
{{</* video youtube="dQw4w9WgXcQ" */>}}     ← YouTube，参数是视频 ID
{{</* video bilibili="BV1xx411c7mD" */>}}    ← B 站，参数是 BV 号
```

视频 ID / BV 号怎么找：

- YouTube：链接 `https://www.youtube.com/watch?v=dQw4w9WgXcQ` 里 `v=` 后面那串。
- Bilibili：链接 `https://www.bilibili.com/video/BV1xx411c7mD` 里的 `BV...`。

## 目录结构

```
hugo.toml                 站点配置（baseURL、taxonomies、圈子卡片、Waline serverURL）
layouts/                  自建主题模板
  _default/baseof.html      整体骨架 + 两侧色带 + 导航高亮
  index.html                首页圈子大卡片（由 fandom 驱动）
  _default/list.html        section 列表页（/fiction/ /art/）
  _default/term.html        圈子/标签聚合页
  _default/single.html      详情页 + 圈子/标签链接 + 方向键翻页 + Waline 评论/浏览量/点赞
  partials/card.html        小卡片（含圈子 + tags + 浏览量）
  partials/image.html       图片处理封装（缩放/WebP/lazy/点击看原图）
  partials/pageview.html    列表页拉取卡片浏览量（只读不计数）
  shortcodes/video.html     B 站 / YouTube 视频嵌入
static/css/main.css       全部样式（含 Waline 变量覆盖）
static/admin/             网页后台（Sveltia CMS）
  index.html                后台入口
  config.yml                collections / 字段配置
static/robots.txt         屏蔽所有搜索引擎爬虫
content/fandoms/          圈子（首页大卡片数据源，每个圈子一个 Page Bundle）
  qixiaoxia/
    index.md                title=七小侠, weight, cover
    cover.png
content/fiction/          同人文（每篇一个 .md）
  summer-rain.md
  yeshanshen-1-00.md …
content/art/              同人图（每个作品一个文件夹 = Page Bundle）
  crimefilm_au/
    index.md                title/cover/images…
    01.jpg
    02.jpg
scripts/docx_to_md.py     docx → markdown 转换脚本
drafts/                   原始素材（docx），已在 .gitignore，不发布
```

> **图片都放 Page Bundle**：圈子封面放 `content/fandoms/<圈子>/`，画图作品的图放 `content/art/<作品>/`，front matter 里只写文件名（`cover.png`、`01.jpg`），不带路径。都会被构建时优化。

## 发布

推送到 `main` 分支即可，GitHub Actions（`.github/workflows/hugo.yml`）会自动构建并部署到 GitHub Pages。

首次需在 GitHub 仓库设置里开启：**Settings → Pages → Build and deployment → Source 选 "GitHub Actions"**。

自定义域名 `chusheng.uk` 由根目录 `CNAME` 文件生效（勿删）。

> **搜索引擎**：`static/robots.txt` 设为 `Disallow: /`，屏蔽所有爬虫（同人站不希望被搜到）。想被收录就删掉这个文件或放开规则。

## 网页后台（Sveltia CMS）

不想碰 git 时，用网页后台发布：打开 **`https://chusheng.uk/admin/`**，用 GitHub 账号登录（授权由 Cloudflare Worker `sveltia-cms-auth` 处理），改完点保存即写回仓库 `main`、自动触发部署。

配置在 `static/admin/config.yml`，三个 collection：**圈子 / 同人文 / 同人图**，字段都是中文。要点：

- **自己加圈子**：进「圈子」→ 新建，填圈子名、排序、封面、简介 —— 首页自动多一张大卡片，无需碰配置。
- **自己加标签**：文/图的「标签」栏直接输入新 tag，随便加，无需碰配置。
- **圈子字段用 relation**：文/图里选圈子是从「圈子」collection 动态拉的下拉（能搜索/自动补全）。**注意**：Sveltia 的 relation 只能选已有的、不能在这里临时新建圈子——要用新圈子，先去「圈子」里建好，再回来选。
- **新建画图/圈子时**能改左上角的 slug（文件夹名），建议用小写英文（如 `crimefilm-au`），避免中文文件夹在 Linux 上的大小写/编码麻烦。

> ⚠️ **关于标签自动补全**：你要的「自由输入 + 已有 tag 自动补全」两者兼得，Sveltia 目前做不到——`list` 组件能自由新增但不提示已有值，`relation` 能提示已有值但不能新建。这里给标签选了 `list`（保证「能随便加新 tag」这个硬需求）。如果你更想要「从已有 tag 里挑（自动补全）」、接受「加新 tag 要先建一次」，我可以把 tag 也改成一个 collection + relation，跟圈子一样——说一声即可。

> **界面语言**：Sveltia 后台语言主要**跟随浏览器语言**，中文系统/浏览器下即中文。`config.yml` 里的 `locale: zh-CN` 是尽力声明；若仍显示英文，把浏览器语言设为中文最稳。

> **前提**：Cloudflare Worker `sveltia-cms-auth.chusheng716.workers.dev` 要已部署并配好 GitHub OAuth App（授权回调指向它）。这步是一次性的，若还没弄，后台会卡在登录——需要另外配置。

## 评论 / 浏览量 / 点赞（Waline）

评论、文章浏览量、点赞都由自建的 [Waline](https://waline.js.org/) 后端提供，后端已部署在 Vercel。

**后端地址（serverURL）**：`https://waline-lime-nine.vercel.app`

- **管理后台**：浏览器打开 `https://waline-lime-nine.vercel.app/ui`。
  - 第一次先访问 `.../ui/register` 注册——**第一个注册的账号自动成为管理员**，先把它注册了占住。
  - 之后在后台可以删除/审核评论、拉黑、看浏览量数据。
- **改 serverURL**（比如换了后端部署）：只改 `hugo.toml` 里这一行，模板会自动引用：
  ```toml
  [params]
    walineServerURL = "https://你的新后端.vercel.app"
  ```
- **前端接在哪**：
  - 详情页 `layouts/_default/single.html` —— `init({ pageview:true, reaction:true })`，标题下方显示阅读数，底部是评论区 + 点赞。
  - 列表/圈子页的小卡片浏览量由 `layouts/partials/pageview.html` 拉取（`update:false`，只读不 +1，避免逛列表把每篇阅读数刷上去）。真正 +1 只发生在详情页。
- **配色**：评论区默认是绿色，已在 `static/css/main.css` 的 `#waline { --waline-theme-color … }` 用站点淡紫/淡粉覆盖。要调色改那几个 `--waline-*` 变量即可。
- Waline 客户端从 jsDelivr CDN 加载（`@waline/client@v3`），无需本地安装依赖。
