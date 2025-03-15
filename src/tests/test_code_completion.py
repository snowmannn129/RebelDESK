#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the AI Code Completion module.

This module contains tests for the code completion functionality.
"""

import os
import sys
import unittest
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.code_completion import (
    CompletionProvider,
    JediCompletionProvider,
    TransformerCompletionProvider,
    SnippetCompletionProvider,
    CodeCompletionManager,
    CompletionWidget
)
from src.utils.config_manager import ConfigManager

class TestCompletionProvider(unittest.TestCase):
    """Tests for the CompletionProvider base class."""
    
    def test_init(self):
        """Test initialization."""
        provider = CompletionProvider()
        self.assertEqual(provider.config, {})
        
        config = {'test': 'value'}
        provider = CompletionProvider(config)
        self.assertEqual(provider.config, config)
        
    def test_get_completions_not_implemented(self):
        """Test that get_completions raises NotImplementedError."""
        provider = CompletionProvider()
        with self.assertRaises(NotImplementedError):
            provider.get_completions("code", 0)


class TestJediCompletionProvider(unittest.TestCase):
    """Tests for the JediCompletionProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {'test': 'value'}
        self.provider = JediCompletionProvider(self.config)
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.provider.config, self.config)
        
    @patch('jedi.Script')
    def test_get_completions_python(self, mock_script):
        """Test getting completions for Python code."""
        # Mock Jedi completions
        mock_completion = MagicMock()
        mock_completion.name = 'test_completion'
        mock_completion.type = 'function'
        mock_completion.description = 'Test completion'
        mock_completion.docstring.return_value = 'Test docstring'
        
        mock_script.return_value.complete.return_value = [mock_completion]
        
        # Test
        completions = self.provider.get_completions("def test():\n    pass\n", 10, language='python')
        
        # Verify
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0]['text'], 'test_completion')
        self.assertEqual(completions[0]['type'], 'function')
        self.assertEqual(completions[0]['description'], 'Test completion')
        self.assertEqual(completions[0]['documentation'], 'Test docstring')
        self.assertEqual(completions[0]['provider'], 'jedi')
        
    def test_get_completions_non_python(self):
        """Test that no completions are returned for non-Python code."""
        completions = self.provider.get_completions("function test() {}", 10, language='javascript')
        self.assertEqual(completions, [])
        
    @patch('jedi.Script')
    def test_get_completions_exception(self, mock_script):
        """Test handling of exceptions."""
        mock_script.return_value.complete.side_effect = Exception("Test exception")
        
        # Test
        completions = self.provider.get_completions("def test():\n    pass\n", 10)
        
        # Verify
        self.assertEqual(completions, [])


