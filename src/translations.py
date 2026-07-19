"""Minimal hand-rolled i18n for the landing page and dashboard shell.

Scope is intentionally narrow: the landing page (login.html) and the
dashboard's navigation chrome (sidebar, header, connection status). The
actual data pages (Training/Activities/Recovery/Profile content, forms)
and everything under /research stay English-only — research paper titles
and citations must never be run through this table.
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    "skip_link": {"en": "Skip to content", "zh": "跳到主要内容"},

    # Landing nav
    "nav.home": {"en": "Home", "zh": "首页"},
    "nav.about": {"en": "About", "zh": "关于"},
    "nav.how": {"en": "How it works", "zh": "工作原理"},
    "nav.signin": {"en": "Sign in", "zh": "登录"},

    # Hero
    "hero.title": {"en": "Run today, or rest?", "zh": "今天该跑步，还是该休息？"},
    "hero.copy": {
        "en": "Slept badly and the plan says intervals? Gaman checks your last seven days and tells you which one to trust.",
        "zh": "昨晚没睡好，计划却安排了间歇训练？Gaman 会分析你过去七天的数据，告诉你该相信哪一个。",
    },
    "hero.cta": {"en": "Open dashboard", "zh": "打开仪表盘"},

    # Benefits
    "benefits.kicker": {"en": "A real Tuesday, not a demo", "zh": "真实的周二，而非演示"},
    "benefits.title": {
        "en": "Sore quads. A race in six weeks. Two easy runs already banked this week.",
        "zh": "大腿酸痛。六周后有比赛。这周已经完成了两次轻松跑。",
    },
    "benefits.copy": {
        "en": "That's the input. Gaman turns it into one session, one number, and the reasoning behind both — not a dashboard you have to interpret yourself.",
        "zh": "这就是输入。Gaman 会把它转化为一次训练、一个数字，以及背后的推理过程——而不是一个需要你自己解读的仪表盘。",
    },
    "preview.kicker": {"en": "Today's run", "zh": "今天的训练"},
    "preview.title": {"en": "Tempo · 8 × 4 min", "zh": "节奏跑 · 8 × 4 分钟"},
    "preview.status": {"en": "Ready to train", "zh": "可以训练"},
    "preview.distance_label": {"en": "Distance", "zh": "距离"},
    "preview.distance_value": {"en": "13.2 km", "zh": "13.2 公里"},
    "preview.duration_label": {"en": "Duration", "zh": "时长"},
    "preview.duration_value": {"en": "52 min", "zh": "52 分钟"},
    "preview.effort_label": {"en": "Target effort", "zh": "目标强度"},
    "preview.effort_value": {"en": "Comfortably hard", "zh": "有点吃力但可控"},
    "preview.note": {
        "en": "Last 7 days sit 12% below your typical week, so the load can absorb one harder session.",
        "zh": "过去 7 天的训练量比平时低 12%，因此这周可以承受一次更高强度的训练。",
    },

    # How it works preview
    "how.kicker": {"en": "How Gaman works", "zh": "Gaman 的工作原理"},
    "how.title": {
        "en": "Your activity becomes a decision you can inspect.",
        "zh": "你的运动数据会变成一个你能亲自查验的决定。",
    },
    "how.copy": {
        "en": "Measured activity data feeds transparent calculations, runner feedback adds context, and optional model guidance stays clearly labeled.",
        "zh": "真实的运动数据驱动透明的计算，跑者反馈补充背景信息，可选的模型建议也会被清楚标注。",
    },
    "how.link": {"en": "See the complete method", "zh": "查看完整方法"},
    "how.step1.label": {"en": "Import", "zh": "导入"},
    "how.step1.detail": {"en": "Strava or Coros", "zh": "Strava 或 Coros"},
    "how.step2.label": {"en": "Compare", "zh": "对比"},
    "how.step2.detail": {"en": "Load and history", "zh": "训练量与历史"},
    "how.step3.label": {"en": "Recommend", "zh": "建议"},
    "how.step3.detail": {"en": "One practical action", "zh": "一个可执行的行动"},
    "how.step4.label": {"en": "Reflect", "zh": "反馈"},
    "how.step4.detail": {"en": "Your feedback", "zh": "你的感受"},

    # Safety
    "safety.kicker": {"en": "Clear boundaries", "zh": "清晰的边界"},
    "safety.title": {
        "en": "Evidence where it exists. Honest limits where it does not.",
        "zh": "有证据的地方讲证据，没有证据的地方讲清楚局限。",
    },
    "safety.copy": {
        "en": "Gaman labels measured data, calculated estimates, rule-based coaching, and optional language-model guidance separately. Recovery support is educational and never a diagnosis. Urgent symptoms are directed to in-person care.",
        "zh": "Gaman 会分别标注实测数据、计算得出的估计值、基于规则的指导，以及可选的语言模型建议。恢复方面的支持仅供参考，绝非诊断。紧急症状请务必寻求线下医疗帮助。",
    },

    # About
    "about.kicker": {"en": "About Gaman", "zh": "关于 Gaman"},
    "about.title": {
        "en": "A running workspace built around the data you already create.",
        "zh": "一个围绕你已有数据构建的跑步工作台。",
    },
    "about.copy1": {
        "en": "Gaman brings activities, goals, workout feedback, shoes, and recovery check-ins into one focused system. It helps runners understand today's session without hiding the calculations or pretending unavailable measurements exist.",
        "zh": "Gaman 将运动记录、目标、训练反馈、跑鞋和恢复打卡整合到一个专注的系统中。它帮助跑者理解今天的训练安排，既不隐藏计算过程，也不假装拥有不存在的数据。",
    },
    "about.copy2": {
        "en": "The product combines direct activity measurements, transparent training-load rules, an inspectable feedback model, and conservative recovery safeguards. Each system has a defined job, and you can read the complete method before trusting a recommendation.",
        "zh": "这个产品结合了直接的运动测量数据、透明的训练负荷规则、可查验的反馈模型，以及保守的恢复保护机制。每个系统都有明确的职责，你可以在信任任何建议之前先阅读完整的方法说明。",
    },
    "about.photo_alt": {
        "en": "A trail leading through a misty mountain valley",
        "zh": "一条穿过云雾缭绕山谷的小径",
    },

    # Footer
    "footer.tagline": {
        "en": "Training direction for runners who want to see the reasoning.",
        "zh": "为想要看清推理过程的跑者提供训练方向。",
    },
    "footer.github": {"en": "GitHub", "zh": "GitHub"},
    "footer.how": {"en": "How it works", "zh": "工作原理"},
    "footer.research": {"en": "Research", "zh": "研究资料"},
    "footer.logout": {"en": "Log out", "zh": "退出登录"},

    # Login dialog
    "dialog.brand": {"en": "Gaman", "zh": "Gaman"},
    "dialog.title": {"en": "Open dashboard", "zh": "打开仪表盘"},
    "dialog.copy": {"en": "Enter your password to continue.", "zh": "请输入密码以继续。"},
    "dialog.password_label": {"en": "Password", "zh": "密码"},
    "dialog.submit": {"en": "Continue", "zh": "继续"},

    # Dashboard sidebar nav
    "nav.overview": {"en": "Overview", "zh": "总览"},
    "nav.training": {"en": "Training", "zh": "训练"},
    "nav.activities": {"en": "Activities", "zh": "活动记录"},
    "nav.recovery": {"en": "Body & Recovery", "zh": "身体与恢复"},
    "nav.recovery_short": {"en": "Recovery", "zh": "恢复"},
    "nav.profile": {"en": "Profile", "zh": "个人资料"},

    # Connection status
    "conn.strava_connected": {"en": "Strava connected", "zh": "Strava 已连接"},
    "conn.strava_not_connected": {"en": "Strava not connected", "zh": "Strava 未连接"},
    "conn.coros_connected": {"en": "Coros connected", "zh": "Coros 已连接"},
    "conn.coros_not_connected": {"en": "Coros not connected", "zh": "Coros 未连接"},
    "conn.fitbit_connected": {"en": "Fitbit connected", "zh": "Fitbit 已连接"},
    "conn.fitbit_not_connected": {"en": "Fitbit not connected", "zh": "Fitbit 未连接"},

    # Sample data banner
    "sample.label": {"en": "Example data", "zh": "示例数据"},
    "sample.copy": {"en": "Connect a source to use your runs.", "zh": "连接数据源以使用你的真实跑步数据。"},

    # Area titles/descriptions (also used from Python via translate())
    "area.overview.title": {"en": "Overview", "zh": "总览"},
    "area.overview.desc": {
        "en": "Today’s work, recovery, and weekly direction.",
        "zh": "今天的训练、恢复状况与本周方向。",
    },
    "area.training.title": {"en": "Training", "zh": "训练"},
    "area.training.desc": {
        "en": "Plan the week and understand the work behind it.",
        "zh": "规划本周训练，理解背后的安排逻辑。",
    },
    "area.activities.title": {"en": "Activities", "zh": "活动记录"},
    "area.activities.desc": {
        "en": "Find a run, inspect the data, and add feedback.",
        "zh": "查找跑步记录，查看数据并添加反馈。",
    },
    "area.recovery.title": {"en": "Body & Recovery", "zh": "身体与恢复"},
    "area.recovery.desc": {
        "en": "Track symptoms and make conservative recovery decisions.",
        "zh": "记录身体状况，做出保守的恢复决策。",
    },
    "area.profile.title": {"en": "Profile & Connections", "zh": "个人资料与连接"},
    "area.profile.desc": {
        "en": "Manage data sources, shoes, races, and privacy.",
        "zh": "管理数据源、跑鞋、比赛与隐私设置。",
    },

    # --- Dashboard data pages: empty/getting-started states ---
    "empty.kicker": {"en": "Getting started", "zh": "开始使用"},
    "empty.title": {"en": "Connect a source to begin", "zh": "连接数据源以开始"},
    "empty.copy": {
        "en": "When Strava or Coros activities arrive, this page will show your real training data.",
        "zh": "当 Strava 或 Coros 的活动数据到达后，此页面将显示你的真实训练数据。",
    },

    # --- Training page ---
    "measured.kicker": {"en": "Measured activity data", "zh": "实测活动数据"},
    "pace.title": {"en": "Pace trend", "zh": "配速趋势"},
    "pace.copy": {
        "en": "Lower pace values are faster. Each point is a loaded Strava or Coros activity.",
        "zh": "配速数值越低代表越快。每个点代表一次已加载的 Strava 或 Coros 活动。",
    },
    "rulebased.kicker": {"en": "Rule-based guidance", "zh": "基于规则的指导"},
    "patterns.title": {"en": "Patterns and suggested sessions", "zh": "训练规律与建议课表"},
    "patterns.copy": {
        "en": "Observations from your loaded runs and the next seven days.",
        "zh": "基于你已加载的跑步记录和未来七天得出的观察。",
    },
    "whatchanged.title": {"en": "What changed", "zh": "发生了什么变化"},
    "suggested.title": {"en": "Suggested sessions", "zh": "建议课表"},
    "raceplanning.kicker": {"en": "Race planning", "zh": "比赛规划"},
    "manageraces.title": {"en": "Manage race dates", "zh": "管理比赛日期"},
    "form.date": {"en": "Date", "zh": "日期"},
    "form.event": {"en": "Event", "zh": "赛事"},
    "form.event_placeholder": {"en": "City Marathon", "zh": "城市马拉松"},
    "form.distance": {"en": "Distance", "zh": "距离"},
    "form.km_placeholder": {"en": "km", "zh": "公里"},
    "form.add_race": {"en": "Add race", "zh": "添加比赛"},
    "form.remove": {"en": "Remove", "zh": "移除"},

    # --- Activities page ---
    "allruns.title": {"en": "All loaded runs", "zh": "所有已加载的跑步记录"},
    "allruns.copy": {
        "en": "Summary measurements from your connected sources.",
        "zh": "来自已连接数据源的汇总测量数据。",
    },
    "th.date": {"en": "Date", "zh": "日期"},
    "th.source": {"en": "Source", "zh": "来源"},
    "th.distance": {"en": "Distance", "zh": "距离"},
    "th.duration": {"en": "Duration", "zh": "时长"},
    "th.heartrate": {"en": "Heart rate", "zh": "心率"},
    "th.pace": {"en": "Pace", "zh": "配速"},
    "th.elevation": {"en": "Elevation", "zh": "爬升"},
    "val.unavailable": {"en": "Unavailable", "zh": "无数据"},
    "runnerctx.kicker": {"en": "Runner-reported context", "zh": "跑者反馈信息"},
    "runfeedback.title": {"en": "Run feedback", "zh": "跑步反馈"},
    "search.feedback_placeholder": {"en": "Search feedback runs", "zh": "搜索反馈记录"},
    "btn.show_all": {"en": "Show all", "zh": "显示全部"},
    "lbl.difficulty": {"en": "Difficulty", "zh": "难度"},
    "lbl.soreness": {"en": "Soreness", "zh": "酸痛程度"},
    "lbl.motivation": {"en": "Motivation", "zh": "动力"},
    "lbl.notes": {"en": "Notes", "zh": "备注"},
    "placeholder.how_did_it_feel": {"en": "How did it feel?", "zh": "感觉如何？"},
    "btn.update_ratings": {"en": "Update ratings", "zh": "更新评分"},
    "btn.save_ratings": {"en": "Save ratings", "zh": "保存评分"},
    "btn.remove_feedback": {"en": "Remove saved feedback", "zh": "删除已保存的反馈"},
    "btn.dismiss_prompt": {"en": "Dismiss this prompt", "zh": "忽略此提醒"},
    "empty.no_feedback_prompts": {"en": "No current feedback prompts.", "zh": "目前没有待反馈的记录。"},
    "empty.no_feedback_match": {"en": "No feedback runs match that search.", "zh": "没有符合搜索条件的反馈记录。"},
    "val.saved": {"en": "Saved", "zh": "已保存"},
    "val.add_ratings": {"en": "Add ratings", "zh": "添加评分"},
    "recentactivities.kicker": {"en": "Recent activities", "zh": "近期活动"},
    "findrun.title": {"en": "Find a run", "zh": "查找跑步记录"},
    "findrun.copy": {
        "en": "Open any activity for a closer look at the data available.",
        "zh": "打开任意活动记录，查看详细数据。",
    },
    "search.activities_placeholder": {"en": "Search date, source, pace, or distance", "zh": "搜索日期、来源、配速或距离"},
    "view.link": {"en": "View", "zh": "查看"},

    # --- Profile page ---
    "datasources.kicker": {"en": "Data sources", "zh": "数据源"},
    "connections.title": {"en": "Connections", "zh": "连接状态"},
    "lbl.strava": {"en": "Strava", "zh": "Strava"},
    "lbl.activityimport": {"en": "Activity import", "zh": "活动导入"},
    "lbl.coros": {"en": "Coros", "zh": "Coros"},
    "val.connected": {"en": "Connected", "zh": "已连接"},
    "val.not_configured": {"en": "Not configured", "zh": "未配置"},
    "caption.credentials": {
        "en": "Credentials stay on the server and are never placed in browser code.",
        "zh": "凭证仅保存在服务器上，绝不会出现在浏览器代码中。",
    },
    "privacy.kicker": {"en": "Privacy", "zh": "隐私"},
    "privacy.title": {"en": "Your data stays inspectable", "zh": "你的数据始终可查验"},
    "privacy.copy": {
        "en": "Gaman uses the activity fields supplied by your sources and labels unavailable measurements instead of inventing them.",
        "zh": "Gaman 只使用数据源提供的活动字段，并会标注不可用的测量项，而不是凭空捏造。",
    },
    "link.read_guidance": {"en": "Read how guidance works", "zh": "了解指导原理"},
    "profile.about.title": {
        "en": "Built around the data runners already create.",
        "zh": "围绕跑者已有的数据构建。",
    },
    "profile.about.copy": {
        "en": "Bring activities, goals, feedback, shoes, and recovery check-ins into one focused workspace.",
        "zh": "将运动记录、目标、反馈、跑鞋和恢复打卡整合到一个专注的工作台中。",
    },

    # --- Ask Gaman panel ---
    "ask.title": {"en": "Ask Gaman", "zh": "问 Gaman"},
    "ask.heading": {"en": "Ask about your training", "zh": "询问关于你训练的问题"},
    "ask.disclaimer": {
        "en": "Answers are grounded in your logged runs and readiness. Educational only — not medical advice.",
        "zh": "回答基于你已记录的跑步数据和身体状态，仅供参考，不构成医疗建议。",
    },
    "ask.your_question": {"en": "Your question", "zh": "你的问题"},
    "ask.placeholder": {"en": "e.g. Should I do the tempo run today?", "zh": "例如：我今天该做节奏跑吗？"},
    "ask.send": {"en": "Send", "zh": "发送"},

    # --- How it works page ---
    "how2.kicker": {"en": "How it works", "zh": "工作原理"},
    "how2.title": {
        "en": "Four kinds of information. Four clearly defined jobs.",
        "zh": "四种信息，四种明确的职责。",
    },
    "how2.copy": {
        "en": "Gaman separates facts, calculations, statistical estimates, and optional language-model guidance so you can understand where every recommendation comes from.",
        "zh": "Gaman 将事实、计算结果、统计估计值和可选的语言模型建议分开呈现，让你清楚每一条建议的来源。",
    },
    "grid1.label": {"en": "01 / Direct activity data", "zh": "01 / 直接活动数据"},
    "grid1.title": {"en": "What your sources measured", "zh": "数据源实测的内容"},
    "grid1.copy": {
        "en": "Distance, duration, average pace, heart rate, elevation, date, and source are displayed as supplied. Missing fields remain unavailable.",
        "zh": "距离、时长、平均配速、心率、爬升、日期和来源均按数据源提供的原样显示。缺失的字段会标注为无数据。",
    },
    "grid2.label": {"en": "02 / Rule-based calculations", "zh": "02 / 基于规则的计算"},
    "grid2.title": {"en": "Transparent training logic", "zh": "透明的训练逻辑"},
    "grid2.copy": {
        "en": "Weekly mileage, recent-versus-baseline load, race timing, tapering, and workout adjustments use deterministic rules that can be explained in plain language.",
        "zh": "周跑量、近期负荷与基线的对比、比赛时间安排、减量训练以及课表调整均使用可以用简单语言解释的确定性规则。",
    },
    "grid3.label": {"en": "03 / Statistical model", "zh": "03 / 统计模型"},
    "grid3.title": {"en": "Feedback-informed difficulty", "zh": "基于反馈的难度评估"},
    "grid3.copy": {
        "en": "After at least five rated runs, an inspectable linear regression uses distance, pace, elevation, and your feedback to estimate workout difficulty. Sparse data falls back safely to rules.",
        "zh": "在至少五次评分后，一个可查验的线性回归模型会结合距离、配速、爬升和你的反馈来估计训练难度。数据不足时会安全地回退到规则计算。",
    },
    "grid4.label": {"en": "04 / Optional language model", "zh": "04 / 可选的语言模型"},
    "grid4.title": {"en": "Expanded recovery education", "zh": "扩展的恢复教育内容"},
    "grid4.copy": {
        "en": "When configured server-side, a language model can expand conservative recovery guidance. It does not control training calculations, diagnose injury, prescribe medication, or replace a clinician.",
        "zh": "在服务器端配置后，语言模型可以扩展保守的恢复指导内容。它不会控制训练计算、诊断伤病、开具药物，也不能替代专业医生。",
    },
    "safetygate.kicker": {"en": "Safety gate", "zh": "安全防线"},
    "safetygate.title": {
        "en": "Urgent symptoms bypass ordinary guidance.",
        "zh": "紧急症状会跳过常规指导。",
    },
    "safetygate.copy": {
        "en": "Chest pain, breathing trouble, severe pain, new numbness or weakness, deformity, or inability to bear weight triggers a prominent recommendation for prompt in-person care. If the optional service is unavailable, built-in conservative guidance remains available.",
        "zh": "胸痛、呼吸困难、剧烈疼痛、新出现的麻木或无力、畸形，或无法负重，都会触发醒目的提示，建议尽快寻求线下医疗救助。如果可选的扩展服务不可用，内置的保守指导仍然可用。",
    },
    "limits.title": {"en": "Current limits", "zh": "当前的局限性"},
    "limits.li1": {"en": "No diagnosis or emergency care", "zh": "不提供诊断或紧急医疗救助"},
    "limits.li2": {"en": "No fabricated cadence, sleep, HRV, splits, or grade-adjusted pace", "zh": "不会编造步频、睡眠、心率变异性、分段配速或坡度调整配速数据"},
    "limits.li3": {"en": "No confidence interval when the data cannot support one", "zh": "当数据不足以支持时，不会给出置信区间"},
    "limits.li4": {"en": "Coros production authentication remains a roadmap item", "zh": "Coros 正式生产环境认证仍在规划中"},
    "limits.li5": {"en": "JSON storage is local and not a durable production database", "zh": "JSON 存储为本地存储，并非持久化的生产级数据库"},
    "nav.back_gaman": {"en": "Back to Gaman", "zh": "返回 Gaman"},

    # --- Run detail page ---
    "nav.back_activities": {"en": "← Back to activities", "zh": "← 返回活动记录"},
    "nav.runfile": {"en": "GAMAN / RUN FILE", "zh": "GAMAN / 跑步档案"},
    "detail.copy": {
        "en": "One run, stripped down to the measurements that matter and compared only with similar activities in your loaded training history.",
        "zh": "一次跑步记录，只保留真正重要的测量数据，并只与你训练历史中相似的活动进行比较。",
    },
    "metric.pace": {"en": "Pace", "zh": "配速"},
    "metric.pace_sub": {"en": "Measured average", "zh": "实测平均值"},
    "metric.hr": {"en": "Heart rate", "zh": "心率"},
    "metric.hr_sub_avg": {"en": "Average bpm", "zh": "平均心率（bpm）"},
    "metric.hr_sub_missing": {"en": "Not supplied by source", "zh": "数据源未提供"},
    "metric.elevation": {"en": "Elevation gain", "zh": "爬升高度"},
    "metric.elevation_sub": {"en": "Measured total", "zh": "实测总量"},
    "comparison.kicker": {"en": "Compared with your history", "zh": "与你的历史记录对比"},
    "comparison.title": {"en": "Similar-distance runs", "zh": "相似距离的跑步记录"},
    "wentwell.kicker": {"en": "What went well", "zh": "表现良好之处"},
    "wentwell.title": {"en": "Useful signals", "zh": "有用的信号"},
    "improve.kicker": {"en": "For next time", "zh": "下一次可以关注"},
    "improve.title": {"en": "What could add context", "zh": "可以补充的背景信息"},
    "recoverynext.kicker": {"en": "Recovery", "zh": "恢复"},
    "recoverynext.title": {"en": "What to consider next", "zh": "接下来需要考虑的事项"},
    "datalimits.kicker": {"en": "Data limits", "zh": "数据局限"},
    "datalimits.title": {"en": "Not available in this activity summary", "zh": "本次活动摘要中不可用的数据"},
    "datalimits.caption": {
        "en": "Gaman does not estimate or fabricate these fields.",
        "zh": "Gaman 不会估算或编造这些字段。",
    },

    # --- Recovery panel ---
    "recoveryguidance.kicker": {"en": "Educational recovery guidance", "zh": "恢复教育指导"},
    "recoveryguidance.title": {"en": "Check in with your body", "zh": "身体状态打卡"},
    "recoveryguidance.badge": {"en": "Not a diagnosis", "zh": "非诊断"},
    "recoveryguidance.intro": {
        "en": "Choose every area that needs attention and describe what you feel. Recent training is added when available. Urgent symptoms bypass ordinary guidance.",
        "zh": "选择所有需要注意的部位，并描述你的感受。近期训练数据会在可用时自动补充。紧急症状会跳过常规指导。",
    },
    "bodyregion.label": {"en": "Choose a body region", "zh": "选择身体部位"},
    "bodyregion.help": {
        "en": "Select the illustration or use the labeled buttons. Multiple areas are supported.",
        "zh": "点击插图或使用下方的标签按钮选择，支持多选。",
    },
    "svg.loading_front": {"en": "Loading front view", "zh": "正在加载正面视图"},
    "svg.loading_back": {"en": "Loading back view", "zh": "正在加载背面视图"},
    "selectedareas.placeholder": {"en": "Select one or more body regions", "zh": "选择一个或多个身体部位"},
    "painlevel.label": {"en": "Pain level", "zh": "疼痛程度"},
    "onset.label": {"en": "When did it begin?", "zh": "何时开始的？"},
    "onset.gradual": {"en": "Gradually", "zh": "逐渐出现"},
    "onset.sudden": {"en": "Suddenly", "zh": "突然出现"},
    "onset.after_run": {"en": "After a specific run", "zh": "特定一次跑步之后"},
    "feel.legend": {"en": "What does it feel like?", "zh": "感觉是怎样的？"},
    "trigger.legend": {"en": "When does it bother you?", "zh": "什么时候会不舒服？"},
    "sensation.sharp": {"en": "sharp", "zh": "尖锐"},
    "sensation.dull": {"en": "dull", "zh": "钝痛"},
    "sensation.tight": {"en": "tight", "zh": "紧绷"},
    "sensation.sore": {"en": "sore", "zh": "酸痛"},
    "sensation.burning": {"en": "burning", "zh": "灼热"},
    "sensation.numb": {"en": "numb", "zh": "麻木"},
    "sensation.tingling": {"en": "tingling", "zh": "刺痛"},
    "trigger.running": {"en": "running", "zh": "跑步时"},
    "trigger.walking": {"en": "walking", "zh": "走路时"},
    "trigger.rest": {"en": "rest", "zh": "休息时"},
    "trigger.movement": {"en": "movement", "zh": "活动时"},
    "notes.label": {"en": "Anything important to share?", "zh": "还有什么重要信息想说明的吗？"},
    "notes.placeholder": {
        "en": "Example: pain after hills, swelling, or a recent fall.",
        "zh": "例如：上坡后疼痛、肿胀，或最近摔倒过。",
    },
    "formnote.urgent": {
        "en": "Chest pain, breathing trouble, severe pain, new numbness or weakness, deformity, or inability to bear weight needs prompt in-person medical attention.",
        "zh": "胸痛、呼吸困难、剧烈疼痛、新出现的麻木或无力、畸形，或无法负重，都需要尽快就医。",
    },
    "btn.create_checkin": {"en": "Create recovery check-in", "zh": "创建恢复打卡"},
    "trainingctx.label": {"en": "Direct activity data used", "zh": "使用的直接活动数据"},

    # --- Daily companion / overview ---
    "sample.activities_label": {"en": "Example activities", "zh": "示例活动"},
    "sample.activities_copy": {
        "en": "Connect Strava or Coros to replace these with your own runs.",
        "zh": "连接 Strava 或 Coros，用你自己的跑步记录替换这些示例。",
    },
    "val.as_needed": {"en": "As needed", "zh": "按需调整"},
    "val.no_target": {"en": "No target", "zh": "无目标"},
    "why.summary": {"en": "Why this workout?", "zh": "为什么安排这个训练？"},
    "warmup.label": {"en": "Warm-up", "zh": "热身"},
    "cooldown.label": {"en": "Cool-down", "zh": "放松"},
    "afterward.label": {"en": "Afterward", "zh": "训练之后"},
    "form.status": {"en": "Status", "zh": "状态"},
    "opt.completed": {"en": "Completed", "zh": "已完成"},
    "opt.shortened": {"en": "Shortened", "zh": "已缩短"},
    "opt.modified": {"en": "Modified", "zh": "已调整"},
    "opt.skipped": {"en": "Skipped", "zh": "已跳过"},
    "form.actual_distance": {"en": "Actual distance", "zh": "实际距离"},
    "placeholder.kilometres": {"en": "Kilometres", "zh": "公里"},
    "form.note": {"en": "Note", "zh": "备注"},
    "placeholder.optional": {"en": "Optional", "zh": "可选"},
    "btn.save_workout": {"en": "Save workout", "zh": "保存训练"},
    "trainingload.kicker": {"en": "Training load", "zh": "训练负荷"},
    "readiness.copy": {
        "en": "Your last seven days compared with your recent weekly baseline.",
        "zh": "过去七天与你近期每周基线的对比。",
    },
    "last7days.label": {"en": "Last 7 days", "zh": "过去 7 天"},
    "typicalweek.label": {"en": "Typical week", "zh": "典型一周"},
    "seeevidence.summary": {"en": "See the evidence", "zh": "查看依据"},
    "openrecovery.link": {"en": "Open Body & Recovery", "zh": "打开身体与恢复"},
    "distanceloaded.label": {"en": "Distance in loaded runs", "zh": "已加载跑步的总距离"},
    "avgpace.label": {"en": "Average pace", "zh": "平均配速"},
    "acrossloaded": {"en": "Across loaded activities", "zh": "所有已加载活动的平均值"},
    "currentrec.label": {"en": "Current recommendation", "zh": "当前建议"},
    "basedon": {"en": "Based on training load and check-ins", "zh": "基于训练负荷和打卡记录"},
    "weeklyplan.kicker": {"en": "Weekly plan", "zh": "每周计划"},
    "thisweek.title": {"en": "This training week", "zh": "本训练周"},
    "plannedvs.copy": {
        "en": "Planned sessions compared with what you logged.",
        "zh": "计划课表与你实际记录的对比。",
    },
    "adjustment.label": {"en": "Suggested adjustment", "zh": "建议调整"},
    "morefromtraining.kicker": {"en": "More from your training", "zh": "更多训练相关内容"},
    "planningrecords.title": {"en": "Planning, records, and long-term context", "zh": "规划、记录与长期背景"},
    "openonlytools.copy": {
        "en": "Open only the tools you need. Your data, forms, and saved history remain available below.",
        "zh": "只打开你需要的工具。你的数据、表单和历史记录仍保留在下方。",
    },
    "racegoal.kicker": {"en": "Race goal", "zh": "比赛目标"},
    "choosepriority": {"en": "Choose a priority race", "zh": "选择一场优先比赛"},
    "raceday.label": {"en": "Race day", "zh": "比赛日"},
    "daysaway": {"en": "{n} days away", "zh": "还有 {n} 天"},
    "targetpace.label": {"en": "Target pace", "zh": "目标配速"},
    "notset": {"en": "Not set", "zh": "未设置"},
    "calculatedfinish": {"en": "Calculated finish range:", "zh": "计算得出的完赛区间："},
    "minuteswithconfidence": {"en": "{low}–{high} minutes with {confidence} confidence.", "zh": "{low}–{high} 分钟，置信度为{confidence}。"},
    "addracedistance": {
        "en": "Add a race distance and recent runs to calculate a finish range.",
        "zh": "添加比赛距离和近期跑步记录，即可计算完赛区间。",
    },
    "pacingapproach": {"en": "Pacing approach:", "zh": "配速策略："},
    "form.racename": {"en": "Race name", "zh": "赛事名称"},
    "placeholder.eventname": {"en": "Event name", "zh": "赛事名称"},
    "form.goaltime": {"en": "Goal time", "zh": "目标时间"},
    "placeholder.minutes": {"en": "minutes", "zh": "分钟"},
    "check.priorityrace": {"en": "Priority race", "zh": "优先比赛"},
    "btn.saveracegoal": {"en": "Save race goal", "zh": "保存比赛目标"},
    "personalbests.kicker": {"en": "Personal bests", "zh": "个人最佳"},
    "fromloadedruns": {"en": "From your loaded runs", "zh": "来自你已加载的跑步记录"},
    "trainingcalendar.kicker": {"en": "Training calendar", "zh": "训练日历"},
    "nav.previous": {"en": "Previous", "zh": "上个月"},
    "nav.today": {"en": "Today", "zh": "今天"},
    "nav.next": {"en": "Next", "zh": "下个月"},
    "day.mon": {"en": "Mon", "zh": "周一"},
    "day.tue": {"en": "Tue", "zh": "周二"},
    "day.wed": {"en": "Wed", "zh": "周三"},
    "day.thu": {"en": "Thu", "zh": "周四"},
    "day.fri": {"en": "Fri", "zh": "周五"},
    "day.sat": {"en": "Sat", "zh": "周六"},
    "day.sun": {"en": "Sun", "zh": "周日"},
    "shoes.kicker": {"en": "Shoes", "zh": "跑鞋"},
    "yourrotation": {"en": "Your rotation", "zh": "你的轮换跑鞋"},
    "trackassigned": {
        "en": "Track assigned distance and replacement mileage.",
        "zh": "追踪分配的距离和更换里程。",
    },
    "form.brand": {"en": "Brand", "zh": "品牌"},
    "form.model": {"en": "Model", "zh": "型号"},
    "form.nickname": {"en": "Nickname", "zh": "昵称"},
    "form.purchasedate": {"en": "Purchase date", "zh": "购买日期"},
    "form.replaceafter": {"en": "Replace after", "zh": "更换里程"},
    "btn.addshoe": {"en": "Add shoe", "zh": "添加跑鞋"},
    "val.retired": {"en": "Retired", "zh": "已退役"},
    "val.active": {"en": "Active", "zh": "使用中"},
    "assocnotacause": {"en": "This is an association, not a cause.", "zh": "这只是相关性，并非因果关系。"},
    "btn.retire": {"en": "Retire", "zh": "退役"},
    "assignshoes.summary": {"en": "Assign shoes to activities", "zh": "为活动分配跑鞋"},
    "btn.assign": {"en": "Assign", "zh": "分配"},
    "noshoes": {"en": "No shoes added yet.", "zh": "还没有添加跑鞋。"},
    "recoveryhistory.kicker": {"en": "Recovery history", "zh": "恢复历史"},
    "symptomsovertime": {"en": "Symptoms over time", "zh": "症状变化趋势"},
    "exportsummary.link": {"en": "Export summary", "zh": "导出摘要"},
    "completeacheckin": {
        "en": "Complete a Body & Recovery check-in to start a timeline.",
        "zh": "完成一次身体与恢复打卡即可开始记录趋势。",
    },
    "adherence.followed": {"en": "Followed", "zh": "已遵循"},
    "adherence.partial": {"en": "Partially followed", "zh": "部分遵循"},
    "adherence.not_followed": {"en": "Not followed", "zh": "未遵循"},
    "btn.update": {"en": "Update", "zh": "更新"},

    # --- Dynamic coaching/analysis sentence templates (Python-generated) ---
    "tl.status.ready": {"en": "Ready to train", "zh": "可以训练"},
    "tl.status.recovery": {"en": "Recovery recommended", "zh": "建议恢复"},
    "tl.status.reduce": {"en": "Reduce load", "zh": "减少训练量"},
    "tl.status.maintain": {"en": "Maintain current load", "zh": "维持当前训练量"},
    "tl.reason.baseline": {
        "en": "{recent} km in the last 7 days versus a {prior} km prior weekly average.",
        "zh": "过去 7 天跑了 {recent} 公里，此前每周平均为 {prior} 公里。",
    },
    "tl.reason.urgent": {
        "en": "A recent recovery check-in contains severe or urgent symptoms.",
        "zh": "近期的恢复打卡中包含严重或紧急症状。",
    },
    "tl.reason.soreness": {
        "en": "Average logged soreness is {soreness}/5.",
        "zh": "记录的平均酸痛程度为 {soreness}/5。",
    },
    "tl.reason.change_high": {
        "en": "Distance is {change}% above the previous four-week weekly average.",
        "zh": "训练距离比过去四周平均值高 {change}%。",
    },
    "tl.reason.change_moderate": {
        "en": "Distance has increased {change}%; avoid adding another large jump.",
        "zh": "训练距离增加了 {change}%；避免再次大幅增加。",
    },
    "tl.reason.no_spike": {
        "en": "No high soreness, severe pain, or large load spike is present in available data.",
        "zh": "现有数据中没有出现高酸痛、剧烈疼痛或训练量骤增的情况。",
    },
    "tl.reason.soreness_unavailable": {
        "en": "Soreness is unavailable until run feedback is logged.",
        "zh": "在记录跑步反馈之前，酸痛程度数据不可用。",
    },
    "tl.reason.motivation": {
        "en": "Average motivation is {motivation}/5.",
        "zh": "平均动力水平为 {motivation}/5。",
    },
    "tl.reason.activity_summary": {
        "en": "Available activities include {elevation} m of climbing and {hard} feedback-rated hard session(s).",
        "zh": "现有活动包含 {elevation} 米爬升，以及 {hard} 次评分为高强度的训练。",
    },
    "tl.missing.sleep": {"en": "sleep", "zh": "睡眠"},
    "tl.missing.hrv": {"en": "HRV", "zh": "心率变异性"},
    "tl.missing.resting_hr": {"en": "resting heart rate", "zh": "静息心率"},

    "pl.reason.schedule": {
        "en": "The weekly schedule assigns {planned} to {weekday}.",
        "zh": "每周计划为{weekday}安排了{planned}。",
    },
    "pl.reason.reduced": {
        "en": "Readiness is '{status}', so {original} was reduced.",
        "zh": "当前状态为“{status}”，因此将{original}调整为更保守的安排。",
    },
    "pl.reason.status_only": {
        "en": "Readiness is '{status}'.",
        "zh": "当前状态为“{status}”。",
    },
    "pl.warmup.default": {"en": "5-10 minutes of easy walking and dynamic mobility.", "zh": "5-10 分钟轻松步行和动态热身。"},
    "pl.cooldown.default": {"en": "5-10 minutes easy, then comfortable mobility.", "zh": "5-10 分钟轻松放松，然后进行舒适的拉伸活动。"},
    "pl.recovery.default": {"en": "At least 24 hours before another hard session.", "zh": "距离下一次高强度训练至少间隔 24 小时。"},
    "pl.purpose.default": {"en": "Build consistent aerobic fitness without unnecessary fatigue.", "zh": "在不增加不必要疲劳的前提下build持续的有氧能力。"},
    "pl.target.controlled": {"en": "Controlled comfortably-hard effort", "zh": "可控的、有点吃力但可控的强度"},
    "pl.purpose.tempo": {"en": "Develop sustained speed and threshold control.", "zh": "发展持续速度和乳酸阈控制能力。"},
    "pl.recovery.tempo": {"en": "Allow 36-48 hours before the next hard session.", "zh": "距离下一次高强度训练至少间隔 36-48 小时。"},
    "pl.target.conversational": {"en": "Conversational effort", "zh": "可以正常交谈的强度"},
    "pl.purpose.long": {"en": "Build endurance and time-on-feet durability.", "zh": "提升耐力和长时间运动的适应能力。"},
    "pl.recovery.long": {"en": "Allow 36-48 hours before a demanding session.", "zh": "距离下一次高强度训练至少间隔 36-48 小时。"},
    "pl.target.rest": {"en": "Rest or pain-free gentle movement", "zh": "休息，或进行无痛的轻度活动"},
    "pl.purpose.rest": {"en": "Absorb recent training and restore readiness.", "zh": "吸收近期训练效果，恢复身体状态。"},
    "pl.recovery.rest": {"en": "Resume when normal movement feels comfortable.", "zh": "当日常活动感觉舒适后再恢复训练。"},
    "pl.type.recovery_day": {"en": "Recovery day", "zh": "恢复日"},
    "pl.target.recovery_low_impact": {"en": "Rest or pain-free low-impact movement", "zh": "休息，或进行无痛的低冲击活动"},
    "pl.purpose.recovery": {
        "en": "Respond conservatively to current soreness, pain, or training-load signals.",
        "zh": "针对当前的酸痛、疼痛或训练负荷信号，采取保守应对。",
    },
    "pl.recovery.recovery": {
        "en": "Reassess symptoms tomorrow before resuming normal training.",
        "zh": "明天重新评估症状后再恢复正常训练。",
    },
    "pl.adjustment.missed": {
        "en": "{missed} planned session(s) were missed. Continue with the schedule; do not stack missed mileage onto one day.",
        "zh": "错过了 {missed} 次计划训练。请继续按计划进行，不要把错过的里程堆到某一天补上。",
    },
    "pl.adjustment.consecutive_hard": {
        "en": "Consecutive feedback-rated hard days were detected. Keep the next session easy or take recovery time.",
        "zh": "检测到连续几天评分为高强度的训练。请将下一次训练安排为轻松跑，或安排恢复时间。",
    },
    "pl.adjustment.none": {
        "en": "No automatic schedule adjustment is needed from available completion data.",
        "zh": "根据现有的完成情况数据，暂不需要自动调整计划。",
    },

    "an.feedback.none": {"en": "No runs found yet. Connect Strava or Coros to get feedback.", "zh": "还没有找到跑步记录。请连接 Strava 或 Coros 以获取反馈。"},
    "an.feedback.total": {"en": "Across the {count} loaded runs, you covered {mileage} km.", "zh": "在已加载的 {count} 次跑步中，你总共跑了 {mileage} 公里。"},
    "an.feedback.pace_narrow": {
        "en": "Pace varied by only {spread} min/km across the loaded runs. If these were meant to serve different purposes, make easy days easier before adding more intensity.",
        "zh": "已加载跑步的配速差异仅为 {spread} 分钟/公里。如果这些训练本应有不同的目的，建议先让轻松日更轻松，再增加强度。",
    },
    "an.feedback.pace_spread": {
        "en": "Pace spans {spread} min/km across the loaded runs, showing a mix of effort levels.",
        "zh": "已加载跑步的配速跨度为 {spread} 分钟/公里，显示出多种强度水平。",
    },
    "an.feedback.hr_narrow": {
        "en": "Average heart rate varies by {diff} bpm across runs with heart-rate data. That may mean several sessions landed at a similar effort, so keep recovery runs clearly easy.",
        "zh": "有心率数据的跑步中，平均心率差异为 {diff} bpm。这可能意味着几次训练的强度相近，请确保恢复跑保持明显轻松。",
    },
    "an.feedback.long_run": {
        "en": "Your longest run was {distance} km, at least 50% longer than the average loaded run.",
        "zh": "你最长的一次跑步为 {distance} 公里，比平均已加载跑步距离长至少 50%。",
    },
    "an.workout.race_day_taper": {
        "en": "Race day in {days} day(s) — tapering this week: reduced long-run volume, easy effort only, extra rest.",
        "zh": "还有 {days} 天比赛 —— 本周进入减量期：减少长距离跑量，只进行轻松强度，增加休息。",
    },
    "an.workout.race_day": {"en": "{label} ({date}): Race day — good luck!", "zh": "{label}（{date}）：比赛日 —— 祝你好运！"},
    "an.workout.already_logged": {"en": "{label} ({date}): already logged.", "zh": "{label}（{date}）：已记录。"},
    "an.workout.day_plan": {"en": "{label} ({date}): {plan}", "zh": "{label}（{date}）：{plan}"},
    "an.workout.easy_run": {"en": "Easy run: 6-8 km @ ~{pace}, keep effort conversational.", "zh": "轻松跑：6-8 公里 @ ~{pace}，保持可以交谈的强度。"},
    "an.workout.tempo_run": {"en": "Tempo run: 5 km @ ~{pace} after a 10 min warm-up.", "zh": "节奏跑：热身 10 分钟后，5 公里 @ ~{pace}。"},
    "an.workout.long_run": {"en": "Long run: {distance} km @ easy effort, focus on time on feet.", "zh": "长距离跑：{distance} 公里，轻松强度，注重持续运动时间。"},
    "an.workout.easy_taper": {"en": "Easy run: 4-6 km @ ~{pace}, keep it light.", "zh": "轻松跑：4-6 公里 @ ~{pace}，保持轻松。"},
    "an.workout.rest": {"en": "Rest or light cross-train.", "zh": "休息或进行轻度交叉训练。"},
    "an.workout.model_adjusted": {
        "en": "Pace targets above adjusted using a trained model fit on {count} logged feedback entries.",
        "zh": "以上配速目标已使用基于 {count} 条已记录反馈拟合的模型进行调整。",
    },
    "an.workout.model_unreliable": {
        "en": "{count} feedback entries logged, but the trained model's pace/difficulty relationship isn't reliable yet — using rule-based baseline paces.",
        "zh": "已记录 {count} 条反馈，但训练模型的配速/难度关系尚不可靠 —— 目前使用基于规则的基线配速。",
    },
    "an.workout.baseline_note": {
        "en": "Pace targets are the rule-based baseline — log feedback on {min_samples}+ runs to unlock model-based adjustment.",
        "zh": "当前配速目标为基于规则的基线值 —— 记录 {min_samples}+ 次跑步反馈即可解锁基于模型的调整。",
    },
    "an.today": {"en": "Today", "zh": "今天"},
    "an.tomorrow": {"en": "Tomorrow", "zh": "明天"},
    "an.weekday.monday": {"en": "Monday", "zh": "周一"},
    "an.weekday.tuesday": {"en": "Tuesday", "zh": "周二"},
    "an.weekday.wednesday": {"en": "Wednesday", "zh": "周三"},
    "an.weekday.thursday": {"en": "Thursday", "zh": "周四"},
    "an.weekday.friday": {"en": "Friday", "zh": "周五"},
    "an.weekday.saturday": {"en": "Saturday", "zh": "周六"},
    "an.weekday.sunday": {"en": "Sunday", "zh": "周日"},
    "an.schedule.easy_run": {"en": "Easy run", "zh": "轻松跑"},
    "an.schedule.tempo_run": {"en": "Tempo run", "zh": "节奏跑"},
    "an.schedule.long_run": {"en": "Long run", "zh": "长距离跑"},
    "an.schedule.easy_taper": {"en": "Easy run (taper)", "zh": "轻松跑（减量期）"},
    "an.schedule.rest": {"en": "Rest", "zh": "休息"},

    "ra.comparison": {
        "en": "This pace was {delta} min/km {direction} than {count} similar-distance run(s).",
        "zh": "这次配速比 {count} 次相似距离的跑步{direction} {delta} 分钟/公里。",
    },
    "ra.slower": {"en": "slower", "zh": "更慢"},
    "ra.faster": {"en": "faster", "zh": "更快"},
    "ra.wentwell.completed": {
        "en": "Completed {distance} km with {elevation} m of climbing.",
        "zh": "完成了 {distance} 公里，爬升 {elevation} 米。",
    },
    "ra.wentwell.faster": {
        "en": "Pace was faster than the available similar-distance baseline.",
        "zh": "配速比可用的相似距离基线更快。",
    },
    "ra.improve.log_feedback": {
        "en": "Log subjective feedback so future recommendations can account for how this effort felt.",
        "zh": "记录主观反馈，以便未来的建议能够考虑这次训练的实际感受。",
    },
    "ra.improve.hr_unavailable": {
        "en": "Average heart rate was unavailable, so effort-zone evaluation could not be calculated.",
        "zh": "平均心率数据不可用，因此无法计算强度区间评估。",
    },
    "ra.recovery": {
        "en": "Use an easy or rest day next if this effort felt hard, soreness is elevated, or pain is worsening.",
        "zh": "如果这次训练感觉吃力、酸痛加剧或疼痛恶化，下一次请安排轻松跑或休息日。",
    },
    "ra.unavailable.splits": {"en": "Splits and negative-split detection", "zh": "分段配速与负分段检测"},
    "ra.unavailable.hr_drift": {"en": "Heart-rate drift", "zh": "心率漂移"},
    "ra.unavailable.cadence": {"en": "Cadence changes", "zh": "步频变化"},
    "ra.unavailable.grade_pace": {"en": "Grade-adjusted pace", "zh": "坡度调整配速"},
    "ra.unavailable.elevation_profile": {"en": "Elevation profile", "zh": "爬升剖面"},
    "ra.unavailable.easy_effort": {
        "en": "Easy-run effort evaluation without personal heart-rate zones",
        "zh": "在没有个人心率区间的情况下评估轻松跑强度",
    },

    "pr.none": {"en": "No activity data is available.", "zh": "暂无可用的活动数据。"},
    "pr.longest_run": {"en": "Longest run", "zh": "最长跑步"},
    "pr.greatest_elevation": {"en": "Greatest elevation gain", "zh": "最大爬升高度"},
    "pr.highest_mileage_week": {"en": "Highest-mileage week", "zh": "单周最高跑量"},
    "pr.consistency_streak": {"en": "Consistency streak", "zh": "连续训练周数"},
    "pr.week": {"en": "week", "zh": "周"},
    "pr.weeks": {"en": "weeks", "zh": "周"},
    "pr.kind.calculated": {"en": "Calculated", "zh": "计算得出"},
    "pr.kind.calculated_weeks": {"en": "Calculated from weeks with a run", "zh": "根据有跑步记录的周计算得出"},
    "pr.kind.estimated": {"en": "Estimated from activity", "zh": "根据活动记录估算"},
    "pr.fastest_1k": {"en": "Fastest 1K", "zh": "最快 1 公里"},
    "pr.fastest_mile": {"en": "Fastest mile", "zh": "最快 1 英里"},
    "pr.fastest_5k": {"en": "Fastest 5K", "zh": "最快 5 公里"},
    "pr.fastest_10k": {"en": "Fastest 10K", "zh": "最快 10 公里"},
    "pr.fastest_half": {"en": "Fastest half marathon", "zh": "最快半程马拉松"},
    "pr.fastest_marathon": {"en": "Fastest marathon", "zh": "最快全程马拉松"},
    "pr.unavailable.split": {"en": "Strongest negative split requires split data from the activity source.", "zh": "最佳负分段成绩需要数据源提供分段数据。"},
    "pr.unavailable.official": {"en": "Official race records require an official-result field.", "zh": "官方比赛记录需要提供官方成绩字段。"},

    "rp.phase.race": {"en": "Race", "zh": "比赛"},
    "rp.phase.taper": {"en": "Taper", "zh": "减量期"},
    "rp.phase.peak": {"en": "Peak", "zh": "巅峰期"},
    "rp.phase.build": {"en": "Build", "zh": "建设期"},
    "rp.phase.base": {"en": "Base", "zh": "基础期"},
    "rp.confidence.moderate": {"en": "Moderate", "zh": "中等"},
    "rp.confidence.low": {"en": "Low", "zh": "较低"},
    "rp.explanation": {
        "en": "Riegel estimate from a {distance} km run in {duration} minutes; range is +/-5% and is not guaranteed.",
        "zh": "基于一次 {distance} 公里、耗时 {duration} 分钟的跑步，使用 Riegel 公式估算；范围为 ±5%，不保证准确。",
    },
    "rp.checklist.shoes": {"en": "Confirm shoes and race logistics", "zh": "确认跑鞋和比赛物流安排"},
    "rp.checklist.sleep": {"en": "Prioritize sleep and familiar meals", "zh": "优先保证睡眠，饮食保持熟悉的食物"},
    "rp.checklist.avoid_hard": {"en": "Avoid unplanned hard efforts", "zh": "避免计划外的高强度训练"},
    "rp.checklist.follow_phase": {"en": "Follow the current phase consistently", "zh": "持续遵循当前训练阶段的安排"},
    "rp.checklist.fueling": {"en": "Practice fueling on longer runs", "zh": "在长距离跑中练习补给策略"},
    "rp.checklist.log_feedback": {"en": "Log feedback after key sessions", "zh": "在关键训练后记录反馈"},
    "rp.pacing.with_target": {
        "en": "Start controlled, settle near goal effort, and only increase effort late if the pace remains sustainable.",
        "zh": "起跑时保持可控，稳定在目标强度附近，只有在配速仍可持续的情况下才在后段提速。",
    },
    "rp.pacing.no_target": {
        "en": "Set a target time to generate a target pace; begin conservatively and avoid an early surge.",
        "zh": "设置目标时间以生成目标配速；起跑保持保守，避免过早冲刺。",
    },

    "rt.trend.stable": {"en": "Stable", "zh": "稳定"},
    "rt.trend.improving": {"en": "Improving", "zh": "改善中"},
    "rt.trend.worsening": {"en": "Worsening", "zh": "恶化中"},

    "sg.urgent": {
        "en": "Urgent safety check: your answers may indicate a symptom that needs prompt in-person medical assessment. Stop running for now. Seek urgent care or emergency help now for chest pain, breathing trouble, new weakness/numbness, loss of bladder or bowel control, deformity, or inability to bear weight. This app cannot assess an injury remotely.",
        "zh": "紧急安全提示：你的回答可能提示需要尽快接受面诊评估的症状。请暂停跑步。如出现胸痛、呼吸困难、新出现的无力/麻木、大小便失禁、畸形或无法负重，请立即寻求紧急医疗救助。本应用无法远程评估伤情。",
    },
    "sg.load_note": {
        "en": " Your recent logged distance changed {change}% versus the prior set of runs.",
        "zh": " 你近期记录的跑步距离相比此前一段时期变化了 {change}%。",
    },
    "sg.body": {
        "en": "For {areas}, reduce or pause painful running for 48–72 hours and keep all movement below pain-provoking levels. Consider gentle, comfortable mobility, sleep, hydration, and low-impact cross-training only if it is pain-free.{load_note} Avoid speed work, hills, and pushing through sharp or worsening pain. Resume gradually only after daily activities and easy movement are comfortable; a licensed clinician or physical therapist can provide an individual assessment. This is educational information, not a diagnosis, treatment plan, or emergency care.",
        "zh": "针对{areas}，请在 48–72 小时内减少或暂停会引发疼痛的跑步，并将所有活动保持在不引发疼痛的强度以下。可以考虑温和、舒适的活动、充足睡眠、补水，以及仅在完全无痛时进行低冲击的交叉训练。{load_note}避免速度训练、坡道训练，以及在剧烈或加重的疼痛下坚持训练。只有在日常活动和轻度活动都感到舒适后，才逐步恢复训练；持证的临床医生或物理治疗师可以提供个体化评估。此内容仅为教育信息，并非诊断、治疗方案或紧急医疗建议。",
    },
}


def translate(key: str, lang: str = "en") -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("en") or key


# Area code -> display label, matching the 34 clickable regions in
# src/static/recovery.js and the BODY_AREAS validation set in app.py.
AREA_LABELS: dict[str, dict[str, str]] = {
    "head_face": {"en": "Head / face", "zh": "头部 / 面部"},
    "jaw": {"en": "Jaw", "zh": "下颌"},
    "neck": {"en": "Neck", "zh": "颈部"},
    "collarbones": {"en": "Collarbones", "zh": "锁骨"},
    "shoulders": {"en": "Shoulders", "zh": "肩部"},
    "biceps_triceps": {"en": "Biceps / triceps", "zh": "肱二头肌 / 肱三头肌"},
    "elbows": {"en": "Elbows", "zh": "肘部"},
    "forearms": {"en": "Forearms", "zh": "前臂"},
    "wrists_hands": {"en": "Wrists / hands", "zh": "手腕 / 手部"},
    "chest": {"en": "Chest", "zh": "胸部"},
    "ribs": {"en": "Ribs / side body", "zh": "肋部 / 侧身"},
    "abdomen": {"en": "Abdomen", "zh": "腹部"},
    "upper_back": {"en": "Upper back", "zh": "上背部"},
    "mid_back": {"en": "Mid back", "zh": "中背部"},
    "lower_back": {"en": "Lower back", "zh": "下背部"},
    "sacrum_si": {"en": "Sacrum / SI joint", "zh": "骶骨 / 骶髂关节"},
    "hips": {"en": "Outer hips", "zh": "髋外侧"},
    "hip_flexors": {"en": "Hip flexors", "zh": "髋屈肌"},
    "glutes": {"en": "Glutes", "zh": "臀肌"},
    "groin_adductors": {"en": "Groin / adductors", "zh": "腹股沟 / 内收肌"},
    "quads": {"en": "Quads", "zh": "股四头肌"},
    "inner_thighs": {"en": "Inner thighs", "zh": "大腿内侧"},
    "outer_thighs": {"en": "Outer thighs / IT band", "zh": "大腿外侧 / 髂胫束"},
    "hamstrings": {"en": "Hamstrings", "zh": "腘绳肌"},
    "kneecap": {"en": "Kneecap", "zh": "髌骨"},
    "inner_knee": {"en": "Inner knee", "zh": "膝内侧"},
    "outer_knee": {"en": "Outer knee", "zh": "膝外侧"},
    "shins": {"en": "Shins", "zh": "胫部"},
    "calves": {"en": "Calves", "zh": "小腿"},
    "achilles": {"en": "Achilles", "zh": "跟腱"},
    "ankles": {"en": "Ankles", "zh": "脚踝"},
    "heels": {"en": "Heels", "zh": "脚跟"},
    "feet": {"en": "Feet / arches", "zh": "脚部 / 足弓"},
    "toes": {"en": "Toes", "zh": "脚趾"},
    # Legacy/broad-region aliases accepted for validation; not surfaced as their
    # own buttons, but translated in case older saved check-ins display them.
    "groin": {"en": "Groin", "zh": "腹股沟"},
    "knees": {"en": "Knees", "zh": "膝部"},
}


def area_label(area_code: str, lang: str = "en") -> str:
    entry = AREA_LABELS.get(area_code)
    if not entry:
        return area_code.replace("_", " ").title()
    return entry.get(lang) or entry.get("en") or area_code
