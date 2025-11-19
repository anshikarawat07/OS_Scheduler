import math
from typing import List, Dict, Tuple, Any

# --------------------- Timeline Helpers ---------------------

def merge_segments(timeline: List[Tuple[int,int,int]]) -> List[Tuple[int,int,int]]:
    """Merge consecutive same-PID segments"""
    if not timeline:
        return []
    merged = []
    cur_pid, s, e = timeline[0]

    for pid, ss, ee in timeline[1:]:
        if pid == cur_pid and ss == e:
            e = ee
        else:
            merged.append((cur_pid, s, e))
            cur_pid, s, e = pid, ss, ee

    merged.append((cur_pid, s, e))
    return merged


# --------------------- FCFS ---------------------

def sched_fcfs(tasks: List[Dict[str,Any]]) -> List[Tuple[int,int,int]]:
    """First-Come First-Serve"""
    ords = sorted(tasks, key=lambda t: (t['arrival'], t['pid']))
    timeline = []
    tcur = 0

    for t in ords:
        start = max(tcur, t['arrival'])
        end = start + t['burst']
        timeline.append((t['pid'], start, end))
        tcur = end

    return timeline


# --------------------- SJF ---------------------

def sched_sjf(tasks: List[Dict[str,Any]], preemptive=False) -> List[Tuple[int,int,int]]:
    """Shortest Job First"""

    # Non-preemptive SJF
    if not preemptive:
        remaining = sorted(tasks, key=lambda t: (t['arrival'], t['burst'], t['pid']))
        timeline = []
        tcur = 0
        completed = set()
        n = len(tasks)

        while len(completed) < n:
            ready = [t for t in remaining if t['arrival'] <= tcur and t['pid'] not in completed]

            if not ready:
                arrivals = [t['arrival'] for t in remaining if t['pid'] not in completed]
                if not arrivals:
                    break
                tcur = min(arrivals)
                continue

            chosen = min(ready, key=lambda t: (t['burst'], t['arrival'], t['pid']))
            start = max(tcur, chosen['arrival'])
            end = start + chosen['burst']
            timeline.append((chosen['pid'], start, end))
            tcur = end
            completed.add(chosen['pid'])

        return timeline

    # Preemptive SJF (SRTF)
    bursts = {t['pid']: t['burst'] for t in tasks}
    arrived = set()
    ready = []
    timeline = []
    tcur = 0
    pids = [t['pid'] for t in tasks]

    while True:
        for t in tasks:
            if t['pid'] not in arrived and t['arrival'] <= tcur:
                arrived.add(t['pid'])
                ready.append(t['pid'])

        if not ready:
            future = [t['arrival'] for t in tasks if t['pid'] not in arrived]
            if not future:
                break
            tcur = min(future)
            continue

        cur = min(ready, key=lambda pid: bursts[pid])
        start = tcur
        bursts[cur] -= 1
        tcur += 1
        end = tcur

        timeline.append((cur, start, end))

        if bursts[cur] == 0:
            ready.remove(cur)

        if all(bursts[p] == 0 for p in pids):
            break

    return merge_segments(timeline)


# --------------------- Priority Scheduling ---------------------

def sched_priority(tasks: List[Dict[str,Any]], preemptive=False) -> List[Tuple[int,int,int]]:
    """Priority scheduling"""

    # Non-preemptive
    if not preemptive:
        remaining = sorted(tasks, key=lambda t: (t['arrival'], t['priority'], t['pid']))
        timeline = []
        tcur = 0
        completed = set()
        n = len(tasks)

        while len(completed) < n:
            ready = [t for t in remaining if t['arrival'] <= tcur and t['pid'] not in completed]

            if not ready:
                arrivals = [t['arrival'] for t in remaining if t['pid'] not in completed]
                if not arrivals:
                    break
                tcur = min(arrivals)
                continue

            chosen = min(ready, key=lambda t: (t['priority'], t['arrival'], t['pid']))
            start = max(tcur, chosen['arrival'])
            end = start + chosen['burst']

            timeline.append((chosen['pid'], start, end))
            tcur = end
            completed.add(chosen['pid'])

        return timeline

    # Preemptive priority
    remaining = {t['pid']: t['burst'] for t in tasks}
    arrived = set()
    ready = []
    timeline = []
    tcur = 0
    pids = [t['pid'] for t in tasks]

    priority = lambda pid: next(x['priority'] for x in tasks if x['pid'] == pid)

    while True:
        for t in tasks:
            if t['pid'] not in arrived and t['arrival'] <= tcur:
                arrived.add(t['pid'])
                ready.append(t['pid'])

        if not ready:
            future = [t['arrival'] for t in tasks if t['pid'] not in arrived]
            if not future:
                break
            tcur = min(future)
            continue

        cur = min(ready, key=lambda pid: priority(pid))
        start = tcur
        remaining[cur] -= 1
        tcur += 1
        end = tcur

        timeline.append((cur, start, end))

        if remaining[cur] == 0:
            ready.remove(cur)

        if all(remaining[p] == 0 for p in pids):
            break

    return merge_segments(timeline)


