# clash_rules

适用于 Surge、OpenClash / Mihomo、Stash 和 Surfboard 的 VPN 分流规则与配置示例。让本地网络和指定网站直连，普通代理流量与 AI 服务分别使用你选择的出口。

使用前需要已有可用的代理节点或订阅。本仓库提供规则和示例，不提供节点服务。

## 开始使用

1. 按客户端选择示例：[Surge](examples/surge.conf)、[OpenClash / Mihomo / Stash](examples/clash.yaml)、[Surfboard](examples/surfboard.conf)。
2. 将示例节点替换为自己的节点；如果合入已有配置，保留节点、监听和 DNS 设置，合并策略组及规则部分，不要重复创建同名配置段或 YAML 键。
3. 在客户端启用规则模式，选择 `Proxies` 的普通代理出口、`AI` 的海外 AI 出口和 `MainlandAI` 的大陆 AI 出口（默认直连）。已有策略组可替换示例中的同名引用。

下表包含配置示例和托管 Surge 配置使用的规则。云厂商 IP 清单默认注释，按需启用。Surge 的进程规则仅在 Mac 上启用。合并时，将自己的节点入口、本地网络和明确的直连例外放在前面，大陆 AI 放在海外 AI 之前，AI 规则放在普通代理、地区规则及最终兜底之前。

## 包含哪些规则

| 规则 | 用途 | 策略 |
| --- | --- | --- |
| [LocalAreaNetwork.list](LocalAreaNetwork.list) | 本地网络、保留地址和路由器管理域名 | `DIRECT` |
| [no_proxy.list](no_proxy.list) | 指定直连的网站 | `DIRECT` |
| [ai-mainland.list](ai-mainland.list) | DeepSeek、豆包、Kimi、通义等大陆服务及区域端点 | `MainlandAI`，默认 `DIRECT` |
| [ai.list](ai.list) | ChatGPT / Codex、Claude、Gemini / Antigravity、Cursor、Grok、Copilot、Perplexity 等 AI 服务 | `AI` |
| [ai-shared.list](ai-shared.list) | AI 使用的共享登录、验证和功能服务 | `AI` |
| [ai-shared-extra.list](ai-shared-extra.list) | 扩展登录、通用 API、CDN 和遥测依赖，也影响其他服务 | `Proxies` |
| [ai-voice.list](ai-voice.list) | ChatGPT 语音的官方 IP 网段快照 | `AI` |
| [ai-process-surge.list](ai-process-surge.list) | AI 桌面应用与专用 CLI 的进程匹配，仅支持 Surge Mac 6+ | `AI` |
| [proxy.list](proxy.list) | 指定使用代理的网站 | `Proxies` |
| [Speedtest.list](Speedtest.list) | Fast、Cloudflare、Ookla 等测速域名及 Surge HTTP User-Agent | `Speedtest` |
| [YouTube.list](YouTube.list) | YouTube 服务 | `YouTube` |
| [Telegram.list](Telegram.list) | Telegram 域名及 IP 网段 | `Telegram` |
| [Bahamut.list](Bahamut.list) | 巴哈姆特動畫瘋 | `Bahamut` |
| [Microsoft.list](Microsoft.list) | Microsoft 服务 | `Microsoft` |
| [Apple.list](Apple.list) | Apple 服务 | `Apple` |
| [ProxyLite.list](ProxyLite.list) | 补充通用代理规则 | `Proxies` |
| [DisneyPlus.list](DisneyPlus.list) | Disney+ 域名 | `DisneyPlus` |
| [Extra_CN.list](Extra_CN.list) | 腾讯及其他国内服务的补充规则 | `DIRECT` |
| [Extra_CN_2.list](Extra_CN_2.list) | 国内域名和 IP 网段的补充规则 | `DIRECT` |
| [china-company-ip.list](china-company-ip.list) | 云厂商 IP 兜底，包含海外区域和其他租户 | 默认关闭；可选 `DIRECT` |

示例在全部自有规则之后引用两份上游兜底清单，接住自有清单没有覆盖的域名：Surge、Surfboard 使用 [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules)，Mihomo、Stash 使用 [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)，`proxy.txt` 走 `Proxies`，`direct.txt` 走 `DIRECT`。两份清单由上游每天自动构建，本仓库不镜像，刷新间隔为 86400 秒。`proxy.txt` 必须排在 `direct.txt` 之前；不需要国内直连兜底时，同时移除这两条引用。详见[上游兜底清单](docs/rule-behavior.md#上游兜底清单)。

`DisneyPlus.list`、`Extra_CN.list`、`Extra_CN_2.list` 由现有托管订阅引用。它们沿用原 `naiixi.com` 清单内容与匹配顺序。`Extra_CN_2.list` 保留了对 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 的来源署名，许可见 [GPL-2.0](licenses/blackmatrix7-GPL-2.0.txt)。

ACL4SSR 的六份快照按各自文件中的 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可维护。快照来自原 Surge 规则缓存，保留规则顺序、匹配选项和上游注释，新增来源和许可说明。测速规则保留托管 Surge 原有七条域名规则和一条 HTTP User-Agent 规则。

`ai-shared.list` 会同时影响使用相同 Google 登录或 Cloudflare 验证域名的其他网站；不需要时可以移除这份规则的引用。其他客户端和 Surge iOS 使用域名规则，不加载 Mac 进程规则。更细的适用范围见[规则说明](docs/rule-behavior.md)。

扩展共享依赖走 `Proxies`，`api.github.com`、`www.google.com`、部分公共 CDN 等主机的全部流量都使用普通代理出口，不占用 AI 出口。`ai.list` 已有的整个 `googleapis.com` 覆盖继续保留，也会影响非 AI 的 Google API。

## 自动更新

示例直接引用 `main` 分支的远程规则，刷新间隔为 **3600 秒（1 小时）**。以后修改现有 `.list` 文件并合入 `main`，客户端会按自身刷新机制获取内容，无需重新导入整份配置。客户端须能访问 `raw.githubusercontent.com`；离线、后台限制和缓存可能推迟生效，需要立即使用时可手动刷新远程规则。

Surge、Mihomo 和 Stash 各自管理规则资源；[Surfboard](https://getsurfboard.com/docs/profile-format/rule/ruleset/) 的后台下载会在下次启动 VPN 时应用。配置订阅更新与规则资源刷新是两个独立过程。

新增或重命名规则文件、改变策略组或匹配顺序时，仍需同步调整客户端配置；客户端不会自动发现仓库里的新文件。

已有 Surge VM 网关、CoreDNS 或 Tailscale 的环境，只合并所需规则引用，保留本机网络和 DNS 配置；具体边界见[本机配置与上游更新](docs/rule-behavior.md#本机配置与上游更新)。

规则来源、匹配边界见[规则说明](docs/rule-behavior.md)；参与维护见[贡献指南](CONTRIBUTING.md)。
