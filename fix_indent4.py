import codecs

with codecs.open('app_restored.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(689, 787): # 690 to 786 is index 689 to 786
    if lines[i].strip():
        # Lines 690-692 might be at 0 spaces.
        # Lines 700-786 might be at 0 spaces.
        # Let's just prefix with 8 spaces if it's currently at 0 spaces.
        # But wait, looking at lines 702-770, they already have some spaces (e.g. `with map_col:` has 0 spaces, `st.markdown` inside it has 4 spaces).
        # So we just add 8 spaces to all of them to shift the entire block properly!
        lines[i] = "        " + lines[i]

with codecs.open('app_restored.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
