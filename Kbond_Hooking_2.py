############ version 1 최초버전 / 원문 데이터만 받기.
# import pyshark
# import time

# # === 설정 ===
# interface_number = '4'
# kbond_ip = '58.123.191.139'
# kbond_port = '15201'
# local_pc_ip = '121.141.233.218'
# # === 필드 정리 함수 ===
# def clean_field(text):
#     return text.replace('\x00', '').replace('\r', '').replace('\n', '').strip()

# # === 2단계 파싱 함수 ===
# def parse_kbond_2stage(fields):
#     try:
#         if len(fields) < 22:
#             return None

#         primary = {
#             '종목코드': fields[5],
#             '종목명': fields[6],
#             '단위': fields[7],
#             '만기일': fields[8][:4] + '-' + fields[8][4:6] + '-' + fields[8][6:] if len(fields[8]) == 8 else fields[8],
#             '대비(bp)': fields[9],
#             '수익률': fields[10],
#             '매수/매도': fields[13],
#             '민평': fields[14],
#             '수량': fields[16],
#             '사용자ID': fields[19],
#             '화면번호': fields[20],
#             'BS구분': fields[21]
#         }

#         followup = {}
#         if "2.483" in fields[29:]:  # 예시: 반복 수치 포인트 존재 확인
#             idx = fields.index("2.483", 29)
#             followup = {
#                 '민평_반복': fields[idx],
#                 '대비_반복': fields[idx + 2] if idx + 2 < len(fields) else '',
#                 '수익률_반복': fields[idx + 4] if idx + 4 < len(fields) else '',
#                 '사용자ID_반복': fields[19],
#                 '화면_반복': fields[20]
#             }

#         return primary, followup
#     except Exception as e:
#         return None, None

# # === 패킷 수신 콜백 ===
# def packet_callback(pkt):
#     try:
#         if 'TCP' in pkt:
#             src_ip = pkt.ip.src
#             dst_ip = pkt.ip.dst
#             src_port = pkt.tcp.srcport
#             dst_port = pkt.tcp.dstport

#             # KBond 서버 -> 내 PC 필터링
#             if not ((src_ip == kbond_ip and dst_port == kbond_port) or (dst_ip == local_pc_ip and src_port == kbond_port)):
#                 return


#             payload = pkt.tcp.payload
#             if payload:
#                 try:
#                     raw_bytes = bytes.fromhex(payload.replace(':', ''))
#                     ascii_data = raw_bytes.decode('euc-kr', errors='ignore')
#                     ascii_data = ascii_data.replace('\x00', '').strip()

#                     if "KR" not in ascii_data and "국고" not in ascii_data:
#                         return

#                     fields = [clean_field(f) for f in ascii_data.split() if f.strip()]
#                     primary, followup = parse_kbond_2stage(fields)

#                     if primary:
#                         now = time.strftime('%H:%M:%S')
#                         connection_info = f"[{src_ip}:{src_port} -> {dst_ip}:{dst_port}]"

#                         output = (
#                             f"{now} {connection_info} 종목: {primary['종목코드']} / {primary['종목명']} | "
#                             f"수익률: {primary['수익률']}% | 민평: {primary['민평']}% | 대비: {primary['대비(bp)']}bp | "
#                             f"수량: {primary['수량']} | 만기: {primary['만기일']} | 구분: {primary['매수/매도']} | "
#                             f"사용자: {primary['사용자ID']} | 화면: {primary['화면번호']}"
#                         )

#                         if followup:
#                             output += (
#                                 f" | 민평_반복: {followup['민평_반복']} | 대비_반복: {followup['대비_반복']} | "
#                                 f"수익률_반복: {followup['수익률_반복']}"
#                             )

#                         print(output)

#                 except Exception as decode_error:
#                     print(f"❌ decode error: {decode_error}")
#     except Exception as e:
#         print(f"❌ packet_callback error: {e}")

# # === 실행 ===
# if __name__ == "__main__":
#     print("🧲 KBond 채권 데이터 실시간 감지 시작 (2단계 파싱)...")
#     capture = pyshark.LiveCapture(interface=interface_number, display_filter='tcp')
#     capture.apply_on_packets(packet_callback)


############ version  2 1차 정제 시도도

# import pyshark
# import time
# import re

