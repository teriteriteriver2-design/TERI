import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

css_addition = """
    /* --- Absolute Nuke of Expander Arrow (arrow_down) --- */
    [data-testid*="ExpanderToggleIcon"],
    [data-testid*="stExpanderToggle"] svg,
    [data-testid*="stExpanderToggle"] .material-icons,
    [data-testid*="stExpanderToggle"] .material-symbols-rounded,
    [data-testid*="stExpanderToggle"] [class*="IconMaterial"],
    .st-emotion-cache-1216y9x {
        display: none !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        color: transparent !important;
    }
"""

content = content.replace('</style>', css_addition + '</style>', 1)
codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Nuked expander arrow CSS')
