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

        stage('🔴 Monitor System') {
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    script {
                        def failureDetected = false
                        sleep(45) // Allow containers to initialize
                        while (!failureDetected) {
                            try {
                                def telemetryData = sh(script: "curl --fail -s http://${env.SERVER_IP}:5001/telemetry", returnStdout: true).trim()
                                if (telemetryData) {
                                    def predictionResponse = sh(script: "curl --fail -s -X POST -H \"Content-Type: application/json\" -d '${telemetryData}' http://${env.SERVER_IP}:5002/predict", returnStdout: true).trim()
                                    if (predictionResponse) {
                                        def responseJson = readJSON(text: predictionResponse)
                                        def failureProb = responseJson.failure_probability
                                        echo "Monitoring... Current Failure Probability: ${(failureProb * 100).round(2)}%"
                                        if (failureProb > 0.90) {
                                            failureDetected = true
                                            // This will fail the stage and correctly set the build to UNSTABLE
                                            error("Heimdall Protocol Activated: Failure probability exceeded 90%.")
                                        }
                                    }
                                }
                            } catch (Exception e) {
                                // This catch is for network errors during monitoring, not for the failure condition itself
                                echo "Monitoring check failed with a network or command error: ${e.message}. Retrying..."
                            }
                            sleep(5)
                        }
                    }
                }
            }
        }
    }
    // =================== FINAL, CORRECTED POST BLOCK ===================
    post {
        // This block runs ONLY when the build is UNSTABLE (e.g., from our error() call)
        unstable {
            script {
                echo "🔴 SELF-HEALING: Build is UNSTABLE. Initiating recovery protocol."
                echo "STEP 1: Destroying faulty infrastructure..."
                sh 'terraform destroy -auto-approve'
                echo "STEP 2: Triggering new build to provision fresh infrastructure..."
                build job: 'heimdall-protocol', wait: false
            }
        }
        // This block runs ONLY on a completely successful build
        success {
            script {
                echo "✅ SUCCESS: Pipeline completed normally. Tearing down infrastructure."
                sh 'terraform destroy -auto-approve'
            }
        }
    }
}

