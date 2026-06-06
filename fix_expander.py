import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

css_addition = """
    /* --- Fix Expander Arrow Icon Font --- */
    .stIconMaterial, .material-icons, .material-symbols-rounded, [class*="IconMaterial"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
        font-feature-settings: 'liga' 1 !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
    }
"""

content = content.replace('</style>', css_addition + '</style>', 1)
codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Applied expander icon CSS fix.')
