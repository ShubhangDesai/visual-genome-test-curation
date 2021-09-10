import stage2.initial_launch, stage2.disagreement_launch
from easyturk import interface
import utils

def launch(hits, rewards, assignments, sandbox):
    hit_ids = interface.launch_annotate_bbox_with_point(hits, rewards, assignments, sandbox)
    return hit_ids

def run_attention_checks(hits):
    return []

def get_iou(bb1, bb2):
    x_left = max(bb1['x'], bb2['x'])
    y_top = max(bb1['y'], bb2['y'])
    x_right = min(bb1['x']+bb1['w'], bb2['x']+bb2['w'])
    y_bottom = min(bb1['y']+bb1['h'], bb2['y']+bb2['h'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    bb1_area = (bb1['x']+bb1['w'] - bb1['x']) * (bb1['y']+bb1['h'] - bb1['y'])
    bb2_area = (bb2['x']+bb2['w'] - bb2['x']) * (bb2['y']+bb2['h'] - bb2['y'])

    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    return iou

def is_disagreement(knowledge):
    iou = get_iou(knowledge['worker_1']['answer'], knowledge['worker_2']['answer'])
    return iou < 0.8

def get_bb_average(bb1, bb2):
    avg_x, avg_y = (bb1['x'] + bb2['x']) // 2, (bb1['y'] + bb2['y']) // 2
    avg_w = (bb1['x'] + bb1['w'] + bb2['x'] + bb2['w']) // 2 - avg_x
    avg_h = (bb1['y'] + bb1['h'] + bb2['y'] + bb2['h']) // 2 - avg_y

    avg_bb = {'x': avg_x, 'y': avg_y, 'w': avg_w, 'h': avg_h}
    return avg_bb

def aggregate(knowledge):
    bb1, bb2 = knowledge['worker_1']['answer'], knowledge['worker_2']['answer']
    if 'worker_3' in knowledge:
        bb3 = knowledge['worker_3']['answer']
        ious = [get_iou(bb1, bb2), get_iou(bb1, bb3), get_iou(bb2, bb3)]

        if max(ious) == ious[0]: answer = get_bb_average(bb1, bb2)
        elif max(ious) == ious[1]: answer = get_bb_average(bb1, bb3)
        else: answer = get_bb_average(bb2, bb3)
    else:
        answer = get_bb_average(bb1, bb2)

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

    worker_knowledge = {'worker_id': worker_id, 'answer': result['objects'][0]['rect']}
    round_knowledge[worker] = worker_knowledge

    if worker == 'worker_2' and not is_disagreement(round_knowledge):
        round_knowledge['final_answer'] = aggregate(round_knowledge)
    elif worker == 'worker_3':
        round_knowledge['final_answer'] = aggregate(round_knowledge)

    task_knowledge[round] = round_knowledge
    stage_knowledge[task_name] = task_knowledge

    return stage_knowledge
