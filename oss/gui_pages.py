# gui_pages.py
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Dict, Tuple, Any

import scheduling_logic as sl  # used in deadlock detection and scheduling helpers below

# small helper to format numeric outputs
def format_val(t, key):
    val = t.get(key)
    if isinstance(val, (int, float)):
        return f"{val:.2f}"
    return ''

# small center pack helper
def center_pack(widget, **kwargs):
    defaults = dict(padx=8, pady=6)
    defaults.update(kwargs)
    widget.pack(anchor='center', **defaults)

# ---------------- Dashboard ----------------
import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *

class DashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # MAIN CONTAINER - use grid for clean alignment
        self.columnconfigure(0, weight=1)

        # Title and subtitle
        title = ttk.Label(self, text='⚙ Smart CPU Scheduler & Manager',
                          font=('Segoe UI', 22, 'bold'))
        title.grid(row=0, column=0, pady=(30, 10), sticky='n')

        subtitle = ttk.Label(self,
                             text='A unified tool for scheduling, comparison, deadlock detection, and power analysis.',
                             font=('Segoe UI', 11))
        subtitle.grid(row=1, column=0, pady=(0, 25), sticky='n')

        # Info cards (row of small boxes)
        card_frame = ttk.Frame(self)
        card_frame.grid(row=2, column=0, pady=10)
        card_frame.columnconfigure((0, 1, 2, 3), weight=1)

        stats = [
            ('📋 Total Tasks', '0'),
            ('⚙ Algorithms', '7'),
            ('🔒 Deadlock Check', 'Available'),
            ('⚡ Power Analysis', 'Active')
        ]

        for i, (text, value) in enumerate(stats):
            card = ttk.Frame(card_frame, borderwidth=1, relief='solid', padding=10)
            card.grid(row=0, column=i, padx=15)
            ttk.Label(card, text=text, font=('Segoe UI', 10, 'bold')).pack()
            ttk.Label(card, text=value, font=('Segoe UI', 11, 'bold'), foreground='deepskyblue').pack()

        # Quick Start guide
        guide_frame = ttk.Frame(self)
        guide_frame.grid(row=3, column=0, pady=30)

        ttk.Label(guide_frame, text='🧭 Quick Start Guide',
                  font=('Segoe UI', 11, 'bold')).pack(pady=5)

        steps = [
            '1️⃣ Go to Task Manager → Add processes (Name, Arrival, Burst, Priority)',
            '2️⃣ Open Scheduler → Select algorithm → Run & view Gantt Chart',
            '3️⃣ Compare tab → Analyze Avg WT & TAT for all algorithms',
            '4️⃣ Deadlock tab → Visualize wait-for graph & detect cycles',
            '5️⃣ Power tab → Estimate CPU energy efficiency'
        ]

        for step in steps:
            ttk.Label(guide_frame, text=step, font=('Segoe UI', 10)).pack(anchor='w')

    def on_show(self):
        pass