class TestTransformerCompletionProvider(unittest.TestCase):
    """Tests for the TransformerCompletionProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock config
        self.config = {
            'ai': {
                'model': {
                    'type': 'local',
                    'local_path': '',
                    'api_endpoint': 'https://api.example.com/completions',
                    'api_key_env': 'TEST_API_KEY'
                },
                'context_lines': 5
            }
        }
        
        # Patch the _load_model_async method to prevent actual loading
        self.patcher = patch('src.ai.code_completion.TransformerCompletionProvider._load_model_async')
        self.mock_load = self.patcher.start()
        
        # Create provider
        self.provider = TransformerCompletionProvider(self.config)
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.provider.config, self.config)
        self.assertFalse(self.provider.model_loaded)
        self.assertIsNone(self.provider.model)
        self.assertIsNone(self.provider.tokenizer)
        self.assertEqual(self.provider.model_type, 'local')
        
    def test_is_model_loaded(self):
        """Test is_model_loaded method."""
        self.assertFalse(self.provider.is_model_loaded())
        
        self.provider.model_loaded = True
        self.assertTrue(self.provider.is_model_loaded())
        
    def test_get_completions_model_not_loaded(self):
        """Test that no completions are returned when model is not loaded."""
        completions = self.provider.get_completions("def test():\n    pass\n", 10)
        self.assertEqual(completions, [])
        
    @patch('torch.no_grad')
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModelForCausalLM')
    def test_get_local_completions(self, mock_model_class, mock_tokenizer_class, mock_no_grad):
        """Test getting completions with a loaded local model."""
        # Set model type to local
        self.provider.model_type = 'local'
        
        # Mock model and tokenizer
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        
        mock_model_class.from_pretrained.return_value = mock_model
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock generate method
        mock_outputs = [MagicMock()]
        mock_model.generate.return_value = mock_outputs
        
        # Mock tokenizer
        mock_inputs = MagicMock()
        mock_inputs['input_ids'] = MagicMock()
        mock_inputs['input_ids'].shape = [1, 5]
        mock_tokenizer.return_value = mock_inputs
        mock_inputs.to.return_value = mock_inputs
        
        # Mock decode
        mock_tokenizer.decode.return_value = "test completion"
        
        # Set model as loaded
        self.provider.model = mock_model
        self.provider.tokenizer = mock_tokenizer
        self.provider.model_loaded = True
        
        # Test
        completions = self.provider.get_completions("def test():\n    pass\n", 10)
        
        # Verify
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0]['text'], 'test completion')
        self.assertEqual(completions[0]['provider'], 'transformer-local')
        
    @patch('requests.post')
    def test_get_api_completions(self, mock_post):
        """Test getting completions with an API-based model."""
        # Set model type to api
        self.provider.model_type = 'api'
        self.provider.model_loaded = True
        
        # Mock environment variable
        with patch.dict(os.environ, {'TEST_API_KEY': 'test_key'}):
            # Mock API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [
                    {'text': 'api completion 1'},
                    {'text': 'api completion 2'}
                ]
            }
            mock_post.return_value = mock_response
            
            # Test
            completions = self.provider.get_completions("def test():\n    pass\n", 10)
            
            # Verify
            self.assertEqual(len(completions), 2)
            self.assertEqual(completions[0]['text'], 'api completion 1')
            self.assertEqual(completions[0]['provider'], 'transformer-api')
            self.assertEqual(completions[1]['text'], 'api completion 2')
            self.assertEqual(completions[1]['provider'], 'transformer-api')
            
            # Verify API call
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(args[0], 'https://api.example.com/completions')
            self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_key')
            
    @patch('requests.post')
    def test_get_api_completions_error(self, mock_post):
        """Test handling API errors."""
        # Set model type to api
        self.provider.model_type = 'api'
        self.provider.model_loaded = True
        
        # Mock environment variable
        with patch.dict(os.environ, {'TEST_API_KEY': 'test_key'}):
            # Mock API error
            mock_post.side_effect = Exception("API error")
            
            # Test
            completions = self.provider.get_completions("def test():\n    pass\n", 10)
            
            # Verify
            self.assertEqual(completions, [])
            
    @patch('requests.post')
    def test_get_api_completions_no_key(self, mock_post):
        """Test handling missing API key."""
        # Set model type to api
        self.provider.model_type = 'api'
        self.provider.model_loaded = True
        
        # Test without environment variable
        completions = self.provider.get_completions("def test():\n    pass\n", 10)
        
        # Verify
        self.assertEqual(completions, [])
        mock_post.assert_not_called()


class TestSnippetCompletionProvider(unittest.TestCase):
    """Tests for the SnippetCompletionProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock config with custom snippets
        self.config = {
            'ai': {
                'snippets': {
                    'python': [
                        {
                            'prefix': 'testfunc',
                            'body': 'def test_function():\n    pass',
                            'description': 'Test function'
                        }
                    ]
                }
            }
        }
        
        # Create provider
        self.provider = SnippetCompletionProvider(self.config)
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.provider.config, self.config)
        self.assertIn('python', self.provider.snippets)
        self.assertEqual(len(self.provider.snippets['python']), 1)
        self.assertEqual(self.provider.snippets['python'][0]['prefix'], 'testfunc')
        
    def test_load_default_snippets(self):
        """Test loading default snippets."""
        # Create provider with empty config
        provider = SnippetCompletionProvider({})
        
        # Verify default snippets were loaded
        self.assertIn('python', provider.snippets)
        self.assertIn('javascript', provider.snippets)
        self.assertTrue(len(provider.snippets['python']) > 0)
        self.assertTrue(len(provider.snippets['javascript']) > 0)
        
    def test_get_completions_matching(self):
        """Test getting completions that match the current word."""
        # Test with matching prefix
        completions = self.provider.get_completions("def test():\n    test", 18, language='python')
        
        # Verify
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0]['text'], 'testfunc')
        self.assertEqual(completions[0]['type'], 'snippet')
        self.assertEqual(completions[0]['provider'], 'snippet')
        
    def test_get_completions_no_match(self):
        """Test getting completions with no matching prefix."""
        # Test with non-matching prefix
        completions = self.provider.get_completions("def test():\n    xyz", 18, language='python')
        
        # Verify
        self.assertEqual(completions, [])
        
    def test_get_completions_language_detection(self):
        """Test language detection from file path."""
        # Test with Python file
        completions = self.provider.get_completions("test", 4, file_path='test.py')
        
        # Verify
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0]['text'], 'testfunc')
        
        # Test with JavaScript file
        provider = SnippetCompletionProvider({})  # Use default snippets
        completions = provider.get_completions("func", 4, file_path='test.js')
        
        # Verify
        self.assertTrue(any(c['text'] == 'function' for c in completions))


