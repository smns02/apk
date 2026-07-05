import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import asyncio
import threading
import aiohttp

# spx.py ဖိုင်ထဲက RuijieLoginManager ကို ခေါ်ယူခြင်း
from spx import RuijieLoginManager

class RuijieApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        
        self.add_widget(Label(text="Ruijie Login Manager", font_size=24))
        
        self.voucher_input = TextInput(hint_text='Enter Voucher Code', multiline=False)
        self.add_widget(self.voucher_input)
        
        self.login_btn = Button(text="Login", size_hint=(1, 0.5))
        self.login_btn.bind(on_press=self.start_login_thread)
        self.add_widget(self.login_btn)
        
        self.status_label = Label(text="Status: Ready")
        self.add_widget(self.status_label)

    def start_login_thread(self, instance):
        voucher = self.voucher_input.text
        if not voucher:
            self.status_label.text = "Error: Enter Voucher Code!"
            return
        
        self.status_label.text = "Status: Connecting..."
        # GUI မခဲအောင် နောက်ကွယ်မှာ အလုပ်လုပ်ပေးမယ့် Thread ကို စတင်ခြင်း
        threading.Thread(target=self.run_async_task, args=(voucher,), daemon=True).start()

    def run_async_task(self, voucher):
        # Async loop အသစ်တစ်ခု ဖန်တီးခြင်း
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        manager = RuijieLoginManager()
        
        async def run_logic():
            try:
                async with aiohttp.ClientSession() as session:
                    # spx.py ထဲက အဓိကလုပ်ဆောင်ချက်ကို ခေါ်သုံးခြင်း
                    await manager.run_auth_flow(session, voucher=voucher, debug=True)
                    Clock.schedule_once(lambda dt: self.update_status("Task Completed!"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f"Error: {str(e)}"))
        
        loop.run_until_complete(run_logic())

    def update_status(self, text):
        self.status_label.text = text

class RuijieLoginApp(App):
    def build(self):
        return RuijieApp()

if __name__ == '__main__':
    RuijieLoginApp().run()
