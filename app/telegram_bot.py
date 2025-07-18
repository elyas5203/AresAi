import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from app.learning_agent import LearningAgent
from app.competitor_analyzer import CompetitorAnalyzer
from app.database import SessionLocal
from app.models import AnalysisResult

# It's better to manage one agent instance
agent = LearningAgent()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user_name = update.effective_user.first_name
    await update.message.reply_html(
        rf"سلام {user_name}! به دستیار کسب و کار خودت خوش اومدی.",
        reply_markup=None, # You can add a custom keyboard later
    )

async def get_advice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches the latest analysis and provides advice."""
    await update.message.reply_text("در حال تحلیل آخرین داده‌ها برای ارائه مشاوره...")

    db = SessionLocal()
    try:
        # Fetch recent analysis results from the database
        latest_analyses = db.query(AnalysisResult).order_by(AnalysisResult.analysis_date.desc()).limit(5).all()

        if not latest_analyses:
            await update.message.reply_text("هنوز هیچ تحلیلی برای ارائه مشاوره وجود ندارد. ابتدا رقبا را تحلیل کنید.")
            return

        # Use the learning agent to get advice
        advice = agent.get_advice(latest_analyses)
        await update.message.reply_text(f"💡 مشاوره:\n\n{advice}")

    finally:
        db.close()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles regular text messages and gets a response from the AI."""
    user_message = update.message.text

    # Get a response from the learning agent
    ai_response = agent.chat(user_message)

    await update.message.reply_text(ai_response)


def run_bot():
    """Starts the Telegram bot."""
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        print("Fatal: TELEGRAM_BOT_TOKEN environment variable not set.")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("advice", get_advice_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot is running...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    run_bot()
