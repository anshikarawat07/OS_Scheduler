# ⚙️ Smart CPU Scheduler & Manager

A modern CPU Scheduling Simulator built using **Python**, **Tkinter**, **TkinterBootstrap**, and **Matplotlib**.  
This project provides Gantt chart visualization, algorithm comparison, deadlock detection, Banker's algorithm, and power-efficiency analysis — all inside a clean GUI.

---

# 📥 Download & Run

## 1️⃣ Clone the Project
```bash
git clone https://github.com/anshikarawat07/OS_Scheduler.git
cd OS_Scheduler
```

---

# 🔧 Install Requirements

### Option A — Install from requirements.txt (recommended)
```bash
pip install -r requirements.txt
```

### Option B — Install manually
```bash
pip install ttkbootstrap matplotlib
```

*(Tkinter is already included with Python.)*

---

# ▶️ Run the Application
```bash
python oss/main.py
```

The GUI will open with all scheduling and analysis tools.

---

# 🚀 Features

## 🧮 CPU Scheduling Algorithms
- FCFS  
- SJF (Non-Preemptive)  
- SJF (Preemptive / SRTF)  
- Priority (Non-Preemptive)  
- Priority (Preemptive)  
- LJF  
- Round Robin  

## 📊 Gantt Chart Visualization
- Auto-generated timeline  
- Color-coded process blocks  

## 📈 Metrics Calculated
- Avg Waiting Time  
- Avg Turnaround Time  
- CPU Utilization  
- Throughput  
- Total Execution Time  

## 🆚 Algorithm Comparison
- Compare all algorithms together  
- Bar + Line chart combination  
- Auto-highlights best performers  

## 🔒 Deadlock Detection
- Hold-and-Wait based detection  
- Wait-For Graph generation  
- Cycle detection using DFS  
- Shows involved processes/resources  

## 🔐 Banker's Algorithm (Safe State)
- Validates safe vs unsafe state  
- Resource request analysis  

## ⚡ Power Efficiency
- Active vs idle energy  
- Efficiency percentage  
- Energy visualization graph  

---

# 🖥️ Application Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Overview of system |
| **Task Manager** | Add/edit/delete tasks |
| **Scheduler** | Run algorithms + Gantt chart |
| **Compare** | Compare all scheduling algorithms |
| **Deadlock** | Detect and explain deadlocks |
| **Power** | Energy & efficiency analysis |

---

# 📁 Project Structure

```
OS_Scheduler/
│
├── oss/
│   ├── app_controller.py
│   ├── gui_pages.py
│   ├── scheduling_logic.py
│   └── requirements.txt
│
├── README.md

```

---

# 🎯 Purpose

Useful for:
- OS Lab Assignments  
- Scheduling Algorithm Demonstrations  
- Academic Learning  
- Visualization of OS concepts  
- Deadlock detection practice  

---

# 🤝 Contributing

Contributions, improvements, and suggestions are welcome.


# 📜 License

Free for educational and learning use.
