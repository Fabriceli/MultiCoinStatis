# -*- coding: utf-8 -*-
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from utils.getWebInfo import *
from utils.getTime import *
from utils.readWriteExcel import *
import os.path

sec = 0

erc20 = {'cs': '0x46b9ad944d1059450da1163511069c718f699d31',
         'jnt': '0xa5fd1a791c4dfcaacc963d4f73c6ae5824149ea7',
         'gnx': '0x6ec8a24cabdc339a06a172f8223ea557055adaa5',
         'eos': '0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0',
         'eth': 'eth', 'btc': 'btc'}
coins = []


class WorkThread(QThread):
    trigger = pyqtSignal()
    triggerText = pyqtSignal(bool, bool, str)  # 错误标志，清空消息标志，信息

    def __init__(self):
        super(WorkThread, self).__init__()

    def run(self):
        for coin in coins:
            upateExcel(coin)
        self.trigger.emit()


def countCoins(fileName, error):
    if error:
        workThread.triggerText.emit(False, False, "{}文件读写完成".format(fileName))
    else:
        workThread.triggerText.emit(False, False, "{}文件读写失败，请关闭该文件，再开始".format(fileName))


def countTime():
    global sec
    sec += 1
    lcdNumber.display(sec)

def setText(error, clear, msg):
    if clear:
        text.clearHistory()
        text.clear()
    if error:
        text.setTextColor(QColor('red'))
    else:
        text.setTextColor(QColor('black'))
    text.append(msg)


def work():
    workThread.triggerText.emit(False, True, "开始抓取数据。。。")
    button.setEnabled(False)
    timer.start(1000)
    workThread.start()
    workThread.trigger.connect(timeStop)
    excel.trigger.connect(countCoins)


def timeStop():
    if len(coins) == 0:
        workThread.triggerText.emit(True, True, "请选择统计的币种。")
    else:
        workThread.triggerText.emit(True, False, "运行结束用时：{}s".format(lcdNumber.value()))
    timer.stop()
    global sec
    sec = 0
    button.setEnabled(True)


def upateExcel(coinsName):
    filename = coinsName + "投资情况"
    sheetdefault = "每日情况"
    sheetdiff = "持仓变化情况"
    firstdiff = ['地址', '持币数', '变化值']
    nowTime = GetTime()
    t = nowTime.getNowTime()
    d = nowTime.getNowDate()
    y = nowTime.getYesterday()

    if coinsName is 'eth':
        doETH(filename, sheetdefault, coinsName, d, t, sheetdiff, firstdiff, y)
    elif coinsName is 'btc':
        doBTC(filename, sheetdefault, coinsName, d, t, sheetdiff, firstdiff, y)
    else:
        doOthers(filename, sheetdefault, coinsName, d, t, sheetdiff, firstdiff, y)

