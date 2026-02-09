"""
API Client for communicating with the Django backend.
"""
import requests
from typing import Optional, Callable
from config import API_BASE_URL


class APIClient:
    """Handle all API communications with the backend."""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token: Optional[str] = None
        self.username: Optional[str] = None
    
    def _get_headers(self, include_content_type: bool = True) -> dict:
        """Get request headers with authentication."""
        headers = {}
        if include_content_type:
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    def _get_multipart_headers(self) -> dict:
        """Get headers for multipart form data."""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user and get token.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Response data with token
            
        Raises:
            Exception: If login fails
        """
        response = requests.post(
            f"{self.base_url}/auth/login/",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]
            self.username = data["username"]
            return data
        elif response.status_code == 401:
            raise Exception("Invalid username or password")
        else:
            raise Exception(f"Login failed: {response.text}")
    
    def logout(self):
        """Clear authentication data."""
        self.token = None
        self.username = None
    
    def register(self, username: str, email: str, password: str) -> dict:
        """
        Register a new user account.
        
        Args:
            username: Desired username
            email: User's email
            password: User's password
            
        Returns:
            Response data with token
            
        Raises:
            Exception: If registration fails
        """
        response = requests.post(
            f"{self.base_url}/auth/register/",
            json={
                "username": username,
                "email": email,
                "password": password,
                "password_confirm": password
            }
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.token = data.get("token")
            self.username = data.get("username")
            return data
        else:
            error_msg = "Registration failed"
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    if 'error' in error_data:
                        error_msg = error_data['error']
                    else:
                        for key, value in error_data.items():
                            if isinstance(value, list):
                                error_msg = f"{key}: {value[0]}"
                            else:
                                error_msg = f"{key}: {value}"
                            break
            except Exception:
                pass
            raise Exception(error_msg)
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset.
        
        Args:
            dataset_id: UUID of the dataset to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            Exception: If deletion fails
        """
        url = f"{self.base_url}/datasets/{str(dataset_id)}/"
        if not url.endswith('/'):
            url += '/'
            
        print(f"DEBUG: Deleting dataset at: {url}")
        
        try:
            # For DELETE, we don't need Content-Type header if there's no body
            response = requests.delete(
                url,
                headers=self._get_headers(include_content_type=False),
                timeout=10
            )
            
            if response.status_code in [200, 201, 204]:
                return True
            else:
                error_msg = f"Server returned status {response.status_code}"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        error_msg = error_data['error']
                    elif isinstance(error_data, dict) and "detail" in error_data:
                        error_msg = error_data['detail']
                except:
                    if response.text and len(response.text) < 100:
                        error_msg = response.text
                
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")
        except Exception as e:
            raise Exception(str(e))
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.token is not None
    
    def upload_dataset(self, file_path: str) -> dict:
        """
        Upload a CSV file to the backend.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Response data with dataset info and summary
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.base_url}/upload/",
                files=files,
                headers=self._get_multipart_headers()
            )
        
        if response.status_code == 201:
            return response.json()
        else:
            error = response.json().get("error", "Upload failed")
            raise Exception(error)
    
    def get_datasets(self) -> list:
        """
        Get list of last 5 uploaded datasets.
        
        Returns:
            List of dataset objects
        """
        response = requests.get(
            f"{self.base_url}/datasets/",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch datasets")
    
    def get_dataset_summary(self, dataset_id: str) -> dict:
        """
        Get full summary for a dataset.
        
        Args:
            dataset_id: UUID of the dataset
            
        Returns:
            Dataset with summary data
        """
        response = requests.get(
            f"{self.base_url}/summary/{dataset_id}/",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch dataset summary")
    
    def get_dataset_data(self, dataset_id: str) -> dict:
        """
        Get raw data from a dataset.
        
        Args:
            dataset_id: UUID of the dataset
            
        Returns:
            Dict with columns and data
        """
        response = requests.get(
            f"{self.base_url}/data/{dataset_id}/",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to fetch dataset data")
    
    def download_report(self, dataset_id: str, save_path: str) -> str:
        """
        Download PDF report and save to file.
        
        Args:
            dataset_id: UUID of the dataset
            save_path: Path to save the PDF
            
        Returns:
            Path to saved file
        """
        response = requests.get(
            f"{self.base_url}/report/{dataset_id}/",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return save_path
        else:
            raise Exception("Failed to download report")


# Global API client instance
api_client = APIClient()
