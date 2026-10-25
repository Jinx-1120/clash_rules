# 规则说明

规则按客户端配置中的顺序匹配，先命中的规则决定出口。推荐顺序为：节点入口和本地例外、内网、明确直连、大陆 AI、海外 AI 域名及共享服务、语音 IP、Mac AI 进程、普通代理、其他分类、可选云厂商 IP、地区规则与最终兜底。策略组名称由使用者决定，规则文件本身不包含策略列。已有服务分类需要优先于 Mac 进程规则时，将进程规则留在这些分类之后。

## 内网与直连

`LocalAreaNetwork.list` 来自 [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR/blob/master/Clash/LocalAreaNetwork.list)，保留来源注释和 IP 项的 `no-resolve` 语义。它包含本地/保留地址、局域网后缀和路由器管理域名，是单独维护的副本，不自动跟踪上游。

IP 项的 `no-resolve` 避免为了匹配内网地址而主动解析每一个公网域名。本地回调、自己的节点入口和私有域名应保留明确的 DIRECT 例外，并排在进程和通用代理规则之前。私有环境信息放在自己的客户端配置中。

`no_proxy.list` 与 `proxy.list` 分别是明确直连和代理的补充清单，并非完整的地区或广告过滤规则库。发生重叠时，以主配置中的先后顺序为准。

教育域名直连使用 `DOMAIN-SUFFIX,edu.cn`，匹配 `edu.cn` 和其子域名，不再匹配 `notedu.cn` 或 `edu.cn.example.com` 等仅含相同文字的域名。

## AI 域名与共享服务

`ai.list` 覆盖已知的 AI 服务域名，不保证第三方插件、自定义网关和未来新增端点全部命中。

保留现有 `DOMAIN-SUFFIX,googleapis.com` 设计：`maps.googleapis.com`、`storage.googleapis.com` 与 Google OAuth API 也会使用 AI 策略。这是有意保留的宽范围，并非仅限 Gemini 的主机清单；`google.com`、`github.com` 和整个共享云/CDN 后缀仍不在这份规则中。

`ai-mainland.list` 单独维护大陆服务与北京区域端点，示例通过 `MainlandAI` 默认直连，也可自行选择代理。Qwen、Moonshot、MiniMax、Z.ai 的国际域名与阿里云新加坡、美国、欧洲、日本、香港的具体模型服务端点放在 `ai.list`。区域端点和路由选择不保证账号资格、服务地区支持或实际可用性。

`ai-shared.list` 单独提供共享主机的分流：`accounts.google.com` 会影响其他 Google 登录，`challenges.cloudflare.com` 会影响其他网站的挑战。TLS 不解密时，不能根据网页来源或加密路径可靠地区分这些请求。可以停用这份规则，但部分 AI 登录或验证请求会随其他规则选择出口。

`ai-shared-extra.list` 是默认关闭的扩展清单，承接新增的共享依赖，不扩大原有 `ai-shared.list` 的默认范围。其中 `api.github.com` 也用于普通 GitHub API，`www.google.com` 与 Google 静态资源也用于搜索和其他 Google 产品；WorkOS、Microsoft/JetBrains 登录、Cognito、Intercom、Stripe、hCaptcha、AWS WAF、公共脚本 CDN 与指定遥测主机也会影响其他服务。启用表示接受这些主机的全部请求走 AI 出口，不能仅按调用页面选择。

Copilot 专属服务域名在 `ai.list` 中，通用 GitHub API 只有启用扩展共享清单才会被它捕获。独立 Grok 网站/API 属于 AI；X/Twitter 内嵌 Grok 使用的 `x.com` 仍按普通社交规则处理。如需同一出口，可手动为相关策略组选择相同节点。

## 语音与可选云厂商 IP

