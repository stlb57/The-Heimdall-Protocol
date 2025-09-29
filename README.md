🚀 **Heimdall Protocol — Autonomous Self-Healing Infrastructure**
*A fully autonomous AIOps experiment that predicts infrastructure failure — and rebuilds itself before it crashes.*

---

### 🧠 Concept

**How do you save an astronaut when you're 400 km away and their life support is failing?**
You don’t wait for alerts.
You **predict the failure — and rebuild the system before it breaks.**

**Heimdall Protocol** is an experimental self-healing framework built with:

> **AWS + Terraform + Jenkins + Docker + Machine Learning**

It **simulates real-time astronaut vitals**, **predicts anomalies using an ML model**, and when a critical failure is detected...

> ⚠️ **It destroys and rebuilds its own infrastructure — without human intervention.**

---

### 🛰️ Mission Control Dashboard – *Predict → Act → Heal*

| Phase        | Component              | Description                                                          |
| ------------ | ---------------------- | -------------------------------------------------------------------- |
| **SIMULATE** | `astronaut.py`         | Streams fake heart rate, oxygen, temperature — with fault injection. |
| **PREDICT**  | `app.py` + OneClassSVM | ML model calculates real-time failure probability.                   |
| **HEAL**     | Jenkins + Terraform    | If probability > 90%, the system destroys and rebuilds itself.       |

---

### ⚙️ System Architecture (Dual-Pipeline Design)

Prevents deadlocks and ensures a clean hand-off between **building** and **healing**.

```
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
   |  [Docker: Simulator] <---> [Docker: ML API]                 |
   |                                                             |
   +-------------------------------------------------------------+
           ^                                     |
           | Archive State &                     | Destroy
           | Trigger Monitor                     |
           +-------------------> Monitor <-----------------------+
```

---

### 🔄 Self-Healing Cycle — *Fully Automated*

✅ **Build & Deploy** → archive `terraform.tfstate`
🤝 **Trigger monitor job** with new server IP
🧠 **Predict continuously via APIs**
🚨 **Threshold breach** → job fails intentionally
🔥 **Terraform destroy**
🚀 **Rebuild from scratch**

---

### 🚀 Getting Started

**Requirements**

* AWS Account + IAM Access
* Terraform & AWS CLI
* Jenkins Server
* Docker Installed

**Setup**

1. Install **Terraform** & **Copy Artifact** plugins in Jenkins
2. Add **AWS & SSH credentials**
3. Create **Two Pipelines**:

```
heimdall-protocol   → uses Jenkinsfile
heimdall-monitor    → uses Jenkinsfile.monitor (SERVER_IP param)
```

4. **Run manually once** — then monitoring takes over forever.

---

### 📁 Project Structure

```
.
├── Jenkinsfile           # Builder pipeline
├── Jenkinsfile.monitor   # Healer pipeline
├── main.tf
├── create_model.py
├── index.html            # Mission Control Dashboard
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
```

---

