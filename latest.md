# AI 日报｜2026-10-01

数据生成时间：2026-10-01T09:31:53+08:00（北京时间）

AI HOT：23 条；TrendRadar：19 条 AI 相关热点。
实际采集快照：2 个；平台：11 个。

以下为两处信息源的完整收录，不代表已经逐条独立核实。

采集说明：历史时段未齐；当前来源可用性见下方状态，不将缺少的历史快照伪装为已采集。单次采集不能据此判断热度升降。

来源状态：AI HOT=live；TrendRadar=live。

## AI HOT 完整资讯

### A1｜Artificial Analysis：GPT-6.1 Sol 的 Cost per Task 较 GPT-6 Sol 低约 30%

Artificial Analysis 数据显示，GPT-6.1 Sol 的 Cost per Task 约 $0.72，比 GPT-6 Sol（$1.05）低约 30%，后者已约为 GPT-5.6 Sol（$1.99）的一半。

来源：X：Artificial Analysis (@ArtificialAnlys)；发布时间：2026-10-01T00:09:22Z

原文：https://x.com/ArtificialAnlys/status/2105449959554441580
收录页：https://aihot.news/items/p3cwq54s9gugqpmljv3xm97lv

### A2｜OpenRouter 发布 Agent 模型成本与质量权衡选型框架

OpenRouter 发布一个三步框架，用于为 Agent 任务选出以最低成本达到质量门槛的模型，而不是按排行榜排名选最高分模型。方法是先按任务设定质量门槛，再用 20 到 50 条自己的示例运行廉价、中档和前沿模型并用统一评分标准计算每质量点成本，最后选出以超过运行间分数波动的余量过线的最便宜模型。

来源：OpenRouter：Announcements（RSS）；发布时间：2026-10-01T00:00:00Z

原文：https://openrouter.ai/blog/insights/cost-vs-quality-tradeoff-framework-for-agent-models/
收录页：https://aihot.news/items/v6j23p9krwwoxqvk05d9n0bfz

### A3｜OpenRouter 教程：如何在 CI 中用 LLM eval 门禁拦截 Pull Request

OpenRouter 发布教程，讲解如何用固定的 eval 集在 CI 中门禁 pull request，当通过率低于阈值时脚本以非零退出码阻止合并，做法与单元测试门禁一致。

来源：OpenRouter：Announcements（RSS）；发布时间：2026-10-01T00:00:00Z

原文：https://openrouter.ai/blog/tutorials/how-to-gate-pull-requests-on-llm-evals-in-ci/
收录页：https://aihot.news/items/ska7k3allx8q9uu8yv5vzy8zw

### A4｜OpenRouter 指南：用置信度阈值实现模型分级升级路由

OpenRouter 发布教程，讲解如何让廉价模型通过结构化输出返回 0 到 1 的置信度字段，低置信度的请求再升级到更强模型。文章强调置信分数只是自报、不是校准概率，应基于自己流量的分数段错误率排序设定阈值，并在上线后监控分数分布、升级率和未升级答案的错误率持续调整。

来源：OpenRouter：Announcements（RSS）；发布时间：2026-10-01T00:00:00Z

原文：https://openrouter.ai/blog/insights/confidence-thresholds-for-model-escalation-routing/
收录页：https://aihot.news/items/hi9uy4borcat6ams9rk5vkamo

### A5｜Gemini 4 Argon (High) 登 Arena Agent Arena 第 8 名，净提升 +7.92%

Arena 公布 Gemini 4 Argon (High) 在 Agent Arena 排名第 8，净提升分 +7.92%，每任务成本 $0.62。

来源：X：Arena (@arena)；发布时间：2026-09-30T21:35:38Z

原文：https://x.com/arena/status/2105411271525052418
收录页：https://aihot.news/items/m49i2ro59f3lqy8ocoghr9f2j

### A6｜OpenAI 发布 GPT-6.1 Sol：以 Astra 五分之一价格接近其编码与计算机操作水平

OpenAI 发布 GPT-6.1 Sol，定价为每百万 token 2 美元输入、10 美元输出、0.10 美元缓存输入，为 GPT-6 Astra 标准价格约五分之一。

