import sys
import json
import os
import time
import socket
import random
from datetime import datetime
from PyQt6.QtCore import QUrl, Qt, QSize, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit,
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QMessageBox, QTabWidget, QMenu, QDialog, QScrollArea,
    QHBoxLayout, QFrame, QCheckBox, QInputDialog, QPlainTextEdit,
    QProgressBar, QStatusBar
)
from PyQt6.QtGui import QAction, QIcon, QFont, QColor, QPalette
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings

DATA_FILE = "navi_data.json"

TLD_ALIASES = {
    ".fav": ".favourite", ".favourite": ".fav",
    ".wrn": ".warn", ".warn": ".wrn",
    ".ntw": ".network", ".network": ".ntw",
    ".glbl": ".global", ".global": ".glbl"
}

TNN_TLDS = [".fav", ".favourite", ".wrn", ".warn", ".ntw", ".network", ".glbl", ".global", ".cops", ".apples", ".pw-navi"]

SEARCH_ENGINES = {
    "Mainstream": {
        "Google": "https://www.google.com/search?q=",
        "Bing": "https://www.bing.com/search?q=",
        "Brave": "https://search.brave.com/search?q=",
        "DuckDuckGo": "https://duckduckgo.com/?q=",
        "Yahoo": "https://search.yahoo.com/search?p="
    },
    "Privacy & Indie": {
        "Startpage": "https://www.startpage.com/do/search?q=",
        "Qwant": "https://www.qwant.com/?q=",
        "Searx": "https://searx.be/search?q=",
        "Mojeek": "https://www.mojeek.com/search?q=",
        "Swisscows": "https://swisscows.com/en/web?query=",
        "Gigablast": "https://www.gigablast.com/search?q=",
        "Metager": "https://metager.org/meta/meta.ger3?eingabe="
    },
    "Eco & Social": {
        "Ecosia": "https://www.ecosia.org/search?q=",
        "OceanHero": "https://oceanhero.today/web?q=",
        "GiveWater": "https://www.givewater.com/?s=",
        "Ekosearch": "https://www.ekosearch.org/search?q="
    },
    "AI & Research": {
        "Perplexity": "https://perplexity.ai/search?q=",
        "Phind": "https://www.phind.com/search?q=",
        "You.com": "https://you.com/search?q=",
        "Consensus": "https://consensus.app/results/?q=",
        "Google Scholar": "https://scholar.google.com/scholar?q=",
        "Wolfram Alpha": "https://www.wolframalpha.com/input?i=",
        "Dimensions": "https://app.dimensions.ai/discover/publication?search_text="
    },
    "Global & Specialized": {
        "Wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search=",
        "Baidu": "https://www.baidu.com/s?wd=",
        "Naver": "https://search.naver.com/search.naver?query=",
        "Yandex": "https://yandex.com/search/?text=",
        "Ask": "https://www.ask.com/web?q=",
        "YouTube": "https://www.youtube.com/results?search_query=",
        "GitHub": "https://github.com/search?q={}&type=repositories",
        "Reddit": "https://www.google.com/search?q={}+site:reddit.com",
        "Wayback": "https://web.archive.org/web/*/",
        "Amazon": "https://www.amazon.com/s?k=",
        "Twitter": "https://twitter.com/search?q="
    }
}

def get_search_url(engine_name, query):
    for cat in SEARCH_ENGINES.values():
        if engine_name in cat:
            base = cat[engine_name]
            return base.format(query) if "{}" in base else base + query
    return SEARCH_ENGINES["Mainstream"]["Google"] + query

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "127.0.0.1"

