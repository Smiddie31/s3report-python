import boto3
import csv
import click
from dataclasses import dataclass, asdict
from typing import Union


@dataclass
class s3_bucket:
    name: str
    encryption: bool
    encryption_type: str
    versioning: str
    logging: str
    log_bucket: str
    public: bool


def find_encryption(name: str, client: boto3.client) -> Union[bool, str]:
    try:
        resp = client.get_bucket_encryption(Bucket=name)
        if (
            resp["ServerSideEncryptionConfiguration"]["Rules"][0][
                "ApplyServerSideEncryptionByDefault"
            ]["SSEAlgorithm"]
            == "AES256"
        ):
            result = True, "SSE"
        else:
            result = True, "KMS"
    except:
        result = False, "None"
    return result


def find_versioning(name: str, client: boto3.client) -> str:
    try:
        result = client.get_bucket_versioning(Bucket=name)
        result = result["Status"]
    except:
        result = "Not Enabled"
    return result


def find_logging(name: str, client: boto3.client) -> Union[str, str]:
    try:
        resp = client.get_bucket_logging(Bucket=name)
        if resp["LoggingEnabled"]:
            log_bucket = resp["LoggingEnabled"]["TargetBucket"]
            result = "Enabled", log_bucket
        else:
            result = "None", "-"
    except:
        result = "None", "-"
    return result


def find_public(name: str, client: boto3.client) -> bool:
    try:
        resp = client.get_bucket_policy_status(Bucket=name)
        if resp["PolicyStatus"]["IsPublic"]:
            result = True
        else:
            result = False
    except:
        result = False
    return result


def create_csv(s3_list: list, file: str):
    keys = s3_list[0].keys()
    with open(f"{file}.csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(s3_list)


@click.command()
@click.option("-f", "--file_name", help="Output CSV Filename", required=True)
def main(file_name):
    s3_client = boto3.client("s3")
    buckets = [item["Name"] for item in s3_client.list_buckets()["Buckets"]]
    bucket_data = []
    for bucket in buckets:
        enc, enc_type = find_encryption(bucket, s3_client)
        ver = find_versioning(bucket, s3_client)
        logging, log_bucket = find_logging(bucket, s3_client)
        pub = find_public(bucket, s3_client)
        b = s3_bucket(bucket, enc, enc_type, ver, logging, log_bucket, pub)
        bucket_data.append(asdict(b))
    create_csv(bucket_data, file_name)


if __name__ == "__main__":
    main()
