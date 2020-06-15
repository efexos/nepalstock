import os
import sys
import time
import numpy
if sys.platform == "win32":
    import msvcrt
import select
import pandas
import traceback

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

def getstockcode(stock):
    file = open(os.getcwd() + "/drivers/stockcodes.txt", "r")
    for line in file:
        word = line.split(" ")
        if (word[1] == stock+"\n"):
            return word[0]

def getstocks():
    print("Enter Stocks: ", end='', flush=True)
    stockLine = sys.stdin.readline()
    stockLine = stockLine.replace("\n", "")
    stockLine = stockLine.upper()
    stockArr = stockLine.split(",")
    stockCodeArr = []
    print("Loading Stock Codes.")
    for stock in stockArr:
        code = getstockcode(stock)
        stockCodeArr = numpy.append(stockCodeArr, code)
        print(stock, "=", code)
    return stockArr, stockCodeArr
    #...!

def getdriver():
    path = os.getcwd()
    chromeOptions = webdriver.ChromeOptions()
    firefoxOptions = webdriver.FirefoxOptions()
    chromeOptions.headless = True
    chromeOptions.add_argument("--log-level=3")
    firefoxOptions.headless = True
    try:
        if sys.platform == "linux":
            driver = webdriver.Chrome(executable_path=path+'/drivers/chromedriver', options=chromeOptions)
        elif sys.platform == "win32":
            driver = webdriver.Chrome(executable_path=path+'/drivers/chromedriver.exe', options=chromeOptions)
        return driver
    except WebDriverException:
        try:
            if sys.platform == "linux":
                driver = webdriver.Firefox(executable_path=path+'/drivers/geckodriver', options=firefoxOptions)
            elif sys.platform == "win32":
                driver = webdriver.Firefox(executable_path=path+'/drivers/geckodriver.exe', options=firefoxOptions)
            return driver
        except WebDriverException:
            print("No supported browsers found.")
            sys.exit(0)
    #...!

def getprices(driver, stock):
    tempArr = []
    tempArr = numpy.append(tempArr, stock)
    data = driver.find_elements_by_xpath("//table[@class='depthIndex']")
    for string in data:
        for line in string.text.split("\n"):
            word = line.split(" ")
            tempArr = numpy.append(tempArr, word[0])
    tempArr = numpy.delete(tempArr, 2)
    return tempArr
    #...!

def getmarket(driver, stock):
    buy = []
    sell = []
    tempArr = []
    switch = "off"
    loop = 0
    data = driver.find_elements_by_xpath("//table[@class='table table-striped table-bordered orderTable']")
    for string in data:
        for line in string.text.split("\n"):
            if line == "Buy Orders Buy Qty Buy Price":
                switch = "buy"
            elif line == "Sell Price Sell Qty Sell Orders":
                switch = "sell"
            if line[0].isdigit() == True:
                if switch == "buy":
                    buy = numpy.append(buy, line)
                elif switch == "sell":
                    sell = numpy.append(sell, line)
    if len(sell) < len(buy):
        while len(sell) < len(buy):
            sell = numpy.append(sell, "--- --- ---")
    elif len(sell) > len(buy):
        while len(buy) < len(sell):
            buy = numpy.append(buy, "--- --- ---")
    while loop < len(buy):
        prices = []
        prices = numpy.append(prices, stock)
        for word in buy[loop].split(" "):
            prices = numpy.append(prices, word)
        for word in sell[loop].split(" "):
            prices = numpy.append(prices, word)
        loop = loop + 1
        tempArr.append(prices)
    tempArr.append(['---','---','---','---','---','---','---'])
    return tempArr
    # ...!

def clearscreen():
    if sys.platform == "linux":
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")
    #...!

def checkexit():
    if sys.platform == "linux":
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            print("Exiting...please wait.")
            return True
    elif sys.platform == "win32":
        if msvcrt.kbhit():
            if msvcrt.getch() == chr(13):
                print("Exiting. Please wait.")
                return True

def main():
    stocks = []
    stocks, stocksCode = getstocks()
    driver = getdriver()
    print("Press 'Enter' to exit")
    print("Loading: ", end='', flush=True)
    while True:
        try:
            loop = 0
            pricesArr = []
            marketArr = []
            while loop < len(stocks):
                try:
                    print(stocks[loop], end='', flush=True)
                    driver.get("http://nepalstock.com/marketdepthofcompany/" + stocksCode[loop])
                    print(".", end='', flush=True)
                    pricesArr.append(getprices(driver, stocks[loop]))
                    getmarket(driver, stocks[loop])
                    marketArr = marketArr + getmarket(driver, stocks[loop])
                    if checkexit() == True:
                        break
                    loop = loop + 1
                except WebDriverException:
                    print("Check internet connection and make sure www.nepsestock.com.np is not down..!")
                    driver.close()
                    sys.exit(0)
            pricesDataFrame = pandas.DataFrame(pricesArr, columns=['StockSymbol','LivePrice','PrevPrice','OpenPrice','HighPrice','LowPrice','ClosePrice'])
            marketDataFrame = pandas.DataFrame(marketArr, columns=['Stock','BuyOrders','BuyQuantity','BuyPrice','SellPrice','SellQuantity','SellOrders'])
            if checkexit() == True:
                break
            clearscreen()
            print("!..Prices..!")
            print(pricesDataFrame, "\n")
            print("!..Market..!")
            print(marketDataFrame)
            time.sleep(1)
            print("Press 'Enter' to exit.")
            print("Refreshing: ", end='', flush=True)
        except KeyboardInterrupt:
            break
    driver.close()
    sys.exit(0)
    #...!

if __name__ == "__main__":
    main()
    #...!