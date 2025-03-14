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
                    'local_path': ''
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
    def test_get_completions(self, mock_model_class, mock_tokenizer_class, mock_no_grad):
        """Test getting completions with a loaded model."""
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
        self.assertEqual(completions[0]['provider'], 'transformer')


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
        
        self.mock_jedi = self.jedi_patcher.start()
        self.mock_transformer = self.transformer_patcher.start()
        
        # Mock provider instances
        self.mock_jedi_instance = MagicMock()
        self.mock_transformer_instance = MagicMock()
        
        self.mock_jedi.return_value = self.mock_jedi_instance
        self.mock_transformer.return_value = self.mock_transformer_instance
        
        # Create manager
        self.manager = CodeCompletionManager(self.config)
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.jedi_patcher.stop()
        self.transformer_patcher.stop()
        
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.manager.config, self.config)
        self.assertTrue(self.manager.enabled)
        self.assertEqual(self.manager.suggestion_delay, 0.3)
        self.assertEqual(self.manager.max_suggestions, 5)
        
        # Check providers
        self.assertEqual(len(self.manager.providers), 2)
        self.assertIs(self.manager.providers[0], self.mock_jedi_instance)
        self.assertIs(self.manager.providers[1], self.mock_transformer_instance)
        
    def test_get_completions(self):
        """Test getting completions from all providers."""
        # Mock provider completions
        self.mock_jedi_instance.get_completions.return_value = [
            {'text': 'jedi1', 'provider': 'jedi'},
            {'text': 'jedi2', 'provider': 'jedi'}
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
        self.assertEqual(completions[2]['text'], 'transformer1')
        self.assertEqual(completions[3]['text'], 'transformer2')
        self.assertEqual(completions[4]['text'], 'transformer3')
        
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
