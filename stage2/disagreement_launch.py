import utils

def prepare_launch(args):
    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    knowledge, tasks = utils.get_knowledge_file(args), utils.get_stage_2_tasks(args)

    remaining_tasks = []
    for task in tasks:
        image_name = task['url'].split('/')[-1]
        task_knowledge = knowledge[image_name]['stage_'+str(args.stage)][task['task_name']]

        assert 'worker_1' in task_knowledge and 'worker_2' in task_knowledge, 'You must finish stage 2 initial launches first'

        if 'final_answer' not in task_knowledge:
            remaining_tasks.append(task)

    assert len(remaining_tasks) != 0, 'Stage 2 disagreement launch done'

    hits = utils.get_hits_from_tasks(remaining_tasks, args)
    assignments = [1 for _ in hits]
    rewards = [utils.get_reward(args) for _ in hits]

    return hits, rewards, assignments
