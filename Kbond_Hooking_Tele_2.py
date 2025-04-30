import os
import logging
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === 설정 ===
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or "7907329062:AAGg3_rd5kwYR5ii60coPC6mgd9iYN5C2Wo"
CSV_PATH = os.path.join(os.getcwd(), 'kbond_log.csv')
CHECK_INTERVAL = 2  # 초 단위

# 로깅 설정
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 채팅별 구독 정보: {chat_id: {code: last_index}}
subscriptions = {}

# === /start 명령: 봇 소개 및 사용법 안내 ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "안녕하세요! KBond 실시간 모니터링 봇입니다.\n"
        "• 구독 시작: /info <종목코드> (예: /info KR103501GE64)\n"
        "• 구독 종료: /end\n"
        "예시) /info KR103501GCC0"
    )

# === /info 명령: 구독 시작 ===
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text('사용법: /info 종목코드 (예: /info KR103501GCC0)')
        return
    code = context.args[0].upper()

    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    except FileNotFoundError:
        await update.message.reply_text('로그 파일이 없습니다.')
        return

    df_code = df[df['종목코드'] == code]
    last_idx = df_code.index.max() if not df_code.empty else -1
    subscriptions.setdefault(chat_id, {})[code] = last_idx
    await update.message.reply_text(f'✅ {code} 구독 시작되었습니다. (/end 로 종료)')
    logger.info(f'Chat {chat_id} subscribed to {code} starting at index {last_idx}')

# === /end 명령: 모든 구독 종료 ===
async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in subscriptions:
        subscriptions.pop(chat_id)
        await update.message.reply_text('🔔 모든 구독이 종료되었습니다.')
        logger.info(f'Chat {chat_id} unsubscribed all')
    else:
        await update.message.reply_text('현재 구독 중인 종목이 없습니다.')

# === 주기적 업데이트 확인 ===
async def check_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not os.path.exists(CSV_PATH):
            return
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        for chat_id, codes in subscriptions.items():
            for code, last_idx in codes.items():
                df_code = df[df['종목코드'] == code]
                if df_code.empty:
                    continue
                new_df = df_code[df_code.index > last_idx]
                if new_df.empty:
                    continue
                for _, row in new_df.iterrows():
                    # 종목명은 raw split 컬럼의 col7
                    name = row.get('col7', '') if 'col7' in row else ''
                    msg = (
                        f"[{row['시간']}] {code} ({name})\n"
                        f"상품: {row['상품구분']} | 수익률: {row['수익률']} | 민평: {row['민평']} | 대비: {row['대비']}bp\n"
                        f"수량: {row['수량']} | 만기: {row['만기']} | 구분: {row['구분']} | 판매자: {row['판매자']}\n"
                        f"화면번호: {row.get('화면', '')}"
                    )
                    await context.bot.send_message(chat_id=chat_id, text=msg)
                    logger.info(f'Sent update to {chat_id} for {code}')
                subscriptions[chat_id][code] = new_df.index.max()
    except Exception as e:
        logger.error(f'Error in check_updates: {e}')

# === 봇 실행 함수 ===
def main() -> None:
    print('▶️ TOKEN =', TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('end', end_command))
    # JobQueue 설정 (python-telegram-bot[job-queue] 설치 필요)
    jq = app.job_queue
    jq.run_repeating(check_updates, interval=CHECK_INTERVAL, first=CHECK_INTERVAL)
    logger.info('텔레그램 봇 시작 (구독 기능 포함)')
    app.run_polling()

if __name__ == '__main__':
    main()
