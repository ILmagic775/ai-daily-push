import requests
import json
from datetime import datetime, timedelta

# ========== 配置 ==========
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/8cd53633-56f3-4ce5-994f-bb595cf41356"
AIHOT_API = "https://aihot.virxact.com/api/v1"

# ========== 获取数据 ==========
def fetch_daily():
    """获取今日AI日报"""
    try:
        resp = requests.get(f"{AIHOT_API}/dailies?limit=1", timeout=15)
        data = resp.json()
        if data.get("items"):
            return data["items"][0]
    except Exception as e:
        print(f"日报获取失败: {e}")
    return None

def fetch_selected(limit=10):
    """获取近7天精选"""
    try:
        resp = requests.get(f"{AIHOT_API}/items?mode=selected&window=7d&limit={limit}", timeout=15)
        data = resp.json()
        return data.get("items", [])
    except Exception as e:
        print(f"精选获取失败: {e}")
    return []

# ========== 格式化 ==========
def format_daily_card(daily, items):
    """格式化为飞书卡片"""
    date_str = daily.get("date", datetime.now().strftime("%Y-%m-%d"))
    lead = daily.get("leadTitle", "暂无")
    lead_detail = daily.get("leadParagraph", "")
    
    # 精选内容
    selected_text = ""
    for i, item in enumerate(items[:8], 1):
        title = item.get("title", "未知")
        summary = item.get("summary", "")[:80]
        score = item.get("score", 0)
        category = item.get("category", "")
        
        # 分类图标
        cat_icon = {
            "model": "🧠",
            "product": "🚀",
            "industry": "📊",
            "paper": "📝",
        }.get(category, "💡")
        
        selected_text += f"{cat_icon} **{title}**\n{summary}... (热度:{score})\n\n"
    
    # 构建卡片
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🔥 AI日报 | {date_str}"
                },
                "template": "red"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"**📌 今日头条**\n{lead}\n\n{lead_detail}"
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": f"**📋 今日精选 Top 8**\n\n{selected_text}"
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": f"🔗 [查看完整日报](https://aihot.news/daily/{date_str}) | [AIHOT首页](https://aihot.news)"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "由 AI日报机器人 自动推送 | 数据来源: AIHOT"
                        }
                    ]
                }
            ]
        }
    }
    return card

# ========== 发送飞书 ==========
def send_to_feishu(card):
    """发送到飞书群"""
    try:
        resp = requests.post(
            FEISHU_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps(card),
            timeout=10
        )
        result = resp.json()
        if result.get("code") == 0:
            print("✅ 推送成功！")
            return True
        else:
            print(f"❌ 推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

# ========== 主流程 ==========
def main():
    print(f"⏰ 开始抓取 AIHOT... {datetime.now()}")
    
    # 1. 获取日报
    daily = fetch_daily()
    if not daily:
        print("❌ 无法获取日报")
        return
    
    # 2. 获取精选
    items = fetch_selected(limit=8)
    
    # 3. 格式化
    card = format_daily_card(daily, items)
    
    # 4. 推送
    send_to_feishu(card)
    
    print("✅ 完成！")

if __name__ == "__main__":
    main()
