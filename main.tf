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
  user_data = <<-EOF
              #!/bin/bash
              # Update the package list
              sudo apt-get update -y
              
              # Install Docker
              sudo apt-get install -y docker.io
              
              # Start the Docker service
              sudo systemctl start docker
              
              # Enable Docker to start on boot
              sudo systemctl enable docker
              
              # Add the 'ubuntu' user to the 'docker' group so we can run
              # Docker commands without sudo. This is critical for Jenkins.
              sudo usermod -aG docker ubuntu
              EOF
  tags = {
    Name = "Heimdall-Protocol-Drone"
  }
}

output "public_ip" {
  value = aws_instance.drone_server.public_ip
}