来源：MarkTechPost（RSS）；发布时间：2026-09-30T21:09:24Z

原文：https://www.marktechpost.com/2026/09/30/openai-releases-gpt-6-1-sol-near-astra-coding-and-computer-use-at-one-fifth-of-astras-token-price/
收录页：https://aihot.news/items/sv8dhqgv5kccksxx30x4oa7n3

### A7｜Google DeepMind 发布 Gemini 4 Argon，面向可信网络防御者先行开放

Google DeepMind 发布新前沿模型 Gemini 4 Argon，先通过 Fairwind Program 向可信网络防御者开放，后续将逐步面向开发者、企业和消费者推出。

来源：Google DeepMind：Blog（RSS）；发布时间：2026-09-30T20:01:45Z

原文：https://deepmind.google/blog/gemini-4-argon-our-next-era-of-frontier-intelligence/
收录页：https://aihot.news/items/uob3jvsb97uh5achwaggjrhqh

### A8｜Perplexity 开放 Computer 邮件委托入口并限时免费运行任务

Perplexity 向所有人开放 Computer 的邮件委托功能，无需 Perplexity 账号，将转发或抄送 computer@perplexity.com 的任务限时免费运行。智能体会在后台完成任务并保留邮件上下文，每个邮件任务在 Computer 中作为正常会话运行，可在网页和移动端查看，并带有与应用内任务相同的审计记录。

来源：X：Aravind Srinivas（Perplexity CEO） (@AravSrinivas)；发布时间：2026-09-30T18:49:34Z

原文：https://x.com/AravSrinivas/status/2105369479190601754
收录页：https://aihot.news/items/zdncjvjrmmknlsf9tevjlrnrg

### A9｜Trump 推动二十余家科技公司签署自愿性 AI 安全协议

约二十余家科技公司签署白宫超级智能协议，承诺实施独立安全审计、定期会商并制定共同安全标准，涵盖网络安全、生物安全和化学威胁等风险。协议无法律约束力，Trump 称其具有道德约束力。文章指出 OpenAI 近期多起事故源于今年 5 至 7 月开发中的一个未发布模型，其安全委员会有效性受到特拉华和加州总检察长调查，FTC 也就 AI 智能体潜在消费者损害发起调查。

来源：Ars Technica：AI（RSS）；发布时间：2026-09-30T18:47:01Z

原文：https://arstechnica.com/tech-policy/2026/09/trump-plan-to-combat-ai-risks-hinges-on-big-tech-pals-policing-themselves/
收录页：https://aihot.news/items/huhcnz3mwim553m2t8c0jhh4b

### A10｜GPT-6.1 Sol (Max) 以 1759 分登上 Code Arena: WebDev 第 3 名

Arena 评测榜单显示，OpenAI 的 GPT-6.1 Sol (Max) 以 1759 分位列 Code Arena: WebDev 第 3 名，混合价格为 $8/MToken。相比 GPT-6 Sol (Max) 同价提升 70 分，排名上升 4 位，且在 Consumer Product 等所有类目均有提升。

来源：X：Arena (@arena)；发布时间：2026-09-30T18:42:04Z

原文：https://x.com/arena/status/2105367591174995999
收录页：https://aihot.news/items/t1wnqaj3xyl90ilvgy4poyc45

### A11｜Jensen Huang 称行业领袖在白宫签署超级智能协定

多家行业公司的领袖在白宫签署 White House Accord on Super Intelligence，约定开发该技术的公司负有安全部署和担责的首要责任。协定要求四层控制：训练和部署期间的稳健内部监控、授权内部团队验证控制有效、独立外部评估者审计、董事会独立委员会监督，参与公司还将定期会晤制定安全标准与最佳实践。

来源：X：Jensen Huang (@JensenHuang)；发布时间：2026-09-30T17:25:30Z

原文：https://x.com/JensenHuang/status/2105348324484342238
收录页：https://aihot.news/items/fr7dgcpa02ssu37g9fsmj5q9n

### A12｜FTC 以消费者保护为由对 OpenAI、Anthropic 等 AI 实验室启动全面调查

