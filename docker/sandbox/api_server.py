from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import subprocess
import tempfile
import os
import json
import hashlib
import logging
from logging.handlers import TimedRotatingFileHandler
from jinja2 import Template
import uvicorn
import shutil

# Configure logging with console and file output
def setup_logging():
    """
    Configure logging to output to both console and file with rotation.
    Log files are named by date and kept for 10 days.
    """
    # Create log directory if it doesn't exist
    log_dir = '/app/logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with time-based rotation
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'sandbox.log'),
        when='midnight',    # Rotate at midnight
        interval=1,         # Every 1 day
        backupCount=10,     # Keep 10 days of logs
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Set the suffix format for rotated files (sandbox.log.YYYY-MM-DD format)
    file_handler.suffix = '%Y-%m-%d'
    logger.addHandler(file_handler)
    
    return logger

# Setup logging
logger = setup_logging()

app = FastAPI()

# Response format for successful operations
def response_success(data: Dict[str, Any] = {}, msg: str = 'OK', status: int = 0) -> Dict[str, Any]:
    return {'status': status, 'msg': msg, 'data': data}

# Response format for failed operations
def response_error(msg: str = 'error', data: Dict[str, Any] = {}, status: int = -1) -> Dict[str, Any]:
    return {'status': status, 'msg': msg, 'data': data}

# Predefined API Key for authentication
API_KEY = "Kp7wRJ9LzF3qX2hN"

# Virtual environment cache directory
VENV_CACHE_DIR = '/app/venv_cache'

# Request model for running code
class CodeRequest(BaseModel):
    custom_unique_id: str
    code: str
    language: str
    pip_packages: Optional[List[str]] = []
    template_params: Optional[Dict[str, Any]] = {}  # Parameters for Jinja2
    tool_type: Optional[str] = None  # Tool type (t1, t2, etc.)
    tool_name: Optional[str] = None  # Tool name (specific tool in tool_type)