# # === 설정 ===
# interface_number = '4'
# kbond_ip = '58.123.191.139'
# kbond_port = '15201'
# local_pc_ip = '121.141.233.218'

# # === 필드 정리 함수 ===
# def clean_field(text):
#     return text.replace('\x00', '').replace('\r', '').replace('\n', '').strip()

# # === 유동 필드 파싱 함수 (정규식/위치 기반 개선) ===
# def parse_kbond_flexible(tokens):
#     result = {
#         '시간': '', '종목코드': '', '수익률': '', '민평': '',
#         '대비': '', '수량': '', '만기': '', '구분': '',
#         '사용자': '', '화면': ''
#     }
#     try:
#         for i, token in enumerate(tokens):
#             if i == 0 and ':' in token:
#                 result['시간'] = token
#             elif re.match(r'^KR\d{9}[A-Z0-9]{2}$', token):
#                 result['종목코드'] = token
#             elif token == '수익률:' and i + 1 < len(tokens):
#                 result['수익률'] = tokens[i + 1] if '%' in tokens[i + 1] else ''
#             elif token == '민평:' and i + 1 < len(tokens):
#                 result['민평'] = tokens[i + 1] if '%' in tokens[i + 1] else ''
#             elif token == '대비:' and i + 1 < len(tokens):
#                 result['대비'] = tokens[i + 1] if 'bp' in tokens[i + 1] else ''
#             elif token == '수량:' and i + 1 < len(tokens):
#                 result['수량'] = tokens[i + 1] if re.match(r'[-+]?\d+(\.\d+)?', tokens[i + 1]) else ''
#             elif token == '만기:' and i + 1 < len(tokens):
#                 result['만기'] = tokens[i + 1] if re.match(r'\d{8}|\d{4}-\d{2}-\d{2}', tokens[i + 1]) else ''
#             elif token == '구분:' and i + 1 < len(tokens):
#                 result['구분'] = tokens[i + 1]
#             elif token == '사용자:' and i + 1 < len(tokens):
#                 # 사용자 ID는 보통 숫자/기호가 아니며 4글자 이상 영문/숫자 혼합
#                 if re.match(r'^[a-zA-Z0-9]{4,}$', tokens[i + 1]):
#                     result['사용자'] = tokens[i + 1]
#             elif token == '화면:' and i + 1 < len(tokens):
#                 if re.match(r'^A\d{5}$', tokens[i + 1]) or re.match(r'^\d{2}:\d{2}:\d{2}$', tokens[i + 1]):
#                     result['화면'] = tokens[i + 1]

#         # 후처리: 수익률, 민평 누락시 백업 - %포함된 값 자동 채택
#         if not result['수익률']:
#             result['수익률'] = next((t for t in tokens if '%' in t and result['수익률'] == ''), '')
#         if not result['민평']:
#             candidates = [t for t in tokens if '%' in t and t != result['수익률']]
#             result['민평'] = candidates[0] if candidates else ''

#         return result
#     except Exception as e:
#         return {'error': str(e)}

# # === 패킷 수신 콜백 ===
# def packet_callback(pkt):
#     try:
#         if 'TCP' in pkt:
#             src_ip = pkt.ip.src
#             dst_ip = pkt.ip.dst
#             src_port = pkt.tcp.srcport
#             dst_port = pkt.tcp.dstport

# #             # KBond 서버 -> 내 PC 필터링
#             if not ((src_ip == kbond_ip and dst_port == kbond_port) or (dst_ip == local_pc_ip and src_port == kbond_port)):
#                 return


#             payload = pkt.tcp.payload
#             if payload:
#                 try:
#                     raw_bytes = bytes.fromhex(payload.replace(':', ''))
#                     ascii_data = raw_bytes.decode('euc-kr', errors='ignore')
#                     ascii_data = ascii_data.replace('\x00', '').strip()

#                     print(f"📦 수신 원문: {ascii_data}")

#                     if "KR" not in ascii_data and "국고" not in ascii_data:
#                         return

#                     tokens = [t for t in re.split(r'[ \t]+', ascii_data) if t.strip() and not re.match(r'^[\\x]+', t)]
#                     print(f"🔍 분리된 토큰 수: {len(tokens)} 예시: {tokens[:10]}")

