# 🩺 Vital Sign Detection using Integrated Sensing and Communication (ISAC)

![Header](images/header.png) <!-- Replace with actual image path -->

This project is a **B.Tech thesis** submitted to **IIIT Kalyani**, which presents a Python-based simulation of a **Joint Radar-Communication system** for contactless monitoring of vital signs using a hybrid **LFM-OFDM** framework.

The system integrates **LFM radar sensing** with **OFDM communication** to detect respiration and heartbeat rates without any physical contact — suitable for modern healthcare and IoT applications.

---

## 📌 Table of Contents

- [🎯 Motivation](#-motivation)
- [📚 Project Summary](#-project-summary)
- [🧑‍💻 Authors & Guide](#-authors--guide)
- [📁 Folder Structure](#-folder-structure)
- [⚙️ Technologies Used](#️-technologies-used)
- [🚀 Setup & Installation](#-setup--installation)
- [🧪 Features & Modules](#-features--modules)
- [📊 Simulation Results](#-simulation-results)
- [📸 Screenshots](#-screenshots)
- [🔬 Future Work](#-future-work)
- [📬 Contact](#-contact)

---

## 🎯 Motivation

Traditional vital sign monitoring involves physical contact sensors such as ECG leads or chest belts. This is inconvenient, especially for:
- Elderly or critically ill patients
- High-infection-risk environments (e.g., COVID-19)
- Remote or long-term monitoring

**Goal:** Design a **contactless** monitoring system that can accurately extract heartbeat and respiration using radio-frequency signals.

---

## 📚 Project Summary

> **Title:** *Vital Sign Detection: Application of Integrated Sensing and Communication*  
> **Institute:** Indian Institute of Information Technology Kalyani  
> **Department:** Electronics and Communication Engineering  
> **Period:** July 2024 – May 2025  

### 🔍 Key Highlights:
- Simulated vital sign monitoring using reflected **LFM chirps**.
- Simultaneously simulated **OFDM communication** to transmit sensed data.
- Signal processing techniques such as **matched filtering**, **FFT**, and **phase extraction**.
- Built an interactive **GUI using Tkinter** for real-time monitoring.

---

## 🧑‍💻 Authors & Guide

| Name            | Reg. No.  | Role         |
|-----------------|-----------|--------------|
| Sayantan Majee  | 810       | Developer    |

**Supervisor:** Dr. Debasish Bera  
*Assistant Professor, Dept. of Computer Science and Engineering, IIIT Kalyani*

---

## 📁 Folder Structure

```plaintext
isac-vital-sign-detection/
├── README.md
├── gui.py
├── main.py
├── radar_module.py
├── ofdm_module.py
├── signal_processing.py
├── utils.py
├── requirements.txt
├── report/                       # Thesis report (PDF)
├── results/                      # Output plots and data
└── images/                       # Screenshots and diagrams
