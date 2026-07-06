# Kivy/Buildozer အတွက် အဆင်သင့်ဖြစ်နေတဲ့ image ကို အသုံးပြုခြင်း
FROM kivy/buildozer:latest

# လိုအပ်တဲ့ system tools တွေကို install လုပ်ခြင်း
RUN sudo apt-get update && sudo apt-get install -y \
    python3-pip \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    && sudo rm -rf /var/lib/apt/lists/*

# အလုပ်လုပ်မယ့် folder ကို သတ်မှတ်ခြင်း
WORKDIR /home/user/host

# လိုအပ်တဲ့ libraries တွေကို ကြိုတင် install လုပ်ခြင်း
RUN pip3 install --upgrade buildozer cython

# build စတင်ရန် command (Docker container စတင်တဲ့အခါ အလိုအလျောက် build မယ်)
CMD ["buildozer", "-v", "android", "debug"]
