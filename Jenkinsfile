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

        // =================== MODIFIED SECTION START ===================
        stage('🔴 Monitor & Self-Heal') {
            steps {
                script {
                    try {
                        timeout(time: 30, unit: 'MINUTES') {
                            def failureDetected = false
                            sleep(45) // Allow containers to initialize
                            while (!failureDetected) {
                                // Get live telemetry directly from the simulator's API endpoint.
                                def telemetryData = sh(script: "curl --fail -s http://${env.SERVER_IP}:5001/telemetry", returnStdout: true).trim()

                                if (telemetryData) {
                                    // Send telemetry to the prediction API.
                                    def predictionResponse = sh(script: "curl --fail -s -X POST -H \"Content-Type: application/json\" -d '${telemetryData}' http://${env.SERVER_IP}:5002/predict", returnStdout: true).trim()

                                    if (predictionResponse) {
                                        def responseJson = readJSON(text: predictionResponse)
                                        def failureProb = responseJson.failure_probability
                                        echo "Monitoring... Current Failure Probability: ${(failureProb * 100).round(2)}%"

                                        if (failureProb > 0.90) {
                                            failureDetected = true
                                            // This error call is caught by the 'catch' block below
                                            error("Heimdall Protocol Activated: Failure probability exceeded 90%.")
                                        }
                                    }
                                }
                                sleep(5)
                            }
                        }
                    } catch (Exception e) {
                        // THIS IS THE SELF-HEALING LOGIC BLOCK
                        echo "🔴 CATCH BLOCK: SELF-HEALING PROTOCOL INITIATED due to: ${e.message}"

                        echo "🔵 STEP 1: Tearing down the old, unstable infrastructure..."
                        sh 'terraform destroy -auto-approve'

                        echo "🟢 STEP 2: Triggering a new build to provision fresh infrastructure. (Not waiting for completion)"
                        build job: 'heimdall-protocol', wait: false

                        // Explicitly set the build result so the 'always' block behaves correctly.
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        // =================== MODIFIED SECTION END =====================
    }
    // =================== MODIFIED POST BLOCK START ==================
    post {
        always {
            script {
                // This 'always' block is now only for normal cleanup.
                // It will only run if the pipeline completes successfully.
                if (currentBuild.result == 'SUCCESS') {
                    echo "✅ Pipeline finished with SUCCESS. Tearing down infrastructure as part of normal cleanup."
                    sh 'terraform destroy -auto-approve'
                } else {
                    echo "🟡 Pipeline did not finish successfully (Status: ${currentBuild.result}). Normal cleanup skipped to allow for investigation or self-healing."
                }
            }
        }
    }
    // =================== MODIFIED POST BLOCK END ====================
}

