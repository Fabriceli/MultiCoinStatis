# encoding:utf-8
from bs4 import BeautifulSoup
import requests,time
from selenium import webdriver
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os.path


class WebInfo(object):
    """
    WebInfo类主要是获取网页信息并抓取相关重要信息  Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36
    """

    def __init__(self, url):
        self.__url = url
        self.__headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/66.0.3359.117 Safari/537.36"
        }

    def getUrl(self):
        return self.__url

    def setUrl(self, urlValue):
        if (urlValue == "") or (type(urlValue) != str):
            return "url为空或不是字符串！"
        self.__url = urlValue

    def getHTMLText(self):
        try:
            r = requests.get(self.__url, headers=self.__headers, timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            return ""

    def fillUnivList(self, ulist, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            for tr in soup.tbody.find_all('tr'):
                tds = tr('td')
                if tds[1].string is None:
                    ulist.append([tds[0].string,
                                  tds[1].a.string,
                                  tds[2].string,
                                  tds[3].string])
                else:
                    ulist.append([tds[0].string,
                                  tds[1].string,
                                  tds[2].string,
                                  tds[3].string])
            return True
        except:
            print("获取失败")
            return False

    # n表示持币万数
    def getList(self, uList, n):
        length = len(uList)
        result = 0
        for i in range(length):
            u1 = uList[i]
            if eval(u1[2]) >= (n * 10000):
                if length > (i + 1):
                    u2 = uList[i + 1]
                    if eval(u2[2]) <= (n * 10000):
                        result = i + 1
                else:
                    result = i + 1
        return result

    # 前百分比
    def getTopPercent(self, uList, top):
        result = 0
        for i in range(top):
            u = uList[i]
            result += eval(u[3][:-1])
        return result

    # 持币地址数
    def getAdressNumber(self, html):
        result = 0
        try:
            ht = etree.HTML(html)
            divs = ht.xpath("//div[@class='row content-boxes-v2']")
            for div in divs:
                p = div.xpath(".//p/text()")[3]
                if result is 0:
                    result = p.split(":")[-1]
                    break
            return result
        except:
            print("获取持币地址数失败")
            return result

    # 对于以太坊价格
    def getPricetoETH(self, url):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/66.0.3359.117 Safari/537.36"
        }
        result = 0
        try:
            response = requests.get(url, headers=headers)
            html = etree.HTML(response.text)
            tr = html.xpath("//tr[@id='ContentPlaceHolder1_tr_valuepertoken']")[0]
            td = tr.xpath("./td[last()]/text()")[0]
            result = td.split("@")[1].split("E")[0]
            return result
        except:
            print("获取对于以太坊价格失败")
            return result

    def getETH(self, uInfo, url):
        driver_path = "chromedriver.exe"
        if os.path.isfile(driver_path):
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome(executable_path=driver_path, options=options)
            try:
                driver.get(url)
                while len(uInfo) <= 500:
                    WebDriverWait(driver, timeout=10).until(
                        EC.presence_of_element_located((By.XPATH, "//tr[@class='J_link'][last()]")))
                    source = driver.page_source
                    self.parsePage(uInfo, source)
                    next_btn = driver.find_element_by_class_name('next-page')
                    next_btn.click()
                    time.sleep(1)
                driver.quit()
                return True, ''
            except:
                driver.quit()
                print("获取失败")
                return False, "ETH获取网页失败"
        else:
            print("{}文件不存在。".format(driver_path))
            return False, "{}文件不存在。".format(driver_path)


    def parsePage(self, uInfo, source):
        html = etree.HTML(source)
        tbody = html.xpath('//tbody')[0]
        trs = tbody.xpath('./tr')
        for tr in trs:
            tds = tr.xpath("./td/span/text()")
            address = tr.xpath("./td/a/text()")
            uInfo.append([tds[0],
                          address[0],
                          tds[1].split(' ETH')[0].replace(',', ''),
                          tds[2],
                          tds[3]])

    # 以太坊价格
    def getETHPrice(self, url):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/66.0.3359.117 Safari/537.36"
        }
        result = 0
        try:
            response = requests.get(url, headers=headers)
            html = etree.HTML(response.text)
            div = html.xpath("//div[@class='service-block-v3 service-block-blue']")[0]
            h4 = div.xpath("./h4[@style='margin-top:2px']")[0]
            font = h4.xpath("./font[@color='white']")[0]
            font2 = font.xpath("./font[@color='white']/text()")[0]
            result = font2.split(' @')[0].split('$')[1]
            return result
        except:
            print("获取对于以太坊价格失败")
            return result

    def getBTC(self, uInfo, url):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/66.0.3359.117 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            html = etree.HTML(response.text)
            tbody = html.xpath("//table[@class='table']")[0]
            trs = tbody.xpath('./tr')
            for i in range(1, len(trs)):
                td = trs[i].xpath("./td")
                address = td[1].xpath("./span/a/text()")[0].replace("\n", "").strip()
                value = td[2].text.replace("\n", "").replace(",", "").strip() + td[2].xpath("./span/text()")[0]
                uInfo.append([td[0].text,
                              address,
                              value,
                              td[3].text])
            return True
        except:
            print("获取BTC失败")
            return False