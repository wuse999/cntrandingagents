"""基于 yfinance 的新闻数据获取函数。"""

import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .stockstats_utils import yf_retry


def _extract_article_data(article: dict) -> dict:
    """从 yfinance 新闻格式中提取文章数据（兼容嵌套 `content` 结构）。"""
    # 处理嵌套 content 结构
    if "content" in article:
        content = article["content"]
        title = content.get("title", "无标题")
        summary = content.get("summary", "")
        provider = content.get("provider", {})
        publisher = provider.get("displayName", "未知来源")

        # 从 canonicalUrl 或 clickThroughUrl 中提取 URL
        url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
        link = url_obj.get("url", "")

        # 获取发布时间
        pub_date_str = content.get("pubDate", "")
        pub_date = None
        if pub_date_str:
            try:
                pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return {
            "title": title,
            "summary": summary,
            "publisher": publisher,
            "link": link,
            "pub_date": pub_date,
        }
    else:
        # 平铺结构的回退处理
        return {
            "title": article.get("title", "无标题"),
            "summary": article.get("summary", ""),
            "publisher": article.get("publisher", "未知来源"),
            "link": article.get("link", ""),
            "pub_date": None,
        }


def get_news_yfinance(
    ticker: str,
    start_date: str,
    end_date: str,
) -> str:
    """
    使用 yfinance 获取指定股票代码的新闻。

    参数：
        ticker: 股票代码（例如 "AAPL"）
        start_date: 开始日期，格式为 yyyy-mm-dd
        end_date: 结束日期，格式为 yyyy-mm-dd

    返回：
        str: 包含新闻文章的格式化字符串
    """
    try:
        stock = yf.Ticker(ticker)
        news = yf_retry(lambda: stock.get_news(count=20))

        if not news:
            return f"{ticker} 没有找到相关新闻。"

        # 解析日期区间并用于过滤
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        news_str = ""
        filtered_count = 0

        for article in news:
            data = _extract_article_data(article)

            # 如果有发布时间，则按日期过滤
            if data["pub_date"]:
                pub_date_naive = data["pub_date"].replace(tzinfo=None)
                if not (start_dt <= pub_date_naive <= end_dt + relativedelta(days=1)):
                    continue

            news_str += f"### {data['title']}（来源：{data['publisher']}）\n"
            if data["summary"]:
                news_str += f"{data['summary']}\n"
            if data["link"]:
                news_str += f"链接：{data['link']}\n"
            news_str += "\n"
            filtered_count += 1

        if filtered_count == 0:
            return f"{ticker} 在 {start_date} 到 {end_date} 之间没有找到相关新闻。"

        return f"## {ticker} 新闻（{start_date} 至 {end_date}）\n\n{news_str}"

    except Exception as e:
        return f"获取 {ticker} 新闻失败：{str(e)}"


def get_global_news_yfinance(
    curr_date: str,
    look_back_days: int = 7,
    limit: int = 10,
) -> str:
    """
    使用 yfinance Search 获取全球/宏观经济新闻。

    参数：
        curr_date: 当前日期，格式为 yyyy-mm-dd
        look_back_days: 向前回看的天数
        limit: 返回的最大文章数

    返回：
        str: 包含全球新闻文章的格式化字符串
    """
    # 用于检索宏观/全球新闻的搜索词
    search_queries = [
        "stock market economy",
        "Federal Reserve interest rates",
        "inflation economic outlook",
        "global markets trading",
    ]

    all_news = []
    seen_titles = set()

    try:
        for query in search_queries:
            search = yf_retry(lambda q=query: yf.Search(
                query=q,
                news_count=limit,
                enable_fuzzy_query=True,
            ))

            if search.news:
                for article in search.news:
                    # 同时兼容平铺结构与嵌套结构
                    if "content" in article:
                        data = _extract_article_data(article)
                        title = data["title"]
                    else:
                        title = article.get("title", "")

                    # 按标题去重
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        all_news.append(article)

            if len(all_news) >= limit:
                break

        if not all_news:
            return f"{curr_date} 没有找到全球新闻。"

        # 计算日期区间
        curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = curr_dt - relativedelta(days=look_back_days)
        start_date = start_dt.strftime("%Y-%m-%d")

        news_str = ""
        for article in all_news[:limit]:
            # 同时兼容平铺结构与嵌套结构
            if "content" in article:
                data = _extract_article_data(article)
                # 跳过晚于 curr_date 发布的文章，避免前视偏差
                if data.get("pub_date"):
                    pub_naive = data["pub_date"].replace(tzinfo=None) if hasattr(data["pub_date"], "replace") else data["pub_date"]
                    if pub_naive > curr_dt + relativedelta(days=1):
                        continue
                title = data["title"]
                publisher = data["publisher"]
                link = data["link"]
                summary = data["summary"]
            else:
                title = article.get("title", "无标题")
                publisher = article.get("publisher", "未知来源")
                link = article.get("link", "")
                summary = ""

            news_str += f"### {title}（来源：{publisher}）\n"
            if summary:
                news_str += f"{summary}\n"
            if link:
                news_str += f"链接：{link}\n"
            news_str += "\n"

        return f"## 全球市场新闻（{start_date} 至 {curr_date}）\n\n{news_str}"

    except Exception as e:
        return f"获取全球新闻失败：{str(e)}"
