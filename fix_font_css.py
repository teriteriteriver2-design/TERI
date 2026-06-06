import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

old_css = "* { font-family: 'Pretendard', sans-serif !important; }"
new_css = "html, body, [class*=\"st-\"], .stApp, .block-container, h1, h2, h3, h4, p, span, div, button, input { font-family: 'Pretendard', sans-serif; }\n.material-icons, .material-symbols-rounded, [class*=\"icon\"], svg, svg * { font-family: inherit !important; }"

if old_css in content:
    content = content.replace(old_css, new_css)
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print("Fixed font-family issue")
else:
    print("Font-family CSS not found")
