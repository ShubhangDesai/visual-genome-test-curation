import utils
from easyturk import interface

def get_tasks(args):
    initial_data = utils.get_initial_data(args)

    tasks = []
    for datum in initial_data:
        name_prefix = '_'.join([datum['subject']['name'], datum['predicate'], datum['object']['name']])

        task_1, task_2 = datum.copy(), datum.copy()
        task_1['task_name'], task_2['task_name'] = name_prefix + '_subject', name_prefix + '_object'

        tasks.append(task_1)
        tasks.append(task_2)

    return tasks

def launch(hits, rewards, assignments, sandbox):
    hit_ids = interface.launch_annotate_bbox_relationships(hits, rewards, assignments, sandbox)
    return hit_ids

def run_attention_checks(hits):
    return []

def is_disagreement(knowledge):
    if len(bboxes1 != len(bboxes2)): return True

    for bbox in bboxes1:
        ious = [iou(bbox, bbox2) for bbox2 in bboxes2]
        if max(ious) < threshold: return True

    return False

def aggregate(bboxes1, bboxes2, bboxes3):
    if bboxes3 == None:
        return avg_bboxes(bboxes1, bboxes2)
    elif not is_disagreement(bboxes1, bboxes3):
        return avg_bboxes(bboxes1, bboxes3)
    elif not is_disagreement(bboxes2, bboxes3):
        return avg_bboxes(bboxes2, bboxes3)
    else:
        # uhhhhhh
        return rip_idk
