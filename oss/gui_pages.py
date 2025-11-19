import math
import csv
import io
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Dict, Tuple, Any
import scheduling_logic as sl  # keep your logic here

# ---------------- Utilities ----------------
def format_val(t, key):
    val = t.get(key)
    if isinstance(val, (int, float)):
        return f"{val:.2f}"
    return ''

def center_pack(widget, **kwargs):
    defaults = dict(padx=8, pady=6)
    defaults.update(kwargs)
    widget.pack(anchor='center', **defaults)

# Simple tooltip implementation (works with ttk/ttkbootstrap)
class Tooltip:
    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self.win = None
        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def schedule(self, _=None):
        self._id = self.widget.after(self.delay, self.show)

    def show(self):
        if self.win or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = ttk.Label(tw, text=self.text, relief="solid", padding=6, background="#ffffe0")
        lbl.pack()

    def hide(self, _=None):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        if self.win:
            self.win.destroy()
            self.win = None

# Small helper to confirm deletion
def confirm_delete(title="Confirm", text="Are you sure?"):
    return messagebox.askyesno(title, text)

# ---------------- Main Pages ----------------

# DashboardPage
# class DashboardPage(ttk.Frame):
#     def __init__(self, parent, controller):
#         super().__init__(parent, padding=12)
#         self.controller = controller

#         # Header
#         hdr = ttk.Frame(self)
#         hdr.pack(fill='x', pady=(6, 16))
#         title = ttk.Label(hdr, text='⚙ Smart CPU Scheduler & Manager', font=('Segoe UI', 20, 'bold'))
#         title.pack(side='left', padx=6)
#         subtitle = ttk.Label(hdr, text='Unified scheduling, deadlock detection & power analysis', font=('Segoe UI', 10))
#         subtitle.pack(side='left', padx=12, pady=6)

#         # Theme quick chooser on the right
#         theme_fr = ttk.Frame(hdr)
#         theme_fr.pack(side='right')
#         ttk.Label(theme_fr, text='Theme:').pack(side='left', padx=(0,6))
#         self.theme_var = tk.StringVar(value=tb.Style().theme.name)
#         self.theme_combo = tb.Combobox(theme_fr, values=list(tb.Style().theme_names()), textvariable=self.theme_var, width=12, state='readonly')
#         # self.theme_combo = tb.Combobox(theme_fr, values=list(tb.Style().themes()), textvariable=self.theme_var, width=12, state='readonly')
#         self.theme_combo.pack(side='left')
#         self.theme_combo.bind('<<ComboboxSelected>>', self.change_theme)
#         Tooltip(self.theme_combo, "Switch UI theme instantly")

#         # Metric cards
#         card_row = ttk.Frame(self)
#         card_row.pack(fill='x', pady=(6, 16))
#         card_row.columnconfigure((0,1,2,3), weight=1)

#         self.cards = {}
#         stats = [
#             ('Total Tasks', '0', 'info'),
#             ('Algorithms', '7', 'success'),
#             ('Deadlock', 'Available', 'warning'),
#             ('Power', 'Active', 'danger')
#         ]
#         for i, (label, value, tag) in enumerate(stats):
#             frame = tb.Frame(card_row, bootstyle=f"{tag}.TFrame", padding=(12,10))
#             frame.grid(row=0, column=i, padx=8, sticky='ew')
#             lbl = ttk.Label(frame, text=label, font=('Segoe UI', 10, 'bold'))
#             lbl.pack(anchor='w')
#             val_lbl = ttk.Label(frame, text=value, font=('Segoe UI', 14, 'bold'))
#             val_lbl.pack(anchor='w', pady=(6,0))
#             self.cards[label] = val_lbl

#         # Quick guide area
#         guide = tb.LabelFrame(self, text='🧭 Quick Start', padding=12)
#         guide.pack(fill='x', pady=(8,12))
#         steps = [
#             '1. Add processes in Task Manager (Name, Arrival, Burst, Priority).',
#             '2. Run Scheduler → choose algorithm → view Gantt chart.',
#             '3. Compare algorithms to inspect Avg WT & TAT.',
#             '4. Use Deadlock tab to visualize wait-for graph and detect cycles.',
#             '5. Power tab shows estimated energy usage & efficiency.'
#         ]
#         for s in steps:
#             ttk.Label(guide, text=s, font=('Segoe UI', 10)).pack(anchor='w', pady=2)

