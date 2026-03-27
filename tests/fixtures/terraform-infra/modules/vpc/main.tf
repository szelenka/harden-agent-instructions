resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"

  tags = {
    Name = "${var.environment}-public"
  }
}

variable "environment" {
  type = string
}

variable "region" {
  type = string
}

output "vpc_id" {
  value = aws_vpc.main.id
}
