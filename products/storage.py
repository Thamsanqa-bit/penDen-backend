from storages.backends.s3boto3 import S3Boto3Storage

class OverwriteS3Boto3Storage(S3Boto3Storage):
    def get_available_name(self, name, max_length=None):
        # If the file already exists, delete it
        self.delete(name)
        return name