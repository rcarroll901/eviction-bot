
variable "env" {
  description = "Environment settings"
  type = object({
    name = string
    SQS_URL = string
    SPREADSHEET_ID = string
    SHEET_NAME = string
    CASE_LINK = string
    CASE_COL = string
    PASTE_COL_BEGIN = string
    PASTE_COL_END = string
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
