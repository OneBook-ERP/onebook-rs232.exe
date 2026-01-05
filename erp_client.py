"""
ERP Client for Waybridge Agent
Handles communication with ERP system with retry logic and error handling
"""

import requests
import time
from typing import Dict, Any, Optional, Tuple
from logger import get_logger
from config_manager import get_config

logger = get_logger()


class ERPClient:
    """Client for communicating with ERP system"""
    
    def __init__(self):
        """Initialize ERP client with configuration"""
        self.config = get_config()
        self.erp_config = self.config.get_section('erp')
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Waybridge-Agent/1.0'
        })
        
        # Add token if available
        token = self.erp_config.get('token', '').strip()
        if token:
            self.session.headers.update({
                'Authorization': f'token {token}'
            })
            logger.info("ERP client initialized with token authentication")
        else:
            logger.warning("ERP client initialized without token authentication")
    
    def send(self, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Send payload to ERP endpoint with retry logic
        
        Args:
            payload: Data to send to the endpoint
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        url = self.erp_config.get('url', '')
        timeout = self.erp_config.get('timeout', 10)
        retry_attempts = self.erp_config.get('retry_attempts', 3)
        retry_delay = self.erp_config.get('retry_delay', 2)
        
        if not url:
            error_msg = "ERP URL not configured"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"Sending data to ERP: {payload}")
        
        for attempt in range(1, retry_attempts + 1):
            try:
                logger.debug(f"Attempt {attempt}/{retry_attempts} - POST to {url}")
                
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=timeout
                )
                
                # Log response details
                logger.debug(f"Response Status: {response.status_code}")
                logger.debug(f"Response Headers: {dict(response.headers)}")
                
                if response.ok:
                    logger.info(f"✓ Data sent successfully (Status: {response.status_code})")
                    
                    # Try to parse response
                    try:
                        response_data = response.json()
                        logger.debug(f"Response Data: {response_data}")
                    except Exception:
                        logger.debug(f"Response Text: {response.text[:500]}")
                    
                    return True, None
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(f"✗ Request failed: {error_msg}")
                    
                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        logger.error(f"Client error - not retrying: {error_msg}")
                        return False, error_msg
                    
                    # Retry on server errors (5xx)
                    if attempt < retry_attempts:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        return False, error_msg
                        
            except requests.exceptions.Timeout:
                error_msg = f"Request timeout after {timeout} seconds"
                logger.warning(f"✗ {error_msg}")
                
                if attempt < retry_attempts:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed after {retry_attempts} attempts: {error_msg}")
                    return False, error_msg
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {str(e)}"
                logger.warning(f"✗ {error_msg}")
                
                if attempt < retry_attempts:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed after {retry_attempts} attempts: {error_msg}")
                    return False, error_msg
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(f"✗ {error_msg}")
                return False, error_msg
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"✗ {error_msg}", exc_info=True)
                return False, error_msg
        
        error_msg = f"Failed after {retry_attempts} attempts"
        logger.error(error_msg)
        return False, error_msg
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to ERP endpoint
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        logger.info("Testing ERP connection...")
        
        test_payload = {
            "weighbridge_id": self.config.get('weighbridge.id', 'TEST'),
            "weight": 0,
            "raw": "connection_test",
            "test": True
        }
        
        success, error = self.send(test_payload)
        
        if success:
            message = "✓ Connection test successful"
            logger.info(message)
            return True, message
        else:
            message = f"✗ Connection test failed: {error}"
            logger.error(message)
            return False, message
    
    def update_token(self, token: str) -> None:
        """
        Update authentication token
        
        Args:
            token: New authentication token
        """
        if token:
            self.session.headers.update({
                'Authorization': f'token {token}'
            })
            logger.info("Authentication token updated")
        else:
            self.session.headers.pop('Authorization', None)
            logger.warning("Authentication token removed")
    
    def close(self) -> None:
        """Close the session"""
        self.session.close()
        logger.info("ERP client session closed")


# Singleton instance
_erp_client_instance: Optional[ERPClient] = None


def get_erp_client() -> ERPClient:
    """
    Get singleton ERP client instance
    
    Returns:
        ERPClient instance
    """
    global _erp_client_instance
    
    if _erp_client_instance is None:
        _erp_client_instance = ERPClient()
    
    return _erp_client_instance


def send(cfg: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    """
    Legacy function for backward compatibility
    
    Args:
        cfg: Configuration dict (ignored, uses ConfigManager instead)
        payload: Data to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    client = get_erp_client()
    success, _ = client.send(payload)
    return success


if __name__ == "__main__":
    # Test ERP client
    client = get_erp_client()
    success, message = client.test_connection()
    print(f"Test result: {message}")
