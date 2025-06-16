# import_s3_to_dynamodb.py
"""Import synthetic data from S3 CSV files to DynamoDB tables"""

import boto3
import csv
import io
from decimal import Decimal
from datetime import datetime

# Configuration - Update these values
S3_BUCKET = "synthetic-data-techshowcase"  # Replace with your actual bucket name
S3_RUNS_KEY = "prod_runs_data.csv"
S3_TARGETS_KEY = "prod_targets_data.csv"
DYNAMODB_RUNS_TABLE = "running-log-prod-Runs"  # Replace with actual table name
DYNAMODB_TARGETS_TABLE = "running-log-prod-Targets"  # Replace with actual table name


def format_date_to_string(date_value):
    """Convert date to yyyy-mm-dd string format"""
    if not date_value:
        return ""

    # If already in correct format, return as-is
    if (
        isinstance(date_value, str)
        and len(date_value) == 10
        and date_value.count("-") == 2
    ):
        try:
            # Validate it's a proper date
            datetime.strptime(date_value, "%Y-%m-%d")
            return date_value
        except ValueError:
            pass

    # Try to parse various date formats
    date_formats = [
        "%Y-%m-%d",  # 2024-01-15
        "%m/%d/%Y",  # 01/15/2024
        "%d/%m/%Y",  # 15/01/2024
        "%Y/%m/%d",  # 2024/01/15
        "%Y-%m-%d %H:%M:%S",  # 2024-01-15 10:30:00
        "%m/%d/%Y %H:%M:%S",  # 01/15/2024 10:30:00
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(str(date_value), fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # If all parsing fails, raise an error
    raise ValueError(f"Unable to parse date: {date_value}")


def get_s3_csv_data(bucket, key):
    """Download and parse CSV from S3"""
    print(f"Downloading {key} from S3 bucket {bucket}...")

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)

    # Parse CSV content
    csv_content = response["Body"].read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(csv_content))

    data = list(csv_reader)
    print(f"Found {len(data)} records in {key}")
    return data


def import_runs_to_dynamodb(runs_data):
    """Import runs data to DynamoDB"""
    print(f"Importing {len(runs_data)} runs to DynamoDB table {DYNAMODB_RUNS_TABLE}...")

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(DYNAMODB_RUNS_TABLE)

    success_count = 0

    for run in runs_data:
        try:
            # Convert data types for DynamoDB
            item = {
                "user_id": run["user_id"],
                "run_id": run["run_id"],
                "date": format_date_to_string(
                    run["date"]
                ),  # Force to yyyy-mm-dd format
                "distance_km": Decimal(str(run["distance_km"])),
                "duration_seconds": int(run["duration_seconds"]),
                "notes": run["notes"],
                "created_at": run["created_at"],
            }

            table.put_item(Item=item)
            success_count += 1

            if success_count % 10 == 0:
                print(f"  Imported {success_count} runs...")

        except Exception as e:
            print(f"Error importing run {run.get('run_id', 'unknown')}: {e}")

    print(f"Successfully imported {success_count} runs ✓")


def import_targets_to_dynamodb(targets_data):
    """Import targets data to DynamoDB"""
    print(
        f"Importing {len(targets_data)} targets to DynamoDB table {DYNAMODB_TARGETS_TABLE}..."
    )

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(DYNAMODB_TARGETS_TABLE)

    success_count = 0

    for target in targets_data:
        try:
            # Convert data types for DynamoDB
            item = {
                "user_id": target["user_id"],
                "target_id": target["target_id"],
                "target_type": target["target_type"],
                "period": target["period"],
                "distance_km": Decimal(str(target["distance_km"])),
                "created_at": target["created_at"],
            }

            table.put_item(Item=item)
            success_count += 1

        except Exception as e:
            print(f"Error importing target {target.get('target_id', 'unknown')}: {e}")

    print(f"Successfully imported {success_count} targets ✓")


def test_connection():
    """Test AWS connections before importing"""
    print("Testing AWS connections...")

    try:
        # Test S3 connection
        s3 = boto3.client("s3")
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"✓ S3 bucket '{S3_BUCKET}' accessible")

        # Test DynamoDB connection
        dynamodb = boto3.resource("dynamodb")
        runs_table = dynamodb.Table(DYNAMODB_RUNS_TABLE)
        targets_table = dynamodb.Table(DYNAMODB_TARGETS_TABLE)

        runs_table.load()
        targets_table.load()
        print(f"✓ DynamoDB tables accessible:")
        print(f"  - {DYNAMODB_RUNS_TABLE}")
        print(f"  - {DYNAMODB_TARGETS_TABLE}")

        return True

    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Please check your AWS credentials and configuration.")
        return False


def main():
    """Main import process"""
    print("=== S3 to DynamoDB Import Tool ===")
    print()

    # Test connections first
    if not test_connection():
        return

    print()

    try:
        # Download and import runs
        runs_data = get_s3_csv_data(S3_BUCKET, S3_RUNS_KEY)
        import_runs_to_dynamodb(runs_data)

        print()

        # Download and import targets
        targets_data = get_s3_csv_data(S3_BUCKET, S3_TARGETS_KEY)
        import_targets_to_dynamodb(targets_data)

        print()
        print("=== Import Complete! ===")
        print(f"✓ Imported {len(runs_data)} runs")
        print(f"✓ Imported {len(targets_data)} targets")
        print("Your synthetic data is now ready for testing!")

    except Exception as e:
        print(f"❌ Import failed: {e}")


if __name__ == "__main__":
    main()