def doETH(filename, sheetdefault, coinsName, d, t, sheetNameDiff, firstdiff, yesterday):
    uEthInfo = []
    uEthToken = []
    firstListEth = ['日期', '统计时间', '5万个以上持有者', '10万个以上持有者', '20万个以上持有者', '50万个以上持有者', '',
                    'top500', 'top250', 'top100', 'top50', 'top25', 'top10', 'top5', 'Price(USD)', 'top6-10',
                    'top11-25', 'top26-50', 'top51-100', 'top101-250', 'top251-500']
    firstListTEth = ['序号', '地址', 'Token数', '百分比', '交易笔数']
    url = 'https://www.yitaifang.com/accounts/'
    urlPrice = 'https://etherscan.io/'
    driver_path = 'chromedriver.exe'
    if os.path.isfile(driver_path):
        webInfo = WebInfo(url)
        success, msg = webInfo.getETH(driver_path, uEthInfo, url)
        if success:
            top500 = webInfo.getTopPercent(uEthInfo, 500)
            top250 = webInfo.getTopPercent(uEthInfo, 250)
            top100 = webInfo.getTopPercent(uEthInfo, 100)
            top50 = webInfo.getTopPercent(uEthInfo, 50)
            top25 = webInfo.getTopPercent(uEthInfo, 25)
            top10 = webInfo.getTopPercent(uEthInfo, 10)
            top5 = webInfo.getTopPercent(uEthInfo, 5)
            uEthToken.append(d)
            uEthToken.append(t)
            uEthToken.append(webInfo.getList(uEthInfo, 5))
            uEthToken.append(webInfo.getList(uEthInfo, 10))
            uEthToken.append(webInfo.getList(uEthInfo, 20))
            uEthToken.append(webInfo.getList(uEthInfo, 50))
            uEthToken.append('')
            uEthToken.append(round(top500, 2))
            uEthToken.append(round(top250, 2))
            uEthToken.append(round(top100, 2))
            uEthToken.append(round(top50, 2))
            uEthToken.append(round(top25, 2))
            uEthToken.append(round(top10, 2))
            uEthToken.append(round(top5, 2))
            uEthToken.append(webInfo.getETHPrice(urlPrice))
            uEthToken.append(round(top10 - top5, 2))
            uEthToken.append(round(top25 - top10, 2))
            uEthToken.append(round(top50 - top25, 2))
            uEthToken.append(round(top100 - top50, 2))
            uEthToken.append(round(top250 - top100, 2))
            uEthToken.append(round(top500 - top250, 2))
            excel.writeExcel(filename, uEthInfo, uEthToken, firstListEth, firstListTEth, sheetdefault, d, len(uEthInfo),
                             sheetNameDiff, firstdiff, yesterday)
        else:
            workThread.triggerText.emit(True, True, "{}抓取网络数据失败，请检查网络连接。".format(coinsName))
    else:
        workThread.triggerText.emit(True, True, "chromedriver.exe驱动文件不存在。")




def doBTC(filename, sheetdefault, coinsName, d, t,sheetNameDiff, firstdiff, yesterday):
    uBTCInfo = []
    uBTCToken = []
    firstListBTC = ['日期', '统计时间', '5万个以上持有者', '10万个以上持有者', '20万个以上持有者', '50万个以上持有者', '', 'Price(USD)']
    firstListTBTC = ['序号', '地址', 'Token数', '交易笔数']
    url = 'https://btc.com/stats/rich-list'
    urlPrice = 'https://etherscan.io/'
    webInfo = WebInfo(url)
    if webInfo.getBTC(uBTCInfo, url):
        uBTCToken.append(d)
        uBTCToken.append(t)
        uBTCToken.append(webInfo.getList(uBTCInfo, 5))
        uBTCToken.append(webInfo.getList(uBTCInfo, 10))
        uBTCToken.append(webInfo.getList(uBTCInfo, 20))
        uBTCToken.append(webInfo.getList(uBTCInfo, 50))
        uBTCToken.append('')
        uBTCToken.append('')
        excel.writeExcel(filename, uBTCInfo, uBTCToken, firstListBTC, firstListTBTC, sheetdefault, d, len(uBTCInfo), sheetNameDiff, firstdiff, yesterday)
    else:
        workThread.triggerText.emit(True, False, "{}抓取网络数据失败，请检查网络连接。".format(coinsName))


def doOthers(filename, sheetdefault, coinsName, d, t, sheetNameDiff, firstdiff, yesterday):
    range = 500  # 最大是500

    uInfo = []
    uToken = []
    firstList = ['日期', '统计时间', '5万个以上持有者', '10万个以上持有者', '20万个以上持有者', '50万个以上持有者', '持币地址数',
                 'top500', 'top250', 'top100', 'top50', 'top25', 'top10', 'top5', 'Price(ETH)', 'top6-10', 'top11-25',
                 'top26-50', 'top51-100', 'top101-250', 'top251-500']
    firstListT = ['序号', '地址', 'Token数', '百分比']
    if range > 500 or range < 0:
        range = 500
    url = 'https://etherscan.io/token/tokenholderchart/' + erc20[coinsName] + '?range=' + str(range)
    urlPrice = 'https://etherscan.io/token/' + erc20[coinsName]
    webInfo = WebInfo(url)
    html = webInfo.getHTMLText()
    if webInfo.fillUnivList(uInfo, html):
        top500 = webInfo.getTopPercent(uInfo, 500)
        top250 = webInfo.getTopPercent(uInfo, 250)
        top100 = webInfo.getTopPercent(uInfo, 100)
        top50 = webInfo.getTopPercent(uInfo, 50)
        top25 = webInfo.getTopPercent(uInfo, 25)
        top10 = webInfo.getTopPercent(uInfo, 10)
        top5 = webInfo.getTopPercent(uInfo, 5)
        uToken.append(d)
        uToken.append(t)
        uToken.append(webInfo.getList(uInfo, 5))
        uToken.append(webInfo.getList(uInfo, 10))
        uToken.append(webInfo.getList(uInfo, 20))
        uToken.append(webInfo.getList(uInfo, 50))
        uToken.append(webInfo.getAdressNumber(html))
        uToken.append(round(top500, 2))
        uToken.append(round(top250, 2))
        uToken.append(round(top100, 2))
        uToken.append(round(top50, 2))
        uToken.append(round(top25, 2))
        uToken.append(round(top10, 2))
        uToken.append(round(top5, 2))
        uToken.append(webInfo.getPricetoETH(urlPrice))
        uToken.append(round(top10 - top5, 2))
        uToken.append(round(top25 - top10, 2))
        uToken.append(round(top50 - top25, 2))
        uToken.append(round(top100 - top50, 2))
        uToken.append(round(top250 - top100, 2))
        uToken.append(round(top500 - top250, 2))
        excel.writeExcel(filename, uInfo, uToken, firstList, firstListT, sheetdefault, d, range, sheetNameDiff, firstdiff, yesterday)
    else:
        workThread.triggerText.emit(True, False, "{}抓取网络数据失败，请检查网络连接。".format(coinsName))


