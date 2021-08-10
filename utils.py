import os, json, argparse, datetime
from PIL import ImageDraw

## BASIC READ FUNCTIONS

def read_json(filepath):
    if not os.path.exists(filepath): return {}
    with open(filepath, 'r') as f:
        data = json.load(f)

    return data

def get_initial_data(args):
    filepath = os.path.join('data', args.exp_name, 'initial_data.json')
    return read_json(filepath)

def get_launch_file(args):
    filename = 'stage_%d_launches.json' % args.stage
    filepath = os.path.join('data', args.exp_name, filename)

    return read_json(filepath)

def get_dump_file(args):
    filepath = os.path.join('data', args.exp_name, 'amt_dump.json')

    return read_json(filepath)

def get_knowledge_file(args):
    filepath = os.path.join('data', args.exp_name, 'images_knowledge.json')

    return read_json(filepath)



## READ FUNCTIONS W/ LOGIC

def get_most_recent_hit_ids_and_assignments(args):
    launches = get_launch_file(args)['launches']
    most_recent_launch = launches[-1]

    return most_recent_launch['hit_ids'], most_recent_launch['assignments']

def most_recent_launch_is_done(args):
    launches = get_launch_file(args)['launches']
    most_recent_launch = launches[-1]

    return most_recent_launch.get('done', False)

def most_recent_launch_is_known(args):
    launches = get_launch_file(args)['launches']
    most_recent_launch = launches[-1]

    return most_recent_launch.get('known', False)

def get_round(args):
    filepath = os.path.join('data', args.exp_name, 'stage_1_launches.json')
    round = read_json(filepath).get('round', 1)

    return round

def get_stage_1_results(args):
    knowledge_file = get_knowledge_file(args)

    stage_1_results = {}
    for image_name, image_knowledge in knowledge_file.items():
        stage_1_knowledge = image_knowledge['stage_1']
        simplified_knowledge = {}

        for task_name, task_knowledge in stage_1_knowledge.items():
            rounds = [int(k.split('_')[-1]) for k in task_knowledge.keys() if 'worker' in k]
            latest_round = sorted(rounds)[-1]

            latest_objects = task_knowledge['worker_' + str(latest_round)]['answer']
            simplified_knowledge[task_name] = latest_objects

        stage_1_results[image_name] = simplified_knowledge

    return stage_1_results

def get_stage_2_results(args):
    knowledge_file = get_knowledge_file(args)

    stage_2_results = {}
    for image_name, image_knowledge in knowledge_file.items():
        if 'stage_2' not in image_knowledge: continue

        stage_2_knowledge = image_knowledge['stage_2']
        simplified_knowledge = {}

        for task_name, task_knowledge in stage_2_knowledge.items():
            rounds = [int(k.split('_')[-1]) for k in task_knowledge.keys() if 'round' in k]
            latest_round = sorted(rounds)[-1]

            latest_answer = task_knowledge['round_' + str(latest_round)]['final_answer']
            simplified_knowledge[task_name] = latest_answer

        stage_2_results[image_name] = simplified_knowledge

    return stage_2_results


## BASIC WRITE FUNCTIONS

def write_json(data, filepath):
    with open(filepath, 'w') as f:
        f.write(json.dumps(data, indent=2, default=datetime_converter))

def save_dump_file(dump, args):
    filepath = os.path.join('data', args.exp_name, 'amt_dump.json')
    write_json(dump, filepath)

def save_knowledge_file(knowledge_file, args):
    filepath = os.path.join('data', args.exp_name, 'images_knowledge.json')
    write_json(knowledge_file, filepath)



## WRITE FUNCTION W/ LOGIC

def save_launch_to_launch_file(hit_ids, assignments, cost, args):
    launch_data = get_launch_file(args)
    if 'launches' not in launch_data: launch_data['launches'] = []

    if 'cost' not in launch_data: launch_data['cost'] = 0
    launch_data['cost'] += cost

    if args.stage == 1 or args.stage == 2:
        if args.stage == 1 and 'round' not in launch_data: launch_data['round'] = 1
        if 'round_done' not in launch_data: launch_data['round_done'] = False

        if launch_data['round_done']:
            launch_data['round_done'] = False
            if args.stage == 1:
                launch_data['round'] += 1

    launch_dict = {'hit_ids': hit_ids, 'assignments': assignments, 'initial': args.initial_launch}
    launch_data['launches'].append(launch_dict)

    filepath = os.path.join('data', args.exp_name, 'stage_%d_launches.json' % args.stage)
    write_json(launch_data, filepath)

def mark_most_recent_launch_as_done(args):
    launch_data = get_launch_file(args)
    launch_data['launches'][-1]['done'] = True

    filepath = os.path.join('data', args.exp_name, 'stage_%d_launches.json' % args.stage)
    write_json(launch_data, filepath)

def update_most_recent_launch_with_approvals(approvals_list, args):
    launch_data = get_launch_file(args)
    launch_data['launches'][-1]['approvals'] = approvals_list

    filepath = os.path.join('data', args.exp_name, 'stage_%d_launches.json' % args.stage)
    write_json(launch_data, filepath)

def mark_most_recent_launch_as_known(args):
    launch_data = get_launch_file(args)
    launch_data['launches'][-1]['known'] = True

    filepath = os.path.join('data', args.exp_name, 'stage_%d_launches.json' % args.stage)
    write_json(launch_data, filepath)

def mark_current_stage_round_as_done(args):
    launch_data = get_launch_file(args)
    launch_data['round_done'] = True

    filepath = os.path.join('data', args.exp_name, 'stage_%d_launches.json' % args.stage)
    write_json(launch_data, filepath)

    #if args.stage == 1: mark_stage_2_round_as_incomplete(args)

