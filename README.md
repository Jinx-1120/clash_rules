# clash_rules

个人维护的分流规则。`proxy.list` / `no_proxy.list` 保持原用途；AI 规则独立维护，不包含节点、账号、订阅令牌或私有 API 地址。

## 内网规则

[LocalAreaNetwork.list](LocalAreaNetwork.list) 同步自 [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR/blob/master/Clash/LocalAreaNetwork.list)，保留来源注释和 `no-resolve` 语义。包含内网/保留地址、局域网后缀和路由器管理域名；`tplogin.cn`、`zte.home`、`www.asusrouter.com` 上游已包含，各保留一次；前两者为后缀规则，后者为精确域名规则。

Surge 使用以下规则；Mihomo 使用同一 URL，配置为 `behavior: classical`、`format: text`，策略为 `DIRECT`。应放在 AI 应用进程规则及通用代理规则之前，让路由器域名优先直连。IP 项的 `no-resolve` 不会主动解析未知域名；额外的私有域名应在自己的私有配置中维护，不上传到公共清单。

```ini
RULE-SET,https://raw.githubusercontent.com/Jinx-1120/clash_rules/main/LocalAreaNetwork.list,DIRECT,update-interval=86400
```

这是独立维护的副本，不会自动追踪上游。后续同步先审阅上游变化、保留本地条目、去重并运行测试，再发布。

## AI 规则

| 文件 | 用途 / 格式 |
| --- | --- |
| [ai.list](ai.list) | OpenAI/ChatGPT/Codex、Claude、Antigravity/Gemini、Cursor、Grok/xAI、GitHub Copilot，以及既有 Perplexity 等服务的域名；Surge RULE-SET / Mihomo classical text |
| [ai-process-surge.list](ai-process-surge.list) | Surge Mac 6+ 的 App bundle、Helper、服务与独立 CLI 路径兜底；不要作为 Mihomo provider 加载；iOS 不提供进程匹配 |
| [ai-shared.list](ai-shared.list) | 共享登录、挑战与特定功能服务；按域名整体分流，有意独立以便选择是否启用 |

维护日期：2026-09-18。覆盖已知核心域名与本地进程，不承诺未来新增服务、任意插件、自定义模型网关或云端执行流量全部被捕获。

## Surge 接入

先创建名为 `AI` 的策略组。把回环、局域网、OAuth 本地回调和实际 VPN 节点入口的 DIRECT 例外放在这些规则之前；AI 规则放在 Google、GitHub、Twitter、国内 IP/GEOIP 和 FINAL 等通用规则之前：

```ini
[Rule]
# 保留自己已有的节点入口 DIRECT 例外；以下是本地网络例外示例。
IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
IP-CIDR,169.254.0.0/16,DIRECT,no-resolve
IP-CIDR6,::1/128,DIRECT,no-resolve
IP-CIDR6,fc00::/7,DIRECT,no-resolve
IP-CIDR6,fe80::/10,DIRECT,no-resolve
DOMAIN,localhost,DIRECT
DOMAIN-SUFFIX,local,DIRECT
RULE-SET,https://raw.githubusercontent.com/Jinx-1120/clash_rules/main/ai.list,AI,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Jinx-1120/clash_rules/main/ai-shared.list,AI,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Jinx-1120/clash_rules/main/ai-process-surge.list,AI,update-interval=86400
# 后接自己的普通规则与 FINAL。
```

不要让前面的 IP 规则先解析所有 AI 域名；`no-resolve` 的例外仅针对 IP 已知的请求。额外私有 LAN 域名按本机环境保留精确 DIRECT，不要把全部公网解析结果归为本地。

Mihomo 可用 `behavior: classical`、`format: text` 引用 `ai.list` 和 `ai-shared.list`，并在规则中加入 `RULE-SET,提供方名称,AI`。进程文件是 Surge 专用，路径规则不能原样移植。

## 影响范围与无法自动区分的情况

