from apscheduler.schedulers.background import BackgroundScheduler
from crawl import fetch_page, parse_page
from database import save_document
scheduler = BackgroundScheduler()
def crawl_onw():
    urls = [
        "https://www.baidu.com",
        "https://example.com",
    ]
    for url in urls:
        html = fetch_page(url)
        if html.startswith("Error"):
            continue
        parsed = parse_page(html)
        result = save_document(url, parsed["title"], parsed["content"])
        print(f'[定时任务]{url} -> {result}')
