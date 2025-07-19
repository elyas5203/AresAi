import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from app.learning_agent import LearningAgent
from app.competitor_analyzer import CompetitorAnalyzer
from app.database import SessionLocal
from app.models import AnalysisResult
from app.content_publisher import ContentPublisher

load_dotenv()

# --- Load Environment Variables ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") # Your personal chat for interaction
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID") # The channel to post to

# --- Initialize Agents ---
agent = LearningAgent()
analyzer = CompetitorAnalyzer()
publisher = ContentPublisher(
    instagram_username=os.getenv("INSTAGRAM_USERNAME"),
    instagram_password=os.getenv("INSTAGRAM_PASSWORD"),
    telegram_bot_token=TELEGRAM_BOT_TOKEN,
    telegram_chat_id=TELEGRAM_CHANNEL_ID # Publisher posts to the channel
)

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message."""
    user_name = update.effective_user.first_name
    await update.message.reply_html(
        f"سلام {user_name}! من چی‌چی، دستیار هوشمندت هستم. چه کاری برات انجام بدم؟"
    )

async def get_advice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches the latest analysis and provides advice."""
    await update.message.reply_text("دارم آخرین تحلیل‌ها رو بررسی می‌کنم تا یه مشورتی بهت بدم...")
    db = SessionLocal()
    try:
        latest_analyses = db.query(AnalysisResult).order_by(AnalysisResult.analysis_date.desc()).limit(5).all()
        if not latest_analyses:
            await update.message.reply_text("هنوز تحلیلی ثبت نشده که بخوام مشاوره بدم. اول باید رقبا رو تحلیل کنی.")
            return
        advice = agent.get_advice(latest_analyses)
        await update.message.reply_text(f"💡 **مشاوره جدید:**\n\n{advice}")
    finally:
        db.close()

async def post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Posts a message to the designated channel."""
    if not TELEGRAM_CHANNEL_ID:
        await update.message.reply_text("آیدی کانال تلگرام در تنظیمات مشخص نشده. لطفاً فایل .env رو چک کن.")
        return

    message_to_post = ' '.join(context.args)
    if not message_to_post:
        await update.message.reply_text("چیزی برای پست کردن نگفتی! لطفاً بعد از دستور /post متنت رو بنویس. مثلاً: `/post این یک پست آزمایشی است`")
        return

    try:
        publisher.post_to_telegram(message_to_post)
        await update.message.reply_text("پست با موفقیت در کانال منتشر شد! ✅")
    except Exception as e:
        await update.message.reply_text(f"متاسفانه موقع پست کردن مشکلی پیش اومد: {e}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles regular text messages for chatting with the AI."""
    user_message = update.message.text
    ai_response = agent.chat(user_message)
    await update.message.reply_text(ai_response)

def run_bot():
    """Starts the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("!!! توکن بات تلگرام در فایل .env تنظیم نشده. برنامه متوقف شد.")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("advice", get_advice_command))
    application.add_handler(CommandHandler("post", post_to_channel))

    # Add message handler for general chat
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("... بات تلگرام با موفقیت اجرا شد")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