# ---------------- Task Manager ----------------
class TaskManagerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        heading = ttk.Label(self, text='🧮 Task Manager', font=('Segoe UI', 16, 'bold'), anchor='center')
        heading.pack(pady=8)

        # form (centered)
        frm = ttk.Frame(self)
        frm.pack(pady=6)

        labels = ['Name', 'Arrival', 'Burst', 'Priority', 'Holding (R)', 'Waiting (R)']
        self.entries = {}
        for i, lbl in enumerate(labels):
            ttk.Label(frm, text=lbl + ':').grid(row=i, column=0, sticky='e', padx=6, pady=4)
            e = ttk.Entry(frm, width=24)
            e.grid(row=i, column=1, padx=6, pady=4)
            self.entries[lbl] = e

        # buttons centered
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text='Add Task', command=self.add_task).pack(side='left', padx=8)
        ttk.Button(btn_frame, text='Clear Selected', command=self.clear_selected).pack(side='left', padx=8)
        ttk.Button(btn_frame, text='Clear All', command=self.clear_all).pack(side='left', padx=8)
        ttk.Button(btn_frame, text='Import CSV', command=lambda: None).pack(side='left', padx=8)

        # Treeview (centered, all columns center-aligned)
        cols = ('pid', 'name', 'arrival', 'burst', 'priority', 'holding', 'waiting', 'ct', 'wt', 'tat')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=10)
        for c in cols:
            self.tree.heading(c, text=c.upper(), anchor='center')
            self.tree.column(c, width=100, anchor='center')
        # make some columns a bit wider
        self.tree.column('pid', width=60)
        self.tree.column('name', width=160)
        self.tree.column('holding', width=140)
        self.tree.column('waiting', width=140)
        self.tree.pack(fill='both', expand=True, padx=16, pady=12)

    def add_task(self):
        try:
            name = self.entries['Name'].get() or f'P{self.controller.next_pid}'
            arrival = int(self.entries['Arrival'].get() or 0)
            burst = int(self.entries['Burst'].get() or 1)
            priority = int(self.entries['Priority'].get() or 0)
            holding = self.entries['Holding (R)'].get().strip()
            waiting = self.entries['Waiting (R)'].get().strip()
            if burst < 1:
                messagebox.showerror('Invalid', 'Burst must be >= 1'); return
        except Exception:
            messagebox.showerror('Invalid', 'Arrival/Burst/Priority must be integers'); return

        self.controller.add_task(name, arrival, burst, priority, holding, waiting)
        self.update_table(self.controller.tasks)
        for e in self.entries.values(): e.delete(0, tk.END)

    def clear_all(self):
        if messagebox.askyesno('Confirm', 'Clear all tasks?'):
            self.controller.clear_tasks()
            self.update_table([])

    def clear_selected(self):
        """Delete only the selected task row from both table and controller list"""
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return

        if not messagebox.askyesno("Confirm", "Delete selected task?"):
            return

        for item in selected:
            values = self.table.item(item, "values")
            if not values:
                continue
            pid = int(values[0])  # assuming first column = PID
            self.controller.clear_selected_task(pid)

    def update_table(self, tasks):
        
        for r in self.tree.get_children():
            self.tree.delete(r)
        for t in sorted(tasks, key=lambda x: x['pid']):
            vals = (f"P{t['pid']}", t['name'], t['arrival'], t['burst'], t['priority'],
                    t.get('holding', ''), t.get('waiting', ''), format_val(t, 'completion'),
                    format_val(t, 'waiting_time'), format_val(t, 'turnaround'))
            
            self.tree.insert('', 'end', values=vals)

    def on_show(self):
        self.update_table(self.controller.tasks)