# --------------------- LJF ---------------------

def sched_ljf(tasks: List[Dict[str,Any]]) -> List[Tuple[int,int,int]]:
    """Longest Job First"""
    remaining = sorted(tasks, key=lambda t: (t['arrival'], -t['burst'], t['pid']))
    timeline = []
    tcur = 0
    completed = set()
    n = len(tasks)

    while len(completed) < n:
        ready = [t for t in remaining if t['arrival'] <= tcur and t['pid'] not in completed]

        if not ready:
            arrivals = [t['arrival'] for t in remaining if t['pid'] not in completed]
            if not arrivals:
                break
            tcur = min(arrivals)
            continue

        chosen = max(ready, key=lambda t: (t['burst'], t['arrival'], t['pid']))
        start = max(tcur, chosen['arrival'])
        end = start + chosen['burst']

        timeline.append((chosen['pid'], start, end))
        tcur = end
        completed.add(chosen['pid'])

    return timeline


# --------------------- Round Robin ---------------------

def sched_rr(tasks: List[Dict[str,Any]], quantum:int) -> List[Tuple[int,int,int]]:
    """Round Robin"""
    q = max(1, int(quantum))

    bursts = {t['pid']: t['burst'] for t in tasks}
    arrived = set()
    ready = []
    timeline = []
    tcur = 0
    pids = [t['pid'] for t in tasks]

    while True:
        for t in tasks:
            if t['pid'] not in arrived and t['arrival'] <= tcur:
                arrived.add(t['pid'])
                ready.append(t['pid'])

        if not ready:
            if all(bursts[p] == 0 for p in pids):
                break
            future = [t['arrival'] for t in tasks if t['pid'] not in arrived]
            if not future:
                break
            tcur = min(future)
            for t in tasks:
                if t['pid'] not in arrived and t['arrival'] <= tcur:
                    arrived.add(t['pid'])
                    ready.append(t['pid'])
            continue

        cur = ready.pop(0)

        if bursts[cur] <= 0:
            continue

        start = tcur
        sl = min(q, bursts[cur])
        bursts[cur] -= sl
        tcur += sl
        end = tcur

        timeline.append((cur, start, end))

        for t in tasks:
            if t['pid'] not in arrived and t['arrival'] <= tcur:
                arrived.add(t['pid'])
                ready.append(t['pid'])

        if bursts[cur] > 0:
            ready.append(cur)

        if all(bursts[p] == 0 for p in pids):
            break

    return merge_segments(timeline)


# --------------------- Apply Timeline ---------------------

def apply_timeline(tasks: List[Dict[str,Any]], timeline: List[Tuple[int,int,int]]):
    """Update task stats"""
    for t in tasks:
        t['start'] = None
        t['completion'] = None
        t['waiting_time'] = None
        t['turnaround'] = None
        t['status'] = 'Waiting'

    for pid, s, e in timeline:
        for t in tasks:
            if t['pid'] == pid:
                if t['start'] is None:
                    t['start'] = s
                t['completion'] = e
                t['status'] = 'Completed'

    for t in tasks:
        if t['start'] is not None:
            t['waiting_time'] = t['completion'] - t['arrival'] - t['burst']
            t['turnaround'] = t['completion'] - t['arrival']


# --------------------- Compute Metrics ---------------------