class InternalPages:
    @staticmethod
    def css(theme):
        themes = {
            "dark": {"bg": "#121212", "card": "#1e1e1e", "txt": "#ffffff", "acc": "#0d6efd", "btn_hover": "#0a58ca"},
            "light": {"bg": "#f8f9fa", "card": "#ffffff", "txt": "#212529", "acc": "#0d6efd", "btn_hover": "#0a58ca"},
            "tnn": {"bg": "#050a05", "card": "#0a110a", "txt": "#00ff41", "acc": "#008f11", "btn_hover": "#00cc33"}
        }
        c = themes.get(theme, themes["dark"])
        return f"""
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: {c['bg']}; color: {c['txt']}; margin: 0; padding: 40px; line-height: 1.6; }}
        h1, h2, h3 {{ color: {c['acc']}; }}
        .header {{ text-align: center; padding-bottom: 50px; border-bottom: 1px solid {c['acc']}; margin-bottom: 40px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }}
        .card {{ background: {c['card']}; padding: 25px; border-radius: 15px; border: 1px solid {c['acc']}; transition: transform 0.3s, box-shadow 0.3s; }}
        .card:hover {{ transform: translateY(-8px); box-shadow: 0 12px 24px rgba(0,0,0,0.4); }}
        .btn {{ display: inline-block; padding: 12px 24px; background: {c['acc']}; color: white; text-decoration: none; border-radius: 8px; margin-top: 15px; font-weight: bold; border: none; cursor: pointer; transition: background 0.2s; }}
        .btn:hover {{ background: {c['btn_hover']}; }}
        .nav-bar {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }}
        .nav-link {{ color: {c['txt']}; text-decoration: none; font-weight: bold; padding: 5px 10px; border-radius: 5px; }}
        .nav-link:hover {{ background: rgba(128,128,128,0.2); }}
        .badge {{ background: {c['acc']}; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px; float: right; }}
        input, textarea {{ width: 100%; padding: 10px; background: {c['bg']}; color: {c['txt']}; border: 1px solid {c['acc']}; border-radius: 5px; margin-top: 10px; }}
        """

    @staticmethod
    def get_home(data):
        return f"""
        <html><head><style>{InternalPages.css(data['settings']['theme'])}</style></head><body>
            <div class='header'>
                <h1>NAVI ULTIMATE</h1>
                <p>Welcome back to the decentralized web. Secure, Private, and Rewarding.</p>
                <div class='nav-bar'>
                    <a href='navi://home' class='nav-link'>Home</a>
                    <a href='navi://pw' class='nav-link'>My Sites</a>
                    <a href='navi://extensions' class='nav-link'>Extensions</a>
                    <a href='navi://store' class='nav-link'>Store</a>
                    <a href='navi://settings' class='nav-link'>Settings</a>
                </div>
            </div>
            <div class='grid'>
                <div class='card'>
                    <h3>🪙 Navit Wallet</h3>
                    <p>Current Balance: <b>{data['navits']} Navits</b></p>
                    <p>You earn 1 Navit every minute you spend browsing.</p>
                    <a href='navi://store' class='btn'>Spend Navits</a>
                </div>
                <div class='card'>
                    <h3>🌐 TNN Site Manager</h3>
                    <p>You have <b>{len(data['sites'])}</b> active decentralized sites.</p>
                    <a href='navi://pw' class='btn'>Manage Sites</a>
                </div>
                <div class='card'>
                    <h3>🛡️ Security Status</h3>
                    <p>Mode: <b>{data['settings']['network_mode'].upper()}</b></p>
                    <p>IP: <b>{get_local_ip()}</b></p>
                    <a href='navi://settings' class='btn'>Change Mode</a>
                </div>
            </div>
        </body></html>
        """

class TOSDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navi Browser - Legal Terms")
        self.setFixedSize(600, 500)
        layout = QVBoxLayout()
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setHtml("""
            <h1 style='color: #dc3545;'>Legal Disclaimer</h1>
            <p><b>1. End-User Responsibility:</b> The user acknowledges that Navi Browser provides access to decentralized networks (TNN) and the Dark Web (Tor). The creator is <b>NOT</b> responsible for any content hosted, visited, or distributed via these networks.</p>
            <p><b>2. No Censorship:</b> TNN domains (.apples, .cops, .fav, etc.) are peer-to-peer. Content is stored on users' local machines. The creator has no power to remove content.</p>
            <p><b>3. Illegal Activity:</b> Any illegal activity performed while using Navi is the sole liability of the user.</p>
            <p><b>4. Data P2P:</b> Your IP address may be used to facilitate connections in TNN mode.</p>
            <hr>
            <p align='center'><i>Clicking "Accept" constitutes a binding agreement that you alone carry all legal liability.</i></p>
        """)
        layout.addWidget(self.content)
        self.btn = QPushButton("I Accept and Understand the Risks")
        self.btn.setStyleSheet("background: #28a745; color: white; padding: 15px; font-weight: bold; border-radius: 10px;")
        self.btn.clicked.connect(self.accept)
        layout.addWidget(self.btn)
        self.setLayout(layout)

