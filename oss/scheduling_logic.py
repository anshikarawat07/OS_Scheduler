import math
from typing import List, Dict, Tuple, Any

# --------------------- Scheduling algorithms & helpers ---------------------

def merge_segments(timeline: List[Tuple[int,int,int]]) -> List[Tuple[int,int,int]]:
    if not timeline: return []
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

def sched_fcfs(tasks: List[Dict[str,Any]]) -> List[Tuple[int,int,int]]:
    ords = sorted(tasks, key=lambda t: (t['arrival'], t['pid']))
    timeline=[]; tcur=0
    for t in ords:
        start = max(tcur, t['arrival'])
        end = start + t['burst']
        timeline.append((t['pid'], start, end)); tcur = end
    return timeline

def sched_sjf(tasks: List[Dict[str,Any]], preemptive=False) -> List[Tuple[int,int,int]]:
    if not preemptive:
        remaining = sorted(tasks, key=lambda t: (t['arrival'], t['burst'], t['pid']))
        timeline=[]; tcur=0; completed=set(); n=len(tasks)
        while len(completed)<n:
            candidates = [t for t in remaining if t['arrival']<=tcur and t['pid'] not in completed]
            if not candidates:
                arrivals = [t['arrival'] for t in remaining if t['pid'] not in completed]
                if not arrivals: break
                tcur = min(arrivals); continue
            chosen = min(candidates, key=lambda t:(t['burst'], t['arrival'], t['pid']))
            start = max(tcur, chosen['arrival']); end = start + chosen['burst']
            timeline.append((chosen['pid'], start, end)); tcur = end; completed.add(chosen['pid'])
        return timeline
    # preemptive (SRTF)
    bursts = {t['pid']: t['burst'] for t in tasks}
    arrived=set(); ready=[]; timeline=[]; tcur=0; pids=[t['pid'] for t in tasks]
    while True:
        for t in tasks:
            if t['pid'] not in arrived and t['arrival']<=tcur:
                arrived.add(t['pid']); ready.append(t['pid'])
        if not ready:
            future=[t['arrival'] for t in tasks if t['pid'] not in arrived]
            if not future: break
            tcur = min(future); continue
        cur = min(ready, key=lambda pid: bursts[pid])
        start = tcur; bursts[cur]-=1; tcur+=1; end=tcur
        timeline.append((cur,start,end))
        if bursts[cur]==0: ready.remove(cur)
        if all(bursts[pid]==0 for pid in pids): break
    return merge_segments(timeline)

def sched_priority(tasks: List[Dict[str,Any]], preemptive=False) -> List[Tuple[int,int,int]]:
    if not preemptive:
        remaining = sorted(tasks, key=lambda t: (t['arrival'], t['priority'], t['pid']))
        timeline=[]; tcur=0; completed=set(); n=len(tasks)
        while len(completed)<n:
            candidates = [t for t in remaining if t['arrival']<=tcur and t['pid'] not in completed]
            if not candidates:
                arrivals = [t['arrival'] for t in remaining if t['pid'] not in completed]
                if not arrivals: break
                tcur = min(arrivals); continue
            chosen = min(candidates, key=lambda t:(t['priority'], t['arrival'], t['pid']))
            start = max(tcur, chosen['arrival']); end=start+chosen['burst']
            timeline.append((chosen['pid'], start, end)); tcur=end; completed.add(chosen['pid'])
        return timeline
    # preemptive priority
    remaining = {t['pid']: t['burst'] for t in tasks}
    arrived=set(); ready=[]; timeline=[]; tcur=0; pids=[t['pid'] for t in tasks]
    while True:
        for t in tasks:
            if t['pid'] not in arrived and t['arrival']<=tcur:
                arrived.add(t['pid']); ready.append(t['pid'])
        if not ready:
            future=[t['arrival'] for t in tasks if t['pid'] not in arrived]
            if not future: break
            tcur=min(future); continue
        cur = min(ready, key=lambda pid: next(x['priority'] for x in tasks if x['pid']==pid))
        start = tcur; remaining[cur]-=1; tcur+=1; end=tcur
        timeline.append((cur,start,end))
        if remaining[cur]==0: ready.remove(cur)
        if all(remaining[pid]==0 for pid in pids): break
    return merge_segments(timeline)

def sched_ljf(tasks: List[Dict[str,Any]]) -> List[Tuple[int,int,int]]:
    remaining = sorted(tasks, key=lambda t: (t['arrival'], -t['burst'], t['pid']))
    timeline=[]; tcur=0; completed=set(); n=len(tasks)
    while len(completed)<n:
        candidates = [t for t in remaining if t['arrival']<=tcur and t['pid'] not in completed]
        if not candidates:
            arrivals = [t['arrival'] for t in remaining if t['pid'] not in completed]
            if not arrivals: break
            tcur = min(arrivals); continue
        chosen = max(candidates, key=lambda t:(t['burst'], t['arrival'], t['pid']))
        start = max(tcur, chosen['arrival']); end = start + chosen['burst']
        timeline.append((chosen['pid'], start, end)); tcur = end; completed.add(chosen['pid'])
    return timeline

