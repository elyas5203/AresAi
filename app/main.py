import os
from python_dotenv import load_dotenv
from app.content_publisher import ContentPublisher
from app.competitor_analyzer import CompetitorAnalyzer
from app.learning_agent import LearningAgent

load_dotenv()

def main():
    """
    Main function to run the application.
    """
    # It is recommended to use environment variables for sensitive data
    INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "your_insta_username")
    INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD", "your_insta_password")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "your_telegram_token")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "your_telegram_chat_id")

    publisher = ContentPublisher(
        instagram_username=INSTAGRAM_USERNAME,
        instagram_password=INSTAGRAM_PASSWORD,
        telegram_bot_token=TELEGRAM_BOT_TOKEN,
        telegram_chat_id=TELEGRAM_CHAT_ID,
    )

    # Example of posting a message
    # In a real application, you would get this data from a web form or another source
    publisher.post_everywhere(text="This is a test post from my AI assistant!")

    analyzer = CompetitorAnalyzer()

    # 1. Find competitors
    # It's better to use more specific keywords for better results
    # For example: "خرید دفترچه یادداشت فانتزی"
    search_keywords = ["فروشگاه اینترنتی لوازم تحریر لوکس"]
    competitor_urls = analyzer.find_competitors(search_keywords)
    print("\nFound Competitors:")
    for url in competitor_urls:
        print(url)

    # 2. Analyze a competitor's website
    analysis_results = []
    if competitor_urls:
        for url in competitor_urls[:3]: # Analyze top 3
            analysis = analyzer.analyze_website(url)
            if analysis:
                analysis_results.append(analysis)

    # 3. Get advice from the learning agent
    agent = LearningAgent()
    advice = agent.get_advice(analysis_results)
    print("\n--- Business Advice ---")
    print(advice)

    # 4. Start a chat session
    print("\n--- Chat with AI Assistant ---")
    print("AI Assistant: Hello! How can I help you improve your business today?")
    while True:
        user_message = input("You: ")
        if user_message.lower() in ["exit", "quit"]:
            break

        ai_response = agent.chat(user_message)
        print(f"AI Assistant: {ai_response}")


if __name__ == "__main__":
    main()
