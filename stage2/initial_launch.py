import utils

def get_relaunch_hits(tasks, args):
    knowledge = utils.get_knowledge_file(args)

    one_assignment_tasks, two_assignment_tasks = [], []
    for task in tasks:
        image_name = task['url'].split('/')[-1]
        if image_name not in knowledge:
            two_assignment_tasks.append(task)
            continue

        task_knowledge = knowledge[image_name]['stage_'+str(args.stage)][task['task_name']]
        has_w1, has_w2 = 'worker_1' in task_knowledge , 'worker_2' in task_knowledge
        if has_w1 and has_w2: continue

        if int(not has_w1) + int(not has_w2) == 1:
            one_assignment_tasks.append(task)
        else:
            two_assignment_tasks.append(task)

    assert len(one_assignment_tasks) + len(two_assignment_tasks) != 0, 'Stage 2 initial launch done'

    one_assignment_hits = utils.get_hits_from_tasks(one_assignment_tasks, args)
    two_assignment_hits = utils.get_hits_from_tasks(two_assignment_tasks, args)

    hits = one_assignment_hits + two_assignment_hits
    assignments = [1 for _ in one_assignment_hits] + [2 for _ in two_assignment_hits]

    return hits, assignments

def get_tasks(args):
    knowledge_file = utils.get_knowledge_file(args)

    tasks = []
    for image_name, image_knowledge in knowledge_file.items():
        stage_1_knowledge = image_knowledge['stage_1']
        relationships = set(['_'.join(k.split('_')[:-1]) for k in stage_1_knowledge.keys()])

        for relationship in relationships:
            subject_knowledge = stage_1_knowledge[relationship + '_subject']
            object_knowledge = stage_1_knowledge[relationship + '_object']
            subjects, objects, i = [], [], 1
            while True:
                worker = 'worker_' + str(i)
                if worker not in subject_knowledge: break

                subjects.extend(subject_knowledge[worker]['answer'])
                objects.extend(object_knowledge[worker]['answer'])
                i += 1

            subject_name, predicate_name, object_name = relationship.split('_')
            for i, subject in enumerate(subjects):
                for j, object in enumerate(objects):
                    subject['name'], object['name'] = subject_name, object_name
                    url = 'https://images.cocodataset.org/test2017/' + image_name # TODO: fix this!!
                    task_name = '_'.join([subject_name, predicate_name, object_name, str(i), str(j)])
                    task = {'url': url, 'subject': subject, 'object': object, 'predicate': predicate_name, 'task_name': task_name}

                    tasks.append(task)

    return tasks

def is_relaunch(args):
    if utils.get_launch_file(args) == {}: return False

    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    return True

def prepare_launch(args):
    tasks = get_tasks(args)
    if is_relaunch(args):
        hits, assignments = get_relaunch_hits(tasks, args)
    else:
        hits = utils.get_hits_from_tasks(tasks, args)
        assignments = [2 for _ in hits]

    rewards = [utils.get_reward(args) for _ in hits]
    return hits, rewards, assignments
