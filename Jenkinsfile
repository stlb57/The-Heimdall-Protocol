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
                echo 'Initializing Terraform...'
                sh 'terraform init'
                echo 'Provisioning AWS EC2 instance...'
                sh 'terraform apply -auto-approve'
                echo 'Extracting server IP address...'
                sh "terraform output -raw public_ip > server_ip.txt"
                script {
                    env.SERVER_IP = readFile('server_ip.txt').trim()
                    echo "Drone server is online at: ${env.SERVER_IP}"
                }
            }
        }

        stage('🔵 Deploy Application') {
            steps {
                echo "Waiting for SSH on ${env.SERVER_IP} to be available..."
                sh "sleep 30 && until ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa ubuntu@${env.SERVER_IP} exit; do echo -n '.'; sleep 5; done"
                withCredentials([sshUserPrivateKey(credentialsId: 'aws-key', keyFileVariable: 'SSH_KEY')]) {
                    echo "Uploading project files..."
                    sh "scp -o StrictHostKeyChecking=no -i ${SSH_KEY} -r . ubuntu@${env.SERVER_IP}:~/heimdall-protocol"
                    echo "Executing remote deployment commands..."
                    sh """
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ubuntu@${env.SERVER_IP} << 'EOF'
                            set -e
                            cd ~/heimdall-protocol
                            echo "Building astronaut-simulator image..."
                            docker build -t astronaut-simulator ./simulator
                            echo "Building prediction-api image..."
                            docker build -t prediction-api ./prediction_api
                            echo "Launching astronaut-simulator container..."
                            docker run -d --rm -p 5001:5001 --name astronaut astronaut-simulator
                            echo "Launching prediction-api container..."
                            docker run -d --rm -p 5002:5002 --name predictor prediction-api
                            echo "✅ Deployment complete. All services are running."
                        EOF
                    """
                }
            }
        }

        stage('🔴 Monitor & Self-Heal') {
            steps {
                echo "Entering continuous monitoring loop. This stage will run for up to 30 minutes."
                timeout(time: 30, unit: 'MINUTES') {
                    script {
                        def failureDetected = false
                        while (!failureDetected) {
                            try {
                                def telemetryLog = sh(script: "ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa ubuntu@${env.SERVER_IP} 'docker logs --tail 1 astronaut'", returnStdout: true).trim()
                                def predictionResponse = sh(
                                    script: "curl -s -X POST -H \"Content-Type: application/json\" -d '${telemetryLog}' http://${env.SERVER_IP}:5002/predict",
                                    returnStdout: true
                                ).trim()
                                def responseJson = readJSON(text: predictionResponse)
                                def failureProb = responseJson.failure_probability
                                echo "Monitoring... Current Failure Probability: ${(failureProb * 100).round(2)}%"
                                if (failureProb > 0.95) {
                                    echo "CRITICAL ALERT! FAILURE PROBABILITY EXCEEDS 95%!"
                                    echo "EXECUTING HEIMDALL PROTOCOL."
                                    failureDetected = true
                                    error("Heimdall Protocol Activated")
                                }
                            } catch (Exception e) {
                                echo "Monitoring check failed: ${e.message}. Retrying..."
                            }
                            sleep(5)
                        }
                    }
                }
            }
        }
    }

    post {
        unstable {
            script {
                echo "Self-Healing: Destroying compromised infrastructure..."
                sh 'terraform destroy -auto-approve'
                echo "Self-Healing: Re-launching the mission to build fresh infrastructure."
                build job: 'heimdall-protocol'
            }
        }
        always {
            echo "Executing final cleanup..."
            sh 'terraform destroy -auto-approve'
            echo "Mission Complete. All infrastructure decommissioned."
        }
    }
}
