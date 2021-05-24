from stages import stage1
import utils

def prepare_relaunch(tasks, args):
    knowledge = utils.get_knowledge_file(args)

    remaining_tasks, assignments = [], []
    for task in tasks:
        image_name = task['url'].split('/')[-1]
        task_knowledge = knowledge[image_name]['stage_'+str(args.stage)][task['task_name']]

        has_w1, has_w2 = 'worker_1' in task_knowledge , 'worker_2' in task_knowledge
        if has_w1 and has_w2: continue

        remaining_tasks.append(task)
        assignments.append(int(not has_w1) + int(not has_w2))

    assert len(remaining_tasks) != 0, 'Stage 1 initial launch done'

    one_assignment_tasks = [task for task, assignment in zip(remaining_tasks, assignments) if assignment==1]
    two_assignment_tasks = [task for task, assignment in zip(remaining_tasks, assignments) if assignment==2]

    one_assignment_hits = get_hits_from_tasks(one_assignment_tasks, args)
    two_assignment_hits = get_hits_from_tasks(two_assignment_tasks, args)

    hits = one_assignment_hits + two_assignment_hits
    assignments = [1 for _ in one_assignment_hits] + [2 for _ in two_assignment_hits]
    rewards = [utils.get_reward(args)  for _ in hits]

    return hits, rewards, assignments

def is_relaunch(args):
    if utils.get_launch_file(args) == {}: return False

    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    return True

def prepare_launch(args):
    if args.stage == 1: stage = stage1
    elif args.stage == 2: stage = stage2

    tasks = stage.get_tasks(args)

    if is_relaunch(args):
        return prepare_relaunch(tasks, args)

    hits = utils.get_hits_from_tasks(tasks, args)
    assignments = [2 for _ in hits]
    rewards = [utils.get_reward(args) for _ in hits]

    return hits, rewards, assignments