#                     data = parse_kbond_flexible(tokens)

#                     if data and data.get('종목코드'):
#                         now = time.strftime('%H:%M:%S')
#                         connection_info = f"[{src_ip}:{src_port} -> {dst_ip}:{dst_port}]"
#                         output_line = (
#                             f"{now} {connection_info} 종목: {data['종목코드']} | 수익률: {data['수익률']} | 민평: {data['민평']} | "
#                             f"대비: {data['대비']} | 수량: {data['수량']} | 만기: {data['만기']} | 구분: {data['구분']} | 사용자: {data['사용자']} | 화면: {data['화면']}"
#                         )
#                         print(output_line)

#                 except Exception as decode_error:
#                     print(f"❌ decode error: {decode_error}")
#     except Exception as e:
#         print(f"❌ packet_callback error: {e}")

# # === 실행 ===
# if __name__ == "__main__":
#     print("🧲 KBond 채권 데이터 실시간 감지 시작 (강화된 필드 추출)...")
#     capture = pyshark.LiveCapture(interface=interface_number, display_filter='tcp')
#     capture.apply_on_packets(packet_callback)


# ############ version  3 정제 완료해서 CSV 저장하기.
# import pyshark
# import time
# import re
# import csv
# import os

# # === 설정 ===
# interface_number = '4'
# kbond_ip = '58.123.191.139'
# kbond_port = '15201'
# # 절대 경로로 CSV 파일 지정
# csv_path = os.path.join(os.getcwd(), 'kbond_log.csv')

# # === CSV 초기화 ===
# if not os.path.exists(csv_path):
#     with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             '시간','종목코드','수익률','민평','대비','수량','만기','구분','사용자','화면','원문'
#         ])
#     print(f"✅ CSV 파일 생성: {csv_path}")

# # === 토큰 정리 함수 ===
# def clean_field(text):
#     return text.replace('\x00','').replace('\r','').replace('\n','').strip()

# # === 유동 필드 파싱 함수 ===
# def parse_kbond_flexible(tokens):
#     result = dict.fromkeys(['시간','종목코드','수익률','민평','대비','수량','만기','구분','사용자','화면'], '')
#     for i, token in enumerate(tokens):
#         if i == 0 and ':' in token:
#             result['시간'] = token
#         elif token.startswith('KR'):
#             result['종목코드'] = token
#         elif token == '수익률:' and i+1 < len(tokens) and '%' in tokens[i+1]:
#             result['수익률'] = tokens[i+1]
#         elif token == '민평:' and i+1 < len(tokens) and '%' in tokens[i+1]:
#             result['민평'] = tokens[i+1]
#         elif token == '대비:' and i+1 < len(tokens) and 'bp' in tokens[i+1]:
#             result['대비'] = tokens[i+1]
#         elif token == '수량:' and i+1 < len(tokens) and re.match(r'[-+]?\d+(\.\d+)?', tokens[i+1]):
#             result['수량'] = tokens[i+1]
#         elif token == '만기:' and i+1 < len(tokens) and re.match(r'\d{8}|\d{4}-\d{2}-\d{2}', tokens[i+1]):
#             result['만기'] = tokens[i+1]
#         elif token == '구분:' and i+1 < len(tokens):
#             result['구분'] = tokens[i+1]
#         elif token == '사용자:' and i+1 < len(tokens) and re.match(r'^[A-Za-z0-9]{4,}$', tokens[i+1]):
#             result['사용자'] = tokens[i+1]
#         elif token == '화면:' and i+1 < len(tokens) and re.match(r'^A\d{5}$', tokens[i+1]):
#             result['화면'] = tokens[i+1]
#     # fallback 수익률/민평
#     if not result['수익률']:
#         for t in tokens:
#             if re.match(r'^\d+\.?\d*%$', t):
#                 result['수익률'] = t
#                 break
#     if not result['민평']:
#         for t in tokens:
#             if '%' in t and t != result['수익률']:
#                 result['민평'] = t
#                 break
#     return result

# # === 간단 fallback extract ===
# def fallback_extract(ascii_data):
#     m = re.search(r'(KR[A-Z0-9]+)', ascii_data)
#     return {
#         '시간':'', '종목코드': (m.group(1) if m else ''),
#         '수익률':'','민평':'','대비':'','수량':'','만기':'','구분':'','사용자':'','화면':''
#     }

