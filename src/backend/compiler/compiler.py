#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compiler implementation for RebelDESK.

This module provides a compiler abstraction layer for compiling and executing code
in various programming languages.
"""

import os
import sys
import logging
import platform
import subprocess
import tempfile
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum

from PyQt5.QtCore import QProcess, QObject, pyqtSignal, pyqtSlot, QTimer

logger = logging.getLogger(__name__)

class CompilationStatus(Enum):
    """Enumeration of compilation status codes."""
    SUCCESS = 0
    COMPILATION_ERROR = 1
    EXECUTION_ERROR = 2
    TIMEOUT_ERROR = 3
    PROCESS_ERROR = 4
    UNSUPPORTED_LANGUAGE = 5
    FILE_NOT_FOUND = 6
    UNKNOWN_ERROR = 7


class CompilerManager(QObject):
    """
    Manages compilation and execution of code in various languages.
    
    This class provides a unified interface for compiling and executing code
    in different programming languages, abstracting away the details of
    specific compilers and interpreters.
    """
    
    # Signals
    compilation_started = pyqtSignal(str)  # language
    compilation_finished = pyqtSignal(str, int)  # language, status
    execution_started = pyqtSignal(str)  # language
    execution_finished = pyqtSignal(str, int)  # language, status
    output_received = pyqtSignal(str)  # output
    error_received = pyqtSignal(str)  # error
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CompilerManager.
        
        Args:
            config (dict, optional): Configuration settings.
        """
        super().__init__()
        
        self.config = config or {}
        self.processes: Dict[str, QProcess] = {}
        self.temp_files: List[str] = []
        
        # Default compiler/interpreter paths
        self.default_compilers = {
            'python': {
                'command': self._get_python_command(),
                'args': ['-u'],  # Unbuffered output
                'file_extensions': ['.py'],
                'needs_compilation': False,
            },
            'javascript': {
                'command': 'node',
                'args': [],
                'file_extensions': ['.js', '.jsx'],
                'needs_compilation': False,
            },
            'cpp': {
                'command': 'g++' if platform.system() != 'Windows' else 'cl',
                'args': ['-std=c++17'] if platform.system() != 'Windows' else ['/EHsc', '/std:c++17'],
                'file_extensions': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
                'needs_compilation': True,
                'output_extension': '.exe' if platform.system() == 'Windows' else '',
            },
            'java': {
                'command': 'javac',
                'args': [],
                'file_extensions': ['.java'],
                'needs_compilation': True,
                'output_extension': '.class',
                'execution_command': 'java',
                'execution_args': [],
            },
        }
        
        # Override with config if provided
        if 'compiler' in self.config:
            for language, settings in self.config.get('compiler', {}).items():
                if language in self.default_compilers:
                    self.default_compilers[language].update(settings)
        
        # Initialize processes
        for language in self.default_compilers:
            self.processes[language] = QProcess()
            self.processes[language].setProcessChannelMode(QProcess.MergedChannels)
    
    def _get_python_command(self) -> str:
        """
        Get the appropriate Python command for the current environment.
        
        Returns:
            str: The Python command.
        """
        # Check if we're running in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # We're in a virtual environment
            if platform.system() == 'Windows':
                return os.path.join(sys.prefix, 'Scripts', 'python.exe')
            else:
                return os.path.join(sys.prefix, 'bin', 'python')
        else:
            # Use system Python
            return 'python' if platform.system() == 'Windows' else 'python3'
    
    def get_supported_languages(self) -> List[str]:
        """
        Get a list of supported programming languages.
        
        Returns:
            list: List of supported language names.
        """
        return list(self.default_compilers.keys())
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect the programming language of a file based on its extension.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            str: The detected language, or None if not recognized.
        """
        ext = Path(file_path).suffix.lower()
        
        for language, settings in self.default_compilers.items():
            if ext in settings.get('file_extensions', []):
                return language
        
        return None
    
    def compile_file(self, file_path: str, output_path: Optional[str] = None,
                    args: Optional[List[str]] = None) -> Tuple[CompilationStatus, str]:
        """
        Compile a source file.
        
        Args:
            file_path (str): Path to the source file.
            output_path (str, optional): Path for the output file.
            args (list, optional): Additional compiler arguments.
            
        Returns:
            tuple: (status, message)
                status (CompilationStatus): The compilation status.
                message (str): Output or error message.
        """
        if not os.path.exists(file_path):
            return CompilationStatus.FILE_NOT_FOUND, f"File not found: {file_path}"
        
        # Detect language
        language = self.detect_language(file_path)
        if not language:
            return CompilationStatus.UNSUPPORTED_LANGUAGE, f"Unsupported file type: {file_path}"
        
        # Get compiler settings
        compiler_settings = self.default_compilers.get(language, {})
        
        # Check if compilation is needed
        if not compiler_settings.get('needs_compilation', False):
            return CompilationStatus.SUCCESS, f"No compilation needed for {language}"
        
        # Prepare output path
        if not output_path:
            output_ext = compiler_settings.get('output_extension', '')
            output_path = str(Path(file_path).with_suffix(output_ext))
        
        # Prepare compilation command
        command = compiler_settings.get('command', '')
        if not command:
            return CompilationStatus.UNSUPPORTED_LANGUAGE, f"No compiler configured for {language}"
        
        # Prepare arguments
        command_args = compiler_settings.get('args', []).copy()
        if args:
            command_args.extend(args)
        
        # Add input and output file paths
        if language == 'cpp':
            if platform.system() == 'Windows' and command == 'cl':
                # MSVC syntax
                command_args.extend(['/Fe:', output_path, file_path])
            else:
                # GCC/Clang syntax
                command_args.extend(['-o', output_path, file_path])
        elif language == 'java':
            # Java syntax
            command_args.append(file_path)
        
        # Emit signal
        self.compilation_started.emit(language)
        
        try:
            # Run the compilation process
            logger.info(f"Compiling {language} file: {file_path}")
            logger.debug(f"Compilation command: {command} {' '.join(command_args)}")
            
            process = subprocess.run(
                [command] + command_args,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Check if compilation was successful
            if process.returncode == 0:
                self.compilation_finished.emit(language, CompilationStatus.SUCCESS.value)
                return CompilationStatus.SUCCESS, f"Compilation successful: {output_path}"
            else:
                error_message = process.stderr or process.stdout
                self.compilation_finished.emit(language, CompilationStatus.COMPILATION_ERROR.value)
                return CompilationStatus.COMPILATION_ERROR, f"Compilation error:\n{error_message}"
                
        except Exception as e:
            logger.error(f"Error compiling {language} file: {str(e)}", exc_info=True)
            self.compilation_finished.emit(language, CompilationStatus.UNKNOWN_ERROR.value)
            return CompilationStatus.UNKNOWN_ERROR, f"Error: {str(e)}"
    
    def execute_file(self, file_path: str, args: Optional[List[str]] = None,
                    working_dir: Optional[str] = None, timeout: Optional[int] = None) -> None:
        """
        Execute a file asynchronously.
        
        This method starts the execution process and returns immediately.
        The execution results are emitted through signals.
        
        Args:
            file_path (str): Path to the file to execute.
            args (list, optional): Command-line arguments for the program.
            working_dir (str, optional): Working directory for the execution.
            timeout (int, optional): Timeout in milliseconds.
        """
        if not os.path.exists(file_path):
            self.error_received.emit(f"File not found: {file_path}")
            self.execution_finished.emit("unknown", CompilationStatus.FILE_NOT_FOUND.value)
            return
        
        # Detect language
        language = self.detect_language(file_path)
        if not language:
            self.error_received.emit(f"Unsupported file type: {file_path}")
            self.execution_finished.emit("unknown", CompilationStatus.UNSUPPORTED_LANGUAGE.value)
            return
        
        # Get compiler settings
        compiler_settings = self.default_compilers.get(language, {})
        
        # Check if compilation is needed
        if compiler_settings.get('needs_compilation', False):
            # Compile the file first
            status, message = self.compile_file(file_path)
            if status != CompilationStatus.SUCCESS:
                self.error_received.emit(message)
                self.execution_finished.emit(language, status.value)
                return
            
            # For compiled languages, we need to execute the compiled output
            if language == 'cpp':
                output_ext = compiler_settings.get('output_extension', '')
                file_path = str(Path(file_path).with_suffix(output_ext))
            elif language == 'java':
                # For Java, we need to use the java command with the class name
                class_name = Path(file_path).stem
                file_path = class_name
        
        # Prepare execution command
        if compiler_settings.get('needs_compilation', False) and 'execution_command' in compiler_settings:
            command = compiler_settings.get('execution_command', '')
            command_args = compiler_settings.get('execution_args', []).copy()
            command_args.append(file_path)
        else:
            command = compiler_settings.get('command', '')
            command_args = compiler_settings.get('args', []).copy()
            command_args.append(file_path)
        
        # Add user arguments
        if args:
            command_args.extend(args)
        
        # Set working directory
        if not working_dir:
            working_dir = str(Path(file_path).parent)
        
        # Get the process for this language
        process = self.processes.get(language)
        if not process:
            process = QProcess()
            self.processes[language] = process
        
        # Connect signals
        process.readyReadStandardOutput.connect(
            lambda: self._handle_process_output(process, language)
        )
        process.readyReadStandardError.connect(
            lambda: self._handle_process_error(process, language)
        )
        process.finished.connect(
            lambda exit_code, exit_status: self._handle_process_finished(
                language, exit_code, exit_status
            )
        )
        
        # Set working directory
        process.setWorkingDirectory(working_dir)
        
        # Set up environment
        env = QProcess.systemEnvironment()
        process.setProcessEnvironment(env)
        
        # Emit signal
        self.execution_started.emit(language)
        
        # Start the process
        logger.info(f"Executing {language} file: {file_path}")
        logger.debug(f"Execution command: {command} {' '.join(command_args)}")
        
        process.start(command, command_args)
        
        # Set timeout if provided
        if timeout:
            QTimer.singleShot(timeout, lambda: self._handle_timeout(process, language))
    
    def execute_code(self, code: str, language: str, args: Optional[List[str]] = None,
                    working_dir: Optional[str] = None, timeout: Optional[int] = None) -> None:
        """
        Execute code directly (without a file).
        
        This method creates a temporary file with the code, executes it,
        and then deletes the temporary file.
        
        Args:
            code (str): The code to execute.
            language (str): The programming language of the code.
            args (list, optional): Command-line arguments for the program.
            working_dir (str, optional): Working directory for the execution.
            timeout (int, optional): Timeout in milliseconds.
        """
        if language not in self.default_compilers:
            self.error_received.emit(f"Unsupported language: {language}")
            self.execution_finished.emit(language, CompilationStatus.UNSUPPORTED_LANGUAGE.value)
            return
        
        # Get file extension for the language
        compiler_settings = self.default_compilers.get(language, {})
        file_extensions = compiler_settings.get('file_extensions', [])
        if not file_extensions:
            self.error_received.emit(f"No file extension defined for {language}")
            self.execution_finished.emit(language, CompilationStatus.UNSUPPORTED_LANGUAGE.value)
            return
        
        # Create a temporary file
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extensions[0], delete=False) as temp_file:
                temp_file.write(code.encode('utf-8'))
                temp_path = temp_file.name
            
            # Add to list of temp files to clean up later
            self.temp_files.append(temp_path)
            
            # Execute the temporary file
            self.execute_file(temp_path, args, working_dir, timeout)
            
        except Exception as e:
            logger.error(f"Error creating temporary file: {str(e)}", exc_info=True)
            self.error_received.emit(f"Error: {str(e)}")
            self.execution_finished.emit(language, CompilationStatus.UNKNOWN_ERROR.value)
    
    def stop_execution(self, language: Optional[str] = None) -> None:
        """
        Stop the execution of a process.
        
        Args:
            language (str, optional): The language to stop. If None, stops all processes.
        """
        if language:
            # Stop specific language
            process = self.processes.get(language)
            if process and process.state() != QProcess.NotRunning:
                process.terminate()
                # Give it some time to terminate gracefully
                if not process.waitForFinished(3000):  # 3 seconds
                    process.kill()  # Force kill if it doesn't terminate
                logger.info(f"Stopped {language} process")
        else:
            # Stop all processes
            for lang, process in self.processes.items():
                if process.state() != QProcess.NotRunning:
                    process.terminate()
                    # Give it some time to terminate gracefully
                    if not process.waitForFinished(3000):  # 3 seconds
                        process.kill()  # Force kill if it doesn't terminate
                    logger.info(f"Stopped {lang} process")
    
    def _handle_process_output(self, process: QProcess, language: str) -> None:
        """
        Handle process standard output.
        
        Args:
            process (QProcess): The process.
            language (str): The programming language.
        """
        output = process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self.output_received.emit(output)
    
    def _handle_process_error(self, process: QProcess, language: str) -> None:
        """
        Handle process standard error.
        
        Args:
            process (QProcess): The process.
            language (str): The programming language.
        """
        error = process.readAllStandardError().data().decode('utf-8', errors='replace')
        self.error_received.emit(error)
    
    def _handle_process_finished(self, language: str, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        """
        Handle process finished event.
        
        Args:
            language (str): The programming language.
            exit_code (int): The exit code.
            exit_status (QProcess.ExitStatus): The exit status.
        """
        if exit_status == QProcess.NormalExit and exit_code == 0:
            status = CompilationStatus.SUCCESS
        else:
            status = CompilationStatus.EXECUTION_ERROR
        
        self.execution_finished.emit(language, status.value)
        logger.info(f"{language} process finished with exit code {exit_code}")
        
        # Clean up temporary files
        self._cleanup_temp_files()
    
    def _handle_timeout(self, process: QProcess, language: str) -> None:
        """
        Handle process timeout.
        
        Args:
            process (QProcess): The process.
            language (str): The programming language.
        """
        if process.state() != QProcess.NotRunning:
            process.terminate()
            # Give it some time to terminate gracefully
            if not process.waitForFinished(3000):  # 3 seconds
                process.kill()  # Force kill if it doesn't terminate
            
            self.error_received.emit(f"Process timed out")
            self.execution_finished.emit(language, CompilationStatus.TIMEOUT_ERROR.value)
            logger.warning(f"{language} process timed out")
    
    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        for temp_file in self.temp_files[:]:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                self.temp_files.remove(temp_file)
            except Exception as e:
                logger.error(f"Error deleting temporary file {temp_file}: {str(e)}", exc_info=True)
    
    def get_build_configurations(self, language: str) -> List[Dict[str, Any]]:
        """
        Get build configurations for a language.
        
        Args:
            language (str): The programming language.
            
        Returns:
            list: List of build configurations.
        """
        # Get configurations from config
        configs = self.config.get('compiler', {}).get(language, {}).get('configurations', [])
        
        # If no configurations are defined, create default ones
        if not configs:
            if language == 'cpp':
                configs = [
                    {
                        'name': 'Debug',
                        'args': ['-g', '-O0', '-Wall', '-Wextra'] if platform.system() != 'Windows' else ['/Od', '/Zi', '/W4'],
                        'description': 'Debug build with no optimization',
                    },
                    {
                        'name': 'Release',
                        'args': ['-O3'] if platform.system() != 'Windows' else ['/O2'],
                        'description': 'Release build with optimization',
                    },
                ]
            elif language == 'java':
                configs = [
                    {
                        'name': 'Debug',
                        'args': ['-g', '-Xlint:all'],
                        'description': 'Debug build with all warnings enabled',
                    },
                    {
                        'name': 'Release',
                        'args': ['-Xlint:none'],
                        'description': 'Release build with no warnings',
                    },
                ]
        
        return configs
    
    def set_build_configuration(self, language: str, config_name: str) -> bool:
        """
        Set the active build configuration for a language.
        
        Args:
            language (str): The programming language.
            config_name (str): The name of the configuration to set.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Get configurations
        configs = self.get_build_configurations(language)
        
        # Find the configuration with the given name
        for config in configs:
            if config.get('name') == config_name:
                # Update the default compiler settings
                if language in self.default_compilers:
                    self.default_compilers[language]['args'] = config.get('args', [])
                
                logger.info(f"Set {language} build configuration to {config_name}")
                return True
        
        logger.warning(f"Build configuration {config_name} not found for {language}")
        return False
    
    def create_build_configuration(self, language: str, name: str, args: List[str],
                                description: str = "") -> bool:
        """
        Create a new build configuration for a language.
        
        Args:
            language (str): The programming language.
            name (str): The name of the configuration.
            args (list): The compiler arguments.
            description (str, optional): A description of the configuration.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Get configurations
        configs = self.get_build_configurations(language)
        
        # Check if a configuration with this name already exists
        for config in configs:
            if config.get('name') == name:
                logger.warning(f"Build configuration {name} already exists for {language}")
                return False
        
        # Create new configuration
        new_config = {
            'name': name,
            'args': args,
            'description': description,
        }
        
        # Add to configurations
        configs.append(new_config)
        
        # Update config
        if 'compiler' not in self.config:
            self.config['compiler'] = {}
        if language not in self.config['compiler']:
            self.config['compiler'][language] = {}
        self.config['compiler'][language]['configurations'] = configs
        
        logger.info(f"Created {language} build configuration: {name}")
        return True
    
    def delete_build_configuration(self, language: str, name: str) -> bool:
        """
        Delete a build configuration for a language.
        
        Args:
            language (str): The programming language.
            name (str): The name of the configuration to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Get configurations
        configs = self.get_build_configurations(language)
        
        # Find the configuration with the given name
        for i, config in enumerate(configs):
            if config.get('name') == name:
                # Remove the configuration
                configs.pop(i)
                
                # Update config
                if 'compiler' in self.config and language in self.config['compiler']:
                    self.config['compiler'][language]['configurations'] = configs
                
                logger.info(f"Deleted {language} build configuration: {name}")
                return True
        
        logger.warning(f"Build configuration {name} not found for {language}")
        return False
    
    def get_compiler_path(self, language: str) -> str:
        """
        Get the path to the compiler/interpreter for a language.
        
        Args:
            language (str): The programming language.
            
        Returns:
            str: The path to the compiler/interpreter.
        """
        return self.default_compilers.get(language, {}).get('command', '')
    
    def set_compiler_path(self, language: str, path: str) -> bool:
        """
        Set the path to the compiler/interpreter for a language.
        
        Args:
            language (str): The programming language.
            path (str): The path to the compiler/interpreter.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if language in self.default_compilers:
            self.default_compilers[language]['command'] = path
            
            # Update config
            if 'compiler' not in self.config:
                self.config['compiler'] = {}
            if language not in self.config['compiler']:
                self.config['compiler'][language] = {}
            self.config['compiler'][language]['command'] = path
            
            logger.info(f"Set {language} compiler path to {path}")
            return True
        
        logger.warning(f"Language {language} not supported")
        return False
    
    def __del__(self):
        """Clean up resources when the object is deleted."""
        # Stop all processes
        self.stop_execution()
        
        # Clean up temporary files
        self._cleanup_temp_files()
