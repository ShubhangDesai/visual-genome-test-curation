import utils

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

def prepare_launch(args):
    assert utils.most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert utils.most_recent_launch_is_known(args), 'You must extract knowledge data first'

    knowledge, tasks = utils.get_knowledge_file(args), get_tasks(args)

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
