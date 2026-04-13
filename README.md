# Stimpack: An Adaptive Rendering Optimization System for Scalable Cloud Gaming

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Paper](https://img.shields.io/badge/Paper-PDF-red)](https://arxiv.org/pdf/2412.19446.pdf)
[![DOI](https://zenodo.org/badge/DOI/10.xxxx/xxxx.svg)](https://doi.org/10.xxxx/xxxx)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Built with uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)](https://www.linux.org/)


Stimpack is the open-source implementation of the research paper **"Stimpack: An Adaptive Rendering Optimization System for Scalable Cloud Gaming"**.

In cloud gaming, high-quality rendering often yields diminishing returns on user-perceived quality when delivered over bandwidth-constrained or lossy networks. Stimpack solves this by adaptively balancing server-side rendering costs against user-perceived quality, maximizing system utility in multi-user scenarios.

<p align="center">
  <img src="figs/stim1.png" height="250" alt="Multi-user Scalability Concept" />
  &nbsp;&nbsp;&nbsp;&nbsp; <img src="figs/stim2.png" height="200" alt="Stimpack System Architecture" />
</p>
<p align="center">
  <em><b>Figure 1:</b> Strategic adaptation for multi-user scalability (Left) and the Stimpack System Architecture (Right).</em>
</p>

### Why Stimpack?
Cloud gaming GPUs are often shared among multiple users. Traditional systems waste resources by rendering at high quality even when the network is poor, leading to GPU bottlenecks and high latency.

**Stimpack maximizes efficiency by:**
- **Workload Adaptation**: Instead of blindly rendering at high quality, Stimpack dynamically scales down the Rendering Quality (RQ) for users under poor network conditions.
- **Utility Maximization**: By reducing unnecessary rendering load that would be lost anyway during network compression, we free up GPU resources to maintain a playable FPS for all concurrent users and accommodate twice the capacity of baseline systems.
- **Evaluated on Network Traces and Unreal Engine-powered Games**: We validate our approach using real-world 3G/4G network traces and Unreal Engine-based games.

---

### Visual Results (Demo)
The following demos show a side-by-side comparison in a multi-user scenario. **Stimpack (Left)** adaptively optimizes rendering quality, balancing performance and computational load.

<p align="center">
  <img src="figs/game1.gif" height="180" alt="Game 1 Demo" />
  <img src="figs/game2.gif" height="180" alt="Game 2 Demo" />
</p>
<p align="center">
  <em><b>Side-by-Side:</b> Stimpack (Left) vs. Non-Stimpack Baseline (Right).</em>
</p>

---

### System Architecture & Scope
As described in the paper, Stimpack consists of two main components: the **In-game Plugin** and the **Central Runtime**.

**This repository contains the official implementation of the Central Runtime and the Quality Prediction models.** It orchestrates the optimization process by communicating with game instances (plugins) to balance rendering costs and user-perceived quality.

1. **Information Manager**: Handles user registration and real-time network/rendering telemetry.
2. **Quality Predictor**: A pre-trained ML engine that estimates user-side VMAF.
3. **RQ Optimizer**: A round-based controller that executes the efficiency-score-based optimization.

---

### Core Components

The project is organized into three primary modules that correspond to the system's logic:

#### 1. `runtime/` — The "Brain" (Central Runtime)
The core execution engine that manages the real-time feedback loop.
* **`runner.py`**: The main orchestrator that runs the multi-threaded optimization environment.
* **`rq_manager.py`**: **[Paper §4.3]** Implements the round-based RQ optimization and efficiency scoring mechanism.
* **`user_registerer.py`**: **[Paper §4.1]** Manages user sessions and ZeroMQ-based IPC ports for game instances.
* **`fl_monitor.py`**: Monitors per-frame rendering latency to ensure SLO compliance.

#### 2. `models/` — The "Eyes" (Quality Predictor)
The pipeline for quantifying and predicting user-perceived quality.
* **`pred_vmaf/`**: **[Paper §4.2]** Contains the pre-trained regression models (Random Forest, SVR, etc.) used to predict VMAF from (Codec, RQ, QP) features.
* **`trained_models/`**: Ready-to-use `.pkl` model files for immediate deployment.
* **VMAF Pipeline**: Scripts to automate quality scoring using Docker-based `easyvmaf`.

#### 3. `net_data/` — The "Environment" (Network Traces)
Tools to simulate the "network-induced lossy compression" discussed in the paper.
* **Traces**: Real-world 3G and 4G network logs used for evaluation.
* **QP Traces**: Tools to convert raw throughput logs into the dynamic QP (Quantization Parameter) profiles that Stimpack reacts to.

---

### Installation & Usage

Stimpack requires Python 3.10+ and uses **uv** for efficient dependency management.

```bash
# Clone the repository
git clone https://github.com/jin-heo/Stimpack.git
cd Stimpack

# Install dependencies using uv
uv sync
```

#### 1. Running the Stimpack Runtime
Start the main quality manager to listen for users and manage rendering:

```bash
uv run runtime/runner.py [log_file] [case_name]
```

#### 2. Simulating Network Dynamics (QP Replay)
In a separate terminal, replay a network trace to simulate changing network quality for a specific user:

```bash
uv run runtime/replay_user_qp.py <user_id> <path_to_trace.csv>
```

#### 3. Training VMAF Models
To retrain the quality prediction models:

```bash
cd models/pred_vmaf
uv run 0_model_train_rev.py
```

---

### Citation
```bibtex
@inproceedings{heo2026stimpack,
  title={Stimpack: An Adaptive Rendering Optimization System for Scalable Cloud Gaming},
  author={Heo, Jin and Wang, Vic and Bhardwaj, Ketan and Gavrilovska, Ada},
  booktitle={23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI 26)},
  year={2026}
}
```

### License
Licensed under the [MIT License](LICENSE).

---

### 🕹️ Fun Fact: Why the name "Stimpack"?

The name **Stimpack** is a tribute to the iconic ability of the **Terran Marine** in Blizzard's *StarCraft* series.

In the game, a Marine injects a Stimpack to trade a bit of health for a massive boost in combat speed and efficiency.
Similarly, our system strategically adjusts (or "sacrifices") unnecessary rendering details to significantly boost the overall **scalability and utility** of the cloud gaming server.

As a former competitive *StarCraft* player, the lead author designed Stimpack with a "gamer-first" mindset: ensuring that every bit of computing power is spent where it actually improves the experience.

<p align="center">
  <img src="figs/marines.gif" width="400" alt="StarCraft Marine Stimpack" />
</p>
