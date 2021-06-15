resource "aws_sqs_queue" "eviction-bot-queue" {
  name                       = "${var.env.name}-eviction-bot"
  max_message_size           = 2048
  visibility_timeout_seconds = 7200 # 2 hrs

  # Retain messages in queue for at most 24 hours
  message_retention_seconds = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.eviction-bot-queue-deadletter.arn
    # Max # of receives before queue sends message to dead-letter queue
    maxReceiveCount = 1
  })

  tags = {
    Environment = var.env.name
  }
}

resource "aws_sqs_queue" "eviction-bot-queue-deadletter" {
  name             = "${var.env.name}-eviction-bot-deadletter"
  max_message_size = 2048

  tags = {
    Environment = var.env.name
  }
}