def mark_stage_2_round_as_incomplete(args):
    filepath = os.path.join('data', args.exp_name, 'stage_2_launches.json')
    stage_2_data = read_json(filepath)

    if stage_2_data != {}:
        stage_2_data['round_done'] = False
        write_json(stage_2_data, filepath)


# STAGE UTIL FUNCTIONS

def stage_round_is_done(stage, args):
    filepath = os.path.join('data', args.exp_name, 'stage_%d_launches.json' % stage)
    return read_json(filepath).get('round_done', False)

def stage_1_round_is_done(args):
    return stage_round_is_done(1, args)

def stage_2_round_is_done(args):
    return stage_round_is_done(2, args)

def is_relaunch(args):
    if get_launch_file(args) == {}: return False

    if args.stage == 1 and stage_1_round_is_done(args):
        assert stage_2_round_is_done(args), 'You must finish stage 2 round %d first' % get_round(args)

        return False
    elif args.stage == 2 and stage_2_round_is_done(args):
        assert stage_1_round_is_done(args), 'You must finish stage 2 round %d first' % get_round(args)

        return False

    assert most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert most_recent_launch_is_known(args), 'You must extract knowledge data first'

    return True

def get_stage_2_tasks(args):
    knowledge_file = get_knowledge_file(args)
    round = get_round(args)

    tasks = []
    for image_name, image_knowledge in knowledge_file.items():
        stage_1_knowledge = image_knowledge['stage_1']

        for task_name, task_knowledge in stage_1_knowledge.items():
            worker = 'worker_' + str(round)
            if worker not in task_knowledge: continue

            subject_name, predicate_name, object_name, main = task_name.split('_')
            subject, object = {'name': subject_name}, {'name': object_name}
            main = subject_name if main == 'subject' else object_name
            url = image_name

            task = {'url': url, 'subject': subject, 'object': object, 'predicate': predicate_name, 'main': main, 'task_name': task_name}
            task['objects'] = [{'rect': rect} for rect in task_knowledge[worker]['answer']]
            task['num_objects'] = len(task['objects'])

            tasks.append(task)

    return tasks


def get_stage_3_tasks(args):
    knowledge_file = get_knowledge_file(args)

    tasks = []
    for image_name, image_knowledge in knowledge_file.items():
        stage_1_knowledge = image_knowledge['stage_1']
        for relationship in get_relationships(stage_1_knowledge):
            subjects, objects = get_subjects_and_objects(relationship, stage_1_knowledge)
            subject_name, predicate_name, object_name = relationship.split('_')
            for i, subject in enumerate(subjects):
                for j, object in enumerate(objects):
                    subject['name'], object['name'] = subject_name, object_name
                    url = image_name
                    task_name = '_'.join([subject_name, predicate_name, object_name, str(i), str(j)])
                    task = {'url': url, 'subject': subject, 'object': object, 'predicate': predicate_name, 'task_name': task_name}

                    tasks.append(task)

    return tasks



## MISC FUNCTIONS

def parse_args(launch=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_name', type=str, required=True)
    parser.add_argument('--stage', type=int, required=True, choices=[1,2,3])
    parser.add_argument('--sandbox', action='store_true')

    if launch:
        launch_args = parser.add_mutually_exclusive_group(required=True)
        launch_args.add_argument('--initial_launch', action='store_true')
        launch_args.add_argument('--disagreement_launch', action='store_true')

    return parser.parse_args()

def get_hits_from_tasks(tasks, args):
    tasks_per_hit = [10, 10, 10][args.stage-1]
    return [tasks[i:i+tasks_per_hit] for i in range(0, len(tasks), tasks_per_hit)]

def get_reward(args):
    return [1, 0.5, 0.5][args.stage-1]

def filter_out_failed_workers(hits, failed_workers):
    failed_workers = set(failed_workers)

    successful_results, approvals_list = [], []
    for _, results in hits.items():
        hit_approvals = []
        for result in results:
            if result['worker_id'] in failed_workers:
                hit_approvals.append(False)
            else:
                hit_approvals.append(True)
                successful_results.append(result)

        approvals_list.append(hit_approvals)

    return successful_results, approvals_list

def get_relationships(stage_1_knowledge):
    return set(['_'.join(k.split('_')[:-1]) for k in stage_1_knowledge.keys()])

def get_subjects_and_objects(relationship, stage_1_knowledge):
    subject_knowledge = stage_1_knowledge[relationship + '_subject']
    object_knowledge = stage_1_knowledge[relationship + '_object']

    # while True:
    #     # TODO: assumes number of rounds for subject/object tasks are the same,
    #     # which is not necessarily true; fix this
    #
    #     worker = 'worker_' + str(i)
    #     if worker not in subject_knowledge: break
    #
    #     subjects.extend(subject_knowledge[worker]['answer'])
    #     objects.extend(object_knowledge[worker]['answer'])
    #     i += 1

    subjects, objects = [], []
    for l, knowledge in [(subjects, subject_knowledge), (objects, object_knowledge)]:
        rounds = [int(k.split('_')[-1]) for k in knowledge.keys() if 'worker' in k]
        latest_round = sorted(rounds)[-1]

        l.extend(knowledge['worker_'+str(latest_round)]['answer'])

    subject_name, _, object_name = relationship.split('_')
    for i in range(len(subjects)): subjects[i]['name'] = subject_name
    for i in range(len(objects)): objects[i]['name'] = object_name

    return subjects, objects

def draw_rects(img, objs, color):
    draw = ImageDraw.Draw(img)
    for box in objs:
        draw.rectangle([box['x'], box['y'], box['x'] + box['w'], box['y'] + box['h']], outline=color, width=3)

    return img

def datetime_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
