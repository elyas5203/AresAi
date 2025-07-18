import requests
from bs4 import BeautifulSoup
from app.database import SessionLocal
from app.models import Competitor, AnalysisResult

class CompetitorAnalyzer:
    def __init__(self):
        self.db = SessionLocal()

    def find_competitors(self, keywords, num_results=10):
        """
        Searches Google for keywords and returns a list of competitor URLs.
        """
        competitors = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        for keyword in keywords:
            print(f"Searching for: {keyword}")
            try:
                response = requests.get(f"https://www.google.com/search?q={keyword}&num={num_results}", headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                for g in soup.find_all('div', class_='g'):
                    anchors = g.find_all('a')
                    if anchors:
                        link = anchors[0]['href']
                        if link.startswith('http'):
                            competitors.append(link)
            except requests.exceptions.RequestException as e:
                print(f"Error searching for {keyword}: {e}")

        unique_urls = list(set(competitors))
        self.store_competitors(unique_urls)
        return unique_urls

    def store_competitors(self, urls):
        """
        Stores new competitor URLs in the database.
        """
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
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
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

    def analyze_instagram_profile(self, username):
        """
        Placeholder for Instagram analysis.
        """
        print(f"Analyzing Instagram profile: {username}")
        return {"username": username, "status": "analysis not implemented"}

if __name__ == '__main__':
    analyzer = CompetitorAnalyzer()
    search_keywords = ["فروشگاه اینترنتی لوازم تحریر لوکس"]
    competitor_urls = analyzer.find_competitors(search_keywords)

    if competitor_urls:
        for url in competitor_urls[:3]: # Analyze and store top 3
            analyzer.analyze_and_store_website(url)
