# virtual_idol_agent_system_pro.py
"""
虚拟网红AI经纪人系统 增强版 —— 多Agent协同运营自动化
依赖安装：
    pip install crewai langchain-openai python-dotenv
运行前：
    1. 在同目录创建 .env 文件，写入 OPENAI_API_KEY=你的key
    2. 运行：python virtual_idol_agent_system_pro.py
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# 加载 .env 环境变量
load_dotenv()

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('agent_operations.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 配置类 ====================
class Config:
    """全局配置，可从环境变量覆盖"""
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.8"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VIRTUAL_IDOL_NAME = "星野アキラ"
    # 是否启用Agent记忆（会增加token消耗）
    ENABLE_AGENT_MEMORY = os.getenv("ENABLE_MEMORY", "False").lower() == "true"
    # 最大重试次数
    MAX_RETRIES = 3

config = Config()

if not config.OPENAI_API_KEY:
    raise ValueError("❌ 请在 .env 文件中设置 OPENAI_API_KEY")

# ==================== LLM 初始化 ====================
llm = ChatOpenAI(
    model=config.LLM_MODEL,
    temperature=config.LLM_TEMPERATURE,
    api_key=config.OPENAI_API_KEY,
    # 如果用DeepSeek，取消下一行注释并修改base_url
    # base_url="https://api.deepseek.com/v1",
)

# ==================== 工具函数（增强版） ====================
def fetch_trending(platform: str = "all") -> str:
    """
    全平台热点采集（模拟）
    可替换为真实API：如微博热搜、抖音Trending API
    """
    logger.info(f"正在拉取 {platform} 实时热点...")
    try:
        # 模拟数据，实际可通过requests调用平台接口
        trends = [
            {"rank":1, "title":"夏日泡泡音乐节阵容官宣", "platform":"微博", "heat":9823411},
            {"rank":2, "title":"当i人被迫参加团建", "platform":"抖音", "heat":8753291},
            {"rank":3, "title":"原来猫咪也会emo", "platform":"小红书", "heat":7654321},
            {"rank":4, "title":"当代年轻人开始养石头了", "platform":"微博", "heat":6543210},
            {"rank":5, "title":"AI绘画新模型发布", "platform":"抖音", "heat":5432109},
        ]
        return json.dumps(trends, ensure_ascii=False)
    except Exception as e:
        logger.error(f"热点抓取失败: {str(e)}")
        return json.dumps([])

def get_virtual_idol_profile(name: str) -> str:
    """获取虚拟网红完整档案（模拟数据库查询）"""
    logger.info(f"查询虚拟网红档案: {name}")
    try:
        # 实际可连接数据库或API
        profile = {
            "name": name,
            "persona": "外冷内热的二次元电音少女，偶尔毒舌，充满好奇心，内心住着一只流浪猫的灵魂",
            "fans": {
                "age_range": "16-28",
                "top_interests": ["电子音乐", "搞笑日常", "治愈系", "社死瞬间", "AI科技"],
                "taboo": ["说教", "过度营销", "负能量", "政治敏感", "人身攻击"]
            },
            "content_bible": {
                "dos": ["使用拟声词", "偶尔引用动漫梗", "保持3:7的吐槽与温柔比例"],
                "donts": ["不要直接说教", "不要出现现实品牌硬广", "不要谈论政治"]
            }
        }
        return json.dumps(profile, ensure_ascii=False)
    except Exception as e:
        logger.error(f"档案查询失败: {str(e)}")
        return "{}"

def generate_ai_art_prompt(description: str) -> str:
    """生成AI绘图提示词（Midjourney/SD格式）"""
    logger.info("生成AI绘图Prompt...")
    base_prompt = (
        f"Anime key visual of {description}, "
        "cyberpunk neon lighting, dynamic pose, floating musical notes, "
        "highly detailed eyes, trending on Pixiv, masterpiece, 8k --ar 9:16"
    )
    return base_prompt

def publish_to_platform(platform: str, content: str, img_prompt: str) -> str:
    """
    模拟多平台发布（可替换为抖音/小红书开放平台API）
    """
    logger.info(f"正在发布内容到 {platform}...")
    # 实际请求中处理API鉴权、限流、异常重试
    return json.dumps({
        "status": "success",
        "platform": platform,
        "content_preview": content[:50] + "...",
        "image_prompt": img_prompt,
        "publish_time": datetime.now().isoformat()
    }, ensure_ascii=False)

def fetch_comments(post_id: str) -> str:
    """模拟帖子评论获取，含情感标签"""
    logger.info(f"抓取帖子 {post_id} 的评论...")
    comments = [
        {"id":1, "user":"小星星123", "text":"阿星今天也超可爱！", "sentiment":"positive"},
        {"id":2, "user":"路过而已", "text":"这衣服链接能不能发一下", "sentiment":"neutral"},
        {"id":3, "user":"黑粉头子", "text":"装什么可爱，天天恰饭", "sentiment":"negative"},
        {"id":4, "user":"电音脑残粉", "text":"什么时候更新新歌？", "sentiment":"positive"},
        {"id":5, "user":"理性观众", "text":"最近内容有点水，希望回归音乐", "sentiment":"negative"},
    ]
    return json.dumps(comments, ensure_ascii=False)

def update_ticket_status(ticket_id: str, status: str) -> str:
    """工单状态更新（用于舆情上报）"""
    logger.warning(f"舆情升级工单: {ticket_id} -> {status}")
    return f"工单 {ticket_id} 已标记为 {status}"

# 工具封装，增加元数据
def create_tool(name, func, description, retry=config.MAX_RETRIES):
    """带重试的Tool工厂函数"""
    original_func = func
    def safe_func(*args, **kwargs):
        for attempt in range(1, retry+1):
            try:
                return original_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"工具 {name} 第{attempt}次调用失败: {str(e)}")
                if attempt == retry:
                    return json.dumps({"error": f"工具{name}失败: {str(e)}"})
                continue
    safe_func.__name__ = func.__name__
    safe_func.__doc__ = func.__doc__
    return Tool(name=name, func=safe_func, description=description)

tools_hotspot = [
    create_tool("获取全网热点", fetch_trending, "输入平台(all/weibo/douyin/xiaohongshu)获取热点榜单，返回JSON"),
    create_tool("查询虚拟网红档案", get_virtual_idol_profile, "输入网红名称，返回完整粉丝画像和内容手册"),
]

tools_content = [
    create_tool("生成绘图Prompt", generate_ai_art_prompt, "输入场景描述，输出高质量AI绘图Prompt(Midjourney)"),
    create_tool("发布内容", publish_to_platform, "输入platform, content, image_prompt，模拟发布并返回状态"),
]

tools_radar = [
    create_tool("抓取评论", fetch_comments, "输入帖子ID，获取所有评论及情感分类"),
    create_tool("创建舆情工单", update_ticket_status, "输入工单ID和状态，用于升级高危舆情"),
]

# ==================== Agent 定义（增强） ====================
agent_kwargs = dict(
    llm=llm,
    verbose=True,
    max_iter=5,           # 最大推理迭代
    allow_delegation=False,
)
if config.ENABLE_AGENT_MEMORY:
    agent_kwargs["memory"] = True  # 开启上下文记忆

# 1. 热点猎手
hotspot_hunter = Agent(
    role="热点猎手",
    goal="实时扫描微博、抖音、小红书等平台，快速筛选出3个与「星野アキラ」人设最契合的热点，并要求推荐理由中体现风险初判。",
    backstory=(
        "你曾是互联网大厂的数据情报分析师，擅长从噪声中提取信号。"
        "你熟悉Z世代文化，能一眼看出哪些热搜有爆款潜质且不会踩雷。"
    ),
    tools=tools_hotspot,
    **agent_kwargs
)

# 2. 人设策划师（长链推理中枢）
content_strategist = Agent(
    role="人设策划师",
    goal=(
        "接收热点列表，执行严格的长链推理："
        "1. 禁忌检查 -> 2. 人设契合度(1-10) -> 3. 情绪切入点选择 -> 4. 创意梗概与金句。"
        "最后输出一份可执行的内容策略文档。"
    ),
    backstory=(
        "你是星野アキラ的‘人设守护神’，拥有多年虚拟偶像企划经验。"
        "你帮助角色在商业变现与粉丝信任间找到完美平衡，从未失手。"
    ),
    tools=[tools_hotspot[1]],  # 仅用档案查询
    **agent_kwargs
)

# 3. 内容工坊（多平台创作+发布）
content_factory = Agent(
    role="内容工坊",
    goal=(
        "将策略转化为爆款内容：1) 抖音口播脚本（带前3秒钩子） "
        "2) 小红书图文（姐妹感） 3) 高质感AI绘图Prompt 4) 选择抖音渠道模拟发布。"
    ),
    backstory=(
        "你是MCN机构的王牌编导，深谙各个平台的流量密码。"
        "你手里的AI绘图工具能一键生成媲美职业插画师的视觉。"
    ),
    tools=tools_content,
    **agent_kwargs
)

# 4. 舆情雷达（智能互动+危机预警）
sentiment_radar = Agent(
    role="舆情雷达",
    goal=(
        "监测帖子评论，执行三级处理："
        "- 合理批评 → 感谢并反馈优化池"
        "- 无脑黑 → 幽默化解"
        "- 恶意攻击 → 创建工单上报并建议隐藏"
        "输出舆情简报与下一轮内容建议。"
    ),
    backstory=(
        "你曾是顶流明星的粉运总监，处理过无数次舆论风暴。"
        "你的信条是：永远不让评论区比内容更精彩。"
    ),
    tools=tools_radar,
    **agent_kwargs
)

# 5. （新增）运营分析师——可选全局评估
analytics_agent = Agent(
    role="运营分析师",
    goal="汇总本次运营全流程数据，生成日报，包括热点命中率、内容互动预估、舆情健康度。",
    backstory="你擅长用数据说话，帮助团队不断优化策略。",
    tools=[],
    **agent_kwargs
)

# ==================== 任务链设计 ====================
task_hunt = Task(
    description=(
        "1. 使用工具拉取全平台(参数'all')实时热点。\n"
        "2. 获取虚拟网红「星野アキラ」的完整档案。\n"
        "3. 交叉分析，输出 Top3 候选热点，每个热点附上：排名、热度、平台、契合度一句话理由及潜在风险提示。"
    ),
    expected_output="JSON格式的3个热点对象数组，键包含rank, title, platform, heat, why, risk_note",
    agent=hotspot_hunter
)

task_strategy = Task(
    description=(
        "基于【前序任务】输出的第一个热点，严格按以下步骤推理，并记录每一环：\n"
        "Step1. 禁忌扫描：该热点是否触碰档案中的taboo？\n"
        "Step2. 契合度评分(1-10)：语气、场景、粉丝期待各维度。\n"
        "Step3. 情绪切入点选择：反差萌/毒舌吐槽/暖心陪伴/科技酷感，选一。\n"
        "Step4. 生成一个50字内梗概和一句传播金句。\n"
        "最终输出包含以上四步推理链的 Markdown 格式策略书。"
    ),
    expected_output="一份结构化的策略文档，标题为热点名称，包含四个步骤的详细推理和最终金句。",
    agent=content_strategist,
    context=[task_hunt]
)

task_produce = Task(
    description=(
        "使用【人设策划师】的策略，创作并发布：\n"
        "1. 抖音口播脚本（15-30秒，前3秒必须设置钩子，末尾带5个#话题）。\n"
        "2. 小红书图文（正文姐妹语气，emoji适当，标题带数字+痛点）。\n"
        "3. 调用工具为上述两条内容分别生成AI绘图Prompt。\n"
        "4. 调用发布工具，将抖音版本发布至平台，并返回发布结果JSON。"
    ),
    expected_output="发布确认JSON + 完整的抖音&小红书内容文本及对应绘图Prompt",
    agent=content_factory,
    context=[task_strategy]
)

task_radar = Task(
    description=(
        "假设帖子已发布，ID为 'post2024'。\n"
        "1. 抓取该帖所有评论。\n"
        "2. 按情感分类，对负面评论执行三级处理，生成具体回复文案示例。\n"
        "3. 若出现恶意攻击，调用工具创建工单（id='T-001', status='升级中'）。\n"
        "4. 生成当日舆情简报：情感比例、高情商回复示例、风险预警、内容优化建议3条。"
    ),
    expected_output="一份带数据统计和建议的舆情简报",
    agent=sentiment_radar,
    context=[task_produce]
)

task_report = Task(
    description=(
        "综合【所有前序任务】的输出，生成一份运营日报，包含：\n"
        "- 本次使用的热点及最终内容主题\n"
        "- 情感分析统计（正/负/中比例）\n"
        "- 关键互动指标（预估）\n"
        "- 风险事件说明\n"
        "- 明日改进建议"
    ),
    expected_output="Markdown格式的运营日报",
    agent=analytics_agent,
    context=[task_hunt, task_strategy, task_produce, task_radar]
)

# ==================== 启动 Crew ====================
crew = Crew(
    agents=[hotspot_hunter, content_strategist, content_factory, sentiment_radar, analytics_agent],
    tasks=[task_hunt, task_strategy, task_produce, task_radar, task_report],
    process=Process.sequential,
    verbose=True,
    memory=config.ENABLE_AGENT_MEMORY,
)

def save_output(result):
    """保存最终结果到文件"""
    filename = f"operation_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 虚拟网红AI经纪人运营输出\n")
        f.write(f"生成时间：{datetime.now().isoformat()}\n\n")
        f.write(str(result))
    logger.info(f"运营结果已保存至 {filename}")

if __name__ == "__main__":
    logger.info("🌟 星野アキラ经纪团队启动：热点猎手 → 人设策划 → 内容工坊 → 舆情雷达 → 运营分析师")
    try:
        result = crew.kickoff()
        print("\n" + "="*60)
        print("📦 最终运营交付物：")
        print(result)
        save_output(result)
    except Exception as e:
        logger.error(f"系统运行异常: {str(e)}", exc_info=True)
        raise