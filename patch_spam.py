import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/gap_sniper.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the inner alert spam with collecting them, and then sending in batch.
old_logic = """
                            # 알람 전송 (AI 분석 없이 링크만)
                            msg = f"🚨 <b>[자동 감시 - 새 매물 발견!]</b>\\n"
                            msg += f"📍 <b>검색어:</b> {query}\\n"
                            msg += f"📰 <b>제목:</b> {title[:40]}...\\n"
                            msg += f"🔗 <b>바로가기:</b>\\n{href}\\n"
                            msg += f"💡 <i>대시보드에서 [수동 가동 버튼]을 누르시면 AI가 갭투자를 분석해드립니다!</i>"
                            send_sniper_telegram_alert(msg)
                            
                except Exception as e:"""

new_logic = """
                            # 방금 찾은 알람 내역만 모으기 (텔레그램 도배 방지)
                            if len(pending_list) <= 10: # 최대 10개까지만 알람 전송
                                msg = f"🚨 <b>[자동 감시 - 새 매물 발견!]</b>\\n"
                                msg += f"📍 <b>검색어:</b> {query}\\n"
                                msg += f"📰 <b>제목:</b> {title[:40]}...\\n"
                                msg += f"🔗 <b>바로가기:</b>\\n{href}\\n"
                                msg += f"💡 <i>대시보드에서 [수동 가동 버튼]을 누르시면 AI가 분석해드립니다!</i>"
                                send_sniper_telegram_alert(msg)
                            elif len(pending_list) == 11:
                                send_sniper_telegram_alert("⚠️ <b>새로운 매물이 너무 많습니다! (10개 초과)</b>\\n나머지는 텔레그램 도배 방지를 위해 알람을 생략했습니다. 대시보드에서 [수동 가동]을 눌러 확인하세요!")
                            
                except Exception as e:"""

content = content.replace(old_logic, new_logic)

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Spam protection patched in gap_sniper.py!")
