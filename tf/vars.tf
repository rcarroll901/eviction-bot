
variable "env" {
  description = "Environment settings"
  type = object({
    name = string
    sqs_url = string
    spreadsheet_id = string
    sheet_name = string
    case_link = string
  })
}

variable "app-version" {
  description = "Version of the application"
  type        = string
  default     = "0.1.8"
}

variable "aws" {
  type = object({
    user   = string
    secret = string
  })
}