# # === 패킷 수신 콜백 ===
# def packet_callback(pkt):
#     if 'TCP' not in pkt:
#         return
#     try:
#         src_ip = pkt.ip.src
#         src_port = pkt.tcp.srcport
#         dst_ip = pkt.ip.dst
#         dst_port = pkt.tcp.dstport

#         # KBond 서버 → 내 PC 필터 (src_port 비교)
#         if not (src_ip == kbond_ip and src_port == kbond_port):
#             return

#         raw = pkt.tcp.payload
#         if not raw:
#             return

#         # RAW ASCII 디코딩
#         raw_bytes = bytes.fromhex(raw.replace(':',''))
#         ascii_data = raw_bytes.decode('euc-kr',errors='ignore').replace('\x00','').strip()
#         print("📦 원문:", ascii_data)

#         # 반드시 KR 코드 포함
#         if not re.search(r'KR[A-Z0-9]+', ascii_data):
#             return

#         # 토큰 분리
#         tokens = [clean_field(t) for t in re.split(r'[ \t]+', ascii_data) if t and not t.startswith('\\x')]
#         print(f"🔍 토큰 수: {len(tokens)} | 예시:", tokens[:8])

#         # 파싱 시도
#         data = parse_kbond_flexible(tokens)
#         print("🎯 파싱 결과:", data)

#         # 종목코드 없으면 fallback
#         if not data['종목코드']:
#             data = fallback_extract(ascii_data)
#             print("⚠️ Fallback 결과:", data)

#         # 그래도 없으면 스킵
#         if not data['종목코드']:
#             return

#         # 출력
#         now = time.strftime('%H:%M:%S')
#         info = f"[{src_ip}:{src_port} -> {dst_ip}:{dst_port}]"
#         out = (
#             f"{now} {info} 종목:{data['종목코드']} | 수익률:{data['수익률']} | 민평:{data['민평']} | "
#             f"대비:{data['대비']} | 수량:{data['수량']} | 만기:{data['만기']} | "
#             f"구분:{data['구분']} | 사용자:{data['사용자']} | 화면:{data['화면']}"
#         )
#         print(out)

#         # 💾 CSV 쓰기
#         print("💾 CSV 쓰기:", data['종목코드'])
#         with open(csv_path,'a',newline='',encoding='utf-8-sig') as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 now, data['종목코드'], data['수익률'], data['민평'],
#                 data['대비'], data['수량'], data['만기'],
#                 data['구분'], data['사용자'], data['화면'],
#                 ascii_data
#             ])

#     except Exception as e:
#         print("❌ packet_callback error:", e)

# # === 메인 실행 ===
# if __name__ == '__main__':
#     print("🧲 KBond 채권 데이터 실시간 감지 시작 (CSV + 스마트 필터)...")
#     capture = pyshark.LiveCapture(interface=interface_number, display_filter='tcp')
#     try:
#         for pkt in capture.sniff_continuously():
#             packet_callback(pkt)
#     except KeyboardInterrupt:
#         print("\n❎ 감지 중단됨 (사용자 요청)")
#     except Exception as e:
#         print("❌ 캡처 에러:", e)


############### version 4 / 정제하고 csv 저장할 때 구분 제대로
# import pyshark
# import time
# import re
# import csv
# import os
# import string

# # === 설정 ===
# interface_number = '4'
# kbond_ip = '58.123.191.139'
# kbond_port = '15201'
# csv_path = os.path.join(os.getcwd(), 'kbond_log.csv')

# # === CSV 초기화 ===
# if not os.path.exists(csv_path):
#     with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             '시간','종목코드','수익률','민평','대비','수량','만기','구분','사용자','화면','raw_ascii'
#         ])
#     print(f"✅ CSV 파일 생성: {csv_path}")

# # === 토큰 정리 함수 ===
# def clean_field(text):
#     return text.replace('\x00','').replace('\r','').replace('\n','').strip()

