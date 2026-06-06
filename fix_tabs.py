import codecs

with codecs.open('app_restored.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 1: tab_search leakage (lines 535 to 610, which means index 534 to 610)
# Wait, let's verify if lines 535-610 are indeed unindented. 
# We'll just check if they are at 0-level and if so, add 4 spaces.
for i in range(534, 611):
    if lines[i].strip() and not lines[i].startswith(" ") and not lines[i].startswith("\t"):
        lines[i] = "    " + lines[i]

# Fix 2: tab_redev leakage (lines 989 to 1037, index 988 to 1037)
# But wait, lines 989-1002 should be inside the `with st.spinner:` which is under `if st.button:`
# The button is at 986: `    if st.button(...)` (4 spaces).
# So `with st.spinner:` (989) should be 8 spaces.
# The code inside the spinner (990-1002) should be 12 spaces!
# And the code after the spinner (1004-1037) should be 8 spaces!
for i in range(988, 1038):
    if lines[i].strip():
        # Let's count original spaces
        orig_spaces = len(lines[i]) - len(lines[i].lstrip())
        
        if 988 <= i <= 1001: # spinner and its contents
            if i == 988: # with st.spinner
                lines[i] = "        " + lines[i].lstrip()
            else: # zones = ..., for zone in zones...
                # if orig_spaces is 4, it means it should be 12 (it was shifted left by 8)
                lines[i] = "        " + lines[i] # just add 8 spaces to whatever it was!
        else: # 1002 to 1037 (UI update outside spinner but inside button)
            # Add 8 spaces to shift everything into the if st.button:
            lines[i] = "        " + lines[i]

with codecs.open('app_restored.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
