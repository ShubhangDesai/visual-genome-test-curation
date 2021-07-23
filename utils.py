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
    if 'cost' not in launch_data: launch_data['cost'] = cost

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



# STAGE UTIL FUNCTIONS

def is_relaunch(args):
    if get_launch_file(args) == {}: return False

    assert most_recent_launch_is_done(args), 'You must finish dumping the launch HITs first'
    assert most_recent_launch_is_known(args), 'You must extract knowledge data first'

    return True

def get_stage_2_tasks(args):
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
                    url = 'https://images.cocodataset.org/test2017/' + image_name # TODO: fix this!!
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
    tasks_per_hit = [10, 10][args.stage-1]
    return [tasks[i:i+tasks_per_hit] for i in range(0, len(tasks), tasks_per_hit)]

def get_reward(args):
    return [1, 0.5][args.stage-1]

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
    subjects, objects, i = [], [], 1
    while True:
        worker = 'worker_' + str(i)
        if worker not in subject_knowledge: break

        subjects.extend(subject_knowledge[worker]['answer'])
        objects.extend(object_knowledge[worker]['answer'])
        i += 1

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
