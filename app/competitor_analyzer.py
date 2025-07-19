import requests
from bs4 import BeautifulSoup
from googlesearch import search
from app.database import SessionLocal
from app.models import Competitor, AnalysisResult

class CompetitorAnalyzer:
    def __init__(self):
        self.db = SessionLocal()

    def find_competitors(self, keywords, num_results=10):
        """
        Searches Google for keywords using the googlesearch library
        and returns a list of competitor URLs.
        """
        competitors = []
        print(f"Searching for competitors with keywords: {keywords}")
        try:
            # The search function is a generator, so we iterate through it
            # lang='fa' for Persian results
            for url in search(' '.join(keywords), num_results=num_results, lang='fa'):
                competitors.append(url)
        except Exception as e:
            print(f"An error occurred during Google search: {e}")

        unique_urls = list(set(competitors))
        self.store_competitors(unique_urls)
        return unique_urls

    def store_competitors(self, urls):
        """
        Stores new competitor URLs in the database.
        """
        if not urls:
            return
        for url in urls:
            exists = self.db.query(Competitor).filter(Competitor.url == url).first()
            if not exists:
                new_competitor = Competitor(url=url)
                self.db.add(new_competitor)
        self.db.commit()
        print(f"Stored {len(urls)} competitor URLs in the database.")

    def analyze_and_store_website(self, url):
        """
        Analyzes a website and stores the results in the database.
        """
        competitor = self.db.query(Competitor).filter(Competitor.url == url).first()
        if not competitor:
            print(f"Competitor with URL {url} not found in database.")
            return None

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string if soup.title else 'No title found'
            description_tag = soup.find('meta', attrs={'name': 'description'})
            description = description_tag['content'] if description_tag else 'No description found'
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            keywords = keywords_tag['content'] if keywords_tag else 'No keywords found'

            analysis = AnalysisResult(
                competitor_id=competitor.id,
                title=title,
                description=description,
                keywords=keywords,
            )
            self.db.add(analysis)
            self.db.commit()
            print(f"Stored analysis for {url}")
            return analysis
        except requests.exceptions.RequestException as e:
            print(f"Could not analyze {url}: {e}")
            return None

if __name__ == '__main__':
    analyzer = CompetitorAnalyzer()
    search_keywords = ["فروشگاه اینترنتی لوازم تحریر لوکس", "خرید آنلاین لوازم تحریر فانتزی"]
    competitor_urls = analyzer.find_competitors(search_keywords)

    if competitor_urls:
        print("\n--- Found Competitors ---")
        for c_url in competitor_urls:
            print(c_url)
            # Analyze and store the first 3 results
            if competitor_urls.index(c_url) < 3:
                analyzer.analyze_and_store_website(c_url)
    else:
        print("No competitors found.")
