# multi-agent-idol-manager
虚拟网红AI经纪人系统

# virtual_idol_agent_system.py
"""
虚拟网红AI经纪人系统 —— 多Agent协同运营自动化
依赖：pip install crewai langchain-openai
运行前：export OPENAI_API_KEY="你的key" （或修改第17行）
"""
import os
import json
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# ========== 配置 ==========
llm = ChatOpenAI(
    model="gpt-4o-mini",     # 可换成 deepseek-chat
    temperature=0.8,
    api_key=os.getenv("OPENAI_API_KEY") or "sk-你的key"
)

# ========== 模拟数据 ==========
def fetch_trending(platform: str = "all") -> str:
    """全平台热点采集"""
    trends = [
        {"rank":1, "title":"夏日泡泡音乐节阵容官宣", "platform":"微博", "heat":9823411},
        {"rank":2, "title":"当i人被迫参加团建", "platform":"抖音", "heat":8753291},
        {"rank":3, "title":"原来猫咪也会emo", "platform":"小红书", "heat":7654321},
        {"rank":4, "title":"当代年轻人开始养石头了", "platform":"微博", "heat":6543210}
    ]
    return json.dumps(trends, ensure_ascii=False)

def get_virtual_idol_profile(name: str) -> str:
    """获取虚拟网红完整档案"""
    profile = {
        "name": name,
        "persona": "外冷内热的二次元电音少女，偶尔毒舌，充满好奇心",
        "fans": {
            "age_range": "16-28",
            "top_interests": ["电子音乐", "搞笑日常", "治愈系", "社死瞬间"],
            "taboo": ["说教", "过度营销", "负能量"]
        }
    }
    return json.dumps(profile, ensure_ascii=False)

def generate_ai_art_prompt(description: str) -> str:
    """生成AI绘图提示词（Midjourney风格）"""
    return (f"Anime key visual of {description}, vibrant neon colors, futuristic street, "
            "character with sharp glowing eyes, floating sound waves, highly detailed, 8k --ar 9:16")

def publish_to_platform(platform: str, content: str, img_prompt: str) -> str:
    """模拟发布（真实场景可接微博/抖音API）"""
    return f"✅ 已发布至 {platform}\n📝 文案：{content[:50]}...\n🖼️ 绘图Prompt已投递：{img_prompt[:80]}..."

def fetch_comments(post_id: str) -> str:
    """模拟帖子评论（含情感标签）"""
    comments = [
        {"user":"小星星123", "text":"阿星今天也超可爱！", "sentiment":"positive"},
        {"user":"路过而已", "text":"这衣服链接能不能发一下", "sentiment":"neutral"},
        {"user":"黑粉头子", "text":"装什么可爱，天天恰饭", "sentiment":"negative"},
        {"user":"电音脑残粉", "text":"什么时候更新新歌？", "sentiment":"positive"}
    ]
    return json.dumps(comments, ensure_ascii=False)

# 注册工具列表
tools_hotspot   = [Tool(name="获取全网热点", func=fetch_trending, description="输入平台(all/weibo/douyin)获取热点榜单"),
                   Tool(name="查询虚拟网红档案", func=get_virtual_idol_profile, description="输入网红名称，获取完整粉丝画像")]

tools_content   = [Tool(name="生成绘图Prompt", func=generate_ai_art_prompt, description="输入场景描述，输出高质量AI绘图Prompt"),
                   Tool(name="发布内容", func=publish_to_platform, description="输入platform, content, image_prompt发布内容")]

tools_radar     = [Tool(name="抓取评论", func=fetch_comments, description="输入帖子ID获取所有评论及情感分类")]

# ========== 4个专业Agent ==========
# 1. 热点猎手
hotspot_hunter = Agent(
    role="热点猎手",
    goal="在全平台筛选出3个与星野アキラ人设最匹配的热点，并给出契合度理由。",
    backstory="你是信息茧房打破者，能从热搜噪声中捞出真正适合二次元电音少女的爆款原料。",
    tools=tools_hotspot,
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# 2. 人设策划师
content_strategist = Agent(
    role="人设策划师",
    goal=("接收热点与粉丝画像，执行长链推理：禁忌检查→人设契合度→情绪切入点→核心创意。"
          "最终输出一份完整内容策略，包含一句话梗概和金句。"),
    backstory="你守护着星野的人格底线，你的每一次策略都经过粉丝画像×品牌调性×热度的三维计算。",
    tools=[tools_hotspot[1]],  # 只用档案查询
    llm=llm,
    verbose=True,
    allow_delegation=True
)

# 3. 内容工坊
content_factory = Agent(
    role="内容工坊",
    goal=("根据策略包，输出：1) 抖音口播脚本（带前3秒钩子） 2) 小红书图文配文（姐妹语气） "
          "3) 调用绘图工具生成配图Prompt 4) 选择最优内容发布到抖音。"),
    backstory="你是全网最懂平台调性的创作机器，手里还握着最先进的AI绘画咒语。",
    tools=tools_content,
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# 4. 舆情雷达
sentiment_radar = Agent(
    role="舆情雷达",
    goal=("监控评论，执行三级分类：合理批评→感谢改进，无脑黑→幽默化解，恶意攻击→上报隐藏。"
          "最后输出一份舆情简报+下次内容优化建议。"),
    backstory="前顶流粉运总监，最擅长用一句俏皮话熄灭评论区战火。",
    tools=tools_radar,
    llm=llm,
    verbose=True,
    allow_delegation=True
)

# ========== 任务链（长链依赖） ==========
task_hunt = Task(
    description="拉取全平台热点 + 获取星野アキラ的完整档案。输出Top3推荐热点，每个附契合度一句话。",
    expected_output="3个热点的JSON列表，带推荐理由",
    agent=hotspot_hunter
)

task_strategy = Task(
    description=("基于[task_hunt]输出的首选热点，严格按步骤推理："
                 "禁忌检查 → 人设契合度(1-10) → 情绪切入点 → 核心创意的金句。"
                 "最终输出含梗概的策略文档。"),
    expected_output="一份策略文档，包含推理链、梗概、金句",
    agent=content_strategist,
    context=[task_hunt]
)

task_produce = Task(
    description=("基于[task_strategy]的策略，创作以下内容："
                 "1. 抖音脚本（带#话题，前3秒钩子）"
                 "2. 小红书图文配文（emoji+标签，姐妹感）"
                 "3. 调用工具为两条内容生成AI绘图Prompt"
                 "4. 选择抖音脚本并调用发布工具，报告结果。"),
    expected_output="发布确认信息及完整内容包",
    agent=content_factory,
    context=[task_strategy]
)

task_radar = Task(
    description=("假设已有帖子ID 'post2024'，抓取评论并分级处理。"
                 "汇总舆情简报：情感比例、高情商回复示例、风险预警、内容优化建议。"),
    expected_output="舆情简报",
    agent=sentiment_radar,
    context=[task_produce]
)

# ========== 启动协同 ==========
crew = Crew(
    agents=[hotspot_hunter, content_strategist, content_factory, sentiment_radar],
    tasks=[task_hunt, task_strategy, task_produce, task_radar],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    print("🌟 星野アキラ经纪团队启动：热点猎手 → 人设策划 → 内容工坊 → 舆情雷达\n")
    result = crew.kickoff()
    print("\n" + "="*50)
    print("最终运营交付物：")
    print(result)
    
