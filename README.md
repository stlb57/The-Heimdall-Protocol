🚀 Heimdall Protocol — Autonomous Self-Healing Infrastructure
A fully autonomous AIOps experiment that predicts infrastructure failure — and rebuilds itself before it crashes.

How do you save an astronaut when you're 400 km away and their life support is failing?
You don’t wait for alerts. You predict the failure — and rebuild the system before it breaks.

Heimdall Protocol is an experimental self-healing framework built with AWS + Terraform + Jenkins + Docker + Machine Learning.

It simulates real-time astronaut vitals, predicts anomalies using an ML model, and when a critical failure is detected, it automatically destroys and rebuilds its own infrastructure — without human intervention.

🛰️ Mission Control Dashboard
🔮 Predict → Act → Heal
Phase

Component

Description

SIMULATE

astronaut.py

Streams fake heart rate, oxygen, temperature — with fault injection.

PREDICT

app.py + OneClassSVM

ML model calculates real-time failure probability.

HEAL

Jenkins + Terraform

If probability > 90%, the system destroys and rebuilds itself.

⚙️ System Architecture
The architecture uses a decoupled, two-pipeline design to prevent deadlocks and ensure a reliable hand-off between building and healing.

+----------------------+       +----------------------+
| Jenkins Job #1       |       | Jenkins Job #2       |
| heimdall-protocol    |       | heimdall-monitor     |
| "The Builder"        |       | "The Healer"         |
+----------------------+       +----------------------+
           |                                     ^
           | Provision & Deploy                  | Re-Trigger
           v                                     |
   +-------------------------------------------------------------+
   |                       AWS EC2 Instance                      |
   |                                                             |
   |  [Docker Container: Simulator] <---> [Docker Container: ML]   |
   |                                                             |
   +-------------------------------------------------------------+
           ^                                     |
           | Archive State &                     | Destroy
           | Trigger Monitor                     |
           +-------------------> Monitor <-----------------------+

🔄 Self-Healing Cycle — Fully Automated
✅ Build & Deploy (heimdall-protocol job)

📦 Archive terraform.tfstate as a build artifact.

🤝 Trigger Monitor with the new EC2 instance IP.

🧠 Continuously Predict failure probability by calling the APIs.

🚨 Threshold Breach → The monitor job calls error(), failing the build.

🔥 Destroy Infrastructure → The post { failure } block copies the artifact and runs terraform destroy.

🚀 Rebuild Instance → The monitor's final step triggers a new heimdall-protocol job.

🚀 Getting Started
✅ Requirements
An AWS Account & IAM Access Key

Terraform & AWS CLI

A running Jenkins Server

Docker Installed

Setup Overview
Configure Jenkins:

Install Terraform and Copy Artifact plugins.

Add AWS & SSH credentials.

Create Two Pipelines:

heimdall-protocol → uses Jenkinsfile

heimdall-monitor → uses Jenkinsfile.monitor (and requires a SERVER_IP string parameter).

Launch:

Manually start the heimdall-protocol job. The monitor will take over automatically upon successful deployment.

📁 Project Structure
.
├── Jenkinsfile           # <-- The "Builder" pipeline
├── Jenkinsfile.monitor   # <-- The "Healer" pipeline
├── main.tf               # Terraform Infrastructure as Code
├── create_model.py       # Script to train & export the ML model
├── index.html            # Mission Control Dashboard UI
│
├── simulator/
│   ├── astronaut.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── prediction_api/
    ├── app.py
    ├── model.pkl
    ├── Dockerfile
    └── requirements.txt
