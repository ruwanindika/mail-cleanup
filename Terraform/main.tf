# IAM role for Lambda execution
data "aws_iam_policy_document" "lambda_assum_role_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "email_cleanup_lambda_role" {
  name               = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assum_role_policy.json
}

# Package the Lambda function code
data "archive_file" "email_cleanup_lambda" {
  type        = "zip"
  source_file = "${path.module}/../src/email_cleaner_lambda/lambda_function.py"
  output_path = "${path.module}/../src/email_cleaner_lambda/function.zip"
}

# Lambda function
resource "aws_lambda_function" "email_cleanup_lambda" {
  filename         = data.archive_file.email_cleanup_lambda.output_path
  function_name    = "email_cleanup_lambda"
  role             = aws_iam_role.email_cleanup_lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.email_cleanup_lambda.output_base64sha256

  runtime = "python3.13"

  layers = [aws_lambda_layer_version.gmail_api_lib.arn]


  environment {
    variables = {
      ENVIRONMENT = "production"
      LOG_LEVEL   = "info"
    }
  }

  tags = {
    Environment = "production"
    Application = "email_cleanup_lambda"
  }
}

# Package the Lambda layer 
data "archive_file" "lambda_layer_zip" {
  type        = "zip"
  source_dir = "${path.module}/../dependencies/python"
  output_path = "${path.module}/../dependencies/python.zip"
}

# lambda layer 
resource "aws_lambda_layer_version" "gmail_api_lib" {
  filename   = data.archive_file.lambda_layer_zip.output_path
  layer_name = "gmail_api_lib"
  source_code_hash = data.archive_file.lambda_layer_zip.output_base64sha256
  compatible_runtimes = ["python3.13"]
}