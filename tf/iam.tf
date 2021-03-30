resource "aws_iam_role" "eviction-bot" {
  name               = "${var.env.name}-eviction-bot"
  assume_role_policy = data.aws_iam_policy_document.eviction-bot-assume.json
}

data "aws_iam_policy_document" "eviction-bot-assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "eviction-bot-cloudwatch" {
  role       = aws_iam_role.eviction-bot.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "eviction-bot" {
  role   = aws_iam_role.eviction-bot.id
  policy = data.aws_iam_policy_document.eviction-bot.json
}

data "aws_iam_policy_document" "eviction-bot" {
  statement {
    sid    = "AccessSQS"
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    resources = [
      aws_sqs_queue.eviction-bot-queue.arn,
    ]
  }

  statement {
    sid    = "AccessS3"
    effect = "Allow"
    actions = [
      "s3:*"
    ]
    resources = [
      "*",
    ]
  }
}