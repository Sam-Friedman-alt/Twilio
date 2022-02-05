from requests import get
import datetime as dt
import os
from twilio.rest import Client

def main():
    STOCK = "TSLA"
    COMPANY_NAME = "Tesla Inc"
    API_KEY_AV = os.environ.get("API_KEY_AV")
    AV_URL = "https://www.alphavantage.co/query"
    AV_FUN = "TIME_SERIES_DAILY"
    AV_PARAMS = {"apikey": API_KEY_AV,
                 "function": AV_FUN,
                 "symbol": STOCK, }

    ## STEP 1: Use https://www.alphavantage.co
    # When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
    today = dt.datetime.now().date()
    yesterday = today - dt.timedelta(days=1)
    day_before_yesterday = yesterday - dt.timedelta(days=1)
    with get(AV_URL, params=AV_PARAMS) as stock_data:
        stock_data.raise_for_status()
        stocks = stock_data.json()
        yes_exist = False
    key_error_count = 0
    while not yes_exist:
        try:
            yes_val = float(stocks["Time Series (Daily)"][f"{yesterday}"]["4. close"])
            yes_exist = True
        except KeyError:
            yesterday = yesterday - dt.timedelta(days=1)
            key_error_count += 1
        if key_error_count > 20:
            break
    two_day_exist = False
    key_error_count = 0
    while not two_day_exist:
        try:
            two_val = float(stocks["Time Series (Daily)"][f"{day_before_yesterday}"]["4. close"])
            two_day_exist = True
        except KeyError:
            day_before_yesterday = day_before_yesterday - dt.timedelta(days=1)
            key_error_count += 1
        if key_error_count > 20:
            break
    percent_change = (yes_val - two_val)/yes_val
    percent_change = percent_change*100
    print(percent_change)
    if abs(yes_val - two_val) > 0.01 * yes_val:
        articles = get_news(COMPANY_NAME)
        send_text(articles, STOCK, percent_change)

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
def get_news(company):
    URL = "https://newsapi.org/v2/everything"
    API_KEY_NEWS = os.environ.get("NEWSAPIKEY")
    KEYWORD = company
    NEWS_PARAMS = {"apiKey": API_KEY_NEWS,
                    "q":KEYWORD}
    with get(URL, params=NEWS_PARAMS) as headlines:
        headlines.raise_for_status()
        headline0 = headlines.json()["articles"][0]['title']
        headline1 = headlines.json()["articles"][1]['title']
        headline2 = headlines.json()["articles"][2]['title']
        desc0 = headlines.json()["articles"][0]['description']
        desc1 = headlines.json()["articles"][1]['description']
        desc2 = headlines.json()["articles"][2]['description']

    news = {"article0":[headline0,desc0], "article1":[headline1,desc1], "article2":[headline2,desc2]}
    print(news)
    return news
## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.
def send_text(news, ticker, change):
    ACCOUNT_SID = os.environ.get("SID")
    AUTH_TOKEN = os.environ.get("TOKEN")
    FROM_NUM = os.environ.get("FROM")
    TO_NUM=os.environ.get("TO")
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    if change >= 0:
        icon = "🔺"
    else:
        icon = "🔻"
    change=abs(change)
    for key, value in news.items():
        body = f"{ticker}: {icon}{round(change)}%\nHeadline: {value[0]}\nBrief: {value[1]}"
        client.messages.create(body=body, from_=FROM_NUM, to=TO_NUM)
# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
if __name__ == '__main__':
    main()
