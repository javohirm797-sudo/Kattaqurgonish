#!/bin/bash

# Loyiha papkasiga o'tish
cd ~/

# Bot allaqachon ishlayotganini tekshirish
if pgrep -f "python3 bot.py" > /dev/null
# Agar ishlayotgan bo'lsa, hech narsa qilmaydi
then
    echo "Bot allaqachon ishlamoqda."
# Agar ishlamayotgan bo'lsa, uni fonda ishga tushiradi
else
    echo "Bot to'xtab qolgan. Qayta ishga tushirilmoqda..."
    source .venv/bin/activate
    nohup python3 bot.py > bot.log 2>&1 &
    echo "Bot fonda ishga tushirildi."
fi
