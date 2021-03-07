import utils

tasks_per_hit = 5
# reward_per_hit = 0.1
reward_per_hit = 0.5

get_hits_from_data = lambda tasks: [tasks[i:i+tasks_per_hit] for i in range(0, len(tasks), tasks_per_hit)]

def prepare_relaunch(args):
    initial_data = utils.get_initial_data(args)
    knowledge = utils.get_knowledge_file(args)

    data, assignments = [], []
    for datum in initial_data:
        image_name = datum['url'].split('/')[-1]
        relationship = '_'.join([datum['subject']['name'], datum['predicate'], datum['object']['name']])
        image_knowledge = knowledge[image_name]['stage_1'][relationship]

        has_w1, has_w2 = 'worker_1' in image_knowledge , 'worker_2' in image_knowledge
        if has_w1 and has_w2: continue

        data.append(datum)
        assignments.append(int(not has_w1) + int(not has_w2))

    assert len(data) != 0, 'Stage 1 initial launch done'
    
    one_assignment_data = [datum for datum, assignment in zip(data, assignments) if assignment==1]
    two_assignment_data = [datum for datum, assignment in zip(data, assignments) if assignment==2]

    one_assignment_hits = get_hits_from_data(one_assignment_data)
    two_assignment_hits = get_hits_from_data(two_assignment_data)

    hits = one_assignment_hits + two_assignment_hits
    assignments = [1 for _ in one_assignment_hits] + [2 for _ in two_assignment_hits]
    rewards = [reward_per_hit for hit in hits]

    return hits, rewards, assignments

def is_relaunch(args):
    if utils.get_launch_file(args) == {}: return False

    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    return True

def prepare_launch(args):
    if is_relaunch(args):
        return prepare_relaunch(args)

    data = utils.get_initial_data(args)

    hits = get_hits_from_data(data)
    assignments = [2 for _ in hits]
    rewards = [reward_per_hit for hit in hits]

    return hits, rewards, assignments
