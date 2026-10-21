import requests
from bs4 import BeautifulSoup
import re
visited_urls = set()

def fetch_page(url):
    if url in visited_urls:
        return "Error:已经爬过这个URL，跳过"
    visited_urls.add(url)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        return f"Error: {e}"

# 解析网页
def parse_page(html):
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else "无标题"

    # 删掉 script 和 style 标签
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # 正则过滤残留的标签文本
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    # 删掉纯CSS样式的行（如 body{color:#333} 这种）
    text = re.sub(r'[a-zA-Z0-9\s\.\#\-\_,:;\(\)]+\{[^{}]*\}', '', text)
    # 清掉多余空白
    text = re.sub(r'\n+', '\n', text).strip()

    return {"title": title, "content": text[:500]}