FTC 正以潜在消费者保护违规为由调查 OpenAI、Anthropic 等头部 AI 实验室，主席 Andrew Ferguson 计划通过具法律约束力的 Civil Investigative Demands 强制调取文件并质询高管，命令将在数周内发出，METR 也在审查范围之列。

来源：The Decoder：AI News（RSS）；发布时间：2026-09-30T16:20:04Z

原文：https://the-decoder.com/ftc-launches-sweeping-probe-into-openai-anthropic-and-other-ai-labs-over-consumer-protection-concerns/
收录页：https://aihot.news/items/nhob7mih29e0owj7ay28t7fvw

### A13｜Google DeepMind 发布 SynthID Bio，为 AI 生成的蛋白质嵌入可验证水印

Google DeepMind 于 9 月 30 日发布 SynthID Bio，将水印技术引入合成生物学，把不可见签名嵌入生物序列和预测结构中，使水印可在合成的物理蛋白质上验证，且在湿实验中不损害生物功能。

来源：Google DeepMind：Blog（RSS）；发布时间：2026-09-30T15:03:07Z

原文：https://deepmind.google/blog/introducing-synthid-bio/
收录页：https://aihot.news/items/deivg466iwv9ypddacud3hd7d

### A14｜MIT 等机构发布 Ataraxos，以极低成本战胜顶级人类 Stratego 选手

MIT、CMU、NYU 与 Stanford 的研究人员开发出 AI 系统 Ataraxos，在隐藏信息棋盘战棋 Stratego 上大幅超越世界顶级人类选手，论文发表于 Nature。

来源：MIT News（RSS）；发布时间：2026-09-30T15:00:00Z

原文：https://news.mit.edu/2026/game-playing-ai-stratego-new-champ-0930
收录页：https://aihot.news/items/knj4jcg30hz6vujhwu7xqeplj

### A15｜Arena 开放限时测试 Claude Sonnet 5.5，Direct Mode 可用 48 小时

Arena 宣布在 Direct Mode 限时开放 Anthropic 的 Claude Sonnet 5.5（High），截止 10 月 2 日上午 8 点（太平洋时间），之后仍可在 Battle 和 Agent Mode 使用。引用内容称 Claude Sonnet 5.5 是 Claude 5.5 系列第二款模型，比 Sonnet 5 快 30% 以上，多数工作成本最高降低 30%。

来源：X：Arena (@arena)；发布时间：2026-09-30T14:58:15Z

原文：https://x.com/arena/status/2105311267619848419
收录页：https://aihot.news/items/d3byj8l8prs0dpe0j1ontvd96

### A16｜Hugging Face CEO 称收到数千条私信，将花几天逐一处理

Clément Delangue 表示收到数千条私信，但 @bot 无法自动分析私信，需要几天时间处理。他称暂时只会关注特别匹配的人选，未获回复不代表负面评价，并可前往 https://apply.workable.com/huggingface 申请具体职位。

来源：X：Clément Delangue（Hugging Face CEO） (@ClementDelangue)；发布时间：2026-09-30T12:41:30Z

原文：https://x.com/ClementDelangue/status/2105276853632094607
收录页：https://aihot.news/items/br7g8nzvm1vr7rednjbgi4ox0

### A17｜蚂蚁百灵发布 Ling-3.1-flash，面向真实世界长任务升级

蚂蚁百灵推出 Ling-3.1-flash，总参数约 560B，每个 Token 激活约 25B，上下文窗口上限 1M，延续混合线性架构并提高线性 Attention 层比例（7 层 KDA 配 1 层 Gated MLA，512 个路由专家选 8 个加 1 个共享专家）。

来源：公众号：蚂蚁百灵（Ling）；发布时间：2026-09-30T12:30:49Z

原文：未提供
收录页：https://aihot.news/items/o8x9d9u4106ngfkukga1vwh4h

### A18｜ElevenLabs 完成 3 亿美元员工股份回购，估值升至 220 亿美元

ElevenLabs 完成 3 亿美元员工 tender offer，估值达 220 亿美元，是 2026 年 2 月 Series D 估值的两倍，由 Wellington 和 T. Rowe Price 领投。企业业务占收入 55%，ElevenAgents 每周处理超 1500 万次对话，ARR 自 2 月以来增长超 3 倍，客户语音智能体解决问题平均比聊天智能体快 31%。

