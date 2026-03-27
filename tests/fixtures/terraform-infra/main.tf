terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "example-tfstate"
    key    = "infra/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.region
}
