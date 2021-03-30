resource "aws_s3_bucket" "eviction-bot-layers" {
  bucket = "${var.env.name}-eviction-bot-layers"
}

resource "aws_s3_bucket" "eviction-bot-metadata" {
  bucket = "${var.env.name}-eviction-bot-metadata"
}

resource "aws_s3_bucket_object" "dependencies-layer" {
  bucket = aws_s3_bucket.eviction-bot-layers.bucket
  key    = "${var.env.name}/dependencies-${var.app-version}"
  source = "dist/dependencies-layer.zip"
  etag   = filemd5("dist/dependencies-layer.zip")
}
