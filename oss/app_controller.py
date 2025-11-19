import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import List, Dict, Tuple, Any

# scheduling_logic must exist in same folder
import scheduling_logic as sl
from gui_pages import DashboardPage, TaskManagerPage, SchedulerPage, ComparePage, DeadlockPage, PowerPage


class SmartSchedulerApp(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")  # Default theme
        self.title('Smart CPU Scheduler & Manager')
        self.geometry('1200x760')

        self.tasks: List[Dict[str, Any]] = []
        self.next_pid = 1
        self.current_timeline: List[Tuple[int, int, int]] = []

        self.rowconfigure(0, weight=0)   # nav
        self.rowconfigure(1, weight=1)   # pages area
        self.columnconfigure(0, weight=1)

        # Navigation bar
        self._create_nav()

        self.pages = {}
        for P in (DashboardPage, TaskManagerPage, SchedulerPage, ComparePage, DeadlockPage, PowerPage):
            frame = P(parent=self, controller=self)
            self.pages[P.__name__] = frame
            frame.grid(row=1, column=0, sticky='nsew')
            frame.grid_remove()  # hide for now

        # Show default page
        self.show_page('DashboardPage')

    def _create_nav(self):
        nav = ttk.Frame(self)
        nav.grid(row=0, column=0, sticky='ew', padx=4, pady=(6, 4))

        # keep nav visually separated
        nav.columnconfigure(0, weight=1)
        btn_frame = ttk.Frame(nav)
        btn_frame.grid(row=0, column=0)  

        btns = [
            ('🏠 Dashboard', 'DashboardPage'),
            ('🧮 Task Manager', 'TaskManagerPage'),
            ('⚙ Scheduler', 'SchedulerPage'),
            ('📊 Compare', 'ComparePage'),
            ('🔒 Deadlock', 'DeadlockPage'),
            ('⚡ Power', 'PowerPage')
        ]

        for txt, page in btns:
            b = ttk.Button(
                btn_frame,
                text=txt,
                command=lambda p=page: self.show_page(p),
                bootstyle="primary-outline"
            )
            b.pack(side='left', padx=8)

    def show_page(self, name: str):
        for k, p in self.pages.items():
            p.grid_remove()
        page = self.pages.get(name)
        if page is None:
            return
        page.grid()   
        page.tkraise()
        if hasattr(page, 'on_show'):
            try:
                page.on_show()
            except Exception:
                pass

    def add_task(self, name, arrival, burst, priority, holding, waiting):
        try:
            arrival_i = int(arrival)
        except Exception:
            arrival_i = 0
        try:
            burst_i = max(1, int(burst))
        except Exception:
            burst_i = 1
        try:
            priority_i = int(priority)
        except Exception:
            priority_i = 0

        t = {
            'pid': self.next_pid,
            'name': (name or f"P{self.next_pid}"),
            'arrival': arrival_i,
            'burst': burst_i,
            'priority': priority_i,
            'holding': (holding or '').strip(),
            'waiting': (waiting or '').strip()
        }
        self.tasks.append(t)
        self.next_pid += 1

        if 'TaskManagerPage' in self.pages:
            try:
                self.pages['TaskManagerPage'].update_table(self.tasks)
            except Exception:
                pass

    def clear_tasks(self):
        """Clear all tasks"""
        self.tasks = []
        self.next_pid = 1
        if 'TaskManagerPage' in self.pages:
            try:
                self.pages['TaskManagerPage'].update_table([])
            except Exception:
                pass
    def clear_selected_task(self, pid: int):
        """Remove a single task from the internal task list by PID"""
        self.tasks = [t for t in self.tasks if t['pid'] != pid]
        self.next_pid = len(self.tasks) + 1
        if 'TaskManagerPage' in self.pages:
            self.pages['TaskManagerPage'].update_table(self.tasks)


    def run_scheduler(self, algo: str, quantum: int = 2):
        """Run selected scheduling algorithm"""
        tasks_snapshot = [dict(t) for t in self.tasks]
        if not tasks_snapshot:
            return [], {'avg_wait': 0, 'avg_tat': 0, 'cpu_util': 0, 'throughput': 0, 'total_exec': 0}

        if algo == 'FCFS':
            tl = sl.sched_fcfs(tasks_snapshot)
        elif algo == 'SJF (Non-preemptive)':
            tl = sl.sched_sjf(tasks_snapshot, preemptive=False)
        elif algo == 'SJF (Preemptive)':
            tl = sl.sched_sjf(tasks_snapshot, preemptive=True)
        elif algo == 'Priority (Non-preemptive)':
            tl = sl.sched_priority(tasks_snapshot, preemptive=False)
        elif algo == 'Priority (Preemptive)':
            tl = sl.sched_priority(tasks_snapshot, preemptive=True)
        elif algo == 'LJF':
            tl = sl.sched_ljf(tasks_snapshot)
        elif algo == 'Round Robin':
            tl = sl.sched_rr(tasks_snapshot, quantum)
        else:
            tl = sl.sched_fcfs(tasks_snapshot)

        metrics = sl.compute_metrics(tasks_snapshot, tl)

       
        for snap in tasks_snapshot:
            for t in self.tasks:
                if t['pid'] == snap['pid']:
                    t.update({k: v for k, v in snap.items() if k in ('start', 'completion', 'waiting_time', 'turnaround')})

        self.current_timeline = tl
        return tl, metrics


