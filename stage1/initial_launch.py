import utils

def get_relaunch_hits(tasks, args):
    knowledge = utils.get_knowledge_file(args)

    remaining_tasks = []
    for task in tasks:
        image_name = task['url']
        if image_name not in knowledge:
            remaining_tasks.append(task)
            continue

        task_knowledge = knowledge[image_name]['stage_'+str(args.stage)][task['task_name']]
        if 'worker_'+str(utils.get_overall_round(args)) in task_knowledge: continue

        remaining_tasks.append(task)

    if len(remaining_tasks) == 0:
        utils.mark_current_stage_round_as_done(args)
        assert False, 'Stage 1 round %d complete. Proceed to stage 2.' % utils.get_overall_round(args)

    hits = utils.get_hits_from_tasks(remaining_tasks, args)
    assignments = [1 for _ in hits]

    return hits, assignments

def get_tasks(args):
    initial_data = utils.get_initial_data(args)

    stage_1_results = utils.get_stage_1_results(args)
    stage_2_results = utils.get_stage_2_results(args)
    stage_3_results = utils.get_stage_3_results(args)

    tasks = []
    for datum in initial_data:
        name_prefix = '_'.join([datum['subject']['name'], datum['predicate'], datum['object']['name']])

        for task, main in [(datum.copy(), 'subject'), (datum.copy(), 'object')]:
            task_name = name_prefix + '_' + main
            task['task_name'] = task_name
            task['main'] = datum[main]['name']

            image_name = datum['url']
            if stage_1_results != {}:
                task['objects'] = [{**obj, **{'prev': True}} for obj in stage_1_results[image_name][task_name]]
            else:
                task['objects'], task['boxes'] = [], []
            task['num_objects'] = max(1, len(task['objects']))

            if stage_3_results == {} or not stage_3_results[image_name][task_name]:
                tasks.append(task)

    return tasks

def prepare_launch(args):
    tasks = get_tasks(args)
    if len(tasks) == 0:
        assert utils.all_rounds_are_done(args), 'Unknown error'
        assert False, 'All images exhaustively labeled. Proceed to stage 4.'

    if utils.is_relaunch(args):
        hits, assignments = get_relaunch_hits(tasks, args)
    else:
        hits = utils.get_hits_from_tasks(tasks, args)
        assignments = [1 for _ in hits]

    rewards = [utils.get_reward(args) for _ in hits]
    return hits, rewards, assignments
