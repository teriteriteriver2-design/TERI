import os
import sys
import glob
from datetime import datetime
import dulwich.porcelain as p

# 1. Load config
with open('.env', 'r', encoding='utf-8') as f:
    env_content = f.read()

GITHUB_TOKEN = None
GITHUB_REPO_URL = None
for line in env_content.splitlines():
    if line.startswith('GITHUB_TOKEN='):
        GITHUB_TOKEN = line.split('=', 1)[1].strip()
    elif line.startswith('GITHUB_REPO_URL='):
        GITHUB_REPO_URL = line.split('=', 1)[1].strip()

if not GITHUB_TOKEN or not GITHUB_REPO_URL:
    print("[오류] .env 파일에서 GITHUB_TOKEN 또는 GITHUB_REPO_URL을 찾을 수 없습니다.")
    input("종료하려면 엔터를 누르세요...")
    sys.exit(1)

# Modify URL to include credentials for push
auth_url = GITHUB_REPO_URL.replace("https://", f"https://oauth2:{GITHUB_TOKEN}@")

repo_dir = '.'
git_dir = os.path.join(repo_dir, '.git')

# 2. Init repo if it doesn't exist
if not os.path.exists(git_dir):
    print("Git 저장소를 초기화합니다...")
    p.init(repo_dir)

print("백업할 파일을 스캔 중입니다...")

# 3. Gather files to add manually to ensure strict ignore rules
ignored_extensions = ['.db', '.sqlite', '.sqlite3', '.log', '.tmp', '.bak']
ignored_dirs = ['venv', '__pycache__', '.git', '.streamlit']
ignored_files = ['.env']

files_to_add = []
for root, dirs, files in os.walk(repo_dir):
    # filter directories in-place
    dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith('.')]
    
    for file in files:
        if file in ignored_files:
            continue
            
        ext = os.path.splitext(file)[1].lower()
        if ext in ignored_extensions:
            continue
            
        rel_path = os.path.relpath(os.path.join(root, file), repo_dir)
        files_to_add.append(rel_path.replace('\\', '/'))

print(f"{len(files_to_add)}개의 파일을 스테이징합니다...")
repo = p.Repo(repo_dir)
p.add(repo, paths=files_to_add)

# 4. Commit
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_msg = f"Auto Backup: {now_str}".encode('utf-8')
print("커밋을 생성합니다...")
commit_id = p.commit(repo, message=commit_msg, author=b"AutoBackup <backup@local>", committer=b"AutoBackup <backup@local>")

# 5. Push
print("GitHub으로 백업을 전송합니다. 잠시만 기다려주세요...")
try:
    # Rename branch to main if it's currently master
    repo.refs[b'refs/heads/main'] = commit_id
    
    # Push to origin main
    p.push(repo, auth_url, b'refs/heads/main')
    print("=================================================")
    print("🎉 백업이 성공적으로 완료되었습니다!")
    print(f"👉 확인 URL: {GITHUB_REPO_URL}")
    print("=================================================")
except Exception as e:
    print(f"[오류] 백업 전송 실패: {e}")

input("창을 닫으려면 아무 키나 누르세요...")
