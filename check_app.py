with open('C:\\Users\\뀽제\\OneDrive\\바탕 화면\\BU\\app.py', 'rb') as f:
    lines = f.readlines()
    print("Total lines:", len(lines))
    for i in range(1070, min(len(lines), 1080)):
        print(f"{i}:", lines[i])
