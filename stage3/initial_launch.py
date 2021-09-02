import utils

def get_relaunch_hits(tasks, args):
    knowledge = utils.get_knowledge_file(args)
    round_num = utils.get_overall_round(args)

    one_assignment_tasks, two_assignment_tasks = [], []
    for task in tasks:
        image_name = task['url']
        if image_name not in knowledge:
            two_assignment_tasks.append(task)
            continue

        task_knowledge = knowledge[image_name]['stage_'+str(args.stage)][task['task_name']]
        round_knowledge = task_knowledge['round_' + str(round_num)]
        has_w1, has_w2 = 'worker_1' in round_knowledge , 'worker_2' in round_knowledge
        if has_w1 and has_w2: continue

        if int(not has_w1) + int(not has_w2) == 1:
            one_assignment_tasks.append(task)
        else:
            two_assignment_tasks.append(task)

    assert len(one_assignment_tasks) + len(two_assignment_tasks) != 0, 'Stage 3 round %d initial launch done' % round_num

    one_assignment_hits = utils.get_hits_from_tasks(one_assignment_tasks, args)
    two_assignment_hits = utils.get_hits_from_tasks(two_assignment_tasks, args)

    hits = one_assignment_hits + two_assignment_hits
    assignments = [1 for _ in one_assignment_hits] + [2 for _ in two_assignment_hits]

    return hits, assignments

def prepare_launch(args):
    assert utils.stage_1_round_is_done(args), 'You must finish stage 3 round %d first' % utils.get_overall_round(args)

    tasks = utils.get_stage_3_tasks(args)
    if utils.is_relaunch(args):
        hits, assignments = get_relaunch_hits(tasks, args)
    else:
        hits = utils.get_hits_from_tasks(tasks, args)
        assignments = [2 for _ in hits]

    rewards = [utils.get_reward(args) for _ in hits]
    return hits, rewards, assignments
