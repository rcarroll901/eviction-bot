
variable "env" {
  description = "Environment settings"
  type = object({
    name                    = string
    SQS_URL                 = string
    CASE_LINK               = string
    NAME_SEARCH_LINK        = string
    AT_API_KEY              = string
    AT_BASE_KEY             = string
    AT_TABLE_NAME           = string
    AT_TABLE_NAME_APPLICANT = string
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