# # === 유동 필드 파싱 함수 ===
# def parse_kbond_flexible(tokens):
#     result = dict.fromkeys([
#         '시간','종목코드','수익률','민평','대비','수량','만기','구분','사용자','화면'
#     ], '')
#     for i, token in enumerate(tokens):
#         if i == 0 and ':' in token:
#             result['시간'] = token
#         elif token.startswith('KR'):
#             result['종목코드'] = token
#         elif token == '수익률:' and i+1 < len(tokens) and '%' in tokens[i+1]:
#             result['수익률'] = tokens[i+1]
#         elif token == '민평:' and i+1 < len(tokens) and '%' in tokens[i+1]:
#             result['민평'] = tokens[i+1]
#         elif token == '대비:' and i+1 < len(tokens) and 'bp' in tokens[i+1]:
#             result['대비'] = tokens[i+1]
#         elif token == '수량:' and i+1 < len(tokens) and re.match(r'[-+]?\d+(\.\d+)?', tokens[i+1]):
#             result['수량'] = tokens[i+1]
#         elif token == '만기:' and i+1 < len(tokens) and re.match(r'\d{8}|\d{4}-\d{2}-\d{2}', tokens[i+1]):
#             result['만기'] = tokens[i+1]
#         elif token == '구분:' and i+1 < len(tokens):
#             result['구분'] = tokens[i+1]
#         elif token == '사용자:' and i+1 < len(tokens) and re.match(r'^[A-Za-z0-9]{4,}$', tokens[i+1]):
#             result['사용자'] = tokens[i+1]
#         elif token == '화면:' and i+1 < len(tokens) and re.match(r'^A\d{5}$', tokens[i+1]):
#             result['화면'] = tokens[i+1]
#     # 수익률/민평 fallback
#     if not result['수익률']:
#         for t in tokens:
#             if re.match(r'^\d+\.?\d*%$', t):
#                 result['수익률'] = t
#                 break
#     if not result['민평']:
#         for t in tokens:
#             if '%' in t and t != result['수익률']:
#                 result['민평'] = t
#                 break
#     return result

# # === 패킷 수신 콜백 ===
# def packet_callback(pkt):
#     if 'TCP' not in pkt:
#         return
#     try:
#         src_ip = pkt.ip.src
#         src_port = pkt.tcp.srcport
#         dst_ip = pkt.ip.dst
#         dst_port = pkt.tcp.dstport
#         # KBond 서버 포트 필터
#         if not (src_ip == kbond_ip and src_port == kbond_port):
#             return
#         raw = pkt.tcp.payload
#         if not raw:
#             return
#         raw_bytes = bytes.fromhex(raw.replace(':',''))
#         # ASCII 원문 디코딩
#         raw_text = raw_bytes.decode('euc-kr', errors='ignore')
#         # Printable 문자만 남기기
#         ascii_data = ''.join(
#             ch for ch in raw_text
#             if ch in string.printable or ord(ch) >= 0x80
#         ).strip()
#         print("📦 원문 ASCII:", ascii_data)
#         # 필수 KR 코드 확인
#         if not re.search(r'KR[A-Z0-9]+', ascii_data):
#             return
#         # 토큰 분리
#         tokens = [clean_field(t) for t in re.split(r'[ \t]+', ascii_data) if t and not t.startswith('\\x')]
#         print(f"🔍 토큰 수: {len(tokens)} | 예시: {tokens[:8]}")
#         # 파싱
#         data = parse_kbond_flexible(tokens)
#         print("🎯 파싱 결과:", data)
#         # Fallback
#         if not data['종목코드']:
#             m = re.search(r'(KR[A-Z0-9]+)', ascii_data)
#             data['종목코드'] = m.group(1) if m else ''
#             print("⚠️ Fallback 종목코드:", data['종목코드'])
#         if not data['종목코드']:
#             return
#         # 출력
#         now = time.strftime('%H:%M:%S')
#         info = f"[{src_ip}:{src_port}->{dst_ip}:{dst_port}]"
#         out = (
#             f"{now} {info} 종목:{data['종목코드']} | 수익률:{data['수익률']} | 민평:{data['민평']} | "
#             f"대비:{data['대비']} | 수량:{data['수량']} | 만기:{data['만기']} | "
#             f"구분:{data['구분']} | 사용자:{data['사용자']} | 화면:{data['화면']}"
#         )
#         print(out)
#         # CSV 저장 (printable ASCII 원문)
#         print("💾 CSV 쓰기:", data['종목코드'])
#         with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 now, data['종목코드'], data['수익률'], data['민평'],
#                 data['대비'], data['수량'], data['만기'],
#                 data['구분'], data['사용자'], data['화면'], ascii_data
#             ])
#     except Exception as e:
#         print("❌ packet_callback error:", e)

