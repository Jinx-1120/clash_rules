# 规则说明

规则按客户端配置中的顺序匹配，先命中的规则决定出口。推荐顺序为：节点入口和本地例外、内网、明确直连、AI 域名、AI 共享服务、Mac AI 进程、普通代理、其他分类与最终兜底。策略组名称由使用者决定，规则文件本身不包含策略列。

## 内网与直连

`LocalAreaNetwork.list` 来自 [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR/blob/master/Clash/LocalAreaNetwork.list)，保留来源注释和 IP 项的 `no-resolve` 语义。它包含本地/保留地址、局域网后缀和路由器管理域名，是单独维护的副本，不自动跟踪上游。

IP 项的 `no-resolve` 避免为了匹配内网地址而主动解析每一个公网域名。本地回调、自己的节点入口和私有域名应保留明确的 DIRECT 例外，并排在进程和通用代理规则之前。私有环境信息放在自己的客户端配置中。

`no_proxy.list` 与 `proxy.list` 分别是明确直连和代理的补充清单，并非完整的地区或广告过滤规则库。发生重叠时，以主配置中的先后顺序为准。

## AI 域名与共享服务

`ai.list` 覆盖已知的 AI 服务域名，不保证第三方插件、自定义网关和未来新增端点全部命中。

`ai-shared.list` 单独提供共享主机的分流：`accounts.google.com` 会影响其他 Google 登录，`challenges.cloudflare.com` 会影响其他网站的挑战。TLS 不解密时，不能根据网页来源或加密路径可靠地区分这些请求。可以停用这份规则，但部分 AI 登录或验证请求会随其他规则选择出口。

GitHub 通用登录/API 不属于 AI 共享清单，Copilot 专属服务域名在 `ai.list` 中。独立 Grok 网站/API 属于 AI；X/Twitter 内嵌 Grok 使用的 `x.com` 仍按普通社交规则处理。如需同一出口，可手动为相关策略组选择相同节点。

## Mac 进程匹配

`ai-process-surge.list` 适用于 Surge Mac 6+，不能作为 Mihomo、Stash 或 Surfboard 的进程规则加载。Surge iOS 使用域名规则。

- App bundle 路径覆盖其 Helper、服务和内置工具，也可能包含下载或浏览器流量。
- 专用 CLI 按可执行文件名或安装路径匹配；Claude 的版本目录和 Cursor 的专用安装目录另有覆盖。路径区分大小写，非标准安装位置可能需要本地补充。
- 外部 `curl`、Python、Node、Chrome、SSH、MCP 和编辑器扩展宿主不继承父进程身份，仍按自身进程和目标域名匹配；没有把通用 `node`、`Electron` 或 `java` 全部划入 AI。
- 远程主机或云端执行的请求不由本机进程规则控制。

这些规则不要求关闭 TLS 校验或启用 MITM。出口的协议、UDP 能力和服务可用性由节点与客户端决定。

## 客户端格式与刷新

Surge 使用 `RULE-SET`；Mihomo / OpenClash 与 Stash 使用 `behavior: classical`、`format: text` 的 HTTP rule provider，并在 `rules` 中引用它。示例使用 3600 秒刷新；刷新失败或客户端暂停时，不代表已经获取最新内容。需要确认生效时，在客户端资源页检查更新时间，并查看请求的实际命中规则。

- [Surge 规则集](https://manual.nssurge.com/rules/ruleset.html)、[进程匹配](https://manual.nssurge.com/rules/process.html)、[规则顺序](https://manual.nssurge.com/rules/overview.html)
- [Mihomo 规则集合](https://wiki.metacubex.one/config/rule-providers/)
- [Stash 规则集](https://stash.wiki/en/rules/rule-set)
- [Surfboard 规则集](https://getsurfboard.com/docs/profile-format/rule/ruleset/)

## AI 服务参考

- [Claude Code 网络要求](https://code.claude.com/docs/en/network-config)、[Claude Desktop 网络要求](https://code.claude.com/docs/en/desktop#network-access-requirements)
- [Cursor 网络清单](https://cursor.com/docs/enterprise/network-configuration)
- [GitHub Copilot allowlist](https://docs.github.com/en/copilot/reference/copilot-allowlist-reference)
- [xAI API](https://docs.x.ai/developers/rest-api-reference/inference)
- [Google Antigravity 文档](https://www.antigravity.google/docs/home)

官方网络说明和客户端观测可作为补充规则的依据；安装包中出现的端点字符串只代表候选依赖，不能单独证明实际请求或必要性。
