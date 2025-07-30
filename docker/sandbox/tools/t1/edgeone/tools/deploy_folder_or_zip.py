import os
import time
import tempfile
import zipfile
from collections.abc import Generator
from typing import Any, Dict, List, Optional
from pathlib import Path

import requests
from qcloud_cos import CosConfig, CosS3Client
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DeployFolderOrZipTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Deploy a ZIP file to EdgeOne Pages
        """
        try:
            zip_file = tool_parameters.get("zip_file")
            environment = tool_parameters.get("environment", "Production")
            
            if not zip_file:
                yield self.create_text_message("ZIP file is required.")
                return
            
            # Get credentials
            api_token = self.runtime.credentials.get("api_token")
            if not api_token:
                yield self.create_text_message("❌ API token is required for ZIP deployment. Please configure your EdgeOne Pages API token.")
                return
            
            project_name = self.runtime.credentials.get("project_name", "")
            
            # Validate file is a ZIP file
            if not zip_file.get('filename', '').lower().endswith('.zip'):
                yield self.create_text_message("❌ Only ZIP files are supported for deployment.")
                return
            
            yield self.create_text_message(f"🚀 Starting deployment of ZIP file: {zip_file.get('filename')}")
            yield self.create_text_message(f"📋 Environment: {environment}")
            
            # Download and save the file temporarily
            zip_path = self._download_file(zip_file)
            
            try:
                # Initialize deployment helper
                deployer = EdgeOneDeployer(api_token, project_name)
                
                # Deploy
                result_url = deployer.deploy(zip_path, environment)
                
                # Return success
                yield self.create_text_message("✅ Deployment completed successfully!")
                yield self.create_text_message(f"🌐 Public URL: {result_url}")
                yield self.create_json_message({
                    "success": True,
                    "url": result_url,
                    "environment": environment,
                    "type": "zip_deployment",
                    "message": f"ZIP file {zip_file.get('filename')} deployed successfully to EdgeOne Pages"
                })
            finally:
                # Cleanup temporary file
                if os.path.exists(zip_path):
                    os.unlink(zip_path)
            
        except Exception as e:
            error_message = f"❌ Deployment failed: {str(e)}"
            yield self.create_text_message(error_message)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "type": "zip_deployment"
            })
    
    def _download_file(self, file_info: Dict) -> str:
        """Download file from Dify to temporary location"""
        file_url = file_info.get('url')
        filename = file_info.get('filename', 'upload.zip')
        
        if not file_url:
            raise Exception("File URL not provided")
        
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        
        # Download file
        response = requests.get(file_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return temp_path


class EdgeOneDeployer:
    def __init__(self, api_token: str, project_name: str = ""):
        self.api_token = api_token
        self.project_name = project_name
        self.base_api_url = ""
        self.temp_project_name = f"dify-upload-{int(time.time())}"
    
    def deploy(self, local_path: str, environment: str = "Production") -> str:
        """Main deployment function"""
        # Determine base API URL
        self._check_and_set_base_url()
        
        # Validate it's a ZIP file
        if not self._is_zip_file(local_path):
            raise Exception("Only ZIP files are supported")
        
        # Upload to COS
        target_path = self._upload_to_cos(local_path, True)
        
        # Get or create project
        project_id = self._get_or_create_project()
        
        # Create deployment
        deployment_id = self._create_deployment(project_id, target_path, True, environment)
        
        # Wait for deployment completion
        deployment_result = self._poll_deployment_status(project_id, deployment_id)
        
        # Get final URL
        return self._get_deployment_url(deployment_result, project_id, environment)
    
    def _check_and_set_base_url(self):
        """Determine which API endpoint to use"""
        base_urls = [
            'https://pages-api.cloud.tencent.com/v1',
            'https://pages-api.edgeone.ai/v1'
        ]
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }
        
        body = {
            'Action': 'DescribePagesProjects',
            'PageNumber': 1,
            'PageSize': 10,
        }
        
        for base_url in base_urls:
            try:
                response = requests.post(base_url, headers=headers, json=body, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('Code') == 0:
                        self.base_api_url = base_url
                        return
            except Exception:
                continue
        
        raise Exception("Invalid API token. Please check your EdgeOne Pages API token.")
    
    def _is_zip_file(self, file_path: str) -> bool:
        """Check if file is a ZIP file"""
        return file_path.lower().endswith('.zip')
    
    def _upload_to_cos(self, local_path: str, is_zip: bool) -> str:
        """Upload ZIP file to EdgeOne COS"""
        # Get COS temporary token
        token_result = self._get_cos_temp_token()
        
        if token_result.get('Code') != 0:
            raise Exception(f"Failed to get COS token: {token_result.get('Message', 'Unknown error')}")
        
        response = token_result['Data']['Response']
        bucket = response['Bucket']
        region = response['Region']
        target_path = response['TargetPath']
        credentials = response['Credentials']
        
        # Initialize COS client
        config = CosConfig(
            Region=region,
            SecretId=credentials['TmpSecretId'],
            SecretKey=credentials['TmpSecretKey'],
            Token=credentials['Token']
        )
        cos_client = CosS3Client(config)
        
        # Upload single ZIP file
        file_name = os.path.basename(local_path)
        key = f"{target_path}/{file_name}"
        
        with open(local_path, 'rb') as file_data:
            cos_client.put_object(
                Bucket=bucket,
                Body=file_data,
                Key=key
            )
        
        return key
    
    def _get_cos_temp_token(self) -> Dict:
        """Get temporary COS token"""
        body = {}
        
        # If project name is provided, try to find existing project
        if self.project_name:
            projects = self._describe_projects(project_name=self.project_name)
            if projects:
                body = {"ProjectId": projects[0]['ProjectId']}
            else:
                raise Exception(f"Project {self.project_name} not found")
        else:
            body = {"ProjectName": self.temp_project_name}
        
        body['Action'] = 'DescribePagesCosTempToken'
        
        return self._make_api_request(body)
    
    def _get_or_create_project(self) -> str:
        """Get existing project or create new one"""
        if self.project_name:
            # Try to find existing project
            projects = self._describe_projects(project_name=self.project_name)
            if projects:
                return projects[0]['ProjectId']
        
        # Create new project
        return self._create_project()
    
    def _describe_projects(self, project_id: str = "", project_name: str = "") -> List[Dict]:
        """Describe EdgeOne Pages projects"""
        filters = []
        if project_id:
            filters.append({"Name": "ProjectId", "Values": [project_id]})
        if project_name:
            filters.append({"Name": "Name", "Values": [project_name]})
        
        body = {
            'Action': 'DescribePagesProjects',
            'Filters': filters,
            'Offset': 0,
            'Limit': 10,
            'OrderBy': 'CreatedOn'
        }
        
        response = self._make_api_request(body)
        return response.get('Data', {}).get('Response', {}).get('Projects', [])
    
    def _create_project(self) -> str:
        """Create new EdgeOne Pages project"""
        project_name = self.project_name or self.temp_project_name
        
        body = {
            'Action': 'CreatePagesProject',
            'Name': project_name,
            'Provider': 'Upload',
            'Channel': 'Custom',
            'Area': 'global'
        }
        
        response = self._make_api_request(body)
        project_id = response.get('Data', {}).get('Response', {}).get('ProjectId')
        
        if not project_id:
            raise Exception("Failed to create project")
        
        return project_id
    
    def _create_deployment(self, project_id: str, target_path: str, is_zip: bool, environment: str) -> str:
        """Create deployment"""
        body = {
            'Action': 'CreatePagesDeployment',
            'ProjectId': project_id,
            'ViaMeta': 'Upload',
            'Provider': 'Upload',
            'Env': environment,
            'DistType': 'Zip' if is_zip else 'Folder',
            'TempBucketPath': target_path
        }
        
        response = self._make_api_request(body)
        deployment_id = response.get('Data', {}).get('Response', {}).get('DeploymentId')
        
        if not deployment_id:
            raise Exception("Failed to create deployment")
        
        return deployment_id
    
    def _poll_deployment_status(self, project_id: str, deployment_id: str) -> Dict:
        """Poll deployment status until completion"""
        max_attempts = 60  # 5 minutes maximum
        attempt = 0
        
        while attempt < max_attempts:
            deployment = self._get_deployment_status(project_id, deployment_id)
            
            if deployment['Status'] != 'Process':
                return deployment
            
            time.sleep(5)
            attempt += 1
        
        raise Exception("Deployment timeout")
    
    def _get_deployment_status(self, project_id: str, deployment_id: str) -> Dict:
        """Get deployment status"""
        body = {
            'Action': 'DescribePagesDeployments',
            'ProjectId': project_id,
            'Offset': 0,
            'Limit': 50,
            'OrderBy': 'CreatedOn',
            'Order': 'Desc'
        }
        
        response = self._make_api_request(body)
        deployments = response.get('Data', {}).get('Response', {}).get('Deployments', [])
        
        for deployment in deployments:
            if deployment.get('DeploymentId') == deployment_id:
                return deployment
        
        raise Exception(f"Deployment {deployment_id} not found")
    
    def _get_deployment_url(self, deployment_result: Dict, project_id: str, environment: str) -> str:
        """Get final deployment URL"""
        if deployment_result['Status'] != 'Success':
            raise Exception(f"Deployment failed with status: {deployment_result['Status']}")
        
        # Get project details for domain info
        projects = self._describe_projects(project_id=project_id)
        if not projects:
            raise Exception("Failed to get project details")
        
        project = projects[0]
        
        # Check for custom domain in production
        if environment == 'Production' and project.get('CustomDomains'):
            for domain in project['CustomDomains']:
                if domain.get('Status') == 'Pass':
                    return f"https://{domain['Domain']}"
        
        # Use preview URL or preset domain
        domain = deployment_result.get('PreviewUrl', '').replace('https://', '') or project.get('PresetDomain', '')
        
        if not domain:
            raise Exception("Failed to get deployment domain")
        
        # Get access token for temporary URL
        token_response = self._get_encipher_token(domain)
        token = token_response.get('Data', {}).get('Response', {}).get('Token')
        timestamp = token_response.get('Data', {}).get('Response', {}).get('Timestamp')
        
        if not token or not timestamp:
            raise Exception("Failed to get access token")
        
        return f"https://{domain}?eo_token={token}&eo_time={timestamp}"
    
    def _get_encipher_token(self, domain: str) -> Dict:
        """Get encipher token for domain access"""
        body = {
            'Action': 'DescribePagesEncipherToken',
            'Text': domain
        }
        
        return self._make_api_request(body)
    
    def _make_api_request(self, body: Dict) -> Dict:
        """Make API request to EdgeOne"""
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(self.base_api_url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('Code') != 0:
            raise Exception(f"API error: {result.get('Message', 'Unknown error')}")
        
        return result