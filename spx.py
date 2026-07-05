import os
import asyncio
import re
import base64
import time
import random
import aiohttp
from urllib.parse import urlparse, parse_qs, urljoin

# Terminal Color Codes
bcyan = "\033[1;36m"
reset = "\033[0m"
white = "\033[0;37m"
bgreen = "\033[1;32m"
bred = "\033[1;31m"
yellow = "\033[0;33m"

r = "\033[1;31m"
g = "\033[1;32m"
w = "\033[0m"

# Global variables
SUCCESS = 0
TIMEOUT_SEC = 10

def show_banner():
    try:
        os.system('clear' if os.name == 'posix' else 'cls')
    except:
        pass
    print(f"{bcyan}")
    print("  ██████╗ ██████╗  █████╗  ██████╗███████╗  ██╗  ██╗")
    print("  ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝  ╚██╗██╔╝")
    print("  ███████╗██████╔╝███████║██║     █████╗     ╚███╔╝ ")
    print("  ╚════██║██╔═══╝ ██╔══██║██║     ██╔══╝     ██╔██╗ ")
    print("  ███████║██║     ██║  ██║╚██████╗███████╗  ██╔╝ ██╗")
    print("  ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝  ╚═╝  ╚═╝")
    print(f"\n        ⚡  C r e a t o r B y S P A C E  X  ⚡{reset}")


# --- Ruijie Login Manager Class ---
class RuijieLoginManager:
    def __init__(self):
        self.ip = None
        self.mac = None
        self.current_sid = None
        self.load_saved_ip()
        self.load_saved_mac()
        self.phone_number = "12345678901"

    def load_saved_ip(self):
        if os.path.exists(".ip"):
            try:
                with open(".ip", "r") as f:
                    self.ip = f.read().strip()
            except:
                self.ip = None

    def load_saved_mac(self):
        if os.path.exists(".mac"):
            try:
                with open(".mac", "r") as f:
                    self.mac = f.read().strip()
            except:
                self.mac = None

    async def auto_detect_gateway(self, session):
        print(f"\n{g}[*] Thank For Your Support {reset}")
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile'
        }

        try:
            async with session.get(test_url, headers=headers, timeout=5, allow_redirects=False) as resp:
                if resp.status in (301, 302):
                    location = resp.headers.get('Location', '')
                    parsed_url = urlparse(location)
                    query_params = parse_qs(parsed_url.query)

                    gw_addr_list = query_params.get('gw_address')
                    if gw_addr_list:
                        self.ip = gw_addr_list[0]
                        with open(".ip", "w") as f:
                            f.write(self.ip)
                        print(f"{g}[+] Bypassing Ruijie Server..{reset}")

                    mac_list = query_params.get('mac') or query_params.get('umac') or query_params.get('usermac')
                    if mac_list:
                        self.mac = mac_list[0]
                        with open(".mac", "w") as f:
                            f.write(self.mac)
                        print(f"{g}[+] Please Wait..{reset}")
                    else:
                        print(f"{r} ERROR {reset}")

                    if gw_addr_list:
                        time.sleep(1)
                        return True
                else:
                    if self.ip and self.mac:
                        print(f"{g}[+] Loading {reset}")
                        return True
                    print(f"{r}[-] ERROR {reset}")
        except Exception as e:
            if self.ip and self.mac:
                print(f"{g}[+] Connection .{reset}")
                return True
            print(f"{r}[-] Connection ERROR {e}{reset}")
        return False

    async def _fetch_sid(self, session):
        if not self.ip or not self.mac:
            print(f"{r}[!] Error{reset}")
            return None

        step1_url = f"https://portal-as.ruijienetworks.com/auth/wifidogAuth/login/?gw_id=c4b25b2c5e82&gw_sn=H1TB2WU006124&gw_address=192.168.110.1&gw_port=2060&ip={self.ip}&mac={self.mac}&slot_num=13&nasip=192.168.1.53&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C326&chap_challenge=%5C063%5C011%5C062%5C043%5C241%5C141%5C312%5C157%5C301%5C271%5C336%5C103%5C074%5C000%5C157%5C317"


        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14; 22101316C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.120 Mobile',
            'X-Requested-With': 'mark.via.gp',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }

        try:
            async with session.get(step1_url, headers=headers, timeout=TIMEOUT_SEC) as r1:
                if r1.status != 200:
                    return None

                body = await r1.text()
                js_match = re.search(r"self\.location\.href\s*=\s*['\"]([^'\"]+)['\"]", body)
                if not js_match:
                    return None

                api_path = js_match.group(1)
                base_url = "https://portal-as.ruijienetworks.com"
                step2_url = urljoin(base_url, api_path)

            async with session.get(step2_url, headers=headers, timeout=TIMEOUT_SEC, allow_redirects=False) as r2:
                if r2.status == 302:
                    location = r2.headers.get('Location', '')
                    parsed_url = urlparse(location)
                    query_params = parse_qs(parsed_url.query)
                    sid_list = query_params.get('sessionId')

                    if sid_list:
                        sid = sid_list[0]
                        self.current_sid = sid
                        print(f"{g}[+] Checking Your Voucher Code {reset}")
                        return sid

        except Exception as e:
            print(f"{r}[!]Error: {e}{reset}")
            return None

    async def login_voucher(self, session, voucher, debug=False):
        global SUCCESS

        if not self.current_sid:
            print(f"[ * ] Wait")
            self.current_sid = await self._fetch_sid(session)

        if not self.current_sid:
            print(f"{r}[!] Failed to process{reset}")
            return False

        data = {
            "accessCode": voucher,
            "sessionId": self.current_sid,
            "apiVersion": 1
        }

        post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()

        headers = {
            "authority": "portal-as.ruijienetworks.com",
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://portal-as.ruijienetworks.com",
            "referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?RES=./../expand/res/kunji5dg96teooiimnl&IS_EG=0&sessionId={self.current_sid}",
            "user-agent": 'Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }

        try:
            async with session.post(post_url, json=data, headers=headers) as req:
                response = await req.text()

                if debug:
                    print(f"{response}")

                if 'logonUrl' in response:
                    SUCCESS += 1
                    print(f'{g}Success Auth Voucher: {voucher}{reset}')
                    return True
                else:
                    if debug:
                        print(f"{r}[-] Failed for voucher: {voucher}{reset}")
                    return False

        except Exception as Error:
            if debug:
                print(f"{r}[!] Error: {Error}{reset}")
            return False

    async def send_request(self, session, log=True):
        if not self.current_sid:
            sid = await self._fetch_sid(session)
            if not sid:
                if log:
                    print(f"{r}[!] ERROR {reset}")
                return False
        else:
            sid = self.current_sid

        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }

        params = {
            'token': sid,
            'phoneNumber': self.phone_number,
        }

        try:
            auth_url = f'http://{self.ip}:2060/wifidog/auth'
            async with session.post(auth_url, params=params, headers=headers, timeout=TIMEOUT_SEC) as response:
                if log:
                    print("[+]Ruijie New Security Bypassed ")

                if response.status == 200:
                    print(f"{g}[+] Successfully Logged In! Internet Is Now Active.]{reset}")
                    return True
                return False

        except Exception as e:
            if log:
                print(f"{r}[!]Error: {e}{reset}")
            return False

    async def run_auth_flow(self, session, voucher, debug=False):
        detected = await self.auto_detect_gateway(session)
        if not detected:
            print(f"{r}[!] Bypass Stopping{reset}")
            return

        sid = await self._fetch_sid(session)
        if not sid:
            print(f"{r}[!] Bypass Stopped{reset}")
            return

        login_success = await self.login_voucher(session, voucher, debug=debug)

        if login_success:
            print(f"{g}[+] Voucher Valid. ...")
            await self.send_request(session, log=debug)
        else:
            print(f"{r}[!] Voucher Authentication Failed.{reset}")


# --- Tool Executor Flow ---
async def start_tool():
    show_banner()
    user_voucher = input(f"\n{yellow} Enter Voucher Code : {reset}").strip()

    if not user_voucher:
        print(f"{r}[!]Need Voucher Code{reset}")
        return

    manager = RuijieLoginManager()
    async with aiohttp.ClientSession() as session:
        print("\n[ * ] Activating Ruijie Server...")
        await manager.run_auth_flow(session, voucher=user_voucher, debug=False)

    input(f"\n{white}Press Enter To Exit...{reset}")

def run():
    """အခြား Script သို့မဟုတ် Main ဖိုင်မှ ဆွဲခေါ်အသုံးပြုရန် Function"""
    try:
        asyncio.run(start_tool())
    except KeyboardInterrupt:
        print("\n[!] Program stopped by user.")


if __name__ == "__main__":
    run()