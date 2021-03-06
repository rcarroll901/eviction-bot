resource "aws_cloudwatch_event_rule" "daily_rule" {
  name                = "daily-at-noon"
  description         = "Run every day at noon"
  schedule_expression = "cron(0 10 ? * 2,3,4,5,6 *)"
}

resource "aws_cloudwatch_event_target" "daily_target" {
  rule  = aws_cloudwatch_event_rule.daily_rule.name
  arn   = aws_lambda_function.eviction-bot.arn
}