# ---------------- Scheduler ----------------
class SchedulerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        top = ttk.Frame(self)
        top.pack(pady=8)
        ttk.Label(top, text='Algorithm:').pack(side='left', padx=6)
        self.algo_combo = ttk.Combobox(top, values=['FCFS','SJF (Non-preemptive)','SJF (Preemptive)',
                                                    'Priority (Non-preemptive)','Priority (Preemptive)','LJF','Round Robin'], width=30, state='readonly')
        self.algo_combo.set('FCFS'); self.algo_combo.pack(side='left')
        ttk.Label(top, text='Quantum:').pack(side='left', padx=6)
        self.quant_entry = ttk.Entry(top, width=6); self.quant_entry.insert(0, '2'); self.quant_entry.pack(side='left')
        ttk.Button(top, text='Run', command=self.run_sched).pack(side='left', padx=8)
        ttk.Button(top, text='Refresh', command=self.refresh_table).pack(side='left')

        cols = ('pid','name','arrival','burst','priority','ct','wt','tat')
        self.table = ttk.Treeview(self, columns=cols, show='headings', height=7)
        for c in cols:
            self.table.heading(c, text=c.upper(), anchor='center')
            self.table.column(c, width=110, anchor='center')
        self.table.column('pid', width=60); self.table.column('name', width=160)
        self.table.pack(fill='x', padx=12, pady=8)

        self.fig = Figure(figsize=(10,3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=6)
        self.metrics_lbl = ttk.Label(self, text='Metrics: --', anchor='center')
        self.metrics_lbl.pack(pady=6)

    def refresh_table(self):
        for r in self.table.get_children():
            self.table.delete(r)
        for t in sorted(self.controller.tasks, key=lambda x: x['pid']):
            self.table.insert('', 'end', values=(f"P{t['pid']}", t['name'], t['arrival'], t['burst'],
                                                t['priority'], format_val(t, 'completion'),
                                                format_val(t, 'waiting_time'), format_val(t, 'turnaround')))

    def draw_gantt(self, timeline: List[Tuple[int, int, int]]):
        self.ax.clear()
        if not timeline:
            self.ax.set_title('No timeline'); self.canvas.draw_idle(); return

        ids = sorted(list({seg[0] for seg in timeline}))
        id_to_y = {pid: i for i, pid in enumerate(ids)}
        colors = ['#3b82f6','#22c55e','#f97316','#ef4444','#a78bfa','#06b6d4','#fde68a']

        for pid, s, e in timeline:
            y = id_to_y[pid]
            self.ax.barh(y, e - s, left=s, height=0.6,
                        color=colors[y % len(colors)], edgecolor='white')
            self.ax.text((s + e) / 2, y, f'P{pid}', va='center', ha='center',
                        color='white', fontsize=9)

        self.ax.set_yticks(list(id_to_y.values()))
        self.ax.set_yticklabels([f'P{pid}' for pid in ids])
        self.ax.set_xlabel('Time')
        self.ax.grid(True, linestyle='--', alpha=0.4)
        self.ax.set_title(f"Gantt Chart for {self.algo_combo.get()}")
        self.canvas.draw_idle()

    def run_sched(self):
        if not self.controller.tasks:
            messagebox.showwarning('No tasks', 'Add tasks first'); return
        algo = self.algo_combo.get()
        try:
            q = int(self.quant_entry.get())
        except Exception:
            q = 2
        tl, m = self.controller.run_scheduler(algo, quantum=q)
        self.controller.current_timeline = tl
        self.draw_gantt(tl)
        self.metrics_lbl.config(text=f"Metrics: Avg WT={m['avg_wait']:.2f}  Avg TAT={m['avg_tat']:.2f}  CPU%={m['cpu_util']:.1f}  Throughput={m['throughput']:.3f}")
        self.refresh_table()

    def on_show(self):
        self.refresh_table()

# ---------------- Compare ----------------
class ComparePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller
        center_pack(ttk.Button(self, text='Run Comparison (All Algos)', command=self.run_all))
        self.fig = Figure(figsize=(10,4), dpi=100); self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self); self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=6)
        self.table = ttk.Treeview(self, columns=('algo','avg_wt','avg_tat'), show='headings', height=6)
        for c in ('algo','avg_wt','avg_tat'):
            self.table.heading(c, text=c.upper(), anchor='center')
            self.table.column(c, width=200, anchor='center')
        self.table.pack(padx=12, pady=8)

    def run_all(self):
        if not self.controller.tasks:
            messagebox.showwarning('No tasks', 'Add tasks first'); return
        algos = ['FCFS','SJF (Non-preemptive)','SJF (Preemptive)','Priority (Non-preemptive)','Priority (Preemptive)','LJF','Round Robin']
        avg_w=[]; avg_t=[]; results={}
        for a in algos:
            tl, m = self.controller.run_scheduler(a, quantum=2)
            avg_w.append(m['avg_wait']); avg_t.append(m['avg_tat']); results[a]=m
        for r in self.table.get_children(): self.table.delete(r)
        for a in algos:
            self.table.insert('', 'end', values=(a, f"{results[a]['avg_wait']:.2f}", f"{results[a]['avg_tat']:.2f}"))
        self.ax.clear()
        x = list(range(len(algos)))
        bars = self.ax.bar(x, avg_w, label='Avg WT', alpha=0.8)
        self.ax.set_xticks(x); self.ax.set_xticklabels(algos, rotation=30, ha='right')
        ax2 = self.ax.twinx()
        ax2.plot(x, avg_t, marker='o', label='Avg TAT')
        self.ax.set_ylabel('Avg Waiting Time'); ax2.set_ylabel('Avg Turnaround Time')
        best_w = min(avg_w); best_w_idx = avg_w.index(best_w); bars[best_w_idx].set_color('#22c55e')
        best_t = min(avg_t); best_t_idx = avg_t.index(best_t)
        ax2.plot(best_t_idx, best_t, marker='o', markersize=12, color='#ff0066')
        self.ax.legend(loc='upper left'); ax2.legend(loc='upper right')
        self.ax.set_title('Comparison of Scheduling Algorithms')
        self.canvas.draw_idle()

    def on_show(self):
        pass

