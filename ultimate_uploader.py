import codecs
import re

content = codecs.open('app_v2.py', encoding='utf-8').read()

# First, remove the previous bulletproof attempt
content = re.sub(r'/\* --- Bulletproof File Uploader Fix --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)

ultimate_css = """
    /* --- Ultimate File Uploader Fix --- */
    /* Hide EVERY text and icon element inside the dropzone natively, leaving ONLY the invisible file input untouched */
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] span,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] small,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] p,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] svg,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] i,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] div {
        display: none !important;
    }
    
    /* Rebuild with bulletproof Emoji icon and Text */
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

content = content.replace('</style>', ultimate_css + '</style>', 1)

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Applied ultimate CSS')
