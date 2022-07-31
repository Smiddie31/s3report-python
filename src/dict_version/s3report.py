import boto3
import csv
import click


def find_encryption(name: str, client: boto3.client) -> dict:
    try:
        resp = client.get_bucket_encryption(Bucket=name)
        if (
            resp["ServerSideEncryptionConfiguration"]["Rules"][0][
                "ApplyServerSideEncryptionByDefault"
            ]["SSEAlgorithm"]
            == "AES256"
        ):
            result = {"Encryption": True, "EncryptionType": "SSE"}
        else:
            result = {"Encryption": True, "EncryptionType": "KMS"}
    except:
        result = {"Encryption": False, "EncryptionType": "None"}
    return result


def find_versioning(name: str, client: boto3.client) -> dict:
    try:
        result = client.get_bucket_versioning(Bucket=name)
        result["Versioning"] = result["Status"]
        result.pop("Status")
        result.pop("ResponseMetadata")
    except:
        result = {"Versioning": "Not Enabled"}
    return result


def find_logging(name: str, client: boto3.client) -> dict:
    try:
        resp = client.get_bucket_logging(Bucket=name)
        if resp["LoggingEnabled"]:
            log_bucket = resp["LoggingEnabled"]["TargetBucket"]
            result = {"BucketLogging": "Enabled", "Delivery Bucket": log_bucket}
        else:
            result = {"BucketLogging": "None", "Delivery Bucket": "-"}
    except:
        result = {"BucketLogging": "None", "Delivery Bucket": "-"}
    return result


def find_public(name: str, client: boto3.client) -> dict:
    try:
        resp = client.get_bucket_policy_status(Bucket=name)
        if resp["PolicyStatus"]["IsPublic"] == True:
            result = {"Public": True}
        else:
            result = {"Public": False}
    except:
        result = {"Public": False}
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
    full_bucket_list = []
    for bucket in buckets:
        bucket_dict = {"Name": bucket}
        bucket_dict.update(find_encryption(bucket, s3_client))
        bucket_dict.update(find_versioning(bucket, s3_client))
        bucket_dict.update(find_logging(bucket, s3_client))
        bucket_dict.update(find_public(bucket, s3_client))
        full_bucket_list.append(bucket_dict)
    create_csv(full_bucket_list, file_name)


if __name__ == "__main__":
    main()