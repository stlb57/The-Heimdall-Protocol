// heimdall-protocol/Jenkinsfile

pipeline {
    agent any

    tools {
        terraform 'terraform-latest'
    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        TF_IN_AUTOMATION      = 'true'
    }

    stages {
        stage('🟢 Provision Drone') {
            steps {
                sh 'terraform init'
                sh 'terraform apply -auto-approve'
                sh "terraform output -raw public_ip > server_ip.txt"
                script {
                    env.SERVER_IP = readFile('server_ip.txt').trim()
                    echo "Drone server is online at: ${env.SERVER_IP}"
                }
            }
        }

        stage('🔵 Deploy Application') {
            steps {
                 sshagent(credentials: ['aws-key']) {
                    sh "sleep 30 && until ssh -o StrictHostKeyChecking=no -o BatchMode=yes ubuntu@${env.SERVER_IP} 'docker --version'; do echo 'Waiting for Docker to be ready...'; sleep 10; done"
                    sh "tar -czvf heimdall-protocol.tar.gz --exclude='.git' --exclude='temp_model_env' --exclude='.terraform' --exclude='*.tfstate*' ."
                    sh "scp -o StrictHostKeyChecking=no -o BatchMode=yes heimdall-protocol.tar.gz ubuntu@${env.SERVER_IP}:~/"
                    sh """
                        ssh -o StrictHostKeyChecking=no -o BatchMode=yes ubuntu@${env.SERVER_IP} << 'EOF'
                            set -e
                            mkdir -p heimdall-protocol
                            tar -xzvf heimdall-protocol.tar.gz -C heimdall-protocol
                            cd heimdall-protocol
                            docker build -t astronaut-simulator ./simulator
                            docker build -t prediction-api ./prediction_api
                            docker stop astronaut || true && docker rm astronaut || true
                            docker stop predictor || true && docker rm predictor || true
                            docker run -d -p 5001:5001 --name astronaut astronaut-simulator
                            docker run -d -p 5002:5002 --name predictor prediction-api
EOF
                    """
                 }
            }
        }
    }
    post {
        success {
            script {
                // ✅ STEP 1: Archive the Terraform state so the monitor can use it.
                echo "Archiving Terraform state files..."
                archiveArtifacts artifacts: 'terraform.tfstate*', followSymlinks: false

                // ✅ STEP 2: Hand off to the monitoring pipeline.
                echo "BUILD SUCCESSFUL. Handing off to the monitoring pipeline..."
                def serverIp = readFile('server_ip.txt').trim()
                build job: 'heimdall-monitor',
                      parameters: [string(name: 'SERVER_IP', value: serverIp)],
                      wait: false
            }
        }
    }
}
