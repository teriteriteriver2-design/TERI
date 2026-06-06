import codecs
import re

content = codecs.open('app_v2.py', encoding='utf-8').read()

new_css = """
    /* --- File Uploader Localization --- */
    /* Hide ALL English Text */
    [data-testid="stFileUploadDropzone"] [data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    [data-testid="stFileUploadDropzone"] small {
        display: none !important;
    }
    
    /* Inject Korean Text cleanly */
    [data-testid="stFileUploadDropzone"]::after {
        content: "여기로 이미지 파일을 드래그하거나 클릭하여 업로드하세요\\A\\A파일당 최대 200MB • JPG, PNG 지원";
        white-space: pre-wrap;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        text-align: center !important;
        display: block !important;
        margin-top: 10px !important;
    }
"""

# Remove the old localization CSS completely first
content = re.sub(r'/\* --- File Uploader Localization --- \*/.*?</style>', '</style>', content, flags=re.DOTALL)

# Inject the new one
content = content.replace('</style>', new_css + '</style>')

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Applied definitive localization CSS')
