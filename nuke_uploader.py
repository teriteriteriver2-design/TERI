import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

css_replacement = """
    /* --- File Uploader Nuke And Rebuild --- */
    /* Hide the broken icon and overlapping text entirely without breaking clickability */
    [data-testid="stFileUploadDropzone"] > div {
        display: none !important;
    }
    
    /* Rebuild with bulletproof Emoji icon and Text */
    [data-testid="stFileUploadDropzone"]::before {
        content: "📁";
        font-size: 42px !important;
        display: block !important;
        text-align: center !important;
        margin-bottom: 15px !important;
        line-height: 1 !important;
    }
    
    [data-testid="stFileUploadDropzone"]::after {
        content: "여기를 클릭하거나 파일을 드래그하여 업로드하세요\\A최대 200MB • JPG, PNG 파일 지원";
        white-space: pre-wrap !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-align: center !important;
        display: block !important;
        line-height: 1.6 !important;
    }
"""

content = content.replace('</style>', css_replacement + '</style>')
codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
print('Applied nuke and rebuild CSS')
