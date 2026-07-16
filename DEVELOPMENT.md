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

## 写新内容

```bash
hugo new content/fiction/我的新文.md    # 同人文
hugo new content/art/我的新图.md        # 同人图
```

也可以直接复制现有示例文件改。字段说明：

**同人文** `content/fiction/*.md`
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

**同人图** `content/art/*.md`
```yaml
---
title: "标题"
date: 2026-07-16
draft: false
thumb: "/img/图片名.jpg"    # 列表缩略图
image: "/img/图片名.jpg"    # 详情页大图
caption: "图片说明"
fandom: ["七小侠"]
tags: ["AU"]
---
创作笔记……
```

## 圈子（fandom）与标签（tags）

两套 taxonomy，在 `hugo.toml` 的 `[taxonomies]` 里定义：

- **fandom（圈子）** — 驱动首页大卡片。每篇作品用 `fandom: [...]` 归入一个或多个圈子。
  圈子聚合页在 `/fandom/<圈子名>/`，混排该圈子下的文和图，页内有「全部 / 同人文 / 同人图」筛选。
- **tags（自由标签）** — 只在详情页和列表小卡片显示，不进首页。可点击跳到 `/tags/<标签>/` 聚合页。

**新增一个圈子**：在 `hugo.toml` 里加一段（首页大卡片就是从这里读的，不写在模板里）：

```toml
[[params.fandoms]]
  name = "圈子名"              # 要和文章 front matter 里的 fandom 值完全一致
  image = "/img/圈子图.jpg"    # 大卡片配图，见下方「图片规范」
  intro = "圈子简介文字"
```

`name` 就是聚合页地址：`name = "七小侠"` → 卡片链到 `/fandom/七小侠/`。删掉某圈子的所有文章后，它的聚合页和首页卡片会自动消失。

## 图片规范

- **放哪**：所有图片放 `static/img/`。`static/` 下的路径直接对应网站根路径——`static/img/x.jpg` → 配置/front matter 里写 `/img/x.jpg`。
- **格式**：`.png / .jpg / .jpeg / .svg / .webp` 都行，模板不对格式做任何假设，`<img>` 直接引用你写的路径。占位用的 `.svg` 只是示例，换成实际图直接改路径即可。
- **文件名一律小写**，用连字符不用空格：`circle-qixiaoxia.png` ✅、`Circle_QiXiaoXia.PNG` ❌。
  > ⚠️ **大小写敏感**：GitHub Actions 跑在 Linux 上，文件系统区分大小写。本地 macOS 不区分，所以 `image = "/img/Foo.PNG"` 在你电脑上能显示、推上去却 404。统一小写可彻底避免这类「本地好好的、线上裂图」。
- 大卡片和缩略图都用 `object-fit: cover`，不同尺寸的图会自动裁切填满，不会撑破布局。

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
hugo.toml                 站点配置（baseURL、taxonomies、圈子卡片）
layouts/                  自建主题模板
  _default/baseof.html      整体骨架 + 两侧色带 + 导航高亮
  index.html                首页圈子大卡片（由 fandom 驱动）
  _default/list.html        section 列表页（/fiction/ /art/）
  _default/term.html        圈子/标签聚合页 + 文/图筛选
  _default/single.html      详情页 + 圈子/标签链接 + 方向键翻页 + 评论容器
  partials/card.html        小卡片（含圈子 + tags）
  shortcodes/video.html     B 站 / YouTube 视频嵌入
static/css/main.css       全部样式
static/img/               图片（文件名一律小写）
content/fiction/          同人文
content/art/              同人图
drafts/                   原始素材（docx），已在 .gitignore，不发布
```

## 发布

推送到 `main` 分支即可，GitHub Actions（`.github/workflows/hugo.yml`）会自动构建并部署到 GitHub Pages。

首次需在 GitHub 仓库设置里开启：**Settings → Pages → Build and deployment → Source 选 "GitHub Actions"**。

自定义域名 `chusheng.uk` 由根目录 `CNAME` 文件生效（勿删）。

## 待办

- 评论系统：详情页已预留 `<div id="waline"></div>` 容器，接 [Waline](https://waline.js.org/) 时在 `layouts/_default/single.html` 里加初始化脚本即可，模板无需改结构。