# # === 실행 ===
# if __name__ == '__main__':
#     print("🧲 KBond 채권 데이터 실시간 감지 시작 (Printable 정제 + CSV)...")
#     capture = pyshark.LiveCapture(interface=interface_number, display_filter='tcp')
#     try:
#         for pkt in capture.sniff_continuously():
#             packet_callback(pkt)
#     except KeyboardInterrupt:
#         print("\n❎ 감지 중단됨 (사용자 요청)")
#     except Exception as e:
#         print("❌ 캡처 에러:", e)


################# version5  필터별로해서 데이터 정제 후 csv 저장하는 버전


# import pyshark
# import time
# import re
# import csv
# import os
# import string

# # === 설정 ===
# interface_number = '4'
# kbond_ip = '58.123.191.139'
# kbond_port = '15201'
# csv_path = os.path.join(os.getcwd(), 'kbond_log.csv')
# max_cols = 60  # 최대 col 개수

# # === CSV 초기화 ===
# if not os.path.exists(csv_path):
#     with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
#         writer = csv.writer(f)
#         headers = [
#             '시간','종목코드','수익률','민평','대비','수량','만기','구분','사용자','화면'
#         ]
#         # col1 ~ colN 헤더 추가
#         headers += [f'col{i+1}' for i in range(max_cols)]
#         writer.writerow(headers)
#     print(f"✅ CSV 파일 생성: {csv_path}")

# # === 토큰 정리 함수 ===
# def clean_field(text):
#     return text.replace('\x00','').replace('\r','').replace('\n','').strip()

# # === 패킷 수신 콜백 ===
# def packet_callback(pkt):
#     if 'TCP' not in pkt:
#         return
#     try:
#         src_ip = pkt.ip.src
#         src_port = pkt.tcp.srcport
#         dst_ip = pkt.ip.dst
#         dst_port = pkt.tcp.dstport

#         # KBond 서버 포트 필터
#         if not (src_ip == kbond_ip and src_port == kbond_port):
#             return

#         raw = pkt.tcp.payload
#         if not raw:
#             return

#         raw_bytes = bytes.fromhex(raw.replace(':',''))
#         raw_text = raw_bytes.decode('euc-kr', errors='ignore')
#         ascii_data = ''.join(
#             ch for ch in raw_text
#             if ch in string.printable or ord(ch) >= 0x80
#         ).strip()
#         print("📦 원문 ASCII:", ascii_data)

#         # 토큰 화살표 'KR' 필터
#         if not re.search(r'KR[A-Z0-9]+', ascii_data):
#             return

#         # '	'로 분리된 컬럼
#         fields = [clean_field(f) for f in ascii_data.split('\t')]
#         print(f"🔍 필드 수: {len(fields)} | 예시: {fields[:10]}")

#         # 기본 파싱 (OPTIONAL)
#         # data = parse_kbond_flexible(tokens) ...

#         # CSV에 저장: 기본 10개 + col1..colN
#         now = time.strftime('%H:%M:%S')
#         code = next((f for f in fields if f.startswith('KR')), '')
#         rate = next((f for f in fields if re.match(r'^\d+\.?\d*%$', f)), '')
#         mint = next((f for f in fields if re.match(r'\d{8}$', f)), '')
#         # 기타 필드는 생략하거나 parse_kbond_flexible 사용
#         row = [now, code, '', '', '', '', mint, '', '', '', '']
#         # col1~colN
#         padded = fields + [''] * max(0, max_cols - len(fields))
#         row += padded[:max_cols]

#         print(f"💾 CSV 쓰기: {row[:15]}")
#         with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
#             writer = csv.writer(f)
#             writer.writerow(row)

#     except Exception as e:
#         print("❌ packet_callback error:", e)

# # === 실행 ===
# if __name__ == '__main__':
#     print("🧲 KBond 데이터 실시간 Raw Split CSV 저장 시작...")
#     capture = pyshark.LiveCapture(interface=interface_number, display_filter='tcp')
#     try:
#         for pkt in capture.sniff_continuously():
#             packet_callback(pkt)
#     except KeyboardInterrupt:
#         print("\n❎ 감지 중단됨 (사용자 요청)")
#     except Exception as e:
#         print("❌ 캡처 에러:", e)


