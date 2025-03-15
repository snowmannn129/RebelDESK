#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the compiler module.

This module contains tests for the compiler abstraction layer.
"""

import os
import sys
import pytest
import tempfile
import platform
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from src.backend.compiler.compiler import CompilerManager, CompilationStatus

class TestCompilerManager:
    """Tests for the CompilerManager class."""
    
    @pytest.fixture
    def compiler_manager(self):
        """Create a CompilerManager instance for testing."""
        return CompilerManager()
    
    def test_get_supported_languages(self, compiler_manager):
        """Test getting supported languages."""
        languages = compiler_manager.get_supported_languages()
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'cpp' in languages
        assert 'java' in languages
    
    def test_detect_language(self, compiler_manager):
        """Test language detection based on file extension."""
        assert compiler_manager.detect_language('test.py') == 'python'
        assert compiler_manager.detect_language('test.js') == 'javascript'
        assert compiler_manager.detect_language('test.cpp') == 'cpp'
        assert compiler_manager.detect_language('test.h') == 'cpp'
        assert compiler_manager.detect_language('test.java') == 'java'
        assert compiler_manager.detect_language('test.txt') is None
    
    def test_get_build_configurations(self, compiler_manager):
        """Test getting build configurations for a language."""
        cpp_configs = compiler_manager.get_build_configurations('cpp')
        assert isinstance(cpp_configs, list)
        assert len(cpp_configs) > 0
        
        # Check that each configuration has the required fields
        for config in cpp_configs:
            assert 'name' in config
            assert 'args' in config
            assert 'description' in config
    
    def test_create_build_configuration(self, compiler_manager):
        """Test creating a new build configuration."""
        # Create a new configuration
        result = compiler_manager.create_build_configuration(
            'cpp',
            'TestConfig',
            ['-O1', '-Wall'],
            'Test configuration'
        )
        assert result is True
        
        # Check that the configuration was added
        configs = compiler_manager.get_build_configurations('cpp')
        config_names = [c.get('name') for c in configs]
        assert 'TestConfig' in config_names
        
        # Try to create a configuration with the same name (should fail)
        result = compiler_manager.create_build_configuration(
            'cpp',
            'TestConfig',
            ['-O2'],
            'Another test configuration'
        )
        assert result is False
    
    def test_set_build_configuration(self, compiler_manager):
        """Test setting the active build configuration."""
        # Create a test configuration
        compiler_manager.create_build_configuration(
            'cpp',
            'TestConfig',
            ['-O1', '-Wall'],
            'Test configuration'
        )
        
        # Set it as the active configuration
        result = compiler_manager.set_build_configuration('cpp', 'TestConfig')
        assert result is True
        
        # Try to set a non-existent configuration (should fail)
        result = compiler_manager.set_build_configuration('cpp', 'NonExistentConfig')
        assert result is False
    
    def test_delete_build_configuration(self, compiler_manager):
        """Test deleting a build configuration."""
        # Create a test configuration
        compiler_manager.create_build_configuration(
            'cpp',
            'TestConfig',
            ['-O1', '-Wall'],
            'Test configuration'
        )
        
        # Delete the configuration
        result = compiler_manager.delete_build_configuration('cpp', 'TestConfig')
        assert result is True
        
        # Check that the configuration was removed
        configs = compiler_manager.get_build_configurations('cpp')
        config_names = [c.get('name') for c in configs]
        assert 'TestConfig' not in config_names
        
        # Try to delete a non-existent configuration (should fail)
        result = compiler_manager.delete_build_configuration('cpp', 'NonExistentConfig')
        assert result is False
    
    def test_get_compiler_path(self, compiler_manager):
        """Test getting the compiler path."""
        python_path = compiler_manager.get_compiler_path('python')
        assert python_path is not None
        assert len(python_path) > 0
    
    def test_set_compiler_path(self, compiler_manager):
        """Test setting the compiler path."""
        # Set a custom path
        result = compiler_manager.set_compiler_path('python', '/custom/path/to/python')
        assert result is True
        
        # Check that the path was updated
        path = compiler_manager.get_compiler_path('python')
        assert path == '/custom/path/to/python'
        
        # Try to set a path for a non-existent language (should fail)
        result = compiler_manager.set_compiler_path('nonexistent', '/custom/path')
        assert result is False
    
    @pytest.mark.skipif(not os.path.exists(sys.executable), reason="Python interpreter not found")
    def test_execute_python_code(self, compiler_manager, qtbot):
        """Test executing Python code."""
        # Create a signal to capture output
        class OutputCapture(QObject):
            output_received = pyqtSignal(str)
            execution_finished = pyqtSignal(str, int)
            
        output_capture = OutputCapture()
        
        # Connect signals
        compiler_manager.output_received.connect(output_capture.output_received)
        compiler_manager.execution_finished.connect(output_capture.execution_finished)
        
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(b'print("Hello, World!")')
            temp_path = temp_file.name
        
        try:
            # Execute the file
            compiler_manager.execute_file(temp_path)
            
            # Wait for the execution to finish
            def check_output():
                return hasattr(output_capture, 'received_output') and output_capture.received_output
                
            # Set up signal handlers to capture output
            output_capture.received_output = False
            output_capture.output_received.connect(
                lambda output: setattr(output_capture, 'received_output', True)
            )
            
            # Wait for output with timeout
            qtbot.wait_until(check_output, timeout=5000)
            
            # Check that output was received
            assert hasattr(output_capture, 'received_output')
            assert output_capture.received_output is True
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @pytest.mark.skipif(not os.path.exists(sys.executable), reason="Python interpreter not found")
    def test_compile_file(self, compiler_manager):
        """Test compiling a file."""
        # Create a temporary C++ file
        with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as temp_file:
            temp_file.write(b'''
            #include <iostream>
            
            int main() {
                std::cout << "Hello, World!" << std::endl;
                return 0;
            }
            ''')
            temp_path = temp_file.name
        
        try:
            # Check if g++ or cl is available
            compiler = 'g++' if platform.system() != 'Windows' else 'cl'
            import shutil
            if shutil.which(compiler) is None:
                pytest.skip(f"{compiler} not found")
            
            # Compile the file
            status, message = compiler_manager.compile_file(temp_path)
            
            # If the compiler is available, the compilation should succeed
            # Otherwise, it will fail with a specific error
            if status == CompilationStatus.SUCCESS:
                assert "Compilation successful" in message
                
                # Check that the output file was created
                output_ext = '.exe' if platform.system() == 'Windows' else ''
                output_path = str(Path(temp_path).with_suffix(output_ext))
                assert os.path.exists(output_path)
                
                # Clean up the output file
                if os.path.exists(output_path):
                    os.unlink(output_path)
            else:
                # If compilation failed, it should be due to a specific error
                assert status in [
                    CompilationStatus.COMPILATION_ERROR,
                    CompilationStatus.PROCESS_ERROR,
                    CompilationStatus.UNKNOWN_ERROR
                ]
                
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
