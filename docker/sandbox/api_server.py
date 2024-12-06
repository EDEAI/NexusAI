from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import subprocess
import tempfile
import os
import json
from jinja2 import Template
import uvicorn

app = FastAPI()

# Response format for successful operations
def response_success(data: Dict[str, Any] = {}, msg: str = 'OK', status: int = 0) -> Dict[str, Any]:
    return {'status': status, 'msg': msg, 'data': data}

# Response format for failed operations
def response_error(msg: str = 'error', data: Dict[str, Any] = {}, status: int = -1) -> Dict[str, Any]:
    return {'status': status, 'msg': msg, 'data': data}

# Predefined API Key for authentication
API_KEY = "Kp7wRJ9LzF3qX2hN"

# Request model for running code
class CodeRequest(BaseModel):
    custom_unique_id: str
    code: str
    language: str
    pip_packages: Optional[List[str]] = []
    template_params: Optional[Dict[str, Any]] = {} # Parameters for Jinja2

# Dependency to verify API Key from request header
def verify_api_key(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid Authorization header")

    token = authorization[7:]  # Remove 'Bearer ' prefix
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return token

# Endpoint to run user-provided code
@app.post("/run_code")
def run_code(request: CodeRequest, api_key: str = Depends(verify_api_key)) -> Dict[str, Any]:
    try:
        # Execute user code and capture stdout and stderr
        if request.language.lower() == 'jinja2':
            stdout, stderr = render_jinja2_template(request.code, request.template_params)
        elif request.language.lower() == 'python3':
            stdout, stderr = execute_user_code(request.custom_unique_id, request.code, request.pip_packages)
        else:
            return response_error(msg="Currently unsupported language", data={"language": request.language})

        # Return success response with output data if execution was successful
        if stderr:
            return response_error(msg="Execution failed", data={"stdout": stdout, "stderr": stderr})
        return response_success(data={"stdout": stdout, "stderr": stderr})
    except Exception as e:
        # Return error response in case of failure
        return response_error(msg=str(e))

# Function to execute user code in a sandbox environment
def execute_user_code(custom_unique_id: str, user_code: str, pip_packages: List[str]) -> Tuple[str, str]:
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            requirements_filename = f"requirements_{custom_unique_id}.txt"
            requirements_path = os.path.join(tempdir, requirements_filename)
            user_code_filename = f"user_code_{custom_unique_id}.py"
            user_code_path = os.path.join(tempdir, user_code_filename)

            # Write pip packages to requirements file if provided
            if pip_packages:
                with open(requirements_path, 'w') as req_file:
                    req_file.write('\n'.join(pip_packages))

            # Write user code to file
            with open(user_code_path, 'w') as code_file:
                code_file.write(user_code)

            # Install pip packages if any
            if pip_packages:
                install_result = subprocess.run(
                    ['firejail', '--quiet', '--private', 'pip', 'install', '-r', requirements_path],
                    capture_output=True,
                    text=True
                )
                if install_result.returncode != 0:
                    raise RuntimeError(f"Pip install failed:\n{install_result.stderr}")

            # Run user code
            result = subprocess.run(
                ['firejail', '--quiet', '--private', 'python3', user_code_path],
                capture_output=True,
                text=True
            )

            stdout, stderr = result.stdout.strip(), result.stderr.strip()

            # Check and convert stdout into JSON string if it's a dictionary
            try:
                stdout_dict = eval(stdout)
                if isinstance(stdout_dict, dict):
                    stdout = json.dumps(stdout_dict)
            except (SyntaxError, NameError, TypeError, ValueError) as parse_exception:
                stderr += f"\nFailed to parse stdout as a dictionary: {parse_exception}"

            return stdout, stderr
    except Exception as e:
        raise RuntimeError(f"Execution failed: {str(e)}")

# Function to render Jinja2 template
def render_jinja2_template(template_code: str, template_params: Dict[str, Any]) -> Tuple[str, str]:
    try:
        template = Template(template_code)
        rendered_output = template.render(template_params)
        return rendered_output.strip(), ""  # stdout, stderr
    except Exception as e:
        return "", str(e)

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8001, workers=int(os.environ.get('SANDBOX_FASTAPI_WORKERS', 10)))