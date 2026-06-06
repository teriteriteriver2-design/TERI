import codecs
import re

content = codecs.open('app_v2.py', encoding='utf-8').read()

# Remove the hacky localization CSS
content = re.sub(r'/\* --- File Uploader Localization --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)

# Remove the notranslate meta tag
tag = "st.markdown('<meta name=\"google\" content=\"notranslate\">', unsafe_allow_html=True)\n"
content = content.replace(tag, "")

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Removed hacky CSS localization and notranslate tag')
