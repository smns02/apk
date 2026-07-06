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

# --- Ruijie Login Manager Class ---
class RuijieLoginManager:
    def __init__(self):
        self.ip = None
        self.mac = None
        self.current_sid = None
        self.phone_number = "12345678901"
        self._load_saved_data()

    def _load_saved_data(self):
        if os.path.exists(".ip"):
            try:
                with open(".ip", "r") as f: self.ip = f.read().strip()
            except: self.ip = None
        if os.path.exists(".mac"):
            try:
                with open(".mac", "r") as f: self.mac = f.read().strip()
            except: self.mac = None

    async def auto_detect_gateway(self, session):
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile'}
        try:
            async with session.get(test_url, headers=headers, timeout=5, allow_redirects=False) as resp:
                if resp.status in (301, 302):
                    loc = resp.headers.get('Location', '')
                    params = parse_qs(urlparse(loc).query)
                    if 'gw_address' in params:
                        self.ip = params['gw_address'][0]
                        with open(".ip", "w") as f: f.write(self.ip)
                    if 'mac' in params:
                        self.mac = params['mac'][0]
                        with open(".mac", "w") as f: f.write(self.mac)
                    return True
        except: return False
        return self.ip is not None

    async def _fetch_sid(self, session):
        if not self.ip or not self.mac: return None
        step1_url = f"https://portal-as.ruijienetworks.com/auth/wifidogAuth/login/?gw_id=c4b25b2c5e82&gw_sn=H1TB2WU006124&gw_address=192.168.110.1&gw_port=2060&ip={self.ip}&mac={self.mac}&slot_num=13&nasip=192.168.1.53&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C326&chap_challenge=%5C063%5C011%5C062%5C043%5C241%5C141%5C312%5C157%5C301%5C271%5C336%5C103%5C074%5C000%5C157%5C317"
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14; 22101316C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.120 Mobile'}
        try:
            async with session.get(step1_url, headers=headers, timeout=10) as r1:
                js_match = re.search(r"self\.location\.href\s*=\s*['\"]([^'\"]+)['\"]", await r1.text())
                if not js_match: return None
                async with session.get(urljoin("https://portal-as.ruijienetworks.com", js_match.group(1)), headers=headers, allow_redirects=False) as r2:
                    sid = parse_qs(urlparse(r2.headers.get('Location', '')).query).get('sessionId')
                    if sid: self.current_sid = sid[0]; return self.current_sid
        except: return None

    async def login_voucher(self, session, voucher):
        if not self.current_sid: await self._fetch_sid(session)
        if not self.current_sid: return False
        data = {"accessCode": voucher, "sessionId": self.current_sid, "apiVersion": 1}
        post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
        headers = {
            "content-type": "application/json",
            "referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?sessionId={self.current_sid}",
            "user-agent": 'Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
        }
        async with session.post(post_url, json=data, headers=headers) as req:
            return 'logonUrl' in await req.text()

    async def send_request(self, session):
        params = {'token': self.current_sid, 'phoneNumber': self.phone_number}
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'}
        try:
            async with session.post(f'http://{self.ip}:2060/wifidog/auth', params=params, headers=headers, timeout=10) as resp:
                return resp.status == 200
        except: return False

# --- UI Setup ---
KV = '''
AnchorLayout:
    anchor_x: 'center'
    anchor_y: 'top'
    padding: [50, 80, 50, 50]
    BoxLayout:
        orientation: 'vertical'
        size_hint: (0.9, None)
        height: self.minimum_height
        spacing: 200
        
        Label:
            text: "SPACE-X"
            font_size: '40sp'
            bold: True
            size_hint_y: None
            height: 300
            
        Label:
            text: "C r e a t o r B y S p a c e X\\nR u i j i e N e t w o r k T o o l k i t V 1.0\\n7 Day : 2500 MMK\\n15 Day : 5000 MMK\\n30 Day : 10000 MMK\\nUnlimited : 30000 MMK"
            halign: "center"
            size_hint_y: None
            height: 50

        Label:
            text: "Ruijie Voucher Code Login"
            font_size: '22sp'
            bold: True
            size_hint_y: None
            height: 10

        TextInput:
            id: token_input
            hint_text: 'Enter Voucher Code'
            font_size: '21sp'
            halign: "center"
            multiline: False
            size_hint_y: None
            height: 110
            
        Button:
            text: 'CONNECT'
            size_hint_y: None
            height: 200
            on_release: app.run_bypass(token_input.text)
            
        Label:
            id: status_label
            text: " > Status : None"
'''

class SpaceXApp(App):
    def build(self):
        Window.clearcolor = (0.08, 0.09, 0.12, 1)
        return Builder.load_string(KV)

    def run_bypass(self, voucher):
        self.root.ids.status_label.text = "> Status : Processing..."
        threading.Thread(target=lambda: asyncio.run(self.execute(voucher))).start()

    async def execute(self, voucher):
        async with aiohttp.ClientSession() as session:
            mgr = RuijieLoginManager()
            await mgr.auto_detect_gateway(session)
            if await mgr.login_voucher(session, voucher):
                if await mgr.send_request(session):
                    Clock.schedule_once(lambda dt: setattr(self.root.ids.status_label, 'text', ">Success : Internet Active "))
                else:
                    Clock.schedule_once(lambda dt: setattr(self.root.ids.status_label, 'text', ">Failed : Auth Error"))
            else:
                Clock.schedule_once(lambda dt: setattr(self.root.ids.status_label, 'text', ">Failed: Invalid Voucher"))

if __name__ == '__main__':
    SpaceXApp().run()