################# version6 D1으로 들어오는 애들만 필터링.
import pyshark
import time
import re
import csv
import os
import string

# === 설정 ===
interface_number = '4'
kbond_ip = '58.123.191.139'
kbond_port = '15201'
csv_path = os.path.join(os.getcwd(), 'kbond_log.csv')
d1_csv_path = os.path.join(os.getcwd(), 'kbond_log_d1.csv')
max_cols = 60  # 최대 col 개수

# === CSV 초기화 ===
headers = [
    '시간','종목코드','상품구분','수익률','민평','대비','수량','만기','구분','판매자','화면'
] + [f'col{i+1}' for i in range(max_cols)]
for path in (csv_path, d1_csv_path):
    if not os.path.exists(path):
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            csv.writer(f).writerow(headers)
        print(f"✅ CSV 생성: {path}")

# === 토큰 정리 함수 ===
def clean_field(text):
    return text.replace('\x00','').replace('\r','').replace('\n','').strip()

# === 패킷 수신 콜백 ===
def packet_callback(pkt):
    if 'TCP' not in pkt:
        return
    try:
        src_ip, src_port = pkt.ip.src, pkt.tcp.srcport
        # KBond 서버 포트 필터
        if not (src_ip == kbond_ip and src_port == kbond_port):
            return

        raw = pkt.tcp.payload
        if not raw:
            return

        raw_bytes = bytes.fromhex(raw.replace(':',''))
        raw_text = raw_bytes.decode('euc-kr', errors='ignore')
        ascii_data = ''.join(
            ch for ch in raw_text
            if ch in string.printable or ord(ch) >= 0x80
        )
        print("📦 원문 ASCII:", ascii_data)

        # 공백/탭 기반 토큰 분리
        fields = [clean_field(f) for f in re.split(r'\s+', ascii_data) if f and not f.startswith('\\x')]
        print(f"🔍 필드 수: {len(fields)} | 예시: {fields[:8]}")

        # D1 필터: 첫 번째 토큰에 'D1' 포함 -> D1B로 변경경
        if not fields or 'D1B' not in fields[0]:
            return
        print(f"🔖 D1B 레코드 감지: {fields[0]}")

        # 상품 구분: FUT 포함 시 선물, else 현물
        category = '선물' if any('FUT' in f.upper() for f in fields) else '현물'

        # 주요 값 추출 (fields 인덱스 기준)
        code = next((f for f in fields if f.startswith('KR')), '')
        yield_rate = fields[14] if len(fields) > 14 else ''
        mint = fields[10] if len(fields) > 10 else ''  # 민평
        diff_bp = fields[15] if len(fields) > 15 else ''
        qty = fields[16] if len(fields) > 16 else ''
        side = fields[13] if len(fields) > 13 else ''  # 매수/매도
        seller = fields[19] if len(fields) > 19 else ''
        maturity = next((f for f in fields if re.match(r'^\d{8}$', f)), '')

        # 시간
        now = time.strftime('%H:%M:%S')
        # 기본 컬럼
        row = [
            now, code, category,
            yield_rate, mint, diff_bp,
            qty, maturity, side,
            seller, ''  # 화면 미추출
        ]
        # col1..colN 패딩
        padded = fields + ['']*(max_cols - len(fields))
        row += padded[:max_cols]

        # CSV 저장
        for path in (csv_path, d1_csv_path):
            print(f"💾 CSV 쓰기 ({path}): {code}")
            with open(path, 'a', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerow(row)

    except Exception as e:
        print("❌ packet_callback error:", e)

# === 메인 실행 ===
if __name__ == '__main__':
    print("🧲 D1 필터 실시간 감지 및 분류 저장 시작...")
    capture = pyshark.LiveCapture(interface=interface_number, display_filter='tcp')
    try:
        for pkt in capture.sniff_continuously():
            packet_callback(pkt)
    except KeyboardInterrupt:
        print("\n❎ 감지 중단됨 (사용자 요청)")
    except Exception as e:
        print("❌ 캡처 에러:", e)