#         # Footer status
#         self.status = ttk.Label(self, text='Status: Ready', font=('Segoe UI', 9, 'italic'))
#         self.status.pack(anchor='w', pady=(10,0))

#     def change_theme(self, _=None):
#         theme = self.theme_var.get()
#         try:
#             tb.Style().theme.use(theme)
#             self.status.config(text=f"Status: Theme switched to {theme}")
#         except Exception as e:
#             messagebox.showerror("Theme Error", f"Could not apply theme: {e}")

    def on_show(self):
        # Update total tasks card
        total = len(getattr(self.controller, 'tasks', []))
        self.cards['Total Tasks'].config(text=str(total))
        self.status.config(text=f"Status: {total} tasks loaded")
class DashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ---- Theme Setup ----
        style = tb.Style()
        style.theme_use("flatly")  # default theme
        self.theme_var = tk.StringVar(value="flatly")

        # ---- Header ----
        header = ttk.Label(self, text="⚙ Smart CPU Scheduler & Manager",
                           font=("Segoe UI", 24, "bold"), anchor="center")
        header.pack(pady=(30, 10))

        subtitle = ttk.Label(self,
                             text="Unified interface for scheduling, comparison, deadlock detection, and power analysis.",
                             font=("Segoe UI", 11),
                             foreground="gray")
        subtitle.pack(pady=(0, 20))

        # ---- Theme Selector ----
        theme_fr = ttk.Frame(self)
        theme_fr.pack(pady=10)
        ttk.Label(theme_fr, text="🎨 Theme:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        self.theme_combo = tb.Combobox(theme_fr,
                                       values=list(style.theme_names()),
                                       textvariable=self.theme_var,
                                       width=15,
                                       state="readonly")
        self.theme_combo.pack(side="left", padx=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        # ---- Cards Section ----
        card_frame = ttk.Frame(self)
        card_frame.pack(pady=30)

        stats = [
            ('📋 Total Tasks', '0', 'info'),
            ('⚙ Algorithms', '7', 'success'),
            ('🔒 Deadlock Check', 'Available', 'warning'),
            ('⚡ Power Analysis', 'Active', 'danger')
        ]

        # Two rows of cards for spacing
        for i in range(0, len(stats), 2):
            row = ttk.Frame(card_frame)
            row.pack(pady=15)
            for text, value, color in stats[i:i + 2]:
                card = tb.Frame(row, padding=20, style=f"{color}.TFrame")
                card.pack(side='left', padx=20, ipadx=10, ipady=10)
                ttk.Label(card, text=text, font=('Segoe UI', 11, 'bold')).pack(pady=(0, 5))
                ttk.Label(card, text=value, font=('Segoe UI', 13, 'bold')).pack()

        # ---- Quick Start Guide ----
        guide_frame = ttk.LabelFrame(self, text='🧭 Quick Start Guide', padding=15)
        guide_frame.pack(pady=30, fill='x', padx=40)

        steps = [
            '① Add processes in “Task Manager” tab.',
            '② Run the selected algorithm in “Scheduler”.',
            '③ Compare metrics like Avg WT & TAT in “Compare”.',
            '④ Detect resource cycles in “Deadlock Detector”.',
            '⑤ Visualize energy efficiency in “Power Analysis”.'
        ]
        for step in steps:
            ttk.Label(guide_frame, text=step, font=('Segoe UI', 10)).pack(anchor='w', pady=3)

        # ---- Footer ----
        footer = ttk.Label(self, text="Developed by OSS Team | Smart Scheduler v2.0",
                           font=("Segoe UI", 9), foreground="gray")
        footer.pack(side="bottom", pady=10)

    # Theme change function
    def change_theme(self, event=None):
        selected = self.theme_var.get()
        self.controller.style.theme_use(selected)
        # Force a full refresh for visible widgets
        for child in self.controller.winfo_children():
            child.update_idletasks()

# Task Manager
class TaskManagerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        heading = ttk.Label(self, text='🧮 Task Manager', font=('Segoe UI', 16, 'bold'))
        heading.pack(pady=6)

        frm = ttk.Frame(self)
        frm.pack(pady=6, fill='x')

        # Left: form
        form = ttk.Frame(frm)
        form.pack(side='left', padx=(0,20))
        labels = ['Name', 'Arrival', 'Burst', 'Priority', 'Holding (R)', 'Waiting (R)']
        self.entries = {}
        for i, lbl in enumerate(labels):
            ttk.Label(form, text=lbl+':').grid(row=i, column=0, sticky='e', padx=6, pady=4)
            e = ttk.Entry(form, width=22)
            e.grid(row=i, column=1, padx=6, pady=4)
            self.entries[lbl] = e
            Tooltip(e, f"Enter {lbl}")

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=(8,0))
        add_btn = tb.Button(btn_frame, text='Add Task', bootstyle='success', command=self.add_task)
        add_btn.pack(side='left', padx=6)
        Tooltip(add_btn, "Add this process to the task list")
        clear_sel = tb.Button(btn_frame, text='Delete Selected', bootstyle='danger-outline', command=self.clear_selected)
        clear_sel.pack(side='left', padx=6)
        Tooltip(clear_sel, "Delete selected process row")
        clear_all = tb.Button(btn_frame, text='Clear All', bootstyle='secondary-outline', command=self.clear_all)
        clear_all.pack(side='left', padx=6)
        Tooltip(clear_all, "Remove all tasks")

        import_btn = tb.Button(btn_frame, text='Import CSV', bootstyle='info-outline', command=self.import_csv)
        import_btn.pack(side='left', padx=6)
        Tooltip(import_btn, "Import tasks from CSV (name,arrival,burst,priority,holding,waiting)")

        # Right: preview area
        preview = ttk.Frame(frm)
        preview.pack(side='left', fill='both', expand=True)

        cols = ('pid', 'name', 'arrival', 'burst', 'priority', 'holding', 'waiting', 'ct', 'wt', 'tat')
        self.tree = ttk.Treeview(preview, columns=cols, show='headings', height=11)
        for c in cols:
            self.tree.heading(c, text=c.upper(), anchor='center')
            anchor = 'center'
            self.tree.column(c, width=100, anchor=anchor)
        self.tree.column('pid', width=60)
        self.tree.column('name', width=140)
        self.tree.pack(fill='both', expand=True, padx=6, pady=8)
        self.tree.bind("<Double-1>", self._on_edit_double_click)

        # Status
        self.stat_lbl = ttk.Label(self, text='0 tasks', font=('Segoe UI', 9))
        self.stat_lbl.pack(anchor='w', padx=8)

    # CSV import
    def import_csv(self):
        path = filedialog.askopenfilename(title='Select CSV', filetypes=[('CSV files','*.csv'), ('All','*.*')])
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                count = 0
                for row in reader:
                    if not row: continue
                    # accept variety of lengths
                    name = row[0] if len(row) > 0 and row[0] else None
                    arrival = int(row[1]) if len(row) > 1 and row[1] != '' else 0
                    burst = int(row[2]) if len(row) > 2 and row[2] != '' else 1
                    priority = int(row[3]) if len(row) > 3 and row[3] != '' else 0
                    holding = row[4] if len(row) > 4 else ''
                    waiting = row[5] if len(row) > 5 else ''
                    self.controller.add_task(name or f'P{self.controller.next_pid}', arrival, burst, priority, holding, waiting)
                    count += 1
                messagebox.showinfo('Import', f'Imported {count} rows from CSV.')
                self.update_table(self.controller.tasks)
        except Exception as e:
            messagebox.showerror('Import Error', f'Failed to import CSV: {e}')

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
        if not confirm_delete('Confirm', 'Clear all tasks?'):
            return
        self.controller.clear_tasks()
        self.update_table([])
        messagebox.showinfo('Cleared', 'All tasks cleared.')

    def clear_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        if not confirm_delete("Confirm", "Delete selected task(s)?"):
            return
        deleted = 0
        for item in selected:
            values = self.tree.item(item, "values") or ()
            if not values: continue
            pidstr = values[0]
            # pid stored as "P{pid}" so strip leading P
            pid = int(str(pidstr).lstrip('P'))
            self.controller.clear_selected_task(pid)
            deleted += 1
        self.update_table(self.controller.tasks)
        messagebox.showinfo('Deleted', f'Deleted {deleted} task(s).')

    def update_table(self, tasks):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for t in sorted(tasks, key=lambda x: x['pid']):
            vals = (f"P{t['pid']}", t.get('name',''), t.get('arrival',''), t.get('burst',''), t.get('priority',''),
                    t.get('holding',''), t.get('waiting',''), format_val(t, 'completion'), format_val(t, 'waiting_time'),
                    format_val(t, 'turnaround'))
            self.tree.insert('', 'end', values=vals)
        self.stat_lbl.config(text=f"{len(tasks)} tasks")

    def _on_edit_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item, 'values')
        if not values:
            return
        pid = int(str(values[0]).lstrip('P'))
        task = next((t for t in self.controller.tasks if t['pid'] == pid), None)
        if not task:
            return
        # Open small edit dialog
        dlg = tk.Toplevel(self)
        dlg.title(f"Edit P{pid}")
        dlg.transient(self)
        dlg.grab_set()
        fields = ['name','arrival','burst','priority','holding','waiting']
        entries = {}
        for i, f in enumerate(fields):
            ttk.Label(dlg, text=f.capitalize()+':').grid(row=i, column=0, padx=8, pady=6, sticky='e')
            e = ttk.Entry(dlg, width=24)
            e.grid(row=i, column=1, padx=8, pady=6)
            e.insert(0, str(task.get(f, '')))
            entries[f] = e
        def save():
            try:
                name = entries['name'].get()
                arrival = int(entries['arrival'].get() or 0)
                burst = int(entries['burst'].get() or 1)
                priority = int(entries['priority'].get() or 0)
            except Exception:
                messagebox.showerror('Invalid', 'Arrival/Burst/Priority must be integers'); return
            # update controller task (assumes controller exposes update_task)
            if hasattr(self.controller, 'update_task'):
                self.controller.update_task(pid, name=name, arrival=arrival, burst=burst, priority=priority,
                                            holding=entries['holding'].get(), waiting=entries['waiting'].get())
            else:
                # fallback: mutate task dict
                task.update({'name':name, 'arrival':arrival, 'burst':burst, 'priority':priority,
                             'holding':entries['holding'].get(), 'waiting':entries['waiting'].get()})
            self.update_table(self.controller.tasks)
            dlg.destroy()
        tb.Button(dlg, text='Save', bootstyle='success', command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def on_show(self):
        self.update_table(getattr(self.controller, 'tasks', []))

# Scheduler Page
class SchedulerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        top = ttk.Frame(self)
        top.pack(pady=8, fill='x')
        ttk.Label(top, text='Algorithm:').pack(side='left', padx=(6,4))
        self.algo_combo = ttk.Combobox(top, values=['FCFS','SJF (Non-preemptive)','SJF (Preemptive)',
                                                    'Priority (Non-preemptive)','Priority (Preemptive)','LJF','Round Robin'],
                                       width=28, state='readonly')
        self.algo_combo.set('FCFS'); self.algo_combo.pack(side='left')
        Tooltip(self.algo_combo, "Choose scheduling algorithm")

        ttk.Label(top, text='Quantum:').pack(side='left', padx=(12,4))
        self.quant_entry = ttk.Entry(top, width=6); self.quant_entry.insert(0, '2'); self.quant_entry.pack(side='left')

        run_btn = tb.Button(top, text='Run', bootstyle='primary', command=self.run_sched)
        run_btn.pack(side='left', padx=8)
        Tooltip(run_btn, "Run the selected algorithm")

        refresh_btn = tb.Button(top, text='Refresh', bootstyle='secondary-outline', command=self.refresh_table)
        refresh_btn.pack(side='left')
        Tooltip(refresh_btn, "Refresh table from tasks")

        # Table for results
        cols = ('pid','name','arrival','burst','priority','ct','wt','tat')
        self.table = ttk.Treeview(self, columns=cols, show='headings', height=7)
        for c in cols:
            self.table.heading(c, text=c.upper(), anchor='center')
            self.table.column(c, width=110, anchor='center')
        self.table.column('pid', width=60); self.table.column('name', width=160)
        self.table.pack(fill='x', padx=12, pady=8)

        # Chart area
        self.fig = Figure(figsize=(10,3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=6)

        # Summary cards and progress
        bottom = ttk.Frame(self)
        bottom.pack(fill='x', pady=(6,0))
        self.avg_w_lbl = ttk.Label(bottom, text='Avg WT: --', font=('Segoe UI', 10))
        self.avg_w_lbl.pack(side='left', padx=12)
        self.avg_t_lbl = ttk.Label(bottom, text='Avg TAT: --', font=('Segoe UI', 10))
        self.avg_t_lbl.pack(side='left', padx=12)
        self.cpu_lbl = ttk.Label(bottom, text='CPU%: --', font=('Segoe UI', 10))
        self.cpu_lbl.pack(side='left', padx=12)
        self.through_lbl = ttk.Label(bottom, text='Throughput: --', font=('Segoe UI', 10))
        self.through_lbl.pack(side='left', padx=12)

        self.progress = ttk.Progressbar(bottom, mode='determinate', length=180)
        self.progress.pack(side='right', padx=12)
        Tooltip(self.progress, "Shows progress while plotting Gantt chart")

        self.current_timeline = []

    def refresh_table(self):
        for r in self.table.get_children():
            self.table.delete(r)
        for t in sorted(getattr(self.controller, 'tasks', []), key=lambda x: x['pid']):
            self.table.insert('', 'end', values=(f"P{t['pid']}", t.get('name',''), t.get('arrival',''), t.get('burst',''),
                                                t.get('priority',''), format_val(t, 'completion'),
                                                format_val(t, 'waiting_time'), format_val(t, 'turnaround')))

    def draw_gantt(self, timeline: List[Tuple[int, int, int]]):
        self.ax.clear()
        if not timeline:
            self.ax.set_title('No timeline'); self.canvas.draw_idle(); return

        ids = sorted(list({seg[0] for seg in timeline}))
        id_to_y = {pid: i for i, pid in enumerate(ids)}
        # nicer palette
        colors = ['#3b82f6','#22c55e','#f97316','#ef4444','#a78bfa','#06b6d4','#fde68a']

        for i, (pid, s, e) in enumerate(timeline):
            y = id_to_y[pid]
            self.ax.barh(y, e - s, left=s, height=0.6, color=colors[y % len(colors)], edgecolor='white')
            self.ax.text((s + e) / 2, y, f'P{pid}', va='center', ha='center', color='white', fontsize=9)

        self.ax.set_yticks(list(id_to_y.values()))
        self.ax.set_yticklabels([f'P{pid}' for pid in ids])
        self.ax.set_xlabel('Time')
        self.ax.grid(True, linestyle='--', alpha=0.4)
        self.ax.set_title(f"Gantt Chart — {self.algo_combo.get()}")
        self.canvas.draw_idle()

    def run_sched(self):
        if not getattr(self.controller, 'tasks', []):
            messagebox.showwarning('No tasks', 'Add tasks first'); return
        algo = self.algo_combo.get()
        try:
            q = int(self.quant_entry.get())
        except Exception:
            q = 2
        # show small progress while running
        self.progress.configure(maximum=100)
        self.progress.start(10)
        try:
            tl, m = self.controller.run_scheduler(algo, quantum=q)
        finally:
            self.progress.stop()
        self.controller.current_timeline = tl
        self.current_timeline = tl
        # update UI metrics
        self.avg_w_lbl.config(text=f"Avg WT: {m['avg_wait']:.2f}")
        self.avg_t_lbl.config(text=f"Avg TAT: {m['avg_tat']:.2f}")
        self.cpu_lbl.config(text=f"CPU%: {m.get('cpu_util',0):.1f}")
        self.through_lbl.config(text=f"Throughput: {m.get('throughput',0):.3f}")
        self.draw_gantt(tl)
        self.refresh_table()

    def on_show(self):
        self.refresh_table()

# Compare Page
class ComparePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller
        top = ttk.Frame(self)
        top.pack(fill='x', pady=(6,8))
        tb.Button(top, text='Run Comparison (All Algos)', bootstyle='info', command=self.run_all).pack(side='left', padx=8)
        tb.Button(top, text='Save Chart', bootstyle='secondary-outline', command=self.save_chart).pack(side='left')

        self.fig = Figure(figsize=(10,4), dpi=100); self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self); self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=6)

        self.table = ttk.Treeview(self, columns=('algo','avg_w','avg_t'), show='headings', height=6)
        for c in ('algo','avg_w','avg_t'):
            self.table.heading(c, text=c.upper(), anchor='center')
            self.table.column(c, width=220, anchor='center')
        self.table.pack(padx=12, pady=8, fill='x')

    def run_all(self):
        if not getattr(self.controller, 'tasks', []):
            messagebox.showwarning('No tasks', 'Add tasks first')
            return

        # Define algorithms
        algos = [
            'FCFS', 'SJF (Non-preemptive)', 'SJF (Preemptive)',
            'Priority (Non-preemptive)', 'Priority (Preemptive)',
            'LJF', 'Round Robin'
        ]

        avg_w = []
        avg_t = []
        results = {}

        # Run all algorithms
        for a in algos:
            tl, m = self.controller.run_scheduler(a, quantum=2)
            avg_w.append(m['avg_wait'])
            avg_t.append(m['avg_tat'])
            results[a] = m

        # Clear old table rows
        for r in self.table.get_children():
            self.table.delete(r)

        # Insert new results
        for a in algos:
            self.table.insert('', 'end', values=(
                a, f"{results[a]['avg_wait']:.2f}", f"{results[a]['avg_tat']:.2f}"
            ))

        # --- Clear both axes properly ---
        self.fig.clf()  # clear entire figure (including twin axes)
        self.ax = self.fig.add_subplot(111)

        # --- Redraw chart ---
        x = list(range(len(algos)))
        bars = self.ax.bar(x, avg_w, label='Avg WT', alpha=0.9)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(algos, rotation=30, ha='right')

        ax2 = self.ax.twinx()
        ax2.plot(x, avg_t, marker='o', label='Avg TAT')

        # Highlight best performers
        best_w = min(avg_w)
        best_w_idx = avg_w.index(best_w)
        bars[best_w_idx].set_color('#22c55e')

        best_t = min(avg_t)
        best_t_idx = avg_t.index(best_t)
        ax2.plot(best_t_idx, best_t, marker='o', markersize=12, color='#ff0066')

        # Labels and legends
        self.ax.set_ylabel('Avg Waiting Time')
        ax2.set_ylabel('Avg Turnaround Time')
        self.ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        self.ax.set_title('Comparison of Scheduling Algorithms')

        self.canvas.draw_idle()

    def save_chart(self):
        path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG','*.png')])
        if not path:
            return
        try:
            self.fig.savefig(path)
            messagebox.showinfo('Saved', f'Chart saved to {path}')
        except Exception as e:
            messagebox.showerror('Save Error', f'Could not save chart: {e}')

    def on_show(self):
        pass

