"""
Go code runner for executing Go programs
"""

import subprocess
import os
from PyQt5.QtCore import QObject, pyqtSignal, QProcess, QSettings


class GoRunner(QObject):
    """Runner for executing Go code"""

    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    execution_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.process = None
        self.settings = QSettings()

    def run(self, file_path):
        """Run a Go file

        Args:
            file_path: Path to the .go file to run
        """
        if self.process and self.process.state() == QProcess.Running:
            self.error_received.emit("A process is already running.\n")
            return

        # Create process
        self.process = QProcess()
        self.process.setWorkingDirectory(os.path.dirname(file_path))

        # Set up environment variables
        env = self.process.processEnvironment()

        # Add custom GOPATH if configured
        gopath = self.settings.value("env/gopath", "")
        if gopath:
            env.insert("GOPATH", gopath)

        # Add custom GOROOT if configured
        goroot = self.settings.value("env/goroot", "")
        if goroot:
            env.insert("GOROOT", goroot)

        # Add extra environment variables
        extra_vars = self.settings.value("env/extra_vars", "")
        if extra_vars:
            for line in extra_vars.split('\n'):
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    env.insert(key.strip(), value.strip())

        self.process.setProcessEnvironment(env)

        # Connect signals
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.process.errorOccurred.connect(self.handle_error)

        # Start the process
        self.output_received.emit(f"Running: {file_path}\n")
        self.output_received.emit("-" * 50 + "\n")

        # Get Go executable path (use custom if configured)
        go_path = self.settings.value("env/go_path", "go")
        if not go_path:
            go_path = "go"

        # Use 'go run' to compile and execute
        # Set unbuffered mode to support interactive input
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.start(go_path, ["run", os.path.basename(file_path)])

    def stop(self):
        """Stop the running process"""
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.output_received.emit("\n[Process terminated]\n")

    def handle_stdout(self):
        """Handle standard output"""
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('utf-8', errors='replace')
        self.output_received.emit(text)

    def handle_stderr(self):
        """Handle standard error"""
        data = self.process.readAllStandardError()
        text = bytes(data).decode('utf-8', errors='replace')
        self.error_received.emit(text)

    def handle_finished(self, exit_code, exit_status):
        """Handle process finished"""
        self.execution_finished.emit(exit_code)

    def handle_error(self, error):
        """Handle process errors"""
        error_messages = {
            QProcess.FailedToStart: "Failed to start Go. Make sure Go is installed and in your PATH.",
            QProcess.Crashed: "Process crashed.",
            QProcess.Timedout: "Process timed out.",
            QProcess.WriteError: "Write error.",
            QProcess.ReadError: "Read error.",
            QProcess.UnknownError: "Unknown error occurred."
        }

        message = error_messages.get(error, "Unknown error occurred.")
        self.error_received.emit(f"\nError: {message}\n")

    def write_input(self, text):
        """Write input to the running process"""
        if self.process and self.process.state() == QProcess.Running:
            # Always add exactly one newline (Scanln needs \n to read)
            text = text.rstrip('\n') + '\n'
            self.process.write(text.encode('utf-8'))
            self.process.waitForBytesWritten()
