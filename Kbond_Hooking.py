import pyshark
import re
import time

# === 설정 ===
interface_number = '4'  # 네트워크 인터페이스 번호
kbond_ip = '121.141.233.218'
kbond_port = '15201'

# === 패킷 파싱 함수 ===
def clean_field(text):
    try:
        # 메모리단위로 끊은 후 공백, 탭문자로 글자 끊기.
        text = text.replace('\x00', '').replace('\r', '').replace('\n', '').strip()
        return text
    except:
        return text

# ascii 코드로 부터 packet preprocessing
def parse_packet_from_ascii_clean(ascii_data):
    try:
        # \n으로 나누고
        lines = ascii_data.split('\n')
        parsed_list = []
        # 탭 들어간거로 strip함.
        for line in lines:
            fields = line.strip().split('\t')
            # 글자수 3개 이하면 진행 -> line이 3개 이하면 원하는 정보 없음을 판단함.
            if len(fields) < 3:
                continue
            # 글자 단위수로 끊기.
            clean_fields = [clean_field(f) for f in fields]
            # 리스트로 어펜드드
            parsed_list.append(clean_fields)
        return parsed_list
    except Exception as e:
        print(f"❌ parse_packet_from_ascii_clean error: {e}")
        return []

# === 패킷 수신 콜백 ===
def packet_callback(pkt):
    try:
        # pshark를 통해 pkt 내 TCP 정보 뽑기.
        if 'TCP' in pkt:
            src_ip = pkt.ip.src
            dst_ip = pkt.ip.dst
            src_port = pkt.tcp.srcport
            dst_port = pkt.tcp.dstport

            # KBond IP+포트 매칭 필터
            if not ((src_ip == kbond_ip and dst_port == kbond_port) or (dst_ip == kbond_ip and src_port == kbond_port)):
                return

            payload = pkt.tcp.payload
            if payload:
                try:
                    raw_bytes = bytes.fromhex(payload.replace(':', ''))
                    ascii_data = raw_bytes.decode('euc-kr', errors='ignore')
                    ascii_data = ascii_data.replace('\x00', '').replace('\r', '').replace('\n', ' ').strip()

                    if "KR" not in ascii_data and "국고" not in ascii_data:
                        return

                    parsed_fields_list = parse_packet_from_ascii_clean(ascii_data)
                    if parsed_fields_list:
                        # IP/포트 정보 같이 출력
                        connection_info = f"[{src_ip}:{src_port} -> {dst_ip}:{dst_port}]"
                        for fields in parsed_fields_list:
                            now = time.strftime('%H:%M:%S')
                            output_line = now + ' ' + connection_info + ' ' + ' '.join(str(val) for val in fields)
                            print(output_line)

                except Exception as decode_error:
                    print(f"❌ decode error: {decode_error}")
    except Exception as e:
        print(f"❌ packet_callback error: {e}")

# === 실행 ===
if __name__ == "__main__":
    print("🧲 KBond 데이터 실시간 감지 시작 (IP 정보 포함)...")
    capture = pyshark.LiveCapture(interface=interface_number, display_filter='tcp')
    capture.apply_on_packets(packet_callback)
