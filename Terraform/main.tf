# IAM role for Lambda execution
data "aws_iam_policy_document" "lambda_assum_role_policy" {
  statement {
    sid    = "1"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com", "scheduler.amazonaws.com", "states.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }

}

resource "aws_iam_role" "email_cleanup_lambda_role" {
  name               = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assum_role_policy.json
}

resource "aws_iam_policy" "ssm_parameter_access_policy" {
  name        = "ssm-parameter-read-write-policy"
  description = "IAM policy to allow read access to specific SSM parameters"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "ssm:PutParameter"
        ]
        Resource = "arn:aws:ssm:us-east-1:161580273020:parameter/mail_credentials"
      }
    ]
  })
}

resource "aws_iam_policy" "ses_send_email_policy" {
  name        = "ses_send_email_policy"
  description = "IAM policy to allowses_send_email_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_execution_policy" {
  name        = "lambda_execution_policy"
  description = "IAM policy to lambda_execution_policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          "arn:aws:lambda:us-east-1:161580273020:function:email_cleanup_lambda:*",
          "arn:aws:lambda:us-east-1:161580273020:function:email_cleanup_lambda"
        ]
      }
    ]
  })
}

# resource "aws_iam_policy" "sfn_execution_policy" {
#   name        = "sfn_execution_policy"
#   description = "IAM policy to sfn_execution_policy"
#   policy = jsonencode({
#     "Version" : "2012-10-17",
#     "Statement" : [
#       {
#         "Effect" : "Allow",
#         "Action" : "states:StartExecution",
#         "Resource" : aws_sfn_state_machine.email_cleanup_step_function.arn
#       }
#     ]
#   })
# }

resource "aws_iam_role_policy_attachment" "attach_sfn_policy_to_role" {
  role       = aws_iam_role.email_cleanup_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"
}

resource "aws_iam_role_policy_attachment" "attach_ssm_policy_to_role" {
  role       = aws_iam_role.email_cleanup_lambda_role.name
  policy_arn = aws_iam_policy.ssm_parameter_access_policy.arn
}


resource "aws_iam_role_policy_attachment" "attach_eventbridge_policy_to_role" {
  role       = aws_iam_role.email_cleanup_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "attach_ses_policy_to_role" {
  role       = aws_iam_role.email_cleanup_lambda_role.name
  policy_arn = aws_iam_policy.ses_send_email_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_lambda_execution_role" {
  role       = aws_iam_role.email_cleanup_lambda_role.name
  policy_arn = aws_iam_policy.lambda_execution_policy.arn
}


# Package the Lambda function code
data "archive_file" "email_cleanup_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../src/email_cleaner_lambda"
  output_path = "${path.module}/../src/email_cleaner_lambda/function.zip"
}

# Lambda function
resource "aws_lambda_function" "email_cleanup_lambda" {
  filename         = data.archive_file.email_cleanup_lambda.output_path
  function_name    = "email_cleanup_lambda"
  role             = aws_iam_role.email_cleanup_lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.email_cleanup_lambda.output_base64sha256
  timeout          = 900
  memory_size      = 512

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

# log retention
resource "aws_cloudwatch_log_group" "my_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.email_cleanup_lambda.function_name}"
  retention_in_days = 7
}

