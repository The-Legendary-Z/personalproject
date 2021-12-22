import time
import alpaca_trade_api as alpaca

# Code for connecting to the API. The credentials have been omitted for security's sake
api = alpaca.REST(ALPACA_KEY_ID,
                    ALPACA_SECRET,
                    'https://paper-api.alpaca.markets')


# List of all the stocks that the bot will buy or sell
portfolio = [
    "AAPL",
    "GOOGL",
    "MSFT"
]


# This records the time when the program started and how often it should loop. It's used to run the program in a
# loop with a given amount of time of delay
starttime = time.time()
looptime = 60.0


# Main loop of the program, it's the one that gets looped by looptime and starttime
while True:

    # This "for" loop cycles through each stock
    for stock in portfolio:
        bars = api.get_barset(stock, "1Min")
        df = bars.df
        tickr = stock


        def rsi(df):
            """
            Given a DataFrame, returns rsi of "close" column.
            Output type is Pandas Series.
            """

            diff = df[(tickr, "close")].diff()

            pos = diff.clip(lower=0)
            neg = -1 * diff.clip(upper=0)

            avg_g = pos.ewm(com=13, adjust=True, min_periods=14).mean()
            avg_l = neg.ewm(com=13, adjust=True, min_periods=14).mean()

            rs = avg_g / avg_l
            rsi = 100 - (100 / (1 + rs))
            rsi = rsi.iloc[98]

            return rsi

        def ema(df, period):
            """
            Given a DataFrame and a period, returns moving average in the period.
            Output type is Pandas Series
            """

            ema = df[(tickr, "close")].ewm(com=period-1).mean()
            ema = ema.iloc[98]

            return ema

        def stochastick(df, period):
            """
            Given a DataFrame, returns stochastic K line.
            Output type is numpy.float64
            """

            c = df.iloc[99, 3]
            lbdf = df.iloc[(100-period):100]

            h = lbdf[(tickr, "high")].max()
            l = lbdf[(tickr, "low")].min()

            stochastick = ((c - l) / (h - l)) * 100

            return stochastick

        def stochasticd(df, period):
            """
            Given a DataFrame, returns stochastic D line.
            Output type is numpy.float64
            """

            lastdf = df.iloc[:99]
            stlastdf = df.iloc[:98]

            stochasticd = (stochastick(df,15)+stochastick(lastdf,15)+stochastick(stlastdf,15))/3

            return stochasticd


        def checkrsi(df):
            """
            Given the result of the rsi function, this function determines if there is a buy or sell signal.
            Outputs an integer.
            """

            lastdf = df.iloc[:99]

            result = 0

            if (rsi(lastdf) < 80) and (rsi(df) >= 80):
                result = 1

            elif (rsi(lastdf) > 20) and (rsi(df) <= 20):
                result = 2

            else:
                result = 0

            print(f"[Log] RSI Signal: {result}")

            return result

        def checkma(df, shortp, longp):
            """
            Given the result of the ema function, this function determines if there is a buy or sell signal.
            Outputs an integer.
            """

            lastdf = df.iloc[:99]

            result = 0

            if (ema(lastdf, shortp) < ema(lastdf, longp)) and (ema(df, shortp) >= ema(df, longp)):
                result = 1

            elif (ema(lastdf, shortp) > ema(lastdf, longp)) and (ema(df, shortp) <= ema(df, longp)):
                result = 2

            else:
                result = 0

            print(f"[Log] MA Signal: {result}")

            return result

        def checkstochastic(df, periodd):

            """
            Given the result of the stochasticd function, this function determines if there is a buy or sell signal.
            Outputs an integer.
            """

            lastdf = df.iloc[:99]

            result = 0

            if stochasticd(lastdf, periodd) < 80 and stochasticd(df, periodd) >= 80:
                result = 1

            elif stochasticd(lastdf, periodd) > 20 and stochasticd(df, periodd) <= 20:
                result = 2

            else:
                result = 0

            print(f"[Log] Stochastic Signal: {result}")

            return result

        # The checkrsi, checkstochastic and checkma functions' output is interpreted as:
        # 0: Do nothing
        # 1: Buy signal
        # 2: Sell signal


        def trade(df):
            """
            Given the checkrsi, checkma and checkstochastic functions, this function processes the signals and makes
            the orders.
            Does not output anything.
            """

            result = 0
            if checkma(df, 1, 5) == checkrsi(df):
                result = checkrsi(df)

            elif chceckma(df, 1, 5) != checkrsi(df) and (checkstochastic(df, 14) == checkma(df, 1 ,5) or checkrsi(df)):
                    result = checkstochastic(df, 14)

            else:
                result = 0

            print(f"[Log] Action: {result}")


            if result == 1:
                api.submit_order(symbol=tickr, qty=1, side="buy", type="market", time_in_force="gtc")

                print(f"[Log] Bought {tickr}")

            elif result == 2:
                api.submit_order(symbol=tickr, qty=1, side="sell", type="market", time_in_force="gtc")

                print(f"[Log] Sold {tickr}")


    trade(df)

    
    # Pauses the loop for an amount of time given by looptime
    time.sleep(looptime - ((time.time() - starttime) % looptime))
