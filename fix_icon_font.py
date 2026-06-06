import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

bad_css = '.material-icons, .material-symbols-rounded, [class*="icon"], svg, svg * { font-family: inherit !important; }'
good_css = '.material-symbols-rounded, .material-icons, [class*="icon"] { font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important; }'

if bad_css in content:
    content = content.replace(bad_css, good_css)
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print('Fixed icon font CSS!')
else:
    print('Bad CSS not found')