# Dependency to verify API Key from request header
def verify_api_key(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid Authorization header")

    token = authorization[7:]  # Remove 'Bearer ' prefix
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return token

# Health check endpoint
@app.get("/health")
def health_check():
    return response_success(data={"status": "healthy"})

# Function to calculate SHA-256 hash of requirements
def get_requirements_hash(pip_packages: List[str]) -> str:
    """
    Calculate SHA-256 hash of pip packages list to create unique environment identifier.
    """
    if not pip_packages:
        return hashlib.sha256(b"").hexdigest()
    
    # Sort packages to ensure consistent hash regardless of order
    sorted_packages = sorted(pip_packages)
    requirements_content = '\n'.join(sorted_packages)
    
    hasher = hashlib.sha256()
    hasher.update(requirements_content.encode('utf-8'))
    return hasher.hexdigest()

# Function to create virtual environment using uv
def create_venv_with_uv(venv_path: str, pip_packages: List[str]) -> bool:
    """
    Create virtual environment using uv and install packages.
    Returns True if successful, False otherwise.
    """
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(venv_path), exist_ok=True)
        
        # Create virtual environment with uv
        logger.info(f"Creating virtual environment at: {venv_path}")
        create_cmd = [
            'uv', 'venv', venv_path,
            '--python', '3.12.10',
            # '--seed'  # Include pip, setuptools, wheel
        ]
        
        result = subprocess.run(create_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to create venv: {result.stderr}")
            return False
        
        # Install packages if any
        if pip_packages:
            logger.info(f"Installing packages: {pip_packages}")
            
            # Create temporary requirements file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as req_file:
                req_file.write('\n'.join(pip_packages))
                req_file_path = req_file.name
            
            try:
                # Install packages using uv
                python_path = os.path.join(venv_path, 'bin', 'python')
                install_cmd = [
                    'uv', 'pip', 'install', 
                    '-r', req_file_path,
                    '--python', python_path
                ]
                
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to install packages: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temporary requirements file
                os.unlink(req_file_path)
        
        logger.info(f"Virtual environment created successfully at: {venv_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating virtual environment: {str(e)}")
        return False

# Function to get or create cached virtual environment
def get_or_create_venv(pip_packages: List[str]) -> str:
    """
    Get existing virtual environment or create new one based on requirements hash.
    Returns path to the virtual environment.
    """
    # Handle empty pip_packages - use fixed base environment
    if not pip_packages:
        base_venv_path = os.path.join(VENV_CACHE_DIR, 'base')
        
        # Check if base environment already exists
        if os.path.exists(base_venv_path) and os.path.exists(os.path.join(base_venv_path, 'bin', 'python')):
            logger.info("Using existing base virtual environment (no dependencies)")
            return base_venv_path
        
        # Create base environment
        logger.info("Creating base virtual environment (no dependencies)")
        if create_venv_with_uv(base_venv_path, []):
            return base_venv_path
        else:
            raise RuntimeError("Failed to create base virtual environment")
    
    # Calculate requirements hash for non-empty packages
    req_hash = get_requirements_hash(pip_packages)
    venv_path = os.path.join(VENV_CACHE_DIR, req_hash)
    
    # Check if virtual environment already exists
    if os.path.exists(venv_path) and os.path.exists(os.path.join(venv_path, 'bin', 'python')):
        logger.info(f"Cache hit: Using existing virtual environment {req_hash}")
        return venv_path
    
    # Cache miss: create new virtual environment
    logger.info(f"Cache miss: Creating new virtual environment {req_hash}")
    
    if create_venv_with_uv(venv_path, pip_packages):
        return venv_path
    else:
        raise RuntimeError(f"Failed to create virtual environment for hash: {req_hash}")

# Function to execute user code with Firejail and cached environment
def execute_user_code_with_cache(custom_unique_id: str, user_code: str, pip_packages: List[str], tool_type: Optional[str] = None, tool_name: Optional[str] = None) -> Tuple[str, str]:
    """
    Execute user code in Firejail sandbox with cached virtual environment and optional tool support.
    """
    try:
        # Get or create virtual environment
        venv_path = get_or_create_venv(pip_packages)
        python_path = os.path.join(venv_path, 'bin', 'python')
        
        # Create temporary directory for user code
        with tempfile.TemporaryDirectory() as tempdir:
            user_code_filename = f"user_code_{custom_unique_id}.py"
            user_code_path = os.path.join(tempdir, user_code_filename)
            
            # Prepare final code with tool support if needed
            final_code = user_code
            if tool_type == 't1' and tool_name:
                tool_path = f'/app/tools/{tool_type}/{tool_name}'
                
                if os.path.exists(tool_path):
                    # Copy tool files to temp directory
                    tool_temp_dir = os.path.join(tempdir, tool_name)
                    shutil.copytree(tool_path, tool_temp_dir)
                    
                    # Add Python path setup for copied tools
                    path_setup = f"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '{tool_name}'))
"""
                    final_code = path_setup + "\n" + user_code
                else:
                    logger.error(f"Tool source path does not exist: {tool_path}")
                    return "", f"Tool directory not found: {tool_path}"
            
            # Write final code to file
            with open(user_code_path, 'w') as code_file:
                code_file.write(final_code)
            
            # Build Firejail command with cached environment
            firejail_cmd = [
                'firejail',
                '--quiet',
                '--private-tmp',                    # Keep /tmp ephemeral
                python_path,                        # Python interpreter from cached venv
                user_code_path                      # User code to execute
            ]
            logger.info(f"Executing code with Firejail: {' '.join(firejail_cmd)}")
            
            # Execute user code
            result = subprocess.run(
                firejail_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 300 second timeout
            )
            stdout, stderr = result.stdout.strip(), result.stderr.strip()
            
            # Try to parse stdout as JSON if it looks like a dictionary
            try:
                stdout_dict = eval(stdout)
                if isinstance(stdout_dict, dict):
                    stdout = json.dumps(stdout_dict)
            except (SyntaxError, NameError, TypeError, ValueError):
                pass  # Keep original stdout if not a valid dictionary
            
            return stdout, stderr
            
    except subprocess.TimeoutExpired:
        return "", "Execution timed out after 300 seconds"
    except Exception as e:
        logger.error(f"Error executing user code: {str(e)}")
        return "", f"Execution failed: {str(e)}"

# Function to render Jinja2 template
def render_jinja2_template(template_code: str, template_params: Dict[str, Any]) -> Tuple[str, str]:
    """
    Render Jinja2 template with given parameters.
    """
    try:
        template = Template(template_code)
        rendered_output = template.render(template_params)
        return rendered_output.strip(), ""  # stdout, stderr
    except Exception as e:
        logger.error(f"Error rendering Jinja2 template: {str(e)}")
        return "", str(e)

# Endpoint to run user-provided code
@app.post("/run_code")
def run_code(request: CodeRequest, api_key: str = Depends(verify_api_key)) -> Dict[str, Any]:
    """
    Execute user code in sandbox environment with cached virtual environments.
    """
    try:
        logger.info(f"Request parameters:")
        logger.info(f"  - custom_unique_id: {request.custom_unique_id}")
        logger.info(f"  - language: {request.language}")
        logger.info(f"  - pip_packages: {request.pip_packages}")
        logger.info(f"  - tool_type: {request.tool_type}")
        logger.info(f"  - tool_name: {request.tool_name}")
        logger.info(f"  - code length: {len(request.code)} characters")
        logger.info(f"  - template_params: {request.template_params}")
        
        # Execute user code based on language
        if request.language.lower() == 'jinja2':
            stdout, stderr = render_jinja2_template(request.code, request.template_params)
        elif request.language.lower() == 'python3':
            stdout, stderr = execute_user_code_with_cache(
                request.custom_unique_id, 
                request.code, 
                request.pip_packages,
                request.tool_type,
                request.tool_name
            )
        else:
            return response_error(
                msg="Currently unsupported language", 
                data={"language": request.language}
            )
        
        logger.info(f"Execution result:")
        logger.info(f"  - stdout: {stdout}")
        logger.info(f"  - stderr: {stderr}")

        # Return response based on execution result
        if stderr:
            logger.error(f"Execution failed")
            return response_error(
                msg="Execution failed", 
                data={"stdout": stdout, "stderr": stderr}
            )
        else:
            logger.info("Execution success")
            return response_success(data={"stdout": stdout, "stderr": stderr})
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return response_error(msg=str(e))

if __name__ == "__main__":
    # Ensure cache directory exists
    os.makedirs(VENV_CACHE_DIR, exist_ok=True)
    
    # Start the FastAPI server
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=8001, 
        workers=int(os.environ.get('SANDBOX_FASTAPI_WORKERS', 10))
    )