# Event bridge scheduler
resource "aws_scheduler_schedule" "lambda_fn_schedule" {
  name                         = "my-daily-lambda-schedule"
  schedule_expression          = "cron(15 02 * * ? *)"
  schedule_expression_timezone = "Australia/Sydney"
  flexible_time_window {
    mode                      = "FLEXIBLE"
    maximum_window_in_minutes = 15
  }

  target {
    arn      = aws_sfn_state_machine.email_cleanup_step_function.arn
    role_arn = aws_iam_role.email_cleanup_lambda_role.arn

    retry_policy {
      maximum_event_age_in_seconds = 3600 # Retry for up to 1hr
      maximum_retry_attempts       = 10   # Maximum of 10 retry attempts
    }
  }


}
