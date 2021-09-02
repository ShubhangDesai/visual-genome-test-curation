import stage2.initial_launch, stage2.disagreement_launch
from easyturk import interface
import utils

def launch(hits, rewards, assignments, sandbox):
    hit_ids = interface.launch_verify_full_rec_relationships(hits, rewards, assignments, sandbox)
    return hit_ids

def run_attention_checks(hits):
    return []

def is_disagreement(knowledge):
    return knowledge['worker_1']['answer'] != knowledge['worker_2']['answer']

def aggregate(knowledge):
    if 'worker_3' in knowledge:
        answer = knowledge['worker_3']['answer']
    else:
        answer = knowledge['worker_1']['answer']

    return answer

def update_knowledge(stage, stage_knowledge, result, worker_id, hit_id, args):
    task_name = result['task_name']
    task_knowledge = stage_knowledge.get(task_name, {'hit_ids': []})
    task_knowledge['hit_ids'].append(hit_id)

    round = 'round_' + str(utils.get_overall_round(args))
    round_knowledge = task_knowledge.get(round, {})

    if 'worker_1' not in round_knowledge: worker = 'worker_1'
    elif 'worker_2' not in round_knowledge: worker = 'worker_2'
    else:
        assert is_disagreement(round_knowledge), 'Unknown error'
        assert 'worker_3' not in round_knowledge, 'Unknown error'
        worker = 'worker_3'

    worker_knowledge = {'worker_id': worker_id, 'answer': result['answer']}
    round_knowledge[worker] = worker_knowledge

    if worker == 'worker_2' and not is_disagreement(round_knowledge):
        round_knowledge['final_answer'] = aggregate(round_knowledge)
    elif worker == 'worker_3':
        round_knowledge['final_answer'] = aggregate(round_knowledge)

    task_knowledge[round] = round_knowledge
    stage_knowledge[task_name] = task_knowledge

    return stage_knowledge
