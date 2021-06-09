
provider "aws" {
  access_key = var.aws.user
  secret_key = var.aws.secret
  region     = "us-east-1"
}

data "aws_region" "active" {}
data "aws_caller_identity" "active" {}