def sched_rr(tasks: List[Dict[str,Any]], quantum:int) -> List[Tuple[int,int,int]]:
    q = max(1,int(quantum))
    bursts = {t['pid']: t['burst'] for t in tasks}
    arrived=set(); ready=[]; timeline=[]; tcur=0; pids=[t['pid'] for t in tasks]
    while True:
        for t in tasks:
            if t['pid'] not in arrived and t['arrival']<=tcur:
                arrived.add(t['pid']); ready.append(t['pid'])
        if not ready:
            if all(bursts[pid]==0 for pid in pids): break
            future=[t['arrival'] for t in tasks if t['pid'] not in arrived]
            if not future: break
            tcur=min(future)
            for t in tasks:
                if t['pid'] not in arrived and t['arrival']<=tcur:
                    arrived.add(t['pid']); ready.append(t['pid'])
            continue
        cur = ready.pop(0)
        if bursts[cur]<=0: continue
        start = tcur
        sl = min(q, bursts[cur]); bursts[cur]-=sl; tcur+=sl; end = tcur
        timeline.append((cur,start,end))
        for t in tasks:
            if t['pid'] not in arrived and t['arrival']<=tcur:
                arrived.add(t['pid']); ready.append(t['pid'])
        if bursts[cur]>0: ready.append(cur)
        if all(bursts[pid]==0 for pid in pids): break
    return merge_segments(timeline)

# --------------------- metrics / timeline application ---------------------

def apply_timeline(tasks: List[Dict[str,Any]], timeline: List[Tuple[int,int,int]]):
    for t in tasks:
        t['start']=None; t['completion']=None; t['waiting_time']=None; t['turnaround']=None; t['status']='Waiting'
    for pid,s,e in timeline:
        for t in tasks:
            if t['pid']==pid:
                if t.get('start') is None: t['start']=s
                t['completion']=e; t['status']='Completed'
    for t in tasks:
        if t.get('start') is not None:
            t['waiting_time'] = t['completion'] - t['arrival'] - t['burst']
            t['turnaround'] = t['completion'] - t['arrival']

def compute_metrics(tasks: List[Dict[str,Any]], timeline: List[Tuple[int,int,int]]):
    apply_timeline(tasks, timeline)
    completed = [t for t in tasks if t.get('start') is not None]
    n = len(completed)
    total_wait = sum(t['waiting_time'] for t in completed) if n>0 else 0
    total_tat = sum(t['turnaround'] for t in completed) if n>0 else 0
    
    timeline_start = min((s for (_,s,_) in timeline), default=0)
    timeline_end = max((e for (_,_,e) in timeline), default=0)
    
    total_exec = sum((e-s) for (_,s,e) in timeline)
    total_time = max(1, timeline_end - timeline_start)
    cpu_util = (total_exec/total_time)*100 if total_time>0 else 0
    avg_wait = total_wait/n if n>0 else 0
    avg_tat = total_tat/n if n>0 else 0
    throughput = n/total_time if total_time>0 else 0
    return {'avg_wait':avg_wait,'avg_tat':avg_tat,'cpu_util':cpu_util,'throughput':throughput,'total_exec':total_exec}

# --------------------- Deadlock Detection ---------------------

def detect_deadlock_from_hold_wait(tasks: List[Dict[str,Any]]) -> Tuple[bool, List[int]]:
    holders = {}
    for t in tasks:
        h = (t.get('holding') or '').strip()
        if h: holders.setdefault(h, []).append(t['pid'])
        
    graph = {t['pid']: set() for t in tasks} 
    
    for t in tasks:
        w = (t.get('waiting') or '').strip()
        if w:
            owners = holders.get(w, [])
            for o in owners:
                if o != t['pid']:
                    graph[t['pid']].add(o)
                    
    # Cycle detection (DFS)
    visited = {} 
    stack = []
    cycle = []
    def dfs(u):
        visited[u]=1; stack.append(u)
        for v in graph.get(u,set()): 
            if visited.get(v,0)==0:
                if dfs(v): return True
            elif visited.get(v,0)==1: 
                idx = stack.index(v); cycle.extend(stack[idx:]); return True
        stack.pop(); visited[u]=2; return False
        
    for node in graph:
        if visited.get(node,0)==0:
            if dfs(node): return True, cycle
            
    return False, []
