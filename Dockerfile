# Kivy/Buildozer official image ကို အသုံးပြုခြင်း
FROM kivy/buildozer:latest

# Root အသုံးပြုခွင့်ပေးခြင်း
USER root

# လိုအပ်တဲ့ System Tools များ Install လုပ်ခြင်း
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    build-essential \
    libncurses5-dev \
    libncursesw5-dev \
    libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# အလုပ်လုပ်မယ့် Workspace သတ်မှတ်ခြင်း
WORKDIR /home/user/host

# Buildozer နှင့် လိုအပ်သော library များ Update လုပ်ခြင်း
RUN pip3 install --upgrade buildozer cython

# Build လုပ်မည့် command (GitHub Action ကနေ ခေါ်ယူရန်)
CMD ["buildozer", "-v", "android", "debug"]
