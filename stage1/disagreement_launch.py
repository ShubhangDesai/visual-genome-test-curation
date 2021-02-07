import utils

reward_per_img = 0.5

def prepare_launch(args):
    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    initial_data = utils.get_initial_data(args)
    knowledge = utils.get_knowledge_file(args)

    data = []
    for datum in initial_data:
        image_name = datum['url'].split('/')[-1]
        image_knowledge = knowledge[image_name]['stage_'+str(args.stage)]

        assert 'worker_1' in image_knowledge and 'worker_2' in image_knowledge, 'You must finish stage 1 initial launches first'

        if 'final_answer' not in image_knowledge:
            data.append(datum)

    assert len(data) != 0, 'Stage 1 disagreement launch done'

    return data, [reward_per_img for _ in data], [1 for _ in data]
