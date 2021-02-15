import stage1.initial_launch
import stage1.disagreement_launch

from easyturk import interface

def launch(hits, rewards, assignments, sandbox):
    hit_ids = interface.launch_specify_num_relationship(hits, rewards, assignments, sandbox)
    return hit_ids

def run_attention_checks(hits):
    return ['A3Q2AW4YWVN2IC']

def is_disagreement(knowledge):
    return abs(knowledge['worker_1']['answer'] - knowledge['worker_2']['answer']) > 4

def aggregate(knowledge):
    worker_1_answer = knowledge['worker_1']['answer']
    worker_2_answer = knowledge['worker_2']['answer']
    if 'worker_3' in knowledge:
        worker_3_answer = knowledge['worker_3']['answer']
        worker_1_diff = abs(worker_1_answer - worker_3_answer)
        worker_2_diff = abs(worker_2_answer - worker_3_answer)

        closer_answer = worker_1_answer if worker_1_diff < worker_2_diff else worker_2_answer
        answers = [worker_3_answer, closer_answer]
    else:
        answers = [worker_1_answer, worker_2_answer]

    return max(answers)

def update_knowledge(stage_knowledge, result, worker_id, hit_id):
    relationship = '_'.join([result['subject']['name'], result['predicate'], result['object']['name']])
    relationship_knowledge = stage_knowledge.get(relationship, {'hit_ids': []})
    relationship_knowledge['hit_ids'].append(hit_id)

    if 'worker_1' not in relationship_knowledge: worker = 'worker_1'
    elif 'worker_2' not in relationship_knowledge: worker = 'worker_2'
    else:
        assert is_disagreement(relationship_knowledge), 'Unknown error'
        assert 'worker_3' not in relationship_knowledge, 'Unknown error'
        worker = 'worker_3'

    worker_knowledge = {'worker_id': worker_id, 'answer': result['num_relationship']}
    relationship_knowledge[worker] = worker_knowledge

    if worker == 'worker_2' and not is_disagreement(relationship_knowledge):
        relationship_knowledge['final_answer'] = aggregate(relationship_knowledge)
    elif worker == 'worker_3':
        relationship_knowledge['final_answer'] = aggregate(relationship_knowledge)

    stage_knowledge[relationship] = relationship_knowledge
    return stage_knowledge
