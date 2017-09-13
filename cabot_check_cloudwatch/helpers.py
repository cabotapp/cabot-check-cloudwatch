import boto3


def get_boto_client(cloudwatch_config):
    return boto3.client('cloudwatch',
        region_name=cloudwatch_config.aws_region,
        aws_access_key_id=cloudwatch_config.aws_access_key_id,
        aws_secret_access_key=cloudwatch_config.aws_secret_access_key,
        aws_session_token=cloudwatch_config.aws_session_token,
    )
