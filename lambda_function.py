import paramiko
import requests
import boto3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Environment variables from Lambda configuration
SFTP_HOST = os.getenv('SFTP_HOST')
SFTP_PORT = int(os.getenv('SFTP_PORT', 22))  # Default port 22 if not set
SFTP_USERNAME = os.getenv('SFTP_USERNAME')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

S3_FILE_NAME = 'test_file.txt'
S3_FILE_CONTENT = 'This is a test file for S3.'

def send_slack_alert(message):
    slack_data = {'text': message}
    response = requests.post(
        SLACK_WEBHOOK_URL, json=slack_data,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to Slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

# def upload_file_to_sftp():
#     try:
#         logger.info('Connecting to SFTP server...')
#         transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
#         transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
#         logger.info('SFTP connection established.')

#         sftp = paramiko.SFTPClient.from_transport(transport)
#         local_file_path = '/tmp/test_file.txt'  # AWS Lambda uses /tmp for temp storage
#         with open(local_file_path, 'w') as file:
#             file.write('This is a test file for SFTP.')

#         logger.info('Uploading file to SFTP...')
#         sftp.put(local_file_path, f'/remote/path/{os.path.basename(local_file_path)}')
#         logger.info('File uploaded to SFTP successfully.')

#         sftp.close()
#         transport.close()
#     except paramiko.ssh_exception.AuthenticationException as e:
#         logger.error(f"Authentication failed for SFTP: {str(e)}")
#         raise
#     except paramiko.ssh_exception.SSHException as e:
#         logger.error(f"SSH error occurred: {str(e)}")
#         raise
#     except Exception as e:
#         logger.error(f"An unexpected error occurred while uploading to SFTP: {str(e)}")
#         raise

def lambda_handler(event, context):
    logger.info('Lambda function has started.')
    try:
        # Test SFTP login
        logger.info('Connecting to SFTP server...')
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        logger.info('SFTP connection established.')
        
        sftp = paramiko.SFTPClient.from_transport(transport)
        logger.info('Listing files on SFTP server...')
        sftp.listdir('.')  # Simple operation to confirm login
        logger.info('SFTP operation successful.')
        
        sftp.close()
        transport.close()

        # Perform additional operations
        # upload_file_to_sftp()
        
    except paramiko.ssh_exception.AuthenticationException as e:
        error_message = f"Failed to complete operations: Authentication failed: {str(e)}"
        logger.error(error_message)
        send_slack_alert(error_message)
        raise
    except boto3.exceptions.Boto3Error as e:
        error_message = f"Failed to complete operations: AWS error: {str(e)}"
        logger.error(error_message)
        send_slack_alert(error_message)
        raise
    except Exception as e:
        error_message = f"Failed to complete operations: An unexpected error occurred: {str(e)}"
        logger.error(error_message)
        send_slack_alert(error_message)
        raise

    logger.info('SFTP login check and additional operations complete.')
    return {
        'statusCode': 200,
        'body': 'SFTP login check and additional operations complete'
    }

# For local testing (you can remove this part if testing on Lambda)
if __name__ == '__main__':
    lambda_handler(None, None)
