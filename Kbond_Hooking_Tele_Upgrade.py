import os
import re
import time
import string
import threading
import logging
import asyncio
import requests

import pyshark
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === 설정 ===
# 토큰 아이디 입력 (안해도 상관없음)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or "7907329062:AAGg3_rd5kwYR5ii60coPC6mgd9iYN5C2Wo"
kbond_ip    = '58.123.191.140' # 140 ~ 142 대역대로 가끔 바뀜.
kbond_port  = '15201'
interface   = '4'  # 인터페이스 번호나 이름

# 구독 정보 구조: { chat_id: { 'codes': { code: thresh }, 'global': default_thresh } }
subscriptions: dict[int, dict] = {}
DEFAULT_THRESHOLD = 0  # 기본 임계치(0 bp) ## 임시 설정

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === 패킷 스니퍼 함수 ===
def packet_sniffer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bpf = f'tcp and host {kbond_ip} and port {kbond_port}'
    logger.info(f"Starting sniffer on {interface} with filter: {bpf}")
    capture = pyshark.LiveCapture(interface=interface, capture_filter=bpf)

    for pkt in capture.sniff_continuously():
        try:
            if not hasattr(pkt, 'tcp'):
                continue
            raw = getattr(pkt.tcp, 'payload', None)
            if not raw:
                continue
            data_bytes = bytes.fromhex(raw.replace(':', ''))
            raw_text = data_bytes.decode('euc-kr', errors='ignore')
            ascii_data = ''.join(ch for ch in raw_text if ch in string.printable or ord(ch) >= 0x80)
            if 'D1B' not in ascii_data:
                continue
            fields = [f.strip() for f in re.split(r'\s+', ascii_data) if f.strip()]
            input_id = fields[0]
            code = ''
            name = ''
            for i, token in enumerate(fields):
                if token.startswith('KR'):
                    code = token
                    if i+1 < len(fields): name = fields[i+1]
                    break
            category = '선물' if any('FUT' in f.upper() for f in fields) else '현물'
            side = fields[13] if len(fields) > 13 else ''
            yield_rt = fields[14] if len(fields) > 14 else ''
            mint = fields[10] if len(fields) > 10 else ''
            try:
                diff_bp = float(fields[15]) if len(fields) > 15 else 0
            except ValueError:
                continue
            qty = fields[16] if len(fields) > 16 else ''
            seller = fields[19] if len(fields) > 19 else ''

            msg = (
                f"종목(종목명): {code}({name}) | 매수/매도: {side} | 구분: {category} | "
                f"수익율: {yield_rt} | 민평: {mint} | 대비: {diff_bp} | 수량: {qty} | 판매자: {seller} " # | 입력 ID: {input_id}"
            )

            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            for chat_id, info in subscriptions.items():
                fltrs = info.get('filters', {})
                if code not in fltrs:
                    continue
                conf = fltrs[code]
                # 매수/매도 필터 매칭
                if conf['side'] and conf['side'] != side:
                    continue
                if abs(diff_bp) >= conf['thresh']:
                    payload = {"chat_id": chat_id, "text": msg}
                    resp = requests.post(url, json=payload)
                    if not resp.ok:
                        logger.error(f"Failed to send to {chat_id}: {resp.status_code}")
        except Exception:
            logger.exception("Error processing packet")

# === Telegram 명령어 핸들러 ===
async def start_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "KBond 실시간 알림 봇\n"
        "/info <종목코드> <임계치> [매수/매도] - 예: /info KR123456 2.5 매도\n"
        "/threshold <bp> - 전역 임계치 설정\n"
        "/end - 모든 구독 해제"
    )

async def info_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = ctx.args
    if len(args) < 2:
        return await update.message.reply_text("사용법: /info 종목코드 임계치 [매수/매도]")
    code = args[0].upper()
    try:
        thresh = float(args[1])
    except ValueError:
        return await update.message.reply_text("임계치는 숫자만 입력하세요.")
    side_arg = args[2] if len(args) > 2 else ''
    sub = subscriptions.setdefault(chat_id, {'filters': {}, 'global': DEFAULT_THRESHOLD})
    sub['filters'][code] = {'thresh': thresh, 'side': side_arg}
    await update.message.reply_text(
        f"✅ 구독됨: {code} (임계치 {thresh}bp, 매수/매도: {side_arg or '전체'})"
    )

async def threshold_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = ctx.args
    if not args:
        return await update.message.reply_text("사용법: /threshold bp")
    try:
        bp = float(args[0])
    except ValueError:
        return await update.message.reply_text("숫자만 입력하세요.")
    sub = subscriptions.setdefault(chat_id, {'filters': {}, 'global': DEFAULT_THRESHOLD})
    sub['global'] = bp
    await update.message.reply_text(f"✅ 전역 임계치 설정됨: {bp}bp")

async def end_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in subscriptions:
        subscriptions.pop(chat_id)
        await update.message.reply_text("🔕 모든 구독 해제됨")
    else:
        await update.message.reply_text("구독 중인 종목이 없습니다.")

# === 메인 실행 ===
def main():
    t = threading.Thread(target=packet_sniffer, daemon=True)
    t.start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("threshold", threshold_command))
    app.add_handler(CommandHandler("end", end_command))
    app.run_polling()

if __name__ == "__main__":
    main()