`ai-voice.list` 是 [OpenAI 官方语音网段](https://openai.com/chatgpt-voice.json)的 2026-10-24 获取快照，当前含 23 条 IPv4 网段，使用 `no-resolve`，独立于纯域名清单。语音优先使用 UDP 3478，节点和客户端须具备相应 UDP 能力；规则本身不会启用 UDP 转发。源数据会变化，维护时需重新获取并核对差异；客户端刷新仓库文件不等同于仓库自动同步官方 JSON。网络要求见 [ChatGPT 官方说明](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps)。

`china-company-ip.list` 的 208 条网段于 2026-10-24 与 [ACL4SSR ChinaCompanyIp.list](https://github.com/ACL4SSR/ACL4SSR/blob/master/Clash/ChinaCompanyIp.list)核对一致，反映云厂商归类，不保证中国大陆地理位置，也不能区分同一云厂商上的租户。示例默认关闭；启用时放在明确域名和服务分类之后、GEOIP/FINAL 之前。沿用本地优化，移除源文件各项的 `no-resolve`，允许未解析域名到此触发解析，以便作为 IP 兜底；因此不要前移到 AI 域名之前，也不要在父级规则加 `no-resolve` 后仍期待触发查询。

## Mac 进程匹配

`ai-process-surge.list` 适用于 Surge Mac 6+，不能作为 Mihomo、Stash 或 Surfboard 的进程规则加载。Surge iOS 使用域名规则。

- App bundle 路径覆盖其 Helper、服务和内置工具，也可能包含下载或浏览器流量。
- 专用 CLI 按可执行文件名或安装路径匹配；Claude 的版本目录和 Cursor 的专用安装目录另有覆盖。路径区分大小写，非标准安装位置可能需要本地补充。
- 外部 `curl`、Python、Node、Chrome、SSH、MCP 和编辑器扩展宿主不继承父进程身份，仍按自身进程和目标域名匹配；没有把通用 `node`、`Electron` 或 `java` 全部划入 AI。
- 远程主机或云端执行的请求不由本机进程规则控制。

这些规则不要求关闭 TLS 校验或启用 MITM。出口的协议、UDP 能力和服务可用性由节点与客户端决定。

## 客户端格式与刷新

Surge 使用 `RULE-SET`；Mihomo / OpenClash 与 Stash 使用 `behavior: classical`、`format: text` 的 HTTP rule provider，并在 `rules` 中引用它。示例使用 3600 秒刷新；刷新失败或客户端暂停时，不代表已经获取最新内容。需要确认生效时，在客户端资源页检查更新时间，并查看请求的实际命中规则。

Surge 示例为域名规则集启用 `extended-matching`，可同时根据 TLS SNI 和 HTTP Host 匹配；这不解密 TLS，也不会替其他客户端启用相同功能。Mihomo 示例中可选清单的 provider 和规则都保持注释，启用时需一起取消注释。

- [Surge 规则集](https://manual.nssurge.com/rules/ruleset.html)、[进程匹配](https://manual.nssurge.com/rules/process.html)、[规则顺序](https://manual.nssurge.com/rules/overview.html)
- [Mihomo 规则集合](https://wiki.metacubex.one/config/rule-providers/)
- [Stash 规则集](https://stash.wiki/en/rules/rule-set)
- [Surfboard 规则集](https://getsurfboard.com/docs/profile-format/rule/ruleset/)

## 本机配置与上游更新

上游保存通用规则、无真实节点的示例及测试。本机 VM 的地址、网关、CoreDNS 监听与转发、Tailscale 原生 DNS 和路由、控制域名的 `always-real-ip` 例外、私有端点复合规则及专用出口、订阅授权和模块设置继续由本机维护。更新规则时保留这些设置，不用示例覆盖完整配置；特定私网出口规则还须排在通用内网直连之前。

已有客户端不会自动引用新增清单。需要迁移本地文件时，只替换对应的 `[Rule]` 引用；若原配置还用 `[Host]` 为该域名清单分配 DNS，同步替换对应的 `RULE-SET:` 路径并保留原 DNS 服务器与顺序。大陆域名仍使用本机选择的大陆解析路径，海外域名及选用的共享依赖使用本机选择的海外解析路径。IP 与进程清单不加入 DNS 分类。这里不提供固定的 DNS 服务器或 VM 地址。

`[Host]` 指定 DNS 上游作用于 Surge 自己执行的查询，不等于所有代理目标由本地解析；见 [Surge DNS 映射](https://manual.nssurge.com/dns/local-dns-mapping.html)。本地运行配置、模块和服务不随规则仓库推送被覆盖，但对已引用的 `ai.list` 等文件的更新仍会改变实际路由。发布前检查格式和匹配范围，发布后另行验收真实请求；冷启动及家庭设备连通性需要在对应环境单独验证。

## AI 服务参考

- [Claude Code 网络要求](https://code.claude.com/docs/en/network-config)、[Claude Desktop 网络要求](https://code.claude.com/docs/en/desktop#network-access-requirements)
- [Cursor 网络清单](https://cursor.com/docs/enterprise/network-configuration)
- [GitHub Copilot allowlist](https://docs.github.com/en/copilot/reference/copilot-allowlist-reference)
- [xAI API](https://docs.x.ai/developers/rest-api-reference/inference)
- [Google Antigravity 文档](https://www.antigravity.google/docs/home)
- [OpenAI 网络域名与语音要求](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps)
- [JetBrains AI / Junie 网络要求](https://youtrack.jetbrains.com/projects/RSRP/articles/SUPPORT-A-297/How-to-allow-access-to-JetBrains-AI-Assistant-Junie-in-the-company-network-firewall-proxy)、[Kiro 防火墙与代理](https://kiro.dev/docs/privacy-and-security/firewalls/)
- [Apple 企业网络中的 Apple Intelligence / Private Cloud Compute 主机](https://support.apple.com/en-us/101555)
- [阿里云模型服务区域端点](https://www.alibabacloud.com/help/en/model-studio/regions)、[香港模型服务端点](https://www.alibabacloud.com/help/en/model-studio/hong-kong-china-global)

2026-10-24 的新增域名来自本地在用规则快照；服务域名合入 `ai.list`，通用登录、CDN 等共享依赖拆入 `ai-shared-extra.list`，不重复收录旧版快照。上述官方资料用于核对特定产品和区域端点，不表示每条本地补充域名均为官方必需项，也不表示已经逐产品完成连通性验收。

官方网络说明和客户端观测可作为补充规则的依据；安装包中出现的端点字符串只代表候选依赖，不能单独证明实际请求或必要性。