class CodeEditor(QWidget):
    def __init__(self, main, mode="site", key=None):
        super().__init__()
        self.main, self.mode, self.key = main, mode, key
        self.setWindowTitle(f"Navi {mode.title()} Editor")
        self.resize(1000, 750)
        layout = QVBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter name/domain (e.g. awesome-site)")
        self.code_input = QPlainTextEdit()
        self.code_input.setPlaceholderText("Paste HTML, CSS, and JS here...")
        
        if key:
            self.title_input.setText(key)
            self.title_input.setReadOnly(True)
            src = main.data['sites' if mode=="site" else 'extensions'].get(key, {})
            self.code_input.setPlainText(src.get('html_content', src.get('code', '')))

        self.save_btn = QPushButton("🚀 Save & Deploy to Network")
        self.save_btn.setStyleSheet("background: #0d6efd; color: white; padding: 15px; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_data_logic)
        
        layout.addWidget(QLabel("<b>Identity/Domain:</b>"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("<b>Source Code:</b>"))
        layout.addWidget(self.code_input)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    def save_data_logic(self):
        name = self.title_input.text().strip()
        code = self.code_input.toPlainText()
        if not name or not code: return
        if self.mode == "site":
            if not any(name.endswith(tld) for tld in TNN_TLDS): name += ".pw-navi"
            self.main.data['sites'][name] = {"html_content": code, "public": True, "created": str(datetime.now())}
        else:
            self.main.data['extensions'][name] = {"code": code, "active": True}
        self.main.save_data()
        QMessageBox.information(self, "Success", f"{self.mode.title()} saved successfully!")
        self.close()

class NaviWebPage(QWebEnginePage):
    def __init__(self, view):
        super().__init__(view)
        self.view = view
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() in ["navi", "app"]:
            self.view.main.handle_cmd(url.toString(), self.view)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class NaviBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navi Browser Ultimate Elite")
        self.resize(1400, 900)
        
        self.data = {
            'sites': {}, 'extensions': {}, 'navits': 50, 'tos_agreed': False,
            'tnn_registry': {}, 'last_reward': 0, 'bookmarks': [],
            'settings': {
                'theme': 'dark', 'engine': 'Google', 'network_mode': 'cleanweb',
                'tor_port': 9050, 'user_agent': 'NaviBot/11.0'
            }
        }
        self.load_data()
        
        if not self.data.get('tos_agreed'):
            if TOSDialog().exec():
                self.data['tos_agreed'] = True
                self.save_data()
            else: sys.exit()

        self.setup_ui()
        self.apply_network_settings()
        self.add_tab(QUrl("navi://home"))

    def setup_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        self.tb = QToolBar("Navigation")
        self.tb.setIconSize(QSize(18, 18))
        self.addToolBar(self.tb)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate)
        
        back_btn = QAction("←", self); back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        next_btn = QAction("→", self); next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        reload_btn = QAction("↻", self); reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        home_btn = QAction("🏠", self); home_btn.triggered.connect(lambda: self.handle_cmd("navi://home", self.tabs.currentWidget()))
        new_tab_btn = QAction("+", self); new_tab_btn.triggered.connect(lambda: self.add_tab(QUrl("navi://home")))
        
        self.tb.addAction(back_btn); self.tb.addAction(next_btn); self.tb.addAction(reload_btn); self.tb.addAction(home_btn)
        self.tb.addWidget(self.url_bar)
        self.tb.addAction(new_tab_btn)
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.update_styles()

    def update_styles(self):
        self.setStyleSheet(BrowserStyles.get(self.data['settings']['theme']))

    def add_tab(self, url):
        view = QWebEngineView()
        view.main = self
        view.setPage(NaviWebPage(view))
        view.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if view == self.tabs.currentWidget() else None)
        view.loadStarted.connect(lambda: self.status.showMessage("Loading..."))
        view.loadFinished.connect(lambda: self.on_load_finish(view))
        idx = self.tabs.addTab(view, "New Tab")
        self.tabs.setCurrentIndex(idx)
        view.setUrl(url if isinstance(url, QUrl) else QUrl(url))
        return view

    def close_tab(self, i):
        if self.tabs.count() > 1: self.tabs.removeTab(i)

    def on_load_finish(self, view):
        self.status.showMessage("Ready", 3000)
        self.tabs.setTabText(self.tabs.indexOf(view), view.page().title()[:15])
        # Inject Extensions
        for ext in self.data['extensions'].values():
            if ext.get('active'): view.page().runJavaScript(ext['code'])
        # Rewards
        if time.time() - self.data['last_reward'] > 60:
            self.data['navits'] += 1
            self.data['last_reward'] = time.time()
            self.save_data()

    def navigate(self):
        text = self.url_bar.text().strip()
        view = self.tabs.currentWidget()
        if not text: return
        if text.startswith("navi://") or text.startswith("app://"):
            self.handle_cmd(text, view); return
        
        # TNN Routing
        found_tld = next((tld for tld in TNN_TLDS if text.endswith(tld)), None)
        if found_tld:
            target = text
            if found_tld in TLD_ALIASES:
                alt = text.replace(found_tld, TLD_ALIASES[found_tld])
                if alt in self.data['sites']: target = alt
            if target in self.data['sites']:
                view.setHtml(self.data['sites'][target]['html_content'])
                return
        
        if "." not in text or " " in text:
            url = get_search_url(self.data['settings']['engine'], text)
        else:
            url = text if "://" in text else "https://" + text
        view.setUrl(QUrl(url))

    def handle_cmd(self, url_str, view):
        cmd = url_str.replace("navi://", "").replace("app://", "").strip("/")
        theme = self.data['settings']['theme']
        
        if cmd in ["home", ""]:
            view.setHtml(InternalPages.get_home(self.data))
        
        elif cmd == "pw":
            cards = "".join([f"<div class='card'><span class='badge'>TNN</span><h3>{k}</h3><p>Online & Decentralized</p><a href='navi://pw/edit/{k}' class='btn'>Edit Source</a></div>" for k in self.data['sites']])
            view.setHtml(f"<html><head><style>{InternalPages.css(theme)}</style></head><body><h1>Site Manager</h1><a href='navi://pw/new' class='btn'>+ Create New TNN Site</a><div class='grid' style='margin-top:20px;'>{cards}</div></body></html>")
            
        elif cmd == "pw/new": 
            self.editor = CodeEditor(self, "site")
            self.editor.show()
            
        elif cmd.startswith("pw/edit/"):
            target = cmd.split("/")[-1]
            self.editor = CodeEditor(self, "site", target)
            self.editor.show()

        elif cmd == "extensions":
            ext_list = "".join([f"<div class='card'><h3>{k}</h3><p>Status: {'Active' if v['active'] else 'Inactive'}</p><a href='navi://ext/toggle/{k}' class='btn'>Toggle</a></div>" for k, v in self.data['extensions'].items()])
            view.setHtml(f"<html><head><style>{InternalPages.css(theme)}</style></head><body><h1>Extension Lab</h1><a href='navi://ext/new' class='btn'>+ New Extension</a><div class='grid'>{ext_list}</div></body></html>")

        elif cmd == "ext/new":
            self.editor = CodeEditor(self, "extension")
            self.editor.show()

        elif cmd == "store":
            items = "".join([f"<div class='card'><h3>{tld}</h3><p>Cost: 30 Navits</p><p>Secure decentralized TLD.</p><a href='navi://buy/{tld}' class='btn'>Register</a></div>" for tld in TNN_TLDS if tld != ".pw-navi"])
            view.setHtml(f"<html><head><style>{InternalPages.css(theme)}</style></head><body><h1>Domain Registry</h1><div class='grid'>{items}</div></body></html>")

        elif cmd.startswith("buy/"):
            tld = "." + cmd.split("/")[-1].strip(".")
            if self.data['navits'] >= 30:
                name, ok = QInputDialog.getText(self, "Register Domain", f"Choose your {tld} domain name:")
                if ok and name:
                    self.data['navits'] -= 30
                    full = name + tld
                    self.data['sites'][full] = {"html_content": f"<h1>Welcome to {full}</h1>", "public": True}
                    self.save_data()
                    self.handle_cmd("navi://home", view)
            else:
                QMessageBox.warning(self, "Insufficient Funds", "You need 30 Navits to buy a TNN domain!")

        elif cmd == "settings":
            engines = "".join([f"<option {'selected' if self.data['settings']['engine']==e else ''}>{e}</option>" for cat in SEARCH_ENGINES.values() for e in cat])
            view.setHtml(f"<html><head><style>{InternalPages.css(theme)}</style></head><body><h1>Global Settings</h1><div class='card'><h3>Search Engine</h3><select id='engine' onchange='window.location.href=\"navi://set/engine/\" + this.value'>{engines}</select></div><div class='card'><h3>Theme</h3><a href='navi://set/theme/dark' class='btn'>Dark</a> <a href='navi://set/theme/light' class='btn'>Light</a> <a href='navi://set/theme/tnn' class='btn'>TNN Neon</a></div></body></html>")

        elif cmd.startswith("set/theme/"):
            self.data['settings']['theme'] = cmd.split("/")[-1]
            self.update_styles(); self.save_data(); self.handle_cmd("navi://settings", view)

    def apply_network_settings(self):
        if self.data['settings']['network_mode'] == "tnn":
            ip = get_local_ip()
            for d, info in self.data['sites'].items():
                if info.get('public'):
                    if d not in self.data['tnn_registry']: self.data['tnn_registry'][d] = []
                    if ip not in self.data['tnn_registry'][d]: self.data['tnn_registry'][d].append(ip)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f: self.data.update(json.load(f))
            except: pass

    def save_data(self):
        with open(DATA_FILE, 'w') as f: json.dump(self.data, f)

