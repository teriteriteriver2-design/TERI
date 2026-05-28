import codecs
from speedauction_engine import call_openai_text
import sys
import time

def restore_app():
    with codecs.open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    chunk_size = 100
    restored_lines = []
    
    system_prompt = """You are an expert Python developer and Korean PropTech specialist.
The user's `app.py` file has been corrupted due to encoding issues. Many Korean characters were replaced by `?`.
Your task is to reconstruct the original Korean text perfectly based on the context.
Rules:
1. Replace all `?` with the most logical Korean words. For example: `??벌자` -> `돈벌자`, `초프리?????크` -> `초프리미엄 프롭테크`, `가??보 ?음` -> `가격정보 없음`.
2. FIX ANY SYNTAX ERRORS caused by missing quotes. For example, if a line is `return f"{uk}????` it should be `return f"{uk}억 원"`
3. DO NOT CHANGE any python logic, variable names, or indentation. ONLY fix the corrupted Korean strings and syntax.
4. Output ONLY the raw Python code. Do not output markdown blocks like ```python. Just the code."""

    for i in range(0, len(lines), chunk_size):
        chunk = "".join(lines[i:i+chunk_size])
        if "?" not in chunk:
            restored_lines.append(chunk)
            continue
            
        print(f"Restoring chunk {i} to {i+chunk_size}...")
        try:
            restored = call_openai_text(system_prompt, chunk)
            if restored.startswith("```python"):
                restored = restored[9:]
            if restored.endswith("```"):
                restored = restored[:-3]
            restored = restored.strip('\n') + '\n'
            restored_lines.append(restored)
            time.sleep(1) # ratelimit
        except Exception as e:
            print(f"Error on chunk {i}: {e}")
            restored_lines.append(chunk)
            
    with codecs.open('app_restored.py', 'w', encoding='utf-8') as f:
        f.writelines(restored_lines)
    print("Done!")

if __name__ == "__main__":
    restore_app()
