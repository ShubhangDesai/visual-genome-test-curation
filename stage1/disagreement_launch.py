import utils

tasks_per_hit = 5
reward_per_hit = 0.5

get_hits_from_data = lambda tasks: [tasks[i:i+tasks_per_hit] for i in range(0, len(tasks), tasks_per_hit)]

def prepare_launch(args):
    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    initial_data = utils.get_initial_data(args)
    knowledge = utils.get_knowledge_file(args)

    data = []
    for datum in initial_data:
        image_name = datum['url'].split('/')[-1]
        relationship = '_'.join([datum['subject']['name'], datum['predicate'], datum['object']['name']])
        image_knowledge = knowledge[image_name]['stage_1'][relationship]

        assert 'worker_1' in image_knowledge and 'worker_2' in image_knowledge, 'You must finish stage 1 initial launches first'

        if 'final_answer' not in image_knowledge:
            data.append(datum)

    assert len(data) != 0, 'Stage 1 disagreement launch done'

    hits = get_hits_from_data(data)
    assignments = [1 for _ in hits]
    rewards = [reward_per_hit for hit in hits]

    return hits, rewards, assignments