def compute_metrics(tasks: List[Dict[str,Any]], timeline: List[Tuple[int,int,int]]):
    """Calculate scheduling metrics"""
    apply_timeline(tasks, timeline)
    done = [t for t in tasks if t['start'] is not None]
    n = len(done)

    total_wait = sum(t['waiting_time'] for t in done) if n else 0
    total_tat = sum(t['turnaround'] for t in done) if n else 0

    timeline_start = min((s for (_, s, _) in timeline), default=0)
    timeline_end = max((e for (_, _, e) in timeline), default=0)

    total_exec = sum((e - s) for (_, s, e) in timeline)
    total_time = max(1, timeline_end - timeline_start)

    cpu_util = (total_exec / total_time) * 100
    avg_wait = total_wait / n if n else 0
    avg_tat = total_tat / n if n else 0
    throughput = n / total_time

    return {
        'avg_wait': avg_wait,
        'avg_tat': avg_tat,
        'cpu_util': cpu_util,
        'throughput': throughput,
        'total_exec': total_exec
    }


# --------------------- Deadlock Detection ---------------------

def detect_deadlock_from_hold_wait(tasks: List[Dict[str,Any]]) -> Tuple[bool, List[int]]:
    """Detect cycle in Wait-For graph"""
    holders = {}
    for t in tasks:
        h = (t.get('holding') or '').strip()
        if h:
            holders.setdefault(h, []).append(t['pid'])

    graph = {t['pid']: set() for t in tasks}

    for t in tasks:
        w = (t.get('waiting') or '').strip()
        if w:
            for owner in holders.get(w, []):
                if owner != t['pid']:
                    graph[t['pid']].add(owner)

    visited = {}
    stack = []
    cycle = []

    def dfs(u):
        visited[u] = 1
        stack.append(u)

        for v in graph.get(u, set()):
            if visited.get(v, 0) == 0:
                if dfs(v):
                    return True
            elif visited.get(v) == 1:
                idx = stack.index(v)
                cycle.extend(stack[idx:])
                return True

        stack.pop()
        visited[u] = 2
        return False

    for node in graph:
        if visited.get(node, 0) == 0:
            if dfs(node):
                return True, cycle

    return False, []


# --------------------- Banker's Algorithm ---------------------

def is_safe_state(processes: List[Dict[str,Any]], available: Dict[str,int]) -> bool:
    """Check safe state"""
    resource_types = list(available.keys())
    work = available.copy()
    finish = {p['pid']: False for p in processes}

    need = {}
    for p in processes:
        need[p['pid']] = {
            r: p.get('max_need', {}).get(r, 0) - p.get('allocation', {}).get(r, 0)
            for r in resource_types
        }

    safe_seq = []
    n = len(processes)

    while len(safe_seq) < n:
        found = False

        for p in processes:
            pid = p['pid']
            if not finish[pid]:
                if all(need[pid][r] <= work[r] for r in resource_types):
                    for r in resource_types:
                        work[r] += p.get('allocation', {}).get(r, 0)
                    finish[pid] = True
                    safe_seq.append(pid)
                    found = True
                    break

        if not found:
            return False

    return True


def request_resources(processes: List[Dict[str,Any]], available: Dict[str,int],
                       pid: int, request: Dict[str,int]) -> Tuple[bool, str]:
    """Process resource request"""
    idx = next((i for i, p in enumerate(processes) if p['pid'] == pid), None)
    if idx is None:
        return False, "PID not found."

    process = processes[idx]

    # Check need
    for r, qty in request.items():
        need = process.get('max_need', {}).get(r, 0) - process.get('allocation', {}).get(r, 0)
        if qty > need:
            return False, f"Request exceeds maximum need for {r}"

    # Check availability
    for r, qty in request.items():
        if qty > available.get(r, 0):
            return False, f"Insufficient available {r}"

    # Simulate allocation
    temp_av = available.copy()
    temp_proc = [p.copy() for p in processes]
    tp = temp_proc[idx]
    tp['allocation'] = tp.get('allocation', {}).copy()

    for r, qty in request.items():
        temp_av[r] -= qty
        tp['allocation'][r] = tp['allocation'].get(r, 0) + qty

    # Check safe state
    if is_safe_state(temp_proc, temp_av):
        for r, qty in request.items():
            available[r] -= qty
            process['allocation'] = process.get('allocation', {})
            process['allocation'][r] = process['allocation'].get(r, 0) + qty
        return True, "Request granted"

    return False, "Request denied (unsafe state)"