class BrowserStyles:
    @staticmethod
    def get(theme):
        themes = {
            "dark": {"bg": "#121212", "fg": "#ffffff", "acc": "#0d6efd", "bar": "#1e1e1e", "tab": "#2b2b2b"},
            "light": {"bg": "#f8f9fa", "fg": "#212529", "acc": "#0d6efd", "bar": "#ffffff", "tab": "#e9ecef"},
            "tnn": {"bg": "#050a05", "fg": "#00ff41", "acc": "#008f11", "bar": "#0a110a", "tab": "#0d1a0d"}
        }
        c = themes.get(theme, themes["dark"])
        return f"""
        QMainWindow {{ background-color: {c['bg']}; }}
        QToolBar {{ background: {c['bar']}; border-bottom: 2px solid {c['acc']}; padding: 10px; spacing: 15px; }}
        QLineEdit {{ background: {c['bg']}; color: {c['fg']}; border: 1px solid {c['acc']}; border-radius: 18px; padding: 8px 18px; font-size: 14px; }}
        QTabWidget::pane {{ border: none; }}
        QTabBar::tab {{ background: {c['tab']}; color: {c['fg']}; padding: 12px 25px; border-top-left-radius: 12px; border-top-right-radius: 12px; margin-right: 3px; font-weight: bold; }}
        QTabBar::tab:selected {{ background: {c['acc']}; color: white; }}
        QStatusBar {{ background: {c['bar']}; color: {c['fg']}; font-size: 12px; }}
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NaviBrowser()
    window.show()
    sys.exit(app.exec())

