import stage2.initial_launch, stage2.disagreement_launch
from easyturk import interface

def launch(hits, rewards, assignments, sandbox):
    hit_ids = interface.launch_verify_relationship_simple(hits, rewards, assignments, sandbox)
    return hit_ids

def run_attention_checks(hits):
    return ['AU3NU1RYO2FVB']

def is_disagreement(knowledge):
    return knowledge['worker_1']['answer'] != knowledge['worker_2']['answer']

def aggregate(knowledge):
    if 'worker_3' in knowledge:
        answer = knowledge['worker_3']['answer']
    else:
        answer = knowledge['worker_1']['answer']

    return answer

def update_knowledge(stage, stage_knowledge, result, worker_id, hit_id):
    task_name = result['task_name']
    task_knowledge = stage_knowledge.get(task_name, {'hit_ids': []})
    task_knowledge['hit_ids'].append(hit_id)

    if 'worker_1' not in task_knowledge: worker = 'worker_1'
    elif 'worker_2' not in task_knowledge: worker = 'worker_2'
    else:
        assert is_disagreement(task_knowledge), 'Unknown error'
        assert 'worker_3' not in task_knowledge, 'Unknown error'
        worker = 'worker_3'

    worker_knowledge = {'worker_id': worker_id, 'answer': result['option']['answer']}
    task_knowledge[worker] = worker_knowledge

    if worker == 'worker_2' and not is_disagreement(task_knowledge):
        task_knowledge['final_answer'] = aggregate(task_knowledge)
    elif worker == 'worker_3':
        task_knowledge['final_answer'] = aggregate(task_knowledge)

    stage_knowledge[task_name] = task_knowledge
    return stage_knowledge