- `ai-shared.list` 的 `accounts.google.com` 会影响其他 Google 登录；`challenges.cloudflare.com` 会影响其他网站的挑战。GitHub 通用登录和 API 域名已按既有远程修改移出 AI 共享列表，Copilot 专属端点仍在 `ai.list`。TLS 不解密时，不能按网页来源或 `/login` 路径可靠区分共享主机。文件可整体停用或自行维护更小的副本，但相关登录可能变为其他出口。
- 不加入全量 `google.com`、`googleapis.com`、`githubusercontent.com`、`cloudflare.com`、`sentry.io`，也不依赖整个云厂商 ASN 或宽泛 `openai` 关键词。普通代码下载、包管理、共享 CDN 和遥测可继续使用普通规则。
- 独立 Grok 网站/API 走 AI。**X/Twitter 内嵌 Grok** 的 `x.com` 请求仍属于现有 Twitter 分流；若必须同一出口，应让 Twitter 与 AI 选择同一出口或使用隔离的专用浏览器。不能在不影响 Twitter 的同时，用域名规则区分其加密页面路径。
- Copilot 的专属服务域名和独立 `copilot` CLI 已覆盖。VS Code/JetBrains 的共享扩展宿主、npm 版运行时可能叫 `node`/`Electron`/`java`，没有把这些通用进程整体划入 AI。核心 Copilot 域名仍可命中；第三方插件和自定义 Enterprise 主机按实际目标补充。
- Surge 按实际可执行文件匹配，不沿父子关系继承。App 内 Helper/语言服务由 bundle 路径覆盖；外部系统 `curl`、Python、Node、Chrome、SSH 和 MCP 由自己的进程及目标规则决定。云端/远程主机发出的请求不受本机规则控制。
- 本机观察到 Claude 的原生 CLI 使用 `~/.local/share/claude/versions/<version>`，因此同时覆盖版本目录，避免只匹配启动 symlink 名称。路径匹配区分大小写；非标准安装位置需补充。
- App bundle 规则覆盖其中的下载、浏览器和工具进程，会增加 AI 出口流量。固定 ISP 的带宽、UDP 能力和账号可用性由出口决定；规则命中不证明语音/WebRTC、登录或流式会话成功。不关闭 TLS 校验或启用 MITM 来实现本清单。

## 验证与维护

```sh
python3 -m unittest discover -s tests -v
```

测试涵盖域名/进程正反例、版本化路径、共享身份边界、重复项和禁止的宽泛匹配。修改后还要通过 Surge 原生格式检查、实际 `rule explain` 和必要的业务验证；离线匹配测试不是 Surge 引擎替身。

```sh
surge-cli rule explain api.openai.com
surge-cli rule explain platform.claude.com
surge-cli rule explain cloudcode-pa.googleapis.com
surge-cli rule explain api2.cursor.sh
surge-cli rule explain api.x.ai
surge-cli rule explain api.githubcopilot.com
surge-cli rule explain example.com process-path=/Applications/ChatGPT.app/Contents/Resources/codex
surge-cli rule explain 127.0.0.1 process-path=/Applications/ChatGPT.app/Contents/Resources/codex
```

发布后检查远程文件实际内容与客户端资源就绪状态。主配置更新与规则集的 `86400` 秒刷新是不同的时钟；需要立即生效时在客户端刷新相应资源并读回匹配结果。

## 依据

- [Surge 进程匹配](https://manual.nssurge.com/rules/process.html)、[规则与 DNS 顺序](https://manual.nssurge.com/rules/overview.html)。
- [OpenAI Codex 身份认证](https://learn.chatgpt.com/docs/auth)，以及本机 OpenAI App 连接和既有规则的域名核对；登录可以在外部浏览器进行。
- [Claude Code 网络要求](https://code.claude.com/docs/en/network-config)、[Desktop 网络要求](https://code.claude.com/docs/en/desktop#network-access-requirements)。
- [Cursor 官方网络清单](https://cursor.com/docs/enterprise/network-configuration)：专属服务、嵌套计算机域名和更新源。
- [GitHub Copilot allowlist](https://docs.github.com/en/copilot/reference/copilot-allowlist-reference)：认证、专属 API、遥测及不同订阅计划的子域。
- [xAI 官方 API](https://docs.x.ai/developers/rest-api-reference/inference)。
- [Google Antigravity 文档](https://www.antigravity.google/docs/home)；补充核对本机官方安装包的 `extensions/antigravity/bin/language_server_macos_arm` 和扩展脚本中的端点字符串。字符串存在只证明候选依赖，不能证明每个地址本次都被访问。
