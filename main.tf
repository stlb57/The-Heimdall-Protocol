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

# === DYNAMIC AMI LOOKUP ===
# This data source programmatically finds the latest Ubuntu 22.04 AMI.
# This is the professional way to avoid using static, hardcoded AMI IDs.
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical's official account ID
}


# 1. Create a Virtual Private Cloud (our own isolated network)
resource "aws_vpc" "heimdall_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "Heimdall-VPC"
  }
}

# 2. Create an Internet Gateway
resource "aws_internet_gateway" "heimdall_igw" {
  vpc_id = aws_vpc.heimdall_vpc.id
  tags = {
    Name = "Heimdall-IGW"
  }
}

# 3. Create a Subnet
resource "aws_subnet" "heimdall_subnet" {
  vpc_id                  = aws_vpc.heimdall_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "Heimdall-Subnet"
  }
}

# 4. Create a Route Table
resource "aws_route_table" "heimdall_rt" {
  vpc_id = aws_vpc.heimdall_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.heimdall_igw.id
  }

  tags = {
    Name = "Heimdall-RouteTable"
  }
}

# 5. Associate the Route Table
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.heimdall_subnet.id
  route_table_id = aws_route_table.heimdall_rt.id
}

# 6. Create a Security Group (Firewall)
resource "aws_security_group" "heimdall_sg" {
  name        = "heimdall-sg"
  description = "Allow SSH and App ports for Heimdall"
  vpc_id      = aws_vpc.heimdall_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 5001
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 5002
    to_port     = 5002
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "Heimdall-SG"
  }
}

# 7. Create the Drone Server
resource "aws_instance" "drone_server" {
  # Use the ID found by our dynamic data source
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  key_name      = "heimdall-key"

  subnet_id              = aws_subnet.heimdall_subnet.id
  vpc_security_group_ids = [aws_security_group.heimdall_sg.id]

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

# 8. Output the public IP
output "public_ip" {
  value = aws_instance.drone_server.public_ip
}
