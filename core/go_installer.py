"""
Go installer and manager for local installation
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class GoInstaller(QObject):
    """Manages Go installation and detection"""
    
    progress_updated = pyqtSignal(int, str)
    installation_finished = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.go_local_dir = os.path.join(self.app_dir, "go_local")
        self.go_version = "1.21.5"  # Latest stable version
        
    def detect_go(self):
        """Detect if Go is installed (system-wide or local)
        
        Returns:
            tuple: (is_installed, go_path, version)
        """
        # Check local installation first
        local_go = self.get_local_go_path()
        if local_go and os.path.exists(local_go):
            try:
                result = subprocess.run([local_go, "version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    return (True, local_go, version)
            except:
                pass
        
        # Check system installation
        try:
            result = subprocess.run(["go", "version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                return (True, "go", version)
        except:
            pass
        
        return (False, None, None)
    
    def get_local_go_path(self):
        """Get path to local Go executable"""
        if platform.system() == "Windows":
            return os.path.join(self.go_local_dir, "go", "bin", "go.exe")
        else:
            return os.path.join(self.go_local_dir, "go", "bin", "go")
    
    def get_go_download_url(self):
        """Get download URL for Go based on OS and architecture"""
        system = platform.system()
        machine = platform.machine().lower()
        
        # Determine architecture
        if machine in ['amd64', 'x86_64']:
            arch = 'amd64'
        elif machine in ['arm64', 'aarch64']:
            arch = 'arm64'
        elif machine in ['i386', 'i686', 'x86']:
            arch = '386'
        else:
            arch = 'amd64'  # Default
        
        # Determine OS and extension
        if system == "Windows":
            os_name = "windows"
            ext = "zip"
        elif system == "Darwin":
            os_name = "darwin"
            ext = "tar.gz"
        elif system == "Linux":
            os_name = "linux"
            ext = "tar.gz"
        else:
            return None
        
        filename = f"go{self.go_version}.{os_name}-{arch}.{ext}"
        url = f"https://go.dev/dl/{filename}"
        
        return url, filename
    
    def download_and_install_go(self):
        """Download and install Go locally"""
        try:
            # Get download URL
            download_info = self.get_go_download_url()
            if not download_info:
                self.installation_finished.emit(False, "Unsupported platform")
                return
            
            url, filename = download_info
            download_path = os.path.join(self.app_dir, filename)
            
            # Create local directory
            os.makedirs(self.go_local_dir, exist_ok=True)
            
            # Download Go
            self.progress_updated.emit(10, "Downloading Go...")
            
            def download_progress(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(int((downloaded / total_size) * 80), 80)
                    self.progress_updated.emit(10 + percent, 
                        f"Downloading: {downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB")
            
            urllib.request.urlretrieve(url, download_path, download_progress)
            
            # Extract Go
            self.progress_updated.emit(90, "Extracting Go...")
            
            if filename.endswith('.zip'):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(self.go_local_dir)
            elif filename.endswith('.tar.gz'):
                with tarfile.open(download_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.go_local_dir)
            
            # Clean up downloaded file
            os.remove(download_path)
            
            # Verify installation
            go_path = self.get_local_go_path()
            if os.path.exists(go_path):
                # Make executable on Unix systems
                if platform.system() != "Windows":
                    os.chmod(go_path, 0o755)
                
                self.progress_updated.emit(100, "Go installed successfully!")
                self.installation_finished.emit(True, go_path)
            else:
                self.installation_finished.emit(False, "Installation verification failed")
                
        except Exception as e:
            self.installation_finished.emit(False, f"Installation failed: {str(e)}")
    
    def get_go_env(self):
        """Get environment variables for Go execution
        
        Returns:
            dict: Environment variables with Go paths
        """
        env = os.environ.copy()
        
        local_go = self.get_local_go_path()
        if os.path.exists(local_go):
            go_root = os.path.dirname(os.path.dirname(local_go))
            go_bin = os.path.dirname(local_go)
            
            env['GOROOT'] = go_root
            
            # Add Go bin to PATH
            if platform.system() == "Windows":
                env['PATH'] = f"{go_bin};{env.get('PATH', '')}"
            else:
                env['PATH'] = f"{go_bin}:{env.get('PATH', '')}"
            
            # Set GOPATH to user directory
            gopath = os.path.join(os.path.expanduser("~"), "go")
            env['GOPATH'] = gopath
            
            # Add GOPATH bin to PATH
            gopath_bin = os.path.join(gopath, "bin")
            if platform.system() == "Windows":
                env['PATH'] = f"{gopath_bin};{env['PATH']}"
            else:
                env['PATH'] = f"{gopath_bin}:{env['PATH']}"
        
        return env
    
    def uninstall_local_go(self):
        """Remove local Go installation"""
        try:
            if os.path.exists(self.go_local_dir):
                shutil.rmtree(self.go_local_dir)
                return True
        except:
            pass
        return False


class GoInstallerThread(QThread):
    """Thread for Go installation to prevent UI blocking"""
    
    progress_updated = pyqtSignal(int, str)
    installation_finished = pyqtSignal(bool, str)
    
    def __init__(self, installer):
        super().__init__()
        self.installer = installer
        
    def run(self):
        self.installer.progress_updated.connect(self.progress_updated.emit)
        self.installer.installation_finished.connect(self.installation_finished.emit)
        self.installer.download_and_install_go()
