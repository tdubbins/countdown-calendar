#!/usr/bin/env python3
"""
Unit tests for EmailService - Clean implementation
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.services.email_service import EmailService


class TestEmailService(unittest.TestCase):
    """Test cases for EmailService"""
    
    def test_generate_verification_token(self):
        """Test token generation creates valid UUID"""
        with patch('app.services.email_service.email_tokens_db.create') as mock_create:
            token = EmailService.generate_verification_token("test-user-id", "test@example.com")
            
            # Check token is UUID format
            self.assertEqual(len(token), 36)  # UUID length
            self.assertIn('-', token)  # UUID contains hyphens
            
            # Check database call was made
            mock_create.assert_called_once()
    
    def test_email_template_generation(self):
        """Test email template contains required elements"""
        from app.templates.email_templates import EmailTemplates
        
        template = EmailTemplates.verification_email("http://example.com/verify/123")
        
        self.assertIn('subject', template)
        self.assertIn('body', template)
        self.assertIn('http://example.com/verify/123', template['body'])
        self.assertIn('Countdown Calendar', template['subject'])


if __name__ == '__main__':
    unittest.main()