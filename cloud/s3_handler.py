
import boto3        # aws sdk for python
import os           # to read environment variables
import json         # to save metrics as json
from datetime import datetime          # for timestamps on filenames
from botocore.exceptions import ClientError  # to catch aws errors

class S3Handler:
    """handles all file storage for the AI dev pod — every agent saves outputs here"""

    ARTIFACT_FOLDERS = {
        "user_stories":    "user_stories/",     # BA agent output
        "design_docs":     "design_docs/",      # Design agent output
        "source_code":     "source_code/",      # Developer agent output
        "test_results":    "test_results/",     # Testing agent output (Person 4)
        "critic_feedback": "critic_feedback/",  # Self-critic agent output
    }

    def __init__(self, bucket_name=None):
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "ai-dev-pod-artifacts")  # get bucket name
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),         # aws key from env
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), # aws secret from env
            region_name=os.getenv("AWS_REGION", "us-east-1"),         # default region
        )

    def save_artifact(self, content, artifact_type, filename=None):
        """save any agent output to the correct S3 folder"""
        folder = self.ARTIFACT_FOLDERS.get(artifact_type, "misc/")  # get folder for this type
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")  # auto generate filename
            filename = f"{artifact_type}_{timestamp}.txt"
        s3_key = folder + filename  # full path in S3

        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content.encode("utf-8"),       # convert text to bytes
                ServerSideEncryption="AES256",      # encrypt file at rest
            )
            print(f"✅ Saved → s3://{self.bucket_name}/{s3_key}")
            return s3_key
        except ClientError as e:
            print(f"❌ Save failed: {e}")
            return None

    def get_artifact(self, s3_key):
        """retrieve a saved artifact from S3"""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response["Body"].read().decode("utf-8")  # convert bytes back to text
        except ClientError as e:
            print(f"❌ Retrieve failed: {e}")
            return None

    def list_artifacts(self, artifact_type):
        """list all saved files of a given type"""
        prefix = self.ARTIFACT_FOLDERS.get(artifact_type, "")
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]  # return list of keys
        except ClientError as e:
            print(f"❌ List failed: {e}")
            return []

    def save_evaluation_metrics(self, metrics):
        """save test evaluation metrics like pass rate, coverage, token cost"""
        content = json.dumps(metrics, indent=2)  # convert dict to formatted json string
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return self.save_artifact(content, "test_results", f"eval_metrics_{timestamp}.json")
