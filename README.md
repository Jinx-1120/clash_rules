# clash_rules

适用于 Surge、OpenClash / Mihomo、Stash 和 Surfboard 的 VPN 分流规则与配置示例。让本地网络和指定网站直连，普通代理流量与 AI 服务分别使用你选择的出口。

使用前需要已有可用的代理节点或订阅。本仓库提供规则和示例，不提供节点服务。

## 开始使用

1. 按客户端选择示例：[Surge](examples/surge.conf)、[OpenClash / Mihomo / Stash](examples/clash.yaml)、[Surfboard](examples/surfboard.conf)。
2. 将示例节点替换为自己的节点；如果合入已有配置，保留节点、监听和 DNS 设置，合并策略组及规则部分，不要重复创建同名配置段或 YAML 键。
3. 在客户端启用规则模式，选择 `Proxies` 的普通代理出口和 `AI` 的 AI 出口。已有策略组可替换示例中的同名引用。

示例已引用下表全部通用规则；Surge 的进程规则仅在 Mac 上启用。合并时，将自己的节点入口、本地网络和明确的直连例外放在前面，AI 规则放在普通代理、地区规则及最终兜底之前。

## 包含哪些规则

| 规则 | 用途 | 示例中的出口 |
| --- | --- | --- |
| [LocalAreaNetwork.list](LocalAreaNetwork.list) | 本地网络、保留地址和路由器管理域名 | `DIRECT` |
| [no_proxy.list](no_proxy.list) | 指定直连的网站 | `DIRECT` |
| [ai.list](ai.list) | ChatGPT / Codex、Claude、Gemini / Antigravity、Cursor、Grok、Copilot、Perplexity 等 AI 服务 | `AI` |
| [ai-shared.list](ai-shared.list) | AI 使用的共享登录、验证和功能服务 | `AI` |
| [ai-process-surge.list](ai-process-surge.list) | AI 桌面应用与专用 CLI 的进程匹配，仅支持 Surge Mac 6+ | `AI` |
| [proxy.list](proxy.list) | 指定使用代理的网站 | `Proxies` |

`ai-shared.list` 会同时影响使用相同 Google 登录或 Cloudflare 验证域名的其他网站；不需要时可以移除这份规则的引用。其他客户端和 Surge iOS 使用域名规则，不加载 Mac 进程规则。更细的适用范围见[规则说明](docs/rule-behavior.md)。

## 自动更新

示例直接引用 `main` 分支的远程规则，刷新间隔为 **3600 秒（1 小时）**。以后修改现有 `.list` 文件并合入 `main`，客户端会按自身刷新机制获取内容，无需重新导入整份配置。客户端须能访问 `raw.githubusercontent.com`；离线、后台限制和缓存可能推迟生效，需要立即使用时可手动刷新远程规则。

Surge、Mihomo 和 Stash 各自管理规则资源；[Surfboard](https://getsurfboard.com/docs/profile-format/rule/ruleset/) 的后台下载会在下次启动 VPN 时应用。配置订阅更新与规则资源刷新是两个独立过程。

新增或重命名规则文件、改变策略组或匹配顺序时，仍需同步调整客户端配置；客户端不会自动发现仓库里的新文件。

规则来源、匹配边界见[规则说明](docs/rule-behavior.md)；参与维护见[贡献指南](CONTRIBUTING.md)。
