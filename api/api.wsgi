#!/usr/bin/python3
import sys
import os
import site

# Add your project directory to the Python path
sys.path.insert(0, "/production/video-api/")

# Change to the project directory
os.chdir("/production/video-api/")

# Activate virtual environment - CORRECTED PATH
venv_path = '/production/venv'

# Add the virtual environment's site-packages to Python path
# Find the correct Python version directory
lib_path = os.path.join(venv_path, 'lib')
if os.path.exists(lib_path):
    for item in os.listdir(lib_path):
        if item.startswith('python'):
            site_packages = os.path.join(lib_path, item, 'site-packages')
            if os.path.exists(site_packages):
                # Add to Python path
                sys.path.insert(0, site_packages)
                # Also use site.addsitedir for proper .pth file processing
                site.addsitedir(site_packages)
                break

# Set virtual environment variables
os.environ['VIRTUAL_ENV'] = venv_path
old_path = os.environ.get('PATH', '')
os.environ['PATH'] = os.path.join(venv_path, 'bin') + ':' + old_path

# Remove system site-packages to avoid conflicts
sys.path = [path for path in sys.path if 'dist-packages' not in path]

# Debug: Print Python path and try to import Flask
print(f"Python executable: {sys.executable}", file=sys.stderr)
print(f"Python path: {sys.path}", file=sys.stderr)
print(f"Virtual env: {os.environ.get('VIRTUAL_ENV')}", file=sys.stderr)

try:
    import flask
    print(f"Flask version: {flask.__version__}", file=sys.stderr)
    print(f"Flask location: {flask.__file__}", file=sys.stderr)
except ImportError as e:
    print(f"Failed to import Flask: {e}", file=sys.stderr)
    raise

# Import your Flask application
try:
    from api import app as application
    print("Successfully imported Flask app", file=sys.stderr)
except ImportError as e:
    print(f"Error importing Flask app: {e}", file=sys.stderr)
    raise

if __name__ == "__main__":
    application.run()