class TestCodeCompletionManager(unittest.TestCase):
    """Tests for the CodeCompletionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock config
        self.config = {
            'ai': {
                'enable': True,
                'suggestion_delay': 300,
                'max_suggestions': 5
            }
        }
        
        # Patch provider classes
        self.jedi_patcher = patch('src.ai.code_completion.JediCompletionProvider')
        self.transformer_patcher = patch('src.ai.code_completion.TransformerCompletionProvider')
        self.snippet_patcher = patch('src.ai.code_completion.SnippetCompletionProvider')
        
        self.mock_jedi = self.jedi_patcher.start()
        self.mock_transformer = self.transformer_patcher.start()
        self.mock_snippet = self.snippet_patcher.start()
        
        # Mock provider instances
        self.mock_jedi_instance = MagicMock()
        self.mock_transformer_instance = MagicMock()
        self.mock_snippet_instance = MagicMock()
        
        self.mock_jedi.return_value = self.mock_jedi_instance
        self.mock_transformer.return_value = self.mock_transformer_instance
        self.mock_snippet.return_value = self.mock_snippet_instance
        
        # Create manager
        self.manager = CodeCompletionManager(self.config)
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.jedi_patcher.stop()
        self.transformer_patcher.stop()
        self.snippet_patcher.stop()
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.manager.config, self.config)
        self.assertTrue(self.manager.enabled)
        self.assertEqual(self.manager.suggestion_delay, 0.3)
        self.assertEqual(self.manager.max_suggestions, 5)
        
        # Check providers
        self.assertEqual(len(self.manager.providers), 3)
        self.assertIs(self.manager.providers[0], self.mock_jedi_instance)
        self.assertIs(self.manager.providers[1], self.mock_snippet_instance)
        self.assertIs(self.manager.providers[2], self.mock_transformer_instance)
        
    def test_get_completions(self):
        """Test getting completions from all providers."""
        # Mock provider completions
        self.mock_jedi_instance.get_completions.return_value = [
            {'text': 'jedi1', 'provider': 'jedi'},
            {'text': 'jedi2', 'provider': 'jedi'}
        ]
        self.mock_snippet_instance.get_completions.return_value = [
            {'text': 'snippet1', 'provider': 'snippet'}
        ]
        self.mock_transformer_instance.get_completions.return_value = [
            {'text': 'transformer1', 'provider': 'transformer'},
            {'text': 'transformer2', 'provider': 'transformer'},
            {'text': 'transformer3', 'provider': 'transformer'}
        ]
        
        # Test
        completions = self.manager.get_completions("def test():\n    pass\n", 10)
        
        # Verify
        self.assertEqual(len(completions), 5)
        self.assertEqual(completions[0]['text'], 'jedi1')
        self.assertEqual(completions[1]['text'], 'jedi2')
        self.assertEqual(completions[2]['text'], 'snippet1')
        self.assertEqual(completions[3]['text'], 'transformer1')
        self.assertEqual(completions[4]['text'], 'transformer2')
        
    def test_get_completions_disabled(self):
        """Test that no completions are returned when disabled."""
        self.manager.enabled = False
        completions = self.manager.get_completions("def test():\n    pass\n", 10)
        self.assertEqual(completions, [])
        
    def test_set_enabled(self):
        """Test enabling and disabling completions."""
        self.assertTrue(self.manager.enabled)
        
        self.manager.set_enabled(False)
        self.assertFalse(self.manager.enabled)
        
        self.manager.set_enabled(True)
        self.assertTrue(self.manager.enabled)
        
    def test_update_config(self):
        """Test updating configuration."""
        new_config = {
            'ai': {
                'enable': False,
                'suggestion_delay': 500,
                'max_suggestions': 10
            }
        }
        
        self.manager.update_config(new_config)
        
        self.assertEqual(self.manager.config, new_config)
        self.assertFalse(self.manager.enabled)
        self.assertEqual(self.manager.suggestion_delay, 0.5)
        self.assertEqual(self.manager.max_suggestions, 10)


class TestCompletionWidget(unittest.TestCase):
    """Tests for the CompletionWidget class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock editor
        self.mock_editor = MagicMock()
        self.mock_editor.toPlainText.return_value = "def test():\n    pass\n"
        self.mock_editor.textCursor.return_value.position.return_value = 10
        self.mock_editor.current_file = "test.py"
        self.mock_editor.language = "python"
        
        # Mock completion manager
        self.mock_manager = MagicMock()
        self.mock_manager.enabled = True
        
        # Create widget
        self.widget = CompletionWidget(self.mock_editor, self.mock_manager)
        
    def test_init(self):
        """Test initialization."""
        self.assertIs(self.widget.editor, self.mock_editor)
        self.assertIs(self.widget.completion_manager, self.mock_manager)
        self.assertEqual(self.widget.current_completions, [])
        
    def test_request_completions(self):
        """Test requesting completions."""
        self.widget.request_completions()
        
        self.mock_manager.request_completions_async.assert_called_once_with(
            "def test():\n    pass\n", 10, "test.py", "python",
            self.widget._show_completions
        )
        
    def test_request_completions_disabled(self):
        """Test that no completions are requested when disabled."""
        self.mock_manager.enabled = False
        self.widget.request_completions()
        
        self.mock_manager.request_completions_async.assert_not_called()
        
    def test_show_completions(self):
        """Test showing completions."""
        completions = [
            {'text': 'test1', 'provider': 'jedi'},
            {'text': 'test2', 'provider': 'transformer'}
        ]
        
        self.widget._show_completions(completions)
        
        self.assertEqual(self.widget.current_completions, completions)
        
    def test_apply_completion(self):
        """Test applying a completion."""
        self.widget.current_completions = [
            {'text': 'test1', 'provider': 'jedi'},
            {'text': 'test2', 'provider': 'transformer'}
        ]
        
        self.widget.apply_completion(1)
        
        # This is just a placeholder test since the actual implementation
        # would insert the text into the editor
        pass
        
    def test_apply_completion_invalid_index(self):
        """Test applying a completion with an invalid index."""
        self.widget.current_completions = [
            {'text': 'test1', 'provider': 'jedi'}
        ]
        
        # Should not raise an exception
        self.widget.apply_completion(1)
        self.widget.apply_completion(-1)


if __name__ == '__main__':
    unittest.main()
