import codecs
import re

content = codecs.open('app_v2.py', encoding='utf-8').read()

content = re.sub(r'/\* --- Fix Expander Arrow Icon Font --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)
content = re.sub(r'/\* --- Absolute Nuke of Expander Arrow \(arrow_down\) --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)
content = re.sub(r'/\* --- Ultimate Expander Icon Replacement --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)

ultimate_expander_css = """
    /* --- Ultimate Expander Icon Replacement --- */
    /* Target EVERYTHING that could possibly render the arrow_down text */
    summary[data-testid*="Expander"] svg,
    summary[data-testid*="Expander"] i,
    summary[data-testid*="Expander"] span[translate="no"],
    summary[data-testid*="Expander"] span[class*="material"],
    summary[data-testid*="Expander"] span[class*="icon"],
    summary[data-testid*="Expander"] span[class*="Icon"] {
        display: none !important;
        opacity: 0 !important;
        font-size: 0 !important;
    }
    
    /* Inject bulletproof emoji chevron */
    summary[data-testid*="Expander"] > div::after {
        content: "🔽";
        float: right;
        font-size: 16px !important;
        color: #38BDF8 !important;
        margin-left: 10px;
        line-height: inherit;
    }
"""

content = content.replace('</style>', ultimate_expander_css + '</style>', 1)

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Applied ultimate expander CSS replacement.')
