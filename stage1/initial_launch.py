import utils

reward_per_img = 0.5

def prepare_relaunch(args):
    initial_data = utils.get_initial_data(args)
    knowledge = utils.get_knowledge_file(args)

    data, assignments = [], []
    for datum in initial_data:
        image_name = datum['url'].split('/')[-1]
        image_knowledge = knowledge[image_name]['stage_'+str(args.stage)]

        has_w1, has_w2 = 'worker_1' in image_knowledge , 'worker_2' in image_knowledge
        if has_w1 and has_w2: continue

        data.append(datum)
        assignments.append(int(not has_w1) + int(not has_w2))

    assert len(data) != 0, 'Stage 1 initial launch done'

    return data, [reward_per_img for _ in data], assignments

def is_relaunch(args):
    if utils.get_launch_file(args) == {}: return False

    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    return True

def prepare_launch(args):
    if is_relaunch(args):
        return prepare_relaunch(args)

    data = utils.get_initial_data(args)
    assignments = [2 for _ in data]

    return data, [reward_per_img for _ in data], assignments
