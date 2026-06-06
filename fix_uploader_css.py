import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

reset_css = """
    /* --- File Uploader CSS Fix --- */
    div[data-testid="stFileUploader"] * {
        background: transparent !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
        border: none !important;
    }
    div[data-testid="stFileUploader"] section {
        background-color: #F8FAFC !important;
        border: 2px dashed #94A3B8 !important;
        padding: 30px !important;
        min-height: 120px !important;
    }
    div[data-testid="stFileUploader"] small {
        display: block !important;
        margin-top: 10px !important;
        opacity: 0.7;
    }
    div[data-testid="stFileUploadDropzone"] div {
        padding: 5px !important;
    }
    /* Exclude stFileUploader from the buggy stVerticalBlock global hover effects */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stFileUploader"]) {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stFileUploader"]):hover {
        transform: none !important;
        box-shadow: none !important;
    }
"""

if '/* --- File Uploader CSS Fix --- */' not in content:
    content = content.replace('</style>', reset_css + '</style>')
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print('Injected CSS fix for file uploader')
else:
    print('Already injected')
