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
                                    // Step 1: Get live telemetry directly from the simulator's API endpoint.
                                    def telemetryData = sh(script: "curl --fail -s http://${env.SERVER_IP}:5001/telemetry", returnStdout: true).trim()

                                    if (telemetryData) {
                                        // Step 2: Send that telemetry to the prediction API.
                                        def predictionResponse = sh(script: "curl --fail -s -X POST -H \"Content-Type: application/json\" -d '${telemetryData}' http://${env.SERVER_IP}:5002/predict", returnStdout: true).trim()

                                        if (predictionResponse) {
                                            def responseJson = readJSON(text: predictionResponse)
                                            def failureProb = responseJson.failure_probability
                                            echo "Monitoring... Current Failure Probability: ${(failureProb * 100).round(2)}%"

                                            if (failureProb > 0.90) {
                                                echo "CRITICAL ALERT! FAILURE PROBABILITY EXCEEDS 90%!"
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
    // =================== MODIFIED SECTION START ===================
    post {
        unstable {
            script {
                echo "🔴 Self-healing triggered due to UNSTABLE status."
                
                echo "🔵 STEP 1: Tearing down the old, unstable infrastructure..."
                sh 'terraform destroy -auto-approve'

                echo "🟢 STEP 2: Triggering a new build to provision fresh infrastructure. (Not waiting for completion)"
                // This is the critical fix. 'wait: false' tells Jenkins to start the
                // new build and immediately let this current build finish, avoiding a deadlock.
                build job: 'heimdall-protocol', wait: false
            }
        }
        always {
            script {
                // This 'always' block is for normal cleanup. The condition ensures it does NOT
                // run during a self-healing event, preventing a double-destroy command.
                if (currentBuild.result != 'UNSTABLE') {
                    echo "Pipeline finished. Tearing down infrastructure as part of normal cleanup."
                    sh 'terraform destroy -auto-approve'
                }
            }
        }
    }
    // =================== MODIFIED SECTION END =====================
}

