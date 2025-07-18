import unittest
import os
import json
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from app.database import SessionLocal, Base
from app.models import Competitor, AnalysisResult, Conversation
from app.competitor_analyzer import CompetitorAnalyzer
from app.learning_agent import LearningAgent
from app.wordpress_manager import WordPressManager
from wordpress_xmlrpc.methods.posts import NewPost

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

    def test_03_learning_agent(self):
        """Test the learning agent module."""
        agent = LearningAgent()
        agent.db = self.db

        agent.chat = lambda user_input, model="llama3", image_data=None: "چطوری رفیق؟"
        response = agent.chat("سلام")
        self.assertIn("رفیق", response)

    @patch('app.wordpress_manager.Client')
    def test_04_wordpress_manager(self, MockClient):
        """Test the WordPress manager module with a mocked client."""
        os.environ["WP_URL"] = "http://dummy.com/xmlrpc.php"
        os.environ["WP_USERNAME"] = "user"
        os.environ["WP_PASSWORD"] = "pass"

        # Configure the mock instance
        mock_instance = MockClient.return_value
        def call_side_effect(method):
            if isinstance(method, NewPost):
                return 1
            else: # For UploadFile
                return {'id': 1, 'url': 'http://dummy.com/image.jpg'}
        mock_instance.call.side_effect = call_side_effect

        manager = WordPressManager()

        product_id = manager.create_product("تست", "توضیحات", "100")
        self.assertEqual(product_id, 1)
        # Verify that the client was called
        self.assertTrue(mock_instance.call.called)


if __name__ == "__main__":
    unittest.main()
