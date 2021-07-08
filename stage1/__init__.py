import stage1.initial_launch
from easyturk import interface

def launch(hits, rewards, assignments, sandbox):
    hit_ids = interface.launch_annotate_bbox_relationships(hits, rewards, assignments, sandbox)
    return hit_ids

def run_attention_checks(hits):
    return []

def update_knowledge(stage, stage_knowledge, result, worker_id, hit_id):
    task_name = result['task_name']
    task_knowledge = stage_knowledge.get(task_name, {'hit_ids': []})
    task_knowledge['hit_ids'].append(hit_id)

    worker = 'worker_1'

    worker_knowledge = {'worker_id': worker_id, 'answer': [o['rect'] for o in result['objects']]}
    task_knowledge[worker] = worker_knowledge

    stage_knowledge[task_name] = task_knowledge
    return stage_knowledge
