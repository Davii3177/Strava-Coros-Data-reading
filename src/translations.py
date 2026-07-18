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
}


def translate(key: str, lang: str = "en") -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get("en") or key
