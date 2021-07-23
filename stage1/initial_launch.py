import utils

def get_relaunch_hits(tasks, args):
    knowledge = utils.get_knowledge_file(args)

    remaining_tasks = []
    for task in tasks:
        image_name = task['url'].split('/')[-1]
        if image_name not in knowledge:
            remaining_tasks.append(task)
            continue

        task_knowledge = knowledge[image_name]['stage_'+str(args.stage)][task['task_name']]
        if 'worker_1' in task_knowledge: continue

        remaining_tasks.append(task)

    assert len(remaining_tasks) != 0, 'Stage 1 initial launch done'

    hits = utils.get_hits_from_tasks(remaining_tasks, args)
    assignments = [1 for _ in hits]

    return hits, assignments

def get_tasks(args):
    initial_data = utils.get_initial_data(args)

    tasks = []
    for datum in initial_data:
        name_prefix = '_'.join([datum['subject']['name'], datum['predicate'], datum['object']['name']])

        for task, main in [(datum.copy(), 'subject'), (datum.copy(), 'object')]:
            task['task_name'] = name_prefix + '_' + main
            task['main'] = datum[main]['name']
            task['num_objects'] = 1

            tasks.append(task)

    return tasks

def prepare_launch(args):
    tasks = get_tasks(args)
    if utils.is_relaunch(args):
        hits, assignments = get_relaunch_hits(tasks, args)
    else:
        hits = utils.get_hits_from_tasks(tasks, args)
        assignments = [1 for _ in hits]

    rewards = [utils.get_reward(args) for _ in hits]
    return hits, rewards, assignments
