from flask import Flask, jsonify, send_from_directory
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


app = Flask(__name__, static_folder='static')



# API לפי מקור
@app.route('/api/news/', methods=['GET'])
def get_news():
    try:
        sources = {
            'kore': scrape_kore,
            "ynet": scrape_ynet,
            'inn': scrape_inn,
            'walla': scrape_walla,
            'israelhayom': scrape_israelhayom
        }
# 'inn': scrape_inn
        news = []

        for _ , func in sources.items():
            print(f"התחלתי להריץ את {func.__name__}")
            items = func()  # הפעלת הפונקציה בפועל
            for item in items:
                item['date'] = datetime.strptime(item['date'], "%H:%M").strftime("%H:%M")
                news.append(item)
            print(f"הסיימתי להריץ את {func.__name__}")

        news_sorted = sorted(news, key=lambda x: x['date'], reverse=True)


        return jsonify({
            'status': 'success',
            'sources': list(sources.keys()),
            'count': len(news_sorted),
            'data': news_sorted
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# הגשת האתר
@app.route('/')
def serve_site():
    return send_from_directory("static", 'index.html')


def scrape_ynet():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        })

        page.goto("https://www.ynet.co.il/news/category/184", timeout=120000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        try:
            expanded_radio = page.query_selector('input[type="radio"][value="expanded"]')
            if expanded_radio:
                expanded_radio.click(force=True)
                page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Error clicking expanded view: {e}")

        for _ in range(5):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(1000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.select(".AccordionSection")
    
    news_items = []
    for sec in sections:  # ללא הגבלה על מספר הפריטים
        title = sec.select_one(".title")
        body = sec.select_one(".itemBody")
        Date = sec.select_one(".DateDisplay")
        

        Date = sec.select_one(".DateDisplay")

        if title and body and Date and "|" not in Date.get_text(strip=True):
            news_items.append({
                "title": title.get_text(strip=True),
                "content": body.get_text(strip=True),
                "date": Date.get_text(strip=True),
                "writer_name": "",
                "source": "ynet"
            })
    return news_items

def scrape_kore():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        })

        page.goto("https://www.kore.co.il/mplus", timeout=120000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        for _ in range(5):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(1000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.select(".post")
    
    news_items = []
    for sec in sections:  # ללא הגבלה על מספר הפריטים
        content = sec.get_text(strip=True)
        start_index = content.find("השימוש במדיה")
        if start_index == -1:
            start_index = 0
        else:
            start_index += 62
        
        if content.startswith("מקודם") or "|" in content[-10:]:
            continue
        
        news_items.append({
            "title": "",
            "content": content[start_index:-5:],
            "date": content[-5:].strip(),
            "writer_name": "",
            "source": "kore"
        })
    
    return news_items


def scrape_walla():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        })

        page.goto("https://news.walla.co.il/breaking", timeout=120000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)


        for _ in range(5):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(1000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.select(".css-3mskgx")
    
    news_items = []
    for sec in sections:  # ללא הגבלה על מספר הפריטים
        title = sec.select_one(".breaking-item-title")
        body = sec.select_one(".text-content")
        date = sec.select_one(".red-time")
        writer_el = sec.select_one(".writer-name-item")

        if title and body and date:
            news_items.append({
                "title": title.get_text(strip=True),
                "content": body.get_text(strip=True),
                "date": date.get_text(strip=True).strip(),
                "writer_name": writer_el.get_text(strip=True) if writer_el else "",
                "source": "walla"
            })

    
    return news_items


def scrape_israelhayom():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        })

        page.goto("https://www.israelhayom.co.il/israelnow", timeout=120000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)


        for _ in range(5):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(1000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.select(".israel-now-flash-component.flashes-tab")
    
    news_items = []
    for sec in sections:  # ללא הגבלה על מספר הפריטים
        title = sec.select_one(".israel-now-main-flash")
        body = sec.select_one(".israel-now-flash-description")
        date = sec.select_one(".israel-now-flash-time-text")
        writer_name = sec.select_one(".israel-now-flash-title")

        
        if title and body:
            news_items.append({
                "title": title.get_text(strip=True),
                "content": body.get_text(strip=True),
                "date": date.get_text(strip=True).strip(),
                "writer_name": writer_name.get_text(strip=True),
                "source": "israelhayom"
            })
    
    return news_items


def scrape_inn():
    news_items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        })

        page.goto("https://www.inn.co.il/flashes/", timeout=120000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        for _ in range(5):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(1000)

        # שלב חשוב: מצא את כל הכתבות (פריטי אקורדיון)
        items = page.query_selector_all("li.accordeon-item")

        for item in items:
            try:
                header = item.query_selector(".accordeon-item__header")
                if not header:
                    continue

                # לחץ לפתיחה
                header.click()
                page.wait_for_timeout(100)

                # שלוף כותרת
                title_el = item.query_selector(".title")
                title = title_el.inner_text().strip() if title_el else "אין כותרת"

                # שלוף תוכן
                content_el = item.query_selector(".article-content-inside")
                content = content_el.inner_text().strip() if content_el else "אין תוכן"

                # שלוף זמן
                date_el = item.query_selector(".flash-date")
                date = date_el.inner_text().strip() if date_el else "אין תאריך"


                news_items.append({
                    "title": title,
                    "content": content,
                    "date": date,
                    "writer_name": "",
                    "source": "inn"
                })

            except Exception as e:
                print("שגיאה בפריט:", e)

        browser.close()

    return news_items

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)