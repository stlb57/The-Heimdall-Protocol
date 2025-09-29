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
                sshagent(credentials: ['aws-key']) {
                    timeout(time: 30, unit: 'MINUTES') {
                        script {
                            def failureDetected = false
                            // Add a delay before the first monitoring check to allow containers to initialize.
                            sleep(45)
                            while (!failureDetected) {
                                try {
                                    // This improved command is more robust. It gets all logs, finds only the lines that are
                                    // JSON (by looking for '{' at the start), and takes the very last one.
                                    def telemetryLog = sh(script: "ssh -o StrictHostKeyChecking=no -o BatchMode=yes ubuntu@${env.SERVER_IP} 'docker logs astronaut | grep \"^{\" | tail -n 1'", returnStdout: true).trim()

                                    // Only proceed if a valid telemetry log was actually found.
                                    if (telemetryLog) {
                                        // We've added '--fail' to ensure that HTTP errors (like 400 or 500) cause this step to fail.
                                        def predictionResponse = sh(script: "curl --fail -s -X POST -H \"Content-Type: application/json\" -d '${telemetryLog}' http://${env.SERVER_IP}:5002/predict", returnStdout: true).trim()

                                        if (predictionResponse) {
                                            def responseJson = readJSON(text: predictionResponse)
                                            def failureProb = responseJson.failure_probability
                                            echo "Monitoring... Current Failure Probability: ${(failureProb * 100).round(2)}%"

                                            if (failureProb > 0.95) {
                                                echo "CRITICAL ALERT! FAILURE PROBABILITY EXCEEDS 95%!"
                                                echo "EXECUTING HEIMDALL PROTOCOL."
                                                failureDetected = true
                                                // The 'error' step marks the stage as unstable, which triggers the 'post' action.
                                                error("Heimdall Protocol Activated")
                                            }
                                        } else {
                                             echo "Received empty response from prediction API. Retrying..."
                                        }

                                    } else {
                                        echo "No valid JSON telemetry log found yet. Retrying..."
                                    }
                                } catch (Exception e) {
                                    // This block will now correctly catch failures from the ssh or curl commands.
                                    echo "Monitoring check failed: ${e.message}. Retrying..."
                                }
                                sleep(5) // Wait 5 seconds before the next check.
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