# ---------------- Deadlock ----------------
class DeadlockPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller
        top = ttk.Frame(self); top.pack(fill='x', padx=12, pady=8)
        ttk.Label(top, text='Process Name').grid(row=0, column=0); ttk.Label(top, text='Holding (R)').grid(row=0, column=1); ttk.Label(top, text='Waiting (R)').grid(row=0, column=2)
        self.p_name = ttk.Entry(top, width=16); self.p_name.grid(row=1, column=0, padx=6)
        self.p_hold = ttk.Entry(top, width=12); self.p_hold.grid(row=1, column=1, padx=6)
        self.p_wait = ttk.Entry(top, width=12); self.p_wait.grid(row=1, column=2, padx=6)
        ttk.Button(top, text='Add as Task (copy fields)', command=self.add_from_inputs).grid(row=1, column=3, padx=8)
        ttk.Button(top, text='Detect Deadlock', command=self.detect).grid(row=1, column=4, padx=8)
        ttk.Button(top, text='Refresh', command=self.refresh).grid(row=1, column=5, padx=6)

        cols = ('pid','name','holding','waiting')
        self.table = ttk.Treeview(self, columns=cols, show='headings', height=6)
        for c in cols:
            self.table.heading(c, text=c.upper(), anchor='center')
            self.table.column(c, width=120, anchor='center')
        self.table.pack(fill='x', padx=12, pady=8)

        self.fig = Figure(figsize=(8,4), dpi=100); self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self); self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=6)
        self.result_lbl = ttk.Label(self, text='', anchor='center'); self.result_lbl.pack(pady=6)

    def add_from_inputs(self):
        name = self.p_name.get().strip() or f'P{self.controller.next_pid}'
        holding = self.p_hold.get().strip(); waiting = self.p_wait.get().strip()
        self.controller.add_task(name, 0, 1, 0, holding, waiting)
        self.refresh()

    def refresh(self):
        for r in self.table.get_children(): self.table.delete(r)
        for t in sorted(self.controller.tasks, key=lambda x: x['pid']):
            self.table.insert('', 'end', values=(f"P{t['pid']}", t.get('name',''), t.get('holding',''), t.get('waiting','')))
        self.draw_graph([])

    def detect(self):
        tasks = self.controller.tasks
        found, cycle = sl.detect_deadlock_from_hold_wait(tasks)
        if found:
            involved_resources = set()
            for pid in cycle:
                tt = next((task for task in tasks if task['pid'] == pid), None)
                if tt:
                    if tt.get('holding'): involved_resources.add(tt.get('holding'))
                    if tt.get('waiting'): involved_resources.add(tt.get('waiting'))
            cycle_names = [f"P{pid}" for pid in cycle]
            self.result_lbl.config(text=f'❌ Deadlock detected! PIDs: {", ".join(cycle_names)}. Resources involved: {", ".join(involved_resources)}', foreground='red')
        else:
            self.result_lbl.config(text='✅ No deadlock detected', foreground='green')
        self.visualize_wait_for_graph(cycle if found else [])

    def visualize_wait_for_graph(self, cycle_nodes: List[int]):
        tasks = self.controller.tasks
        holders = {}
        for t in tasks:
            h = (t.get('holding') or '').strip()
            if h: holders.setdefault(h, []).append(t['pid'])
        edges = []
        for t in tasks:
            w = (t.get('waiting') or '').strip()
            if w:
                owners = holders.get(w, [])
                for o in owners:
                    if o != t['pid']:
                        edges.append((t['pid'], o))
        self.draw_graph(edges, cycle_nodes)

    def draw_graph(self, edges: List[Tuple[int,int]], cycle_nodes: List[int] = []):
        self.ax.clear()
        tasks = self.controller.tasks
        pid_to_task = {t['pid']: t for t in tasks}
        nodes = sorted({n for e in edges for n in e} | {t['pid'] for t in tasks})
        if not nodes:
            self.ax.text(0.5, 0.5, 'No nodes to display', ha='center'); self.ax.axis('off'); self.canvas.draw_idle(); return
        n = len(nodes); pos = {}
        for i, pid in enumerate(nodes):
            angle = 2 * math.pi * i / n
            pos[pid] = (math.cos(angle), math.sin(angle))
        for pid, (x, y) in pos.items():
            color = '#22c55e' if pid not in cycle_nodes else '#ef4444'
            self.ax.scatter(x, y, s=1200, color=color, zorder=3)
            name = pid_to_task.get(pid, {}).get('name', f'P{pid}')
            self.ax.text(x, y, f'{name}\n(P{pid})', ha='center', va='center', color='white', fontsize=9, zorder=4)
        for a, b in edges:
            x1, y1 = pos[a]; x2, y2 = pos[b]
            dx = x2 - x1; dy = y2 - y1
            dist = math.sqrt(dx*dx + dy*dy)
            offset_factor = 0.1 / dist if dist > 0 else 0
            x_start = x1 + dx * offset_factor; y_start = y1 + dy * offset_factor
            x_end = x2 - dx * offset_factor; y_end = y2 - dy * offset_factor
            arrow_color = '#ff0033' if (a in cycle_nodes or b in cycle_nodes) else '#000000'
            self.ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start), arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2, mutation_scale=15))
            mid_x = x1 + dx / 2.5; mid_y = y1 + dy / 2.5
            label_x = mid_x + dy * 0.05; label_y = mid_y - dx * 0.05
            waiting_resource = pid_to_task[a].get('waiting', '')
            self.ax.text(label_x, label_y, f'{waiting_resource} (Held by P{b})', fontsize=8, color='blue' if arrow_color == '#000000' else '#ff0033', ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))
        self.ax.axis('off'); self.ax.set_title('Wait-For Graph (red = in deadlock cycle) showing resources')
        self.canvas.draw_idle()

    def on_show(self):
        self.refresh()

