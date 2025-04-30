# 실시간이 아니라 물어볼때마다 알려주는거.
import os
import logging
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === 설정 ===
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or "7907329062:AAGg3_rd5kwYR5ii60coPC6mgd9iYN5C2Wo"
CSV_PATH = os.path.join(os.getcwd(), 'kbond_log.csv')

# 로깅
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === /info 명령 핸들러 ===
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("사용법: /info 종목코드 (예: /info KR103501GCC0)")
        return

    code = context.args[0].upper()
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    except FileNotFoundError:
        await update.message.reply_text("로그 파일이 없습니다.")
        return

    df_code = df[df['종목코드'] == code]
    if df_code.empty:
        await update.message.reply_text(f"[{code}] 데이터가 없습니다.")
        return

    latest = df_code.iloc[-1]
    msg = (
        f"[{latest['시간']}] {code} 정보\n"
        f"상품: {latest['상품구분']} | 수익률: {latest['수익률']} | 민평: {latest['민평']} | 대비: {latest['대비']}bp\n"
        f"수량: {latest['수량']} | 만기: {latest['만기']} | 구분: {latest['구분']} | 판매자: {latest['판매자']}\n"
        f"화면번호: {latest.get('화면', '')}"
    )
    await update.message.reply_text(msg)

# === 봇 구동 ===
def main() -> None:
    print("▶️ TOKEN =", TOKEN)  # 디버그: 올바른 토큰이 찍히는지 확인
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("info", info_command))
    logger.info("텔레그램 봇 시작")
    app.run_polling()

if __name__ == "__main__":
    main()
