import codecs
import re

content = codecs.open('app_v2.py', encoding='utf-8').read()

# Replace any occurrence of the emoji or broken characters before "AI 비서는"
content = re.sub(
    r'with st\.expander\("[^"]*AI 비서는 언제 토큰\(비용\)을 소모하나요\?"\):',
    'with st.expander("[안내] AI 비서는 언제 토큰(비용)을 소모하나요?"):',
    content
)

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)

print('Patched successfully!')