def addcs(state):
    if state == Qt.Checked:
        coins.append('cs')
    else:
        coins.remove('cs')


def addjnt(state):
    if state == Qt.Checked:
        coins.append('jnt')
    else:
        coins.remove('jnt')


def addgnx(state):
    if state == Qt.Checked:
        coins.append('gnx')
    else:
        coins.remove('gnx')


def addeos(state):
    if state == Qt.Checked:
        coins.append('eos')
    else:
        coins.remove('eos')

def addeth(state):
    if state == Qt.Checked:
        coins.append('eth')
    else:
        coins.remove('eth')

def addbtc(state):
    if state == Qt.Checked:
        coins.append('btc')
    else:
        coins.remove('btc')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName('区块链统计')
    app.setWindowIcon(QIcon('blockchain.ico'))
    top = QWidget()
    top.resize(600, 300)
    top.setWindowTitle('统计小工具')
    top.setWindowIcon(QIcon('blockchain.ico'))
    layout = QVBoxLayout(top)

    lbl1 = QLabel('选择统计的币：')

    cs = QCheckBox('CS')
    cs.stateChanged.connect(addcs)

    jnt = QCheckBox('JNT')
    jnt.stateChanged.connect(addjnt)

    gnx = QCheckBox('GNX')
    gnx.stateChanged.connect(addgnx)

    eos = QCheckBox('EOS')
    eos.stateChanged.connect(addeos)

    eth = QCheckBox('ETH')
    eth.stateChanged.connect(addeth)

    btc = QCheckBox('BTC')
    btc.stateChanged.connect(addbtc)

    # 币种布局
    hbox1 = QHBoxLayout()
    hbox1.addWidget(lbl1)
    hbox1.addStretch()
    hbox1.addWidget(cs)
    hbox1.addStretch()
    hbox1.addWidget(jnt)
    hbox1.addStretch()
    hbox1.addWidget(gnx)
    hbox1.addStretch()
    hbox1.addWidget(eos)
    hbox1.addStretch()
    hbox1.addWidget(eth)
    hbox1.addStretch()
    hbox1.addWidget(btc)

    # 显示进度布局
    hboxDetail = QHBoxLayout()
    text = QTextBrowser()
    lcdNumber = QLCDNumber()
    lcdNumber.setSegmentStyle(QLCDNumber.Flat)
    hboxDetail.addWidget(lcdNumber)
    hboxDetail.addWidget(text)

    button = QPushButton("开始")
    hbox = QHBoxLayout()
    hbox.addWidget(button)

    layout.addLayout(hbox1)
    layout.addLayout(hbox)
    layout.addLayout(hboxDetail)

    timer = QTimer()
    workThread = WorkThread()
    excel = ReadWriteExcel()
    button.clicked.connect(work)
    timer.timeout.connect(countTime)
    workThread.triggerText.connect(setText)

    top.show()
    sys.exit(app.exec_())
