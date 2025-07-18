import os
from telegram import Bot

class ContentPublisher:
    def __init__(self, instagram_username, instagram_password, telegram_bot_token, telegram_chat_id):
        self.instagram_username = instagram_username
        self.instagram_password = instagram_password
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_bot = Bot(token=self.telegram_bot_token)

    def post_to_instagram(self, image_path, caption):
        """
        This method is a placeholder for posting to Instagram.
        In a real-world scenario, you would use a library like instaloader or a private API.
        For this example, we will just print the action.
        """
        print(f"Posting to Instagram: {image_path} with caption: {caption}")
        # Here you would add the actual code to post to Instagram
        # For example, using a library like instaloader:
        # L = instaloader.Instaloader()
        # L.login(self.instagram_username, self.instagram_password)
        # L.upload_post(image_path, caption)
        return True

    def post_to_telegram(self, text):
        """
        Posts a message to a Telegram channel.
        """
        try:
            self.telegram_bot.send_message(chat_id=self.telegram_chat_id, text=text)
            print("Message sent to Telegram successfully.")
            return True
        except Exception as e:
            print(f"Error sending message to Telegram: {e}")
            return False

    def post_everywhere(self, image_path=None, text=""):
        """
        Posts content to all configured platforms.
        """
        if image_path:
            self.post_to_instagram(image_path, text)
        self.post_to_telegram(text)

if __name__ == '__main__':
    # Example usage:
    # Make sure to set these environment variables before running
    INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") # This is your channel ID

    publisher = ContentPublisher(
        instagram_username=INSTAGRAM_USERNAME,
        instagram_password=INSTAGRAM_PASSWORD,
        telegram_bot_token=TELEGRAM_BOT_TOKEN,
        telegram_chat_id=TELEGRAM_CHAT_ID
    )

    publisher.post_everywhere(image_path="path/to/your/image.jpg", text="Hello from my AI assistant!")
