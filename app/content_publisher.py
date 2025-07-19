import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

class ContentPublisher:
    def __init__(self, instagram_username, instagram_password, telegram_bot_token, telegram_chat_id):
        self.instagram_username = instagram_username
        self.instagram_password = instagram_password
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        if self.telegram_bot_token:
            self.telegram_bot = Bot(token=self.telegram_bot_token)
        else:
            self.telegram_bot = None

    def post_to_instagram(self, image_path, caption):
        """
        Placeholder for posting to Instagram.
        """
        print(f"Posting to Instagram: {image_path} with caption: {caption}")
        # Actual Instagram posting logic would go here
        return True

    async def post_to_telegram_async(self, text):
        """
        Asynchronously posts a message to a Telegram channel.
        """
        if not self.telegram_bot or not self.telegram_chat_id:
            print("Telegram bot token or chat ID is not configured.")
            return False
        try:
            await self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=text)
            print("Message sent to Telegram successfully.")
            return True
        except Exception as e:
            print(f"Error sending message to Telegram: {e}")
            return False

    def post_to_telegram(self, text):
        """
        Synchronous wrapper for the async post method.
        """
        return asyncio.run(self.post_to_telegram_async(text))

    async def post_everywhere_async(self, image_path=None, text=""):
        """
        Asynchronously posts content to all configured platforms.
        """
        if image_path:
            self.post_to_instagram(image_path, text)
        await self.post_to_telegram_async(text)

    def post_everywhere(self, image_path=None, text=""):
        """
        Synchronous wrapper for posting everywhere.
        """
        asyncio.run(self.post_everywhere_async(image_path, text))


if __name__ == '__main__':
    # Example usage:
    publisher = ContentPublisher(
        instagram_username=os.getenv("INSTAGRAM_USERNAME"),
        instagram_password=os.getenv("INSTAGRAM_PASSWORD"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHANNEL_ID") # Note: Using channel ID for publishing
    )

    if publisher.telegram_bot:
        print("Testing Telegram publisher...")
        publisher.post_to_telegram("این یک پیام آزمایشی از طرف دستیار هوشمند است.")
    else:
        print("Telegram credentials not found in .env file.")
