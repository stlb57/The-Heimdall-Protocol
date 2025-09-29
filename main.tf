terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "drone_server" {
  ami           = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"
  key_name      = "heimdall-key"

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y
              sudo apt-get install -y docker.io
              sudo systemctl start docker
              sudo systemctl enable docker
              sudo usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "Heimdall-Protocol-Drone"
  }
}

output "public_ip" {
  value = aws_instance.drone_server.public_ip
}
