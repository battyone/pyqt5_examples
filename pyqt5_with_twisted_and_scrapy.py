from PyQt5.QtWidgets import QApplication, QDialog, QTabWidget, QWidget, QGroupBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import sys
app = QApplication(sys.argv)

import qt5reactor
qt5reactor.install()

from twisted.internet import defer, reactor
from twisted.python import log
log.startLogging(sys.stdout)

from scrapy.crawler import CrawlerRunner
from scrapy import Spider
from waitingspinnerwidget import QtWaitingSpinner

def run_later(seconds, function, *args, **kwargs):
    d = defer.Deferred()

    def fire():
        value = function(*args, **kwargs)
        d.callback(value)

    reactor.callLater(seconds, fire)
    return d      
    
class CustomSpider(Spider):
    name = 'quotes_spider'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        quotes = response.xpath("//div[@class='quote']//span[@class='text']/text()").extract()
        yield {'quotes': quotes}

        
class DownloadDataDialog(QDialog):
    def __init__(self, reactor, parent=None):
        super(DownloadDataDialog, self).__init__(parent)
        
        self.reactor = reactor
        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)

        tabWidget = QTabWidget(self)
        tabWidget.addTab(MyTab(tabWidget), "MyTab")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        self.setLayout(mainLayout)

        self.setWindowTitle("Download option chain data from web")
        
    def closeEvent(self, e):
        self.reactor.stop()
        e.accept()

class MyTab(QWidget):
    def __init__(self, parent=None):
        super(MyTab, self).__init__(parent)
        
        dataGroup = QGroupBox('Data')
        
        getButton = QPushButton('Download')
        getButton.clicked.connect(self.download_data)

        dataLayout = QVBoxLayout()
        dataLayout.addWidget(getButton)
        dataGroup.setLayout(dataLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(dataGroup)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        
    def download_data(self):
        self.parentWidget().window().spinner.start()
        d = run_later(0, self.run_spider)
        d.addCallback(self.FinishedDownload)
        
    def run_spider(self):
        print('run')
        crawler = CrawlerRunner({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'FEED_FORMAT': 'json',
            'FEED_URI': 'output.json',
            'DOWNLOAD_DELAY': 3,
            'LOG_STDOUT': True,
            'LOG_FILE': 'scrapy_output.txt',
            'ROBOTSTXT_OBEY': False,
            'RETRY_ENABLED': True,
            'RETRY_HTTP_CODES': [500, 503, 504, 400, 404, 408],
            'RETRY_TIMES': 5
        })
        
        # instantiate a spider
        spider = CustomSpider()
        d = crawler.crawl(spider)

    def FinishedDownload(self, results, *args, **kwargs):
        self.parentWidget().window().spinner.stop()

if __name__ == '__main__':
   
    tabdialog = DownloadDataDialog(reactor)
    tabdialog.show()
    reactor.run()