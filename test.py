import ftplib
import os
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_file_to_ftp(host, port, username, password, local_file, remote_file=None):
    """
    FTP file upload with extensive network error diagnostics
    """
    try:
        # Explicitly resolve the hostname to IP
        resolved_ip = socket.gethostbyname(host)
        logger.info(f"Resolved {host} to IP: {resolved_ip}")
    except socket.gaierror as e:
        logger.error(f"Hostname resolution failed: {e}")
        return False

    try:
        # Create a socket to test connectivity
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(10)
        
        # Test connection before FTP
        connection_result = test_socket.connect_ex((host, port))
        test_socket.close()
        
        if connection_result != 0:
            logger.error(f"Cannot connect to {host}:{port}. Error code: {connection_result}")
            logger.error("Possible reasons:")
            logger.error("1. Firewall blocking the port")
            logger.error("2. Server not running")
            logger.error("3. Incorrect network configuration")
            return False

        # Proceed with FTP upload
        with ftplib.FTP(timeout=30) as ftp:
            logger.info(f"Attempting to connect to {host}:{port}")
            ftp.connect(host, port)
            
            logger.info(f"Logging in as {username}")
            ftp.login(user=username, passwd=password)
            
            logger.info(f"Server message: {ftp.getwelcome()}")
            
            # File upload logic (same as previous script)
            if not os.path.exists(local_file):
                logger.error(f"Local file not found: {local_file}")
                return False
            
            remote_file = remote_file or os.path.basename(local_file)
            
            file_size = os.path.getsize(local_file)
            logger.info(f"Uploading {local_file} ({file_size} bytes)")
            
            with open(local_file, 'rb') as file:
                ftp.storbinary(f'STOR {remote_file}', file, blocksize=8192)
            
            logger.info(f"File uploaded successfully to {remote_file}")
            return True

    except socket.timeout:
        logger.error("Connection timed out. Check network connectivity.")
    except socket.error as e:
        logger.error(f"Socket error: {e}")
        logger.error("Possible network connectivity issues:")
        logger.error("1. No network route")
        logger.error("2. Firewall blocking connection")
        logger.error("3. Network interface problems")
    except ftplib.all_errors as e:
        logger.error(f"FTP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    return False

# Example usage
if __name__ == "__main__":
    success = upload_file_to_ftp(
        host='192.168.0.201',
        port=21,
        username='ftpuser',
        password='ftppassword',
        local_file='hello_world.txt'
    )
    
    if not success:
        print("Detailed diagnostic information is in the logs")


