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
                            docker run -d --rm -p 5001:5001 --name astronaut astronaut-simulator
                            docker run -d --rm -p 5002:5002 --name predictor prediction-api
EOF
                    """
                }
            }
        }

        stage('🔴 Monitor & Self-Heal') {
            steps {
                // THIS STAGE HAS BEEN REFACTORED TO RESOLVE THE SYNTAX ERROR
                script {
                    sshagent(credentials: ['aws-key']) {
                        timeout(time: 30, unit: 'MINUTES') {
                            def failureDetected = false
                            echo "Allowing 30 seconds for containers to initialize..."
                            sleep(30)

                            while (!failureDetected) {
                                try {
                                    // Get last 10 lines, filter for one that starts with '{', and get the last match.
                                    def telemetryLog = sh(script: "ssh -o StrictHostKeyChecking=no -o BatchMode=yes ubuntu@${env.SERVER_IP} 'docker logs --tail 10 astronaut | grep \"^{\" | tail -n 1'", returnStdout: true).trim()

                                    if (telemetryLog.isEmpty()) {
                                        echo "No valid JSON telemetry log found yet. Retrying in 5 seconds..."
                                    } else {
                                        echo "Found valid telemetry log: ${telemetryLog}"
                                        def predictionResponse = sh(script: "curl --fail --show-error --silent -X POST -H \"Content-Type: application/json\" -d '${telemetryLog}' http://${env.SERVER_IP}:5002/predict", returnStdout: true).trim()
                                        
                                        def responseJson = readJSON(text: predictionResponse)
                                        def failureProb = responseJson.failure_probability

                                        echo "Monitoring... Current Failure Probability: ${(failureProb * 100).round(2)}%"
                                        if (failureProb > 0.95) {
                                            echo "CRITICAL ALERT! FAILURE PROBABILITY EXCEEDS 95%!"
                                            echo "EXECUTING HEIMDALL PROTOCOL."
                                            failureDetected = true
                                            error("Heimdall Protocol Activated")
                                        }
                                    }
                                } catch (Exception e) {
                                    echo "Monitoring check failed: ${e.message}. The services might still be starting up. Retrying in 5 seconds..."
                                }
                                sleep(5)
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        unstable {
            script {
                sh 'terraform destroy -auto-approve'
                build job: 'heimdall-protocol'
            }
        }
        always {
            sh 'terraform destroy -auto-approve'
        }
    }
}
