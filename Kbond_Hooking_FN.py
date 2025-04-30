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

# === 기존 CSV 파일 삭제 및 초기화 ===
for path in (csv_path, d1_csv_path):
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ 기존 파일 삭제: {path}")

# === CSV 생성 ===
headers = [
    '시간','종목코드','상품구분','수익률','민평','대비','수량','만기','구분','판매자','화면'
] + [f'col{i+1}' for i in range(max_cols)]
for path in (csv_path, d1_csv_path):
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

        # D1 필터: 첫 번째 토큰에 'D1B' 포함
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
