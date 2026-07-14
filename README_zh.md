[English](./README.md) | [Español](./README_es.md) | **中文**

<div align="center">

<img src="assets/banner.svg" alt="SuearchHermes" width="720"/>

# SuearchHermes

**为 Hermes Agent 提供免费的 Google 搜索 — 无需 API Key，无需付费，真正的 Google 结果**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Hermes](https://img.shields.io/badge/Hermes-Agent-6E40C9?style=flat&logo=gnometerminal&logoColor=white)](https://github.com/NousResearch/hermes-agent)
[![agy](https://img.shields.io/badge/Antigravity%20CLI-agy-4285F4?style=flat&logo=google&logoColor=white)](https://github.com/google-antigravity/antigravity-cli)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](./LICENSE)
[![Cost](https://img.shields.io/badge/费用-免费%20%E2%80%A2%20无需%20API%20Key-brightgreen?style=flat)]()

</div>

---

## 📰 新闻

- **2026-07-14** 🚀 **v1.0.0 发布**：首次公开发布。通过 Antigravity CLI (agy) 为 Hermes Agent 提供 Google 搜索插件。免费，无需 API Key，通过 Gemini 实现 Google 搜索接地。包含一键安装程序、完整的 Hermes `WebSearchProvider` ABC 实现和自动配置。([发布说明](https://github.com/leonardo-ferioli/SuearchHermes/releases/tag/v1.0.0))

---

## 🎯 为什么？

Hermes Agent 内置了 `web_search` 支持，但所有内置后端都有问题：

| 后端 | 费用 | API Key | 质量 | 问题 |
|---|---|---|---|---|
| **Firecrawl** | 💰 付费 | 需要 | ⭐⭐⭐⭐ | 按请求计费 |
| **Tavily** | 💰 付费 | 需要 | ⭐⭐⭐⭐ | 免费额度有限 |
| **Brave (免费)** | ⚠️ 有限 | 需要 | ⭐⭐⭐ | 每月 2,000 次查询 |
| **DDGS** | ✅ 免费 | 无需 | ⭐ | 质量差，被限速 |
| **SuearchHermes** | ✅ 免费 | **无需** | ⭐⭐⭐⭐⭐ | **使用 Google via Gemini** |

---

## ✨ 主要特性

- 🔍 **真正的 Google 搜索** — 通过 Gemini 搜索接地，非网页抓取
- 🆓 **零成本** — 无需 API Key，无需付费
- 🧠 **综合答案** — Gemini 阅读结果并给出简洁答案和来源
- 🔌 **即插即用** — 实现 Hermes 的 `WebSearchProvider` ABC
- ⚡ **一键安装** — `./install.sh` 全部搞定
- 🌐 **干净的来源域名** — 返回 `github.com`，不是不透明的重定向 URL

---

## 🚀 快速开始

### 前提条件

1. **Hermes Agent** 已安装
2. **Antigravity CLI** (`agy`) 已安装并认证：

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
agy  # 用你的 Google 账户登录
```

### 安装

```bash
git clone https://github.com/leonardo-ferioli/SuearchHermes.git
cd SuearchHermes
./install.sh
```

### 使用

直接让 Hermes 搜索：

```
> 搜索：Rust 最新稳定版本
> 搜索：最好的 Python 框架 2026
```

---

## 📝 示例

```json
{
  "success": true,
  "data": {
    "web": [
      {"title": "Rust 1.97.0...", "url": "rust-lang.org", "description": "...", "position": 1},
      {"title": "releases.rs", "url": "https://releases.rs", "description": "", "position": 2}
    ]
  }
}
```

---

## 🛣️ 路线图

- [x] v1.0.0 — 核心插件、安装程序、文档
- [ ] **v1.1.0** — 提取支持（通过 agy 提取页面内容）
- [ ] **v1.2.0** — 可配置的提示模板
- [ ] **v1.3.0** — 响应缓存
- [ ] **v2.0.0** — 直接集成 Gemini API（绕过 agy CLI）

---

## 📄 许可证

MIT — 见 [LICENSE](./LICENSE)

---

## 👤 作者

**Leonardo Ferioli** — [@leonardo-ferioli](https://github.com/leonardo-ferioli)

---

<div align="center">

**SuearchHermes** — 免费的 Google 搜索，为 Hermes Agent 而生。

如果这个项目对你有帮助，请考虑 ⭐ 给仓库点星。

</div>
