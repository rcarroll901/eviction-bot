output "sqs-url" {
  value = aws_sqs_queue.eviction-bot-queue.id
}
