import sqlite3
import datetime

DB_NAME = "schedule.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            is_auto INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    
    # Check if auto schedules exist, if not, insert them
    c.execute("SELECT count(*) FROM schedules WHERE is_auto = 1")
    count = c.fetchone()[0]
    
    if count == 0:
        auto_schedules = [
            ("2026-05-28", "🏦 금리", "한국은행 금융통화위원회 (통화정책방향)", 1),
            ("2026-06-17", "🇺🇸 FOMC", "미국 연방공개시장위원회(FOMC) 기준금리 결정", 1),
            ("2026-07-16", "🏦 금리", "한국은행 금융통화위원회 (통화정책방향)", 1),
            ("2026-07-31", "💸 세금", "재산세(건축물, 주택1기분) 납부 마감일", 1),
            ("2026-08-27", "🏦 금리", "한국은행 금융통화위원회 (통화정책방향)", 1),
            ("2026-09-16", "🇺🇸 FOMC", "미국 연방공개시장위원회(FOMC) 기준금리 결정", 1),
            ("2026-09-30", "💸 세금", "재산세(토지, 주택2기분) 납부 마감일", 1),
            ("2026-10-15", "🏦 금리", "한국은행 금융통화위원회 (통화정책방향)", 1),
            ("2026-11-04", "🇺🇸 FOMC", "미국 연방공개시장위원회(FOMC) 기준금리 결정", 1),
            ("2026-11-26", "🏦 금리", "한국은행 금융통화위원회 (통화정책방향)", 1),
            ("2026-12-15", "💸 세금", "종합부동산세(종부세) 정기분 납부 마감일", 1),
            ("2026-12-16", "🇺🇸 FOMC", "미국 연방공개시장위원회(FOMC) 기준금리 결정", 1),
        ]
        c.executemany("INSERT INTO schedules (date_str, category, description, is_auto) VALUES (?, ?, ?, ?)", auto_schedules)
        conn.commit()
        
    conn.close()

def get_schedules():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Only fetch schedules from today onwards, or recent ones
    c.execute("SELECT id, date_str, category, description, is_auto FROM schedules ORDER BY date_str ASC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "date": r[1], "category": r[2], "description": r[3], "is_auto": bool(r[4])} for r in rows]

def add_schedule(date_str, category, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO schedules (date_str, category, description, is_auto) VALUES (?, ?, ?, 0)", 
              (date_str, category, description))
    conn.commit()
    conn.close()

def delete_schedule(schedule_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM schedules WHERE id = ? AND is_auto = 0", (schedule_id,))
    conn.commit()
    conn.close()
