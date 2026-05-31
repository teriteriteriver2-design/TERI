import os

# Fix sentiment_crawler.py
sent_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/sentiment_crawler.py'
with open(sent_file, 'r', encoding='utf-8') as f:
    sent = f.read()

sent = sent.replace("res.get('link', '')", "res.get('href', '')")

# Also, if GPT strips [LINK: ], we should just parse "[LINK: " from evidence if it's there or just let GPT output the link properly.
with open(sent_file, 'w', encoding='utf-8') as f:
    f.write(sent)


# Fix speedauction_engine.py
eng_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/speedauction_engine.py'
with open(eng_file, 'r', encoding='utf-8') as f:
    eng = f.read()

eng = eng.replace("LINK: {res.get('link','')}", "LINK: {res.get('href','')}")

with open(eng_file, 'w', encoding='utf-8') as f:
    f.write(eng)

# Let's fix app_v2.py so if link is "[LINK: ]" or "#", we remove the anchor or disable it.
# Actually, now that it gets real links, it will just work.
print("href fixed!")
