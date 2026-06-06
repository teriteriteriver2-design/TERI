import codecs
import re

content = codecs.open('speedauction_engine.py', encoding='utf-8').read()

if 'API_USAGE_TOKENS' not in content:
    content = content.replace('import json', 'import json\n\nAPI_USAGE_TOKENS = 0\n')
    
    # Replace for call_openai_json
    content = re.sub(
        r"resp = requests.post\(url, headers=headers, json=data, timeout=45\)\s*if resp\.status_code == 200:\s*content = resp\.json\(\)\['choices'\]\[0\]\['message'\]\['content'\]",
        "resp = requests.post(url, headers=headers, json=data, timeout=45)\n        if resp.status_code == 200:\n            res_json = resp.json()\n            global API_USAGE_TOKENS\n            API_USAGE_TOKENS += res_json.get('usage', {}).get('total_tokens', 0)\n            content = res_json['choices'][0]['message']['content']",
        content
    )
    
    # Replace for call_openai_text
    content = re.sub(
        r"resp = requests.post\(url, headers=headers, json=data, timeout=45\)\s*if resp\.status_code == 200:\s*return resp\.json\(\)\['choices'\]\[0\]\['message'\]\['content'\]",
        "resp = requests.post(url, headers=headers, json=data, timeout=45)\n        if resp.status_code == 200:\n            res_json = resp.json()\n            global API_USAGE_TOKENS\n            API_USAGE_TOKENS += res_json.get('usage', {}).get('total_tokens', 0)\n            return res_json['choices'][0]['message']['content']",
        content
    )

    # Replace for call_openai_vision_json
    content = re.sub(
        r"resp = requests.post\(url, headers=headers, json=data, timeout=60\)\s*if resp\.status_code == 200:\s*content = resp\.json\(\)\['choices'\]\[0\]\['message'\]\['content'\]",
        "resp = requests.post(url, headers=headers, json=data, timeout=60)\n        if resp.status_code == 200:\n            res_json = resp.json()\n            global API_USAGE_TOKENS\n            API_USAGE_TOKENS += res_json.get('usage', {}).get('total_tokens', 0)\n            content = res_json['choices'][0]['message']['content']",
        content
    )
    
    codecs.open('speedauction_engine.py', 'w', encoding='utf-8').write(content)
    print('Patched speedauction_engine.py successfully!')
else:
    print('Already patched.')
