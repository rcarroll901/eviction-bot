terraform {
  backend "remote" {
    organization = "just-city"

    workspaces {
      prefix = "eviction-bot-"
    }
  }
}