# ---------------- Power ----------------
class PowerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller
        top = ttk.Frame(self)
        center_pack(top)
        ttk.Label(top, text='Power rate (energy per time unit)').pack(side='left', padx=6)
        self.rate = ttk.Entry(top, width=8); self.rate.insert(0, '1'); self.rate.pack(side='left', padx=6)
        ttk.Button(top, text='Compute Power Efficiency', command=self.compute_power).pack(side='left', padx=6)
        self.result_lbl = ttk.Label(self, text='Energy & Efficiency Stats will appear here.', anchor='center'); self.result_lbl.pack(pady=8)
        self.fig = Figure(figsize=(9, 4), dpi=100); 
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self); self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=6)

    def compute_power(self):
        if not getattr(self.controller, 'current_timeline', None):
            messagebox.showwarning('No schedule', 'Run a scheduling algorithm first.'); return
        try:
            rate = float(self.rate.get())
        except ValueError:
            messagebox.showerror('Invalid', 'Enter numeric rate value.'); return
        tl = self.controller.current_timeline
        min_start = min((s for (_, s, _) in tl), default=0)
        max_end = max((e for (_, _, e) in tl), default=0)
        total_time = max_end - min_start
        total_exec = sum(e - s for (_, s, e) in tl)
        idle_time = total_time - total_exec
        energy_used = total_exec * rate
        energy_idle = idle_time * (rate * 0.2)
        total_energy = energy_used + energy_idle
        efficiency = (energy_used / total_energy) * 100 if total_energy > 0 else 0
        self.result_lbl.config(text=(f"Total Span Time: {total_time} | Active Energy: {energy_used:.2f} | Idle Energy: {energy_idle:.2f} | Efficiency: {efficiency:.1f}%"))
        self.ax.clear()
        self.ax.bar(['Energy Usage'], [energy_used], label='Active Energy')
        self.ax.bar(['Energy Usage'], [energy_idle], bottom=[energy_used], label='Idle Energy (20% power)')
        self.ax.set_ylabel('Energy Units'); self.ax.set_title('Power Efficiency Visualization'); self.ax.legend()
        self.canvas.draw_idle()

    def on_show(self):
        pass