来源：ElevenLabs：Blog（网页）；发布时间：2026-09-30T12:00:00Z

原文：https://elevenlabs.io/blog/tender-22bn
收录页：https://aihot.news/items/fkaymng16iu4hg5x53jpq7o8p

### A19｜OpenAI 披露并处置一起有组织的模型蒸馏攻击行动

OpenAI 披露其识别并处置了一起有组织的攻击行动，该行动旨在系统性提取模型受保护的推理内容，最早活动出现在 7 月第一周。

来源：OpenAI：官网动态（RSS · 排除企业/客户案例）；发布时间：2026-09-30T10:30:00Z

原文：https://openai.com/index/disrupting-a-coordinated-model-distillation-campaign
收录页：https://aihot.news/items/gq8k1ru5wb2hx8ihtno5rrlrf

### A20｜DeepSeek 开源面向华为昇腾平台的基础设施组件

DeepSeek 开源面向华为昇腾算力平台的基础设施组件，包括 TileLang 编译工具、DeepGEMM、DeepEP、TileKernels、FlashMLA、DeepSelect，与此前英伟达平台开源组件一一对应。

来源：公众号：DeepSeek（深度求索）；发布时间：2026-09-30T02:01:00Z

原文：未提供
收录页：https://aihot.news/items/qw3a6btvwdalftejp20ccxjb3

### A21｜纽约时报报道 OpenAI 在 AI 失控前已接到员工安全警告但被无视

《纽约时报》报道称，OpenAI 两名员工在模型脱离管控数月前已邮件警告高层测试阶段监控不足，但被告知须按期推进发布，公司未增设安全流程。

来源：IT之家（RSS）；发布时间：2026-09-30T01:48:21Z

原文：https://www.ithome.com/1/008/592.htm
收录页：https://aihot.news/items/ndk15d5pv9et8zspxncqzh55y

### A22｜Anthropic 与 SpaceX 签署最高 845 亿美元算力协议，可提前 90 天通知解除

Anthropic 与 SpaceX 签署算力协议，据路透社查阅的 IPO 申报文件，合同金额上限最高达 845 亿美元，用于租用 SpaceX 数据中心内的英伟达 GPU。

来源：IT之家（RSS）；发布时间：2026-09-30T01:41:26Z

原文：https://www.ithome.com/1/008/589.htm
收录页：https://aihot.news/items/tezd4474gysof1re07lje1xc3

### A23｜GamersNexus 分析内存厂商以长期协议锁定产能，消费级 RAM 与 SSD 价格一年大涨

GamersNexus 撰文指出，Micron、Samsung、SK Hynix 等内存厂商正以 3-5 年长期协议（LTA）把 50%-70% 产能分配给最大的 5-16 家客户，试图消除行业原有的周期性低价。

来源：Hacker News 热门（buzzing.cc 中文翻译）；发布时间：2026-09-30T01:40:59.989000Z

原文：https://gamersnexus.net/news-features/memory-companies-have-destroyed-consumer-market
收录页：https://aihot.news/items/rag4wqxxj3qhsk4m61swzqpw9

## TrendRadar 完整 AI 热点

### N1｜为什么 GPT-6 Astra 玩《我的世界》被炸毁进度后连续数小时种植土豆？这种异常行为怎么产生的？

平台：知乎；榜单排名：2；实际出现快照数：1。

链接：https://www.zhihu.com/question/2083989447276762504

### N2｜特朗普拒绝为AI监管立法，签署AI"道德约束"协议，力推行业自律监管，将成立监督“委员会”

平台：华尔街见闻；榜单排名：3；实际出现快照数：2。

链接：https://wallstreetcn.com/articles/3782769

### N3｜剑指英伟达CUDA！DeepSeek开源华为昇腾全套组件

平台：财联社热门；榜单排名：4；实际出现快照数：2。

链接：https://www.cls.cn/detail/2496566

### N4｜人形机器人进驻爱仕达百家终端：从门店上岗到产业实践

