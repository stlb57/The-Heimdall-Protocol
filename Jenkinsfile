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
                            
                            echo "Building astronaut simulator..."
                            docker build -t astronaut-simulator ./simulator
                            
                            echo "Building prediction API..."
                            docker build -t prediction-api ./prediction_api
                            
                            # --- THIS IS THE FIX ---
                            # Always stop and remove old containers before starting new ones.
                            echo "Cleaning up old containers..."
                            docker stop astronaut || true && docker rm astronaut || true
                            docker stop predictor || true && docker rm predictor || true
                            
                            echo "Launching new containers..."
                            docker run -d -p 5001:5001 --name astronaut astronaut-simulator
                            docker run -d -p 5002:5002 --name predictor prediction-api
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
                            sleep(45) // Allow containers to initialize
                            while (!failureDetected) {
                                try {
                                    def telemetryLog = sh(script: "ssh -o StrictHostKeyChecking=no -o BatchMode=yes ubuntu@${env.SERVER_IP} 'docker logs astronaut 2>/dev/null | grep \"^{\\\"heart_rate\" | tail -n 1'", returnStdout: true).trim()

                                    if (telemetryLog) {
                                        def predictionResponse = sh(script: "curl --fail -s -X POST -H \"Content-Type: application/json\" -d '${telemetryLog}' http://${env.SERVER_IP}:5002/predict", returnStdout: true).trim()

                                        if (predictionResponse) {
                                            def responseJson = readJSON(text: predictionResponse)
                                            def failureProb = responseJson.failure_probability
                                            echo "Monitoring... Current Failure Probability: ${(failureProb * 100).round(2)}%"

                                            if (failureProb > 0.95) {
                                                echo "CRITICAL ALERT! FAILURE PROBABILITY EXCEEDS 95%!"
                                                echo "EXECUTING HEIMDALL PROTOCOL."
                                                failureDetected = true
                                                error("Heimdall Protocol Activated") // Trigger 'unstable' post-build action
                                            }
                                        }
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
    }
    post {
        unstable {
            script {
                echo "Self-healing triggered. Rebuilding infrastructure..."
                sh 'terraform destroy -auto-approve'
                build job: 'heimdall-protocol'
            }
        }
        always {
            script {
                // Ensure cleanup happens even on a successful or aborted build
                if (currentBuild.result != 'UNSTABLE') {
                    echo "Pipeline finished. Tearing down infrastructure..."
                    sh 'terraform destroy -auto-approve'
                }
            }
        }
    }
}
