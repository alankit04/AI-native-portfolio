import os
from pathlib import Path

BASE = Path("data")
BASE.mkdir(exist_ok=True)


def _s3_enabled() -> bool:
    return bool(os.getenv("S3_BUCKET"))


def save_case_document(case_id: str, content: bytes):
    if _s3_enabled():
        import boto3
        s3 = boto3.client("s3")
        s3.put_object(Bucket=os.environ["S3_BUCKET"], Key=f"cases/{case_id}.txt", Body=content)
        return
    (BASE / f"{case_id}.txt").write_bytes(content)


def load_case_document(case_id: str) -> str:
    if _s3_enabled():
        import boto3
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=os.environ["S3_BUCKET"], Key=f"cases/{case_id}.txt")
        return obj["Body"].read().decode("utf-8")
    path = BASE / f"{case_id}.txt"
    return path.read_text() if path.exists() else ""
