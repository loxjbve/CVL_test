import pandas as pd
from binance.exceptions import BinanceAPIException
from binance.client import Client
import datetime
import mplfinance as mpf
def klines(symbol):
    api_key = ''
    api_secret = ''

    client = Client(api_key, api_secret)

    try:
        # 获取过去12小时内5分钟级别的K线数据
        interval = Client.KLINE_INTERVAL_5MINUTE
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=24)
        klines = client.get_historical_klines(symbol, interval, start_time.strftime("%d %b %Y %H:%M:%S"),
                                              end_time.strftime("%d %b %Y %H:%M:%S"))
        # 提取K线数据
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        for kline in klines:
            dates.append(datetime.datetime.fromtimestamp(kline[0] / 1000.0))
            opens.append(float(kline[1]))
            highs.append(float(kline[2]))
            lows.append(float(kline[3]))
            closes.append(float(kline[4]))
            volumes.append(float(kline[5]))

        # 将数据转换为pandas DataFrame
        data = pd.DataFrame(
            {'Open': opens, 'High': highs, 'Low': lows, 'Close': closes, 'Volume': volumes},
            index=dates
        )
        # 绘制K线图
        plot = mpf.plot(data, type='candle', style='charles', volume=True, ylabel='Price', ylabel_lower='Volume', returnfig=True)
        current_price = data['Close'][-1]
        intraday_change = round((current_price - data['Close'][0]) / data['Close'][0] * 100,3)
        return plot[0], current_price, intraday_change

    except BinanceAPIException:
        #
        return None, None, None