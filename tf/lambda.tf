resource "aws_lambda_function" "eviction-bot" {
  function_name = "${var.env.name}-eviction-bot"
  runtime       = "python3.7"
  memory_size   = 2048
  role          = aws_iam_role.eviction-bot.arn
  reserved_concurrent_executions = 3

  # Code artifact + dependencies
  filename         = "dist/eviction-bot-lambda.zip"
  source_code_hash = filebase64sha256("dist/eviction-bot-lambda.zip")
  layers           = [aws_lambda_layer_version.dependencies.arn]

  # Handler function name
  handler = "runner.lambda_handler"

  # timeout is measured in n seconds
  timeout = 30

  environment {
    variables = {
      SQS_URL = var.env.SQS_URL
      CASE_LINK = var.env.CASE_LINK
      AT_API_KEY = var.env.AT_API_KEY
      AT_BASE_KEY = var.env.AT_BASE_KEY
      AT_TABLE_NAME = var.env.AT_TABLE_NAME
      NAME_SEARCH_LINK = var.env.NAME_SEARCH_LINK
      AT_TABLE_NAME_APPLICANT= var.env.AT_TABLE_NAME_APPLICANT
    }
  }

  tags = {
    Environment = var.env.name,
  }
}

resource "aws_lambda_layer_version" "dependencies" {
  layer_name  = "${var.env.name}-eviction-bot-dependencies"
  description = "Selenium + Chromedriver webscraping dependencies"
  s3_bucket   = aws_s3_bucket.eviction-bot-layers.bucket
  s3_key      = aws_s3_bucket_object.dependencies-layer.id
  source_code_hash = filebase64sha256("dist/dependencies-layer.zip")
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_event_source_mapping" "eviction-bot-queue-trigger" {
  event_source_arn = aws_sqs_queue.eviction-bot-queue.arn
  function_name    = aws_lambda_function.eviction-bot.arn
  # can scale how many messages get sent at once (tunable = can make var)
  batch_size = 1
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id   = "AllowExecutionFromCloudWatch"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.eviction-bot.arn
  principal      = "events.amazonaws.com"
  source_arn     = aws_cloudwatch_event_rule.daily_rule.arn
}