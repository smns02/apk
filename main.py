from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
import asyncio
import aiohttp
import threading
import os
import re
import base64
from urllib.parse import urlparse, parse_qs, urljoin

# --- Ruijie Manager Class ---
class RuijieLoginManager:
    def __init__(self):
        self.ip = None
        self.mac = None
        self.current_sid = None
        self.phone_number = "12345678901"

    async def auto_detect_gateway(self, session):
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            async with session.get(test_url, headers=headers, timeout=5, allow_redirects=False) as resp:
                if resp.status in (301, 302):
                    loc = resp.headers.get('Location', '')
                    params = parse_qs(urlparse(loc).query)
                    self.ip = params.get('gw_address', [None])[0]
                    self.mac = params.get('mac', [None])[0]
                    return True
        except: return False
        return False

    async def _fetch_sid(self, session):
        if not self.ip or not self.mac: return None
        step1_url = f"https://portal-as.ruijienetworks.com/auth/wifidogAuth/login/?gw_id=c4b25b2c5e82&gw_sn=H1TB2WU006124&gw_address=192.168.110.1&gw_port=2060&ip={self.ip}&mac={self.mac}&url=http%3A%2F%2F192.168.0.1%2F"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            async with session.get(step1_url, headers=headers, timeout=10) as r1:
                js_match = re.search(r"self\.location\.href\s*=\s*['\"]([^'\"]+)['\"]", await r1.text())
                if js_match:
                    async with session.get(urljoin("https://portal-as.ruijienetworks.com", js_match.group(1)), headers=headers, allow_redirects=False) as r2:
                        sid = parse_qs(urlparse(r2.headers.get('Location', '')).query).get('sessionId')
                        if sid: self.current_sid = sid[0]; return self.current_sid
        except: return None

    async def login_voucher(self, session, voucher):
        if not self.current_sid: await self._fetch_sid(session)
        if not self.current_sid: return False
        data = {"accessCode": voucher, "sessionId": self.current_sid, "apiVersion": 1}
        post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
        async with session.post(post_url, json=data) as req:
            return 'logonUrl' in await req.text()

    async def send_request(self, session):
        params = {'token': self.current_sid, 'phoneNumber': self.phone_number}
        try:
            async with session.post(f'http://{self.ip}:2060/wifidog/auth', params=params, timeout=10) as resp:
                return resp.status == 200
        except: return False

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 50
    spacing: 20
    Label:
        text: "S P A C E - X"
        font_size: '30sp'
    TextInput:
        id: token_input
        hint_text: 'Enter Voucher Code'
        multiline: False
    Button:
        text: 'CONNECT'
        on_release: app.run_bypass(token_input.text)
    Label:
        id: status_label
        text: "> Status : Waiting"
'''

class SpaceXApp(App):
    def build(self):
        return Builder.load_string(KV)
    def run_bypass(self, voucher):
        self.root.ids.status_label.text = "> Status : Processing..."
        threading.Thread(target=lambda: asyncio.run(self.execute(voucher))).start()
    async def execute(self, voucher):
        async with aiohttp.ClientSession() as session:
            mgr = RuijieLoginManager()
            await mgr.auto_detect_gateway(session)
            if await mgr.login_voucher(session, voucher) and await mgr.send_request(session):
                Clock.schedule_once(lambda dt: setattr(self.root.ids.status_label, 'text', "> Success"))
            else:
                Clock.schedule_once(lambda dt: setattr(self.root.ids.status_label, 'text', "> Failed"))

if __name__ == '__main__':
    SpaceXApp().run()
