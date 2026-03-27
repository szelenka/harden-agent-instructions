resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-cluster"
}

resource "aws_ecs_service" "app" {
  name            = "${var.environment}-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.environment}-app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512

  container_definitions = jsonencode([{
    name  = "app"
    image = var.image
    portMappings = [{
      containerPort = 8080
    }]
  }])
}

variable "environment" {
  type = string
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "image" {
  type = string
}
