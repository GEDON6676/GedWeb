import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebEngineCore import *
import subprocess


homepage = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/mainpage/index.html"

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        print(os.path.join(os.path.dirname(os.path.realpath(__file__)), "homepage\index.html"))

        # Create the QTabWidget and add it to the central widget area
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.setWindowTitle("GedWeb")
        self.setWindowIcon(QIcon("GedWeb.ico"))
        settings = QSettings('Gedon76', 'GedWeb')
        size = settings.value('Browser/Size', QSize(800, 600))
        state = settings.value('Browser/State', None)
        if state is not None:
            self.restoreState(state)
        self.resize(size)

        # Create a new tab for the default homepage
        self.add_tab(homepage)

        self.navtb = QToolBar()
        self.addToolBar(self.navtb)

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        back_btn = QAction('↶', self)
        back_btn.triggered.connect(self.current_browser().back)
        self.navtb.addAction(back_btn)

        forward_btn = QAction('↷', self)
        forward_btn.triggered.connect(self.current_browser().forward)
        self.navtb.addAction(forward_btn)

        reload_btn = QAction('↻', self)
        reload_btn.triggered.connect(self.current_browser().reload)
        self.navtb.addAction(reload_btn)

        home_btn = QAction('⌂', self)
        home_btn.triggered.connect(self.go_to_homepage)
        self.navtb.addAction(home_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.navtb.addWidget(self.urlbar)
        daurlbar = self.urlbar

        history_btn = QAction('History', self)
        history_btn.triggered.connect(self.show_history_menu)
        self.navtb.addAction(history_btn)

        addtab_btn = QToolButton()
        addtab_btn.setText('+')
        addtab_btn.clicked.connect(lambda: self.add_tab(homepage))
        self.tabs.setCornerWidget(addtab_btn, Qt.TopRightCorner)

        self.history_menu = QMenu(self)

        self.show()

        self.tabs.currentChanged.connect(self.update_urlbar)
        self.current_browser().loadFinished.connect(self.update_title)
        self.current_browser().loadFinished.connect(self.update_urlbar)

    def add_tab(self, url):
    # Create a new QWebEngineView and add it as a tab
        browser = QWebEngineView()

        # Create an instance of GedWebUrlRequestInterceptor and add it to the page object

        browser.setUrl(QUrl(url))
        browser.setWindowTitle(browser.page().title())

        index = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentWidget(browser)

        # Connect titleChanged signal to update_tab_title function
        browser.page().titleChanged.connect(lambda title: self.update_tab_title(index, title))

        # Create a close button for the tab
        close_btn = QToolButton()
        close_btn.setText('x')
        close_btn.clicked.connect(lambda: self.close_tab(index))
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, close_btn)
        self.update_title()


    def close_tab(self, index):
        # Close the tab at the given index
        widget = self.tabs.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.tabs.removeTab(index)  
        self.update_title()

    def update_tab_title(self, index, title):
        # Update tab title
        self.tabs.setTabText(index, title)

    def current_browser(self):
        # Get the QWebEngineView for the current tab
        return self.tabs.currentWidget()
    
    def go_to_homepage(self):
        url = QUrl(homepage)
        self.current_browser().setUrl(url)

    def update_title(self):
        title = self.current_browser().page().title()
        self.setWindowTitle('% s (GedWeb)' % title)
        icon_url = self.current_browser().page().iconUrl().toString()

        # Установите значок окна, используя полученный URL
        self.setWindowIcon(QIcon(icon_url))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if self.is_url_reachable(self.urlbar.text()):
            q = QUrl('http://' + self.urlbar.text())
        else:
            q = QUrl('http://duckduckgo.com/?q=% s' % self.urlbar.text().replace(' ', '+'))
        self.current_browser().setUrl(q)

    def update_urlbar(self):
        self.urlbar.setText(self.current_browser().url().toString())
        self.urlbar.setCursorPosition(0)
    def is_url_reachable(self, url):
        # Проверяем, доступен ли URL-адрес
        command = ['ping', '/n', '1', url]
        return subprocess.call(command) == 0


    def closeEvent(self, event):
        # Save the current size and state of the main window in QSettings
        settings = QSettings('Gedon76', 'GedWeb')
        settings.setValue('Browser/Size', self.size())
        settings.setValue('Browser/State', self.saveState())
        super(MainWindow, self).closeEvent(event)
        
    def show_history_menu(self):
        # Clear the history menu and add the session history
        self.history_menu.clear()
        history = self.current_browser().history()
        for i in range(history.count()):
            url = history.itemAt(i).url()
            action = QAction(url.toString(), self)
            action.triggered.connect(lambda checked, url=url: self.current_browser().setUrl(url))
            self.history_menu.addAction(action)

        # Show the history menu under the history button
        pos = self.mapToGlobal(self.navtb.pos()) + QPoint(0, self.navtb.height()) + QPoint(self.navtb.width(), 0)
        self.history_menu.popup(pos)


app = QApplication(['', '--no-sandbox'])
app.setStyle("Fusion")
dark_palette = QPalette()
dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
dark_palette.setColor(QPalette.WindowText, Qt.white)
dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
dark_palette.setColor(QPalette.ToolTipText, Qt.white)
dark_palette.setColor(QPalette.Text, Qt.white)
dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ButtonText, Qt.white)
dark_palette.setColor(QPalette.BrightText, Qt.red)
dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
dark_palette.setColor(QPalette.HighlightedText, Qt.black)
app.setPalette(dark_palette)
window = MainWindow()
window.show()  # отображаем окно
window.update_title()  # вызываем метод после отображения окна
sys.exit(app.exec_())
