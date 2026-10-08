# AI 日报｜2026-10-08

数据生成时间：2026-10-08T10:40:27+08:00（北京时间）

AI HOT：18 条；TrendRadar：15 条 AI 相关热点。
实际采集快照：3 个；平台：11 个。

以下为两处信息源的完整收录，不代表已经逐条独立核实。

来源状态：AI HOT=live；TrendRadar=live。

## AI HOT 完整资讯

### A1｜【AIHOT 通知】旧版接口 2026 年 10 月 31 日停用，推送机器人和脚本请尽快迁移

这条消息来自 AIHOT 旧版接口 /api/public/*：它将于 2026 年 10 月 31 日停用，之后这里不会再有新资讯。如果它是群机器人或脚本推送来的，请转告维护的人把地址换成 https://aihot.news/api/v1，字段一一对应；迁移指南和可以直接交给 AI 改写代码的提示词见 https://aihot.news/agent?tab=api#legacy-api-migration 。同一天起旧域名 aihot.virxact.com 的所有地址都只跳转到 aihot.news，RSS、MCP 等地址也请换成新域名；收藏的网页链接照样能打开。

来源：AIHOT；发布时间：2026-10-08T02:00:00Z

原文：https://aihot.news/agent?tab=api#legacy-api-migration
收录页：https://aihot.news/agent?tab=api#legacy-api-migration

### A2｜GPT-6 Luna Decisions 上架 OpenRouter

OpenRouter 宣布 GPT-6 Luna Decisions 上线。OpenAI 的 Decisions API 可让应用选择合适的模型、工具或动作，支持发送文本、JSON 或图片并返回带概率的类型化答案。定价为输入 $0.10/M、输出免费，上下文 1M；引用 OpenAI 开发者账号称其决策速度比通过 Responses API 的 GPT-6 Luna 最快 10 倍。

来源：X：OpenRouter (@OpenRouter)；发布时间：2026-10-07T20:21:00Z

原文：https://x.com/OpenRouter/status/2107929204142874759
收录页：https://aihot.news/items/x40bi9csoomsdaflejehop22y

### A3｜Anthropic 发布 Claude Haiku 5.5，Artificial Analysis 智能指数得分 43

Anthropic 发布 Claude Haiku 5.5，在 Artificial Analysis 智能指数得 43 分，较上一代 Haiku 一年内提升 26 分。

来源：X：Artificial Analysis (@ArtificialAnlys)；发布时间：2026-10-07T19:12:16Z

原文：https://x.com/ArtificialAnlys/status/2107911905822351609
收录页：https://aihot.news/items/r8dupnljjbgk9r9lio9w0o6u6

### A4｜LangChain 重构 Deep Agents 的 Skills 支持，新增工具绑定、固定技能与线程内重载

LangChain 重构 Deep Agents 的 Skills 支持，针对企业技能库增至数千个技能的场景推出三项更新：工具可绑定到技能、仅在该技能被读取时加载，用户可通过 /meeting-prep 之类的显式请求固定技能以在首次模型调用前加载，长线程可通过将 skills_metadata 设为 None 重载新增或变更的技能。

来源：LangChain：Blog（RSS）；发布时间：2026-10-07T18:49:50Z

原文：https://www.langchain.com/blog/revamping-skills-in-deep-agents
收录页：https://aihot.news/items/m3vyz2bex4i58vffqfx586u3h

### A5｜NVIDIA 与 Microsoft 推出 RTX Spark 平台并宣布 MXC 让 AI Agent 落地 Windows PC

NVIDIA 与 Microsoft 在旧金山活动上宣布为 Windows PC 共同打造 AI Agent 软硬件。

来源：NVIDIA Blog（RSS）；发布时间：2026-10-07T18:45:28Z

原文：https://blogs.nvidia.com/blog/local-ai-rtx-spark-microsoft-windows-event/
收录页：https://aihot.news/items/t02toac3ii8mp1lxzl4blewdd

### A6｜Cursor 公布 Claude Haiku 5.5 定价并下调 Claude Sonnet 5.5 缓存读取价格

Cursor 公布 Claude Haiku 5.5 定价为每 M 输入 token $0.10、输出 token $0.50，输入超过 100k token 时为 $0.50/M 和 $2.50/M。Claude Sonnet 5.5 缓存读取价格也从 $0.20/M 降至 $0.10/M，用户可在 cursor.com/evals 上通过 CursorBench 对比 Haiku 5.5 的表现。

来源：X：Cursor (@cursor_ai)；发布时间：2026-10-07T18:14:03Z

原文：https://x.com/cursor_ai/status/2107897257651769464
收录页：https://aihot.news/items/vk1sotxx6v25hhgn55mwgv4nv

### A7｜Claude Code v2.1.293 发布：新增 Claude Haiku 5.5 并修复大量问题

Claude Code 发布 v2.1.293，新增 Claude Haiku 5.5（claude-haiku-5-5）作为 Anthropic API 默认 Haiku 模型，支持 1M 上下文，价格为 $0.10/$0.50 每百万 token（超 100K 提示为 $0.50/$2.50）。

来源：Claude Code：GitHub Releases（RSS）；发布时间：2026-10-07T18:10:20Z

原文：https://github.com/anthropics/claude-code/releases/tag/v2.1.293
收录页：https://aihot.news/items/vd2lvzvjz4tujiqupl30ifq3k

### A8｜Anthropic 为 Claude Max 和 Team 套餐推出月度 Platform API 额度

Anthropic 正在为 Claude Max 和 Team 套餐推出月度 Claude Platform API 额度：Max 5x 为 $100，Max 20x 为 $200，Team 最多 $500 且可共享。额度适用于任何模型，包括 Haiku 5.5，可在自己的代码或第三方 harness 中使用。

来源：X：Claude Devs (@ClaudeDevs)；发布时间：2026-10-07T18:08:53Z

原文：https://x.com/ClaudeDevs/status/2107895957933408429
收录页：https://aihot.news/items/ponkn6n046yorr5pg1yv3yjm5

### A9｜Anthropic 将 Claude Sonnet 5.5 缓存读取价格减半至每百万 token $0.10

Anthropic 宣布将 Claude Sonnet 5.5 的缓存读取价格减半，降至每百万 token $0.10。官方称这使 Sonnet 5.5 在多数长期运行任务上的运行成本降低约 20%。

来源：X：Claude (@claudeai)；发布时间：2026-10-07T18:01:21Z

原文：https://x.com/claudeai/status/2107894060229034197
收录页：https://aihot.news/items/zn6imszjo14gki6kr2uyydknp

### A10｜OpenAI 向全部 ChatGPT 用户推出 GPT-6 与 Intelligent UI

OpenAI 发布面向更广泛用户的 GPT-6，并随 GPT-6 在 ChatGPT 中引入 Intelligent UI，可生成图形、按钮、表单、图表和可交互组件来回答问题。

来源：OpenAI：官网动态（RSS · 排除企业/客户案例）；发布时间：2026-10-07T18:00:58Z

原文：https://openai.com/index/gpt-6-for-everyone/
收录页：https://aihot.news/items/uir31g728myjry383z17txvrw

### A11｜Perplexity 开源 pplx-embed-v2-late 多模态 late-interaction 嵌入模型（9B 与 0.6B）

Perplexity 开源 pplx-embed-v2-late，两个针对文本和图像的 late-interaction 多向量嵌入模型，大小为 9B 和 0.6B，共享同一嵌入空间，权重已在 Hugging Face 提供。9B 可用于索引多模态数据，0.6B 可在设备端查询，无需 OCR 即可检索 PDF 页面；模型在 MADQA 得分 92.4%，BrowseComp+ 得分 64%。

来源：X：Aravind Srinivas（Perplexity CEO） (@AravSrinivas)；发布时间：2026-10-07T16:33:02Z

原文：https://x.com/AravSrinivas/status/2107871834205196784
收录页：https://aihot.news/items/lfy2ww68p9lgpxxhu5jssflwf

### A12｜Unsloth 开源教程：本地训练 Qwen3.5 0.8B 决策模型，准确率从 20.7% 提升至 74.3%

Unsloth 发布教程与开源仓库，可将 Qwen3.8、Gemma 4 等 LLM 微调为输出选项概率的决策模型，Qwen3.5 0.8B 在 3 个决策基准上的合计准确率从 20.7% 提到 74.3%，仅需 4GB 显存。

来源：X：Unsloth (@UnslothAI)；发布时间：2026-10-07T16:21:14Z

原文：https://x.com/UnslothAI/status/2107868866361930236
收录页：https://aihot.news/items/y7db2ly158hip5dw1evmjw5kv

### A13｜Microsoft Research Asia 开源 Agent Lightning v1.0：3,500 行代码的真实 harness 智能体 RL 训练框架

Microsoft Research Asia 提出 Harnessed Agentic RL 训练范式并开源重建的 Agent Lightning v1.0，让部署时使用的同一 agent harness 直接参与强化学习，无需在训练框架内重写 agent。

来源：Microsoft Research 博客（RSS）；发布时间：2026-10-07T16:00:00Z

原文：https://www.microsoft.com/en-us/research/blog/agent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses/
收录页：https://aihot.news/items/t9wypjd9cbb42ttuq7vrpp07l

### A14｜亚利桑那州法院裁定 AI 生成受害者视频带有不当情感分量 将重新量刑

亚利桑那州上诉法院裁定，Gabriel Horcasitas 2021 年路怒枪杀 Christopher Pelkey 一案维持过失杀人定罪，但因量刑听证中播放的 AI 生成受害者视频带有不当情感分量，法官须重新考虑刑期。

来源：404 Media（RSS）；发布时间：2026-10-07T14:46:15Z

原文：https://www.404media.co/undue-emotional-weight/
收录页：https://aihot.news/items/iz93flwr7h9m7po4wnu8sm4hy

### A15｜Google 开放 SynthID Detector 门户，可检测图片、视频和音频是否由 AI 生成

Google 介绍检测媒体是否由 AI 生成的方法：访问 https://synthid.com 上传图片、视频或音频文件，门户会扫描文件是否包含来自 Google 或其合作伙伴的 SynthID 水印。

来源：X：Google (@Google)；发布时间：2026-10-07T14:12:16Z

原文：https://x.com/Google/status/2107836410254291345
收录页：https://aihot.news/items/don06si59xc143ed92gdmlnvo

### A16｜a16z 解析德州为何让数据中心排队等电

a16z 的 Ryan McEntush 分析德州电网暂停审批数据中心的原因：并网队列从 2024 年底的 63 GW 激增到今年 6 月的 474 GW，约 90% 是数据中心，开发商大量投机性申请且社区沟通不足。

来源：a16z：News（RSS）；发布时间：2026-10-07T14:01:44Z

原文：https://www.a16z.news/p/why-texas-is-making-data-centers
收录页：https://aihot.news/items/yk3grmalszldrwd1p8bxk0cki

### A17｜Nemotron 系列微调后达到 IOI 2026 与 IMO 2026 金牌水平

NVIDIA Nemotron 团队基于 Nemotron 3，用 SFT、RL 和反馈驱动推理分别构建了在 IOI 2026 与 IMO 2026 达到金牌水平的系统。

来源：Hugging Face 社区博客（混合发现）；发布时间：2026-10-07T12:45:31Z

原文：https://huggingface.co/blog/nvidia/nemotron-ioi-and-imo-2026
收录页：https://aihot.news/items/r96kyuxfie0w9mup4206gzn29

### A18｜Mistral Large 4 进入 Code Arena: WebDev 排名第45，得分1534

Arena 宣布 Mistral Large 4 登陆 Code Arena: WebDev，以 1534 分排名第 45，比 Mistral Large 3（第130名）高 304 分，比 Mistral Medium 3.5 高 271 分。

来源：X：Arena (@arena)；发布时间：2026-10-07T06:18:23Z

原文：https://x.com/arena/status/2107717155374727602
收录页：https://aihot.news/items/kxqn0rzbtjdxg7ibbjge08tzt

## TrendRadar 完整 AI 热点

### N1｜数学大爆炸！OpenAI 一夜攻克722个数学难题，准黎曼猜想已被证明

平台：华尔街见闻；榜单排名：3；实际出现快照数：3。

链接：https://wallstreetcn.com/articles/3783101

### N2｜标普500创出新高，但几乎只有AI交易在涨

平台：华尔街见闻；榜单排名：3；实际出现快照数：2。

链接：https://wallstreetcn.com/articles/3783091

### N3｜人形机器人进驻爱仕达百家终端：从门店上岗到产业实践

平台：财联社热门；榜单排名：5；实际出现快照数：3。

链接：https://www.cls.cn/detail/2495303

### N4｜Claude Haiku5.5发布

平台：bilibili 热搜；榜单排名：6；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=Claude+Haiku5.5%E5%8F%91%E5%B8%83

### N5｜吧友教AI写文,焚诀大公开

平台：贴吧；榜单排名：6；实际出现快照数：3。

链接：https://tieba.baidu.com/hottopic/browse/hottopic?amp%3Btopic_name=%E5%90%A7%E5%8F%8B%E6%95%99AI%E5%86%99%E6%96%87%2C%E7%84%9A%E8%AF%80%E5%A4%A7%E5%85%AC%E5%BC%80&topic_id=28366390

### N6｜苏姿丰：AI芯片需求非常旺盛 AMD将持续大幅扩产

平台：财联社热门；榜单排名：7；实际出现快照数：2。

链接：https://www.cls.cn/detail/2498239

### N7｜Claude拿下概率论「圣杯」，AI跨过菲尔兹奖终点线

平台：华尔街见闻；榜单排名：8；实际出现快照数：3。

链接：https://wallstreetcn.com/articles/3783107

### N8｜AI公开的722篇论文会影响数学吗

平台：bilibili 热搜；榜单排名：10；实际出现快照数：2。

链接：https://search.bilibili.com/all?keyword=AI%E5%85%AC%E5%BC%80%E7%9A%84722%E7%AF%87%E8%AE%BA%E6%96%87%E4%BC%9A%E5%BD%B1%E5%93%8D%E6%95%B0%E5%AD%A6%E5%90%97

### N9｜美股三季报下周拉开帷幕：标普500每股收益预计增长27%，英伟达和美光两家公司将贡献1/3

平台：华尔街见闻；榜单排名：10；实际出现快照数：1。

链接：https://wallstreetcn.com/articles/3783100

### N10｜谷歌签下科技史上最大核能协议：3590兆瓦锁定20年，Gemini同步嵌入能源运营

平台：华尔街见闻；榜单排名：10；实际出现快照数：1。

链接：https://wallstreetcn.com/articles/3783087

### N11｜如何看待 OpenAI 公开 722 份数学手稿，宣布解决包含「准黎曼猜想」的数百个数学问题？

平台：知乎；榜单排名：12；实际出现快照数：2。

链接：https://www.zhihu.com/question/2091064625987170716

### N12｜AI算力订单暴增至500亿美元！英伟达支持的Lambda拟融资40亿美元冲刺IPO

平台：财联社热门；榜单排名：13；实际出现快照数：1。

链接：https://www.cls.cn/detail/2498406

### N13｜当AI浪潮遭遇“减速”之问，回看30年前那场浪潮走向

平台：澎湃新闻；榜单排名：17；实际出现快照数：1。

链接：https://www.thepaper.cn/newsDetail_forward_34141698

### N14｜AI短片生化危机爆发夜前传

平台：bilibili 热搜；榜单排名：21；实际出现快照数：2。

链接：https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E7%89%87%E7%94%9F%E5%8C%96%E5%8D%B1%E6%9C%BA%E7%88%86%E5%8F%91%E5%A4%9C%E5%89%8D%E4%BC%A0

### N15｜OpenAI全面上线GPT-6

平台：百度热搜；榜单排名：24；实际出现快照数：1。

链接：https://www.baidu.com/s?wd=OpenAI%E5%85%A8%E9%9D%A2%E4%B8%8A%E7%BA%BFGPT-6

核对：AI HOT 18 条；TrendRadar 15 条。
