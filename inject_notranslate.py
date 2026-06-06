import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

if 'notranslate' not in content:
    inject = "st.markdown('<meta name=\"google\" content=\"notranslate\">', unsafe_allow_html=True)\n"
    content = content.replace('st.set_page_config(', inject + 'st.set_page_config(')
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print('Injected notranslate tag.')
