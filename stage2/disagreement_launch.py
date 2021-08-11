import utils

def prepare_launch(args):
    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    knowledge, tasks = utils.get_knowledge_file(args), utils.get_stage_2_tasks(args)
    round_num = utils.get_round(args)

    remaining_tasks, num_incomplete = [], 0
    for task in tasks:
        image_name = task['url']
        task_knowledge = knowledge[image_name]['stage_'+str(args.stage)][task['task_name']]
        round_knowledge = task_knowledge['round_' + str(round_num)]

        assert 'worker_1' in round_knowledge and 'worker_2' in round_knowledge, 'You must finish stage 3 initial launches first'

        if 'final_answer' not in round_knowledge:
            remaining_tasks.append(task)
        else:
            num_incomplete += int(not round_knowledge['final_answer'])

    if len(remaining_tasks) == 0:
        utils.mark_current_stage_round_as_done(args)

        if num_incomplete == 0:
            postfix = 'All images exhaustively labeled. Proceed to stage 3.'
            utils.mark_all_rounds_as_done(args)
        else:
            postfix = str(num_incomplete) + ' images not exhaustively labeled; therefore, another round is needed. Proceed back to stage 1.'

        assert False, 'Stage 2 round %d disagreement launch done. %s' % (round_num, postfix)

    hits = utils.get_hits_from_tasks(remaining_tasks, args)
    assignments = [1 for _ in hits]
    rewards = [utils.get_reward(args) for _ in hits]

    return hits, rewards, assignments
