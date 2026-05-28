import codecs
import re

content = codecs.open('speedauction_engine.py', encoding='utf-8').read()

if 'import billing_db' not in content:
    content = content.replace('API_USAGE_TOKENS = 0', 'API_USAGE_TOKENS = 0\nimport billing_db')
    
    # Cost logic: 1000 tokens = 13.5 KRW -> 1 token = 0.0135 KRW
    replace_str = """global API_USAGE_TOKENS
            used = res_json.get('usage', {}).get('total_tokens', 0)
            API_USAGE_TOKENS += used
            billing_db.deduct_balance(used * 0.0135)"""
            
    content = re.sub(
        r"global API_USAGE_TOKENS\s*API_USAGE_TOKENS \+= res_json\.get\('usage', \{\}\)\.get\('total_tokens', 0\)",
        replace_str,
        content
    )
    
    codecs.open('speedauction_engine.py', 'w', encoding='utf-8').write(content)
    print('Patched speedauction_engine.py successfully!')
else:
    print('Already patched.')
