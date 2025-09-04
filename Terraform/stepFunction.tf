# resource "aws_iam_role" "sfn_exec_role" {
#   name = "sfn_exec_role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = {
#         Service = "states.amazonaws.com"
#       }
#     }]
#   })
# }

# resource "aws_iam_role_policy" "sfn_policy" {
#   name = "sfn_policy"
#   role = aws_iam_role.sfn_exec_role.id
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action   = "lambda:InvokeFunction"
#       Effect   = "Allow"
#       Resource = aws_lambda_function.email_cleanup_lambda.arn
#     }]
#   })
# }

resource "aws_sfn_state_machine" "email_cleanup_step_function" {
  name     = "EmailCleanerStepFunction"
  role_arn = aws_iam_role.email_cleanup_lambda_role.arn
  definition = jsonencode({
    StartAt = "InvokeLambda"
    States = {
      InvokeLambda = {
        Type     = "Task"
        Resource = aws_lambda_function.email_cleanup_lambda.arn
        Retry = [
          {
            "ErrorEquals" : ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"],
            "IntervalSeconds" : 2,
            "MaxAttempts" : 3,
            "BackoffRate" : 2.0
          },
          {
            "ErrorEquals" : ["Sandbox.Timedout"],
            "IntervalSeconds" : 5,
            "MaxAttempts" : 5,
            "BackoffRate" : 1.5
          }
        ],
        End = true
      }
    }
  })
}
