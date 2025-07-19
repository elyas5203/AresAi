import unittest
from unittest.mock import patch, MagicMock
import os
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
        """Set up an in-memory SQLite database for testing."""
        cls.engine = create_engine("sqlite:///:memory:")
        SessionLocal.configure(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database."""
        cls.db.close()
        Base.metadata.drop_all(bind=cls.engine)

    def setUp(self):
        """Create a new session for each test."""
        self.db = SessionLocal()

    def tearDown(self):
        """Rollback the session to keep tests isolated."""
        self.db.rollback()
        self.db.close()

    def test_01_database_creation(self):
        """Test if tables are created."""
        self.assertIn("competitors", Base.metadata.tables)
        self.assertIn("analysis_results", Base.metadata.tables)

    @patch('app.competitor_analyzer.search')
    def test_02_competitor_analyzer(self, mock_search):
        """Test finding and storing competitors."""
        mock_search.return_value = ["http://example-competitor.com"]
        analyzer = CompetitorAnalyzer()
        analyzer.db = self.db

        urls = analyzer.find_competitors(["test keyword"])
        self.assertIn("http://example-competitor.com", urls)

        competitor = self.db.query(Competitor).filter_by(url="http://example-competitor.com").first()
        self.assertIsNotNone(competitor)

    @patch('app.learning_agent.requests.post')
    def test_03_learning_agent(self, mock_post):
        """Test the learning agent's chat and advice methods."""
        # Mock the response from Ollama API
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [
            '{"message": {"content": "سلام رفیق! "}, "done": false}'.encode('utf-8'),
            '{"message": {"content": "چه خبر؟"}, "done": true}'.encode('utf-8')
        ]
        mock_post.return_value = mock_response

        agent = LearningAgent()
        agent.db = self.db

        # Test chat
        response = agent.chat("سلام")
        self.assertEqual(response, "سلام رفیق! چه خبر؟")

        # Test get_advice with no analysis
        mock_post.return_value.iter_lines.return_value = ['{"message": {"content": "هیچ تحلیلی پیدا نکردم"}, "done": true}'.encode('utf-8')]
        advice_no_analysis = agent.get_advice([])
        self.assertIn("هیچ تحلیلی", advice_no_analysis)

        # Test get_advice with analysis results
        mock_post.return_value.iter_lines.return_value = ['{"message": {"content": "یک راهکار خوب اینه که..."}, "done": true}'.encode('utf-8')]
        comp = Competitor(url="http://test.com")
        self.db.add(comp)
        self.db.commit()
        analysis = AnalysisResult(competitor_id=comp.id, description="توضیحات تستی")
        self.db.add(analysis)
        self.db.commit()
        advice_with_analysis = agent.get_advice([analysis])
        self.assertIn("راهکار", advice_with_analysis)

    @patch('app.wordpress_manager.Client')
    def test_04_wordpress_manager(self, MockClient):
        """Test WordPress product creation."""
        os.environ["WP_URL"] = "http://dummy-wp.com/xmlrpc.php"
        os.environ["WP_USERNAME"] = "wp_user"
        os.environ["WP_PASSWORD"] = "wp_pass"

        mock_client_instance = MockClient.return_value
        mock_client_instance.call.return_value = 1 # Mock post ID

        manager = WordPressManager()
        product_id = manager.create_product("محصول تستی", "توضیحات محصول", "99000")
        self.assertEqual(product_id, 1)
        self.assertTrue(mock_client_instance.call.called)

if __name__ == "__main__":
    unittest.main()