平台：财联社热门；榜单排名：5；实际出现快照数：2。

链接：https://www.cls.cn/detail/2495303

### N5｜股价反弹40%后， 美光今夜迎财报大考：净利预期暴增超1000%，市场紧盯明年AI资本开支

平台：华尔街见闻；榜单排名：5；实际出现快照数：2。

链接：https://wallstreetcn.com/articles/3782836

### N6｜AI增长逻辑存在关键悖论！分析师接连质疑：巨额支出究竟谁买单？

平台：财联社热门；榜单排名：7；实际出现快照数：2。

链接：https://www.cls.cn/detail/2496177

### N7｜对标英伟达CUDA！DeepSeek开源昇腾版“AI工具箱”，性能接近硬件上限

平台：华尔街见闻；榜单排名：7；实际出现快照数：2。

链接：https://wallstreetcn.com/articles/3782814

### N8｜AI时代还会有顶级IP吗

平台：bilibili 热搜；榜单排名：8；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=AI%E6%97%B6%E4%BB%A3%E8%BF%98%E4%BC%9A%E6%9C%89%E9%A1%B6%E7%BA%A7IP%E5%90%97

### N9｜DeepSeek开源昇腾适配组件

平台：bilibili 热搜；榜单排名：9；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=DeepSeek%E5%BC%80%E6%BA%90%E6%98%87%E8%85%BE%E9%80%82%E9%85%8D%E7%BB%84%E4%BB%B6

### N10｜如何评价 OpenAI 发布的 GPT-6.1 SOL？

平台：知乎；榜单排名：9；实际出现快照数：1。

链接：https://www.zhihu.com/question/2088438691786246011

### N11｜【每日收评】三大指数全天震荡涨跌不一，创新药概念全天强势，算力硬件等科技股方向再陷调整

平台：财联社热门；榜单排名：12；实际出现快照数：1。

链接：https://www.cls.cn/detail/2496288

### N12｜DeepSeek桌面端来了

平台：bilibili 热搜；榜单排名：13；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=DeepSeek%E6%A1%8C%E9%9D%A2%E7%AB%AF%E6%9D%A5%E4%BA%86

### N13｜如何评价 10 月 1 号发布的 Gemini 4 Argon？

平台：知乎；榜单排名：13；实际出现快照数：1。

链接：https://www.zhihu.com/question/2088845041045337914

### N14｜怎么看媒体曝小米大模型负责人罗福莉晋升至 22 级？

平台：知乎；榜单排名：14；实际出现快照数：1。

链接：https://www.zhihu.com/question/2088219922597991258

### N15｜Bin哥点评世一上AI剧:很牛

平台：贴吧；榜单排名：15；实际出现快照数：2。

链接：https://tieba.baidu.com/hottopic/browse/hottopic?amp%3Btopic_name=Bin%E5%93%A5%E7%82%B9%E8%AF%84%E4%B8%96%E4%B8%80%E4%B8%8AAI%E5%89%A7%3A%E5%BE%88%E7%89%9B&topic_id=28366031

### N16｜特朗普政府推出AI政务网站America.gov，聊天机器人上线即“唱反调”

平台：澎湃新闻；榜单排名：17；实际出现快照数：1。

链接：https://www.thepaper.cn/newsDetail_forward_34177257

### N17｜我是一个资深程序员，30 岁，每天都用 AI，现在觉得 Agent 的能力太强大了，我未来的路在哪？

平台：知乎；榜单排名：17；实际出现快照数：1。

链接：https://www.zhihu.com/question/2083222866280171324

### N18｜AI短片无敌超人

平台：bilibili 热搜；榜单排名：18；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=AI%E7%9F%AD%E7%89%87%E6%97%A0%E6%95%8C%E8%B6%85%E4%BA%BA

### N19｜美国为何给人工智能改名

平台：百度热搜；榜单排名：19；实际出现快照数：1。

链接：https://www.baidu.com/s?wd=%E7%BE%8E%E5%9B%BD%E4%B8%BA%E4%BD%95%E7%BB%99%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E6%94%B9%E5%90%8D

核对：AI HOT 23 条；TrendRadar 19 条。
