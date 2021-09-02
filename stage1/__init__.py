import stage1.initial_launch
from easyturk import interface
import utils

def launch(hits, rewards, assignments, sandbox):
    hit_ids = interface.launch_annotate_points(hits, rewards, assignments, sandbox)
    return hit_ids

def run_attention_checks(hits):
    return ['AU3NU1RYO2FVB']

def update_knowledge(stage, stage_knowledge, result, worker_id, hit_id, args):
    task_name = result['task_name']
    task_knowledge = stage_knowledge.get(task_name, {'hit_ids': []})
    task_knowledge['hit_ids'].append(hit_id)

    worker = 'worker_'+str(utils.get_overall_round(args))

    worker_knowledge = {'worker_id': worker_id, 'answer': result['objects']}
    task_knowledge[worker] = worker_knowledge

    stage_knowledge[task_name] = task_knowledge
    return stage_knowledge
