import codecs
import re

content = codecs.open('app_v2.py', encoding='utf-8').read()

# First, remove ALL my previous hacky CSS injected blocks
content = re.sub(r'/\* --- File Uploader Nuke And Rebuild --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)
content = re.sub(r'/\* --- File Uploader CSS Fix --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)
content = re.sub(r'\[data-testid="stFileUploadDropzone"\].*?</style>', '</style>', content, flags=re.DOTALL)

bulletproof_uploader_css = """
    /* --- Bulletproof File Uploader Fix --- */
    /* Target ANY element containing the word 'upload' in class or testid */
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] > div {
        display: none !important;
    }
    [data-testid*="FileUploader"] [data-testid*="Dropzone"]::before {
        content: "📁";
        font-size: 45px !important;
        display: block !important;
        text-align: center !important;
        margin-bottom: 10px !important;
    }
    [data-testid*="FileUploader"] [data-testid*="Dropzone"]::after {
        content: "여기를 클릭하거나 이미지를 드래그하여 업로드하세요\\A최대 200MB 지원";
        white-space: pre-wrap !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-align: center !important;
        display: block !important;
        line-height: 1.5 !important;
    }
"""

# Replace the first style block (the global one)
content = content.replace('</style>', bulletproof_uploader_css + '</style>', 1)

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Applied bulletproof CSS')