# Deadlock Page
class DeadlockPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        top = ttk.Frame(self); top.pack(fill='x', padx=12, pady=6)
        ttk.Label(top, text='Process Name').grid(row=0, column=0); ttk.Label(top, text='Holding (R)').grid(row=0, column=1); ttk.Label(top, text='Waiting (R)').grid(row=0, column=2)
        self.p_name = ttk.Entry(top, width=16); self.p_name.grid(row=1, column=0, padx=6)
        self.p_hold = ttk.Entry(top, width=12); self.p_hold.grid(row=1, column=1, padx=6)
        self.p_wait = ttk.Entry(top, width=12); self.p_wait.grid(row=1, column=2, padx=6)
        tb.Button(top, text='Add as Task', bootstyle='success', command=self.add_from_inputs).grid(row=1, column=3, padx=8)
        tb.Button(top, text='Detect Deadlock', bootstyle='danger', command=self.detect).grid(row=1, column=4, padx=8)
        tb.Button(top, text='Refresh', bootstyle='secondary-outline', command=self.refresh).grid(row=1, column=5, padx=6)

        cols = ('pid','name','holding','waiting')
        self.table = ttk.Treeview(self, columns=cols, show='headings', height=6)
        for c in cols:
            self.table.heading(c, text=c.upper(), anchor='center')
            self.table.column(c, width=120, anchor='center')
        self.table.pack(fill='x', padx=12, pady=8)

        # Wait-for graph area
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

        if found and cycle:
            involved_resources = set()
            involved_processes = []
            for pid in cycle:
                t = next((task for task in tasks if task['pid'] == pid), None)
                if t:
                    involved_processes.append(f"P{pid} ({t.get('name', '')})")
                    if t.get('holding'):
                        involved_resources.add(t['holding'])
                    if t.get('waiting'):
                        involved_resources.add(t['waiting'])

            reason_text = (
                "❌ DEADLOCK DETECTED!\n\n"
                "💥 Reason: Circular wait formed among processes.\n"
                "Each process is holding a resource and waiting for another that’s already held.\n\n"
                f"🧩 Processes involved: {', '.join(involved_processes)}\n"
                f"📦 Resources involved: {', '.join(involved_resources)}\n\n"
                "💡 How to Solve:\n"
                "1️⃣ Terminate one process in the cycle.\n"
                "2️⃣ Preempt (take back) one held resource.\n"
                "3️⃣ Use a fixed resource request order to prevent circular wait.\n"
            )

            self.result_lbl.config(text=reason_text, foreground='red')
        else:
            self.result_lbl.config(
                text="✅ No deadlock detected.\nAll processes are in a safe state.",
                foreground='green'
            )

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
            self.ax.text(label_x, label_y, f'{waiting_resource} (Held by P{b})', fontsize=8, color='blue' if arrow_color == '#000000' else '#ff0033', ha='center', va='center', bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', pad=1))
        self.ax.axis('off'); self.ax.set_title('Wait-For Graph (red = in deadlock cycle) showing resources')
        self.canvas.draw_idle()

    def on_show(self):
        self.refresh()

# Power Page
class PowerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller

        top = ttk.Frame(self); top.pack(fill='x', pady=6)
        ttk.Label(top, text='Power rate (energy per time unit):').pack(side='left', padx=6)
        self.rate = ttk.Entry(top, width=8); self.rate.insert(0, '1'); self.rate.pack(side='left', padx=6)
        tb.Button(top, text='Compute Power Efficiency', bootstyle='primary', command=self.compute_power).pack(side='left', padx=6)

        self.result_lbl = ttk.Label(self, text='Energy & Efficiency Stats will appear here.', anchor='center'); self.result_lbl.pack(pady=8)

        self.fig = Figure(figsize=(9, 4), dpi=100); self.ax = self.fig.add_subplot(111)
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
        # Draw stacked bar
        self.ax.clear()
        self.ax.bar(['Energy Usage'], [energy_used], label='Active Energy')
        self.ax.bar(['Energy Usage'], [energy_idle], bottom=[energy_used], label='Idle Energy (20% power)')
        # show percentage label inside bar
        self.ax.text(0, energy_used + energy_idle/2, f'{efficiency:.1f}% efficient', ha='center', va='center', fontsize=10, fontweight='bold', color='white' if efficiency>50 else 'black', bbox=dict(facecolor='#333', alpha=0.6, pad=4))
        self.ax.set_ylabel('Energy Units'); self.ax.set_title('Power Efficiency Visualization'); self.ax.legend()
        self.canvas.draw_idle()

    def on_show(self):
        pass

# ---------------- Module-level launcher ----------------
def create_app(root, controller, initial_theme="superhero"):
    """
    root: tk.Tk instance
    controller: object implementing:
        - tasks (list)
        - next_pid (int)
        - add_task(name,arrival,burst,priority,holding,waiting)
        - clear_tasks()
        - clear_selected_task(pid)
        - run_scheduler(algo, quantum) -> (timeline, metrics)
        - (optional) update_task(pid, **kwargs)
    """
    # Apply theme
    style = tb.Style(initial_theme)

    # container frame for pages (stacked)
    pages = {}
    container = ttk.Frame(root)
    container.pack(fill='both', expand=True)
    for P in (DashboardPage, TaskManagerPage, SchedulerPage, ComparePage, DeadlockPage, PowerPage):
        page = P(container, controller)
        page.place(relx=0, rely=0, relwidth=1, relheight=1)
        pages[P.__name__] = page

    # Simple sidebar
    sidebar = ttk.Frame(root)
    sidebar.place(relx=0, rely=0, relwidth=0.18, relheight=1)
    content = ttk.Frame(root)
    content.place(relx=0.18, rely=0, relwidth=0.82, relheight=1)

    # Re-parent pages into content
    for page in pages.values():
        page.master = content
        page.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show(page_name):
        for name, page in pages.items():
            if name == page_name:
                page.lift()
                if hasattr(page, 'on_show'):
                    try:
                        page.on_show()
                    except Exception:
                        pass
            else:
                page.lower()

    # Sidebar buttons
    btns = [
        ('Dashboard', 'DashboardPage'),
        ('Task Manager', 'TaskManagerPage'),
        ('Scheduler', 'SchedulerPage'),
        ('Compare', 'ComparePage'),
        ('Deadlock', 'DeadlockPage'),
        ('Power', 'PowerPage'),
    ]
    for i, (label, pn) in enumerate(btns):
        b = tb.Button(sidebar, text=label, bootstyle='info' if i==0 else 'secondary', width=20, command=lambda p=pn: show(p))
        b.pack(pady=10, padx=8)
    # set initial page
    show('DashboardPage')

    return pages

# End of file
