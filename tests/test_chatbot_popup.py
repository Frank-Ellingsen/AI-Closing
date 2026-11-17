import unittest
import os
import re
from fastapi.testclient import TestClient
from src.api.api_server import app

class TestChatbotPopupIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_aurora_html_has_chatbot_components(self):
        path = os.path.join('app', 'index.html')
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check trigger button
        self.assertIn('id="chatbot-toggle-btn"', content)
        self.assertIn('toggleChatbot()', content)
        
        # Check drawer dialog
        self.assertIn('id="chatbot-drawer"', content)
        self.assertIn('id="chat-role-user"', content)
        self.assertIn('id="chat-role-admin"', content)
        self.assertIn('id="chatbot-quick-chips"', content)
        self.assertIn('id="chatbot-messages"', content)
        self.assertIn('id="chatbot-input"', content)
        
        # Check JS engine
        self.assertIn('function toggleChatbot()', content)
        self.assertIn('function setChatbotRole(', content)
        self.assertIn('function generateChatbotReply(', content)
        self.assertIn('function initChatbotGreeting()', content)

    def test_carbon_html_has_chatbot_components(self):
        path = 'index.html'
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check trigger button
        self.assertIn('id="chatbot-toggle-btn"', content)
        self.assertIn('toggleChatbot()', content)
        
        # Check drawer dialog
        self.assertIn('id="chatbot-drawer"', content)
        self.assertIn('id="chat-role-user"', content)
        self.assertIn('id="chat-role-admin"', content)
        self.assertIn('id="chatbot-quick-chips"', content)
        self.assertIn('id="chatbot-messages"', content)
        self.assertIn('id="chatbot-input"', content)
        
        # Check JS engine
        self.assertIn('function toggleChatbot()', content)
        self.assertIn('function setChatbotRole(', content)
        self.assertIn('function generateChatbotReply(', content)
        self.assertIn('function initChatbotGreeting()', content)

    def test_api_ui_endpoints_serve_chatbot(self):
        # Aurora UI
        r_aurora = self.client.get("/ui/aurora")
        self.assertEqual(r_aurora.status_code, 200)
        self.assertIn("chatbot-toggle-btn", r_aurora.text)
        self.assertIn("chatbot-drawer", r_aurora.text)

        # Carbon UI
        r_carbon = self.client.get("/ui/carbon")
        self.assertEqual(r_carbon.status_code, 200)
        self.assertIn("chatbot-toggle-btn", r_carbon.text)
        self.assertIn("chatbot-drawer", r_carbon.text)

    def test_chatbot_knowledge_coverage(self):
        # Test that both Aurora and Carbon have knowledge of key controller / superbruker topics
        for filepath in ['app/index.html', 'index.html']:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Controller topics
            self.assertIn('Bergen Marine', content)
            self.assertIn('1920', content)
            self.assertIn('agio', content.lower())
            self.assertIn('duckdb', content.lower())
            
            # Superbruker topics
            self.assertIn('Business Central', content)
            self.assertIn('Xledger', content)
            self.assertIn('Visma', content)
            self.assertIn('BAI2', content)
            self.assertIn('7799', content) # Øresavrunding konto

if __name__ == '__main__':
    unittest.main()
