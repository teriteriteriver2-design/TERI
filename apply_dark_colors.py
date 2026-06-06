import re

file_path = "C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    # Text colors
    "color:#111827": "color:#f8fafc",
    "color:#1F2937": "color:#f1f5f9",
    "color:#374151": "color:#e2e8f0",
    "color:#475569": "color:#cbd5e1",
    "color:#4B5563": "color:#94a3b8",
    "color:#6B7280": "color:#64748b",
    "color:black;": "color:#f8fafc;",
    "color: black;": "color: #f8fafc;",
    
    # Backgrounds
    "background: white;": "background: rgba(30,41,59,0.5);",
    "background:white;": "background: rgba(30,41,59,0.5);",
    "background:#F8FAFC": "background:rgba(15,23,42,0.6)",
    "background:#F3F4F6": "background:rgba(30,41,59,0.6)",
    "background:#E5E7EB": "background:rgba(255,255,255,0.1)",
    
    # Borders
    "border:1px solid #CBD5E1": "border:1px solid rgba(255,255,255,0.1)",
    "border:1px solid #E5E7EB": "border:1px solid rgba(255,255,255,0.05)",
    "border-bottom:1px solid #E5E7EB": "border-bottom:1px solid rgba(255,255,255,0.05)",
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Dark mode colors applied to app_v2.py")
