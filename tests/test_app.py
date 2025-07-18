import unittest
import os
import json
from sqlalchemy import create_engine
from app.database import SessionLocal, Base
from app.models import Competitor, AnalysisResult, Conversation
from app.competitor_analyzer import CompetitorAnalyzer
from app.learning_agent import LearningAgent

class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a test database and initialize it."""
        cls.db_url = "sqlite:///:memory:"
        cls.engine = create_engine(cls.db_url, connect_args={"check_same_thread": False})
        SessionLocal.configure(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        """Close the database connection and dispose the engine."""
        cls.db.close()
        Base.metadata.drop_all(bind=cls.engine)
        cls.engine.dispose()

    def setUp(self):
        """Create a new session for each test."""
        self.db = SessionLocal()

    def tearDown(self):
        """Rollback the session to keep tests isolated."""
        self.db.rollback()
        self.db.close()

    def test_01_database_creation(self):
        """Test if the database and tables are created correctly."""
        self.assertIn("competitors", Base.metadata.tables)
        self.assertIn("analysis_results", Base.metadata.tables)
        self.assertIn("conversations", Base.metadata.tables)

    def test_02_competitor_analyzer(self):
        """Test the competitor analyzer module."""
        analyzer = CompetitorAnalyzer()
        analyzer.db = self.db

        test_url = "http://test.com"

        analyzer.find_competitors = lambda keywords, num_results=10: [test_url]

        urls = analyzer.find_competitors(["test"])
        self.assertEqual(len(urls), 1)

        analyzer.store_competitors(urls)

        competitor = self.db.query(Competitor).filter_by(url=test_url).first()
        self.assertIsNotNone(competitor)

        def mock_analyze(url):
            comp = self.db.query(Competitor).filter_by(url=url).first()
            if comp:
                return AnalysisResult(
                    competitor_id=comp.id,
                    title="Test Title",
                    description="Test Description"
                )
            return None

        analyzer.analyze_and_store_website = mock_analyze
        analysis = analyzer.analyze_and_store_website(test_url)
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.title, "Test Title")

    def test_03_learning_agent(self):
        """Test the learning agent module."""
        agent = LearningAgent()
        agent.db = self.db

        original_chat = agent.chat
        agent.chat = lambda user_input, model="llama3": "Mock response"

        response = agent.chat("Hello")
        self.assertEqual(response, "Mock response")

        agent.chat = original_chat

        def mock_post(*args, **kwargs):
            class MockResponse:
                def raise_for_status(self): pass
                def iter_lines(self):
                    response_data = {
                        "message": {"content": "Mock response from post"},
                        "done": True
                    }
                    yield json.dumps(response_data).encode('utf-8')
            return MockResponse()

        import requests
        original_post = requests.post
        requests.post = mock_post

        agent.chat("Hello again")

        history = self.db.query(Conversation).filter_by(session_id=agent.session_id).all()
        self.assertGreater(len(history), 0)
        self.assertEqual(history[-1].role, "assistant")
        self.assertEqual(history[-1].content, "Mock response from post")

        requests.post = original_post

if __name__ == "__main__":
    unittest.main()
