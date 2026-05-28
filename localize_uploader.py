import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

new_css = """
    /* --- File Uploader Localization --- */
    /* Hide English Text */
    [data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p {
        display: none !important;
    }
    [data-testid="stFileUploadDropzone"] > div > small {
        display: none !important;
    }
    
    /* Inject Korean Text */
    [data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"]::after {
        content: "여기로 이미지 파일을 드래그하거나 클릭하여 업로드하세요";
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        display: block !important;
        margin-bottom: 5px !important;
    }
    [data-testid="stFileUploadDropzone"] > div::after {
        content: "파일당 최대 200MB • JPG, PNG 지원";
        font-size: 13px !important;
        color: #64748B !important;
        display: block !important;
        margin-top: 8px !important;
    }
"""

if 'File Uploader Localization' not in content:
    content = content.replace('</style>', new_css + '</style>')
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print('Injected localization CSS')
else:
    print('Already localized')
