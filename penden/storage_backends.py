# storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
import logging

logger = logging.getLogger(__name__)


class SafeS3Boto3Storage(S3Boto3Storage):
    def delete(self, name):
        """
        Override delete method to handle permission errors gracefully
        """
        try:
            super().delete(name)
            return True
        except Exception as e:
            # Log the error but don't crash the application
            logger.warning(f"S3 delete permission denied for {name}. Error: {str(e)}")
            # Return False to indicate delete failed, but don't raise exception
            return False

    def save(self, name, content):
        """
        Also override save to handle any permission issues there
        """
        try:
            return super().save(name, content)
        except Exception as e:
            logger.error(f"S3 save failed for {name}. Error: {str(e)}")
            raise  # Re-raise for save operations as they're critical