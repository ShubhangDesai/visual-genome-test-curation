import stages
import utils

def update_knowledge(stage, stage_knowledge, result, worker_id, hit_id):
    task_name = result['task_name']
    task_knowledge = stage_knowledge.get(task_name, {'hit_ids': []})
    task_knowledge['hit_ids'].append(hit_id)

    if 'worker_1' not in task_knowledge: worker = 'worker_1'
    elif 'worker_2' not in task_knowledge: worker = 'worker_2'
    else:
        assert stage.is_disagreement(task_knowledge), 'Unknown error'
        assert 'worker_3' not in task_knowledge, 'Unknown error'
        worker = 'worker_3'

    worker_knowledge = {'worker_id': worker_id, 'answer': [o['rect'] for o in result['objects']]} # TODO
    task_knowledge[worker] = worker_knowledge

    if worker == 'worker_2' and not stage.is_disagreement(task_knowledge):
        task_knowledge['final_answer'] = stage.aggregate(task_knowledge)
    elif worker == 'worker_3':
        task_knowledge['final_answer'] = stage.aggregate(task_knowledge)

    stage_knowledge[task_name] = task_knowledge
    return stage_knowledge

def main(args):
    # Get launch stage
    if args.stage == 1: stage = stages.stage1
    elif args.stage == 2: stage = stages.stage2

    assert not utils.most_recent_launch_is_known(args), 'Launch knowledge already extracted'

    # Get the most recent HIT results
    dump = utils.get_dump_file(args)
    hit_ids, assignments = utils.get_most_recent_hit_ids_and_assignments(args)

    hits = {}
    for hit_id, assignment in zip(hit_ids, assignments):
        assert hit_id in dump and len(dump[hit_id]) == assignment, 'Did not finish dumping launch HITs'
        hits[hit_id] = dump[hit_id]

    # Run attention checks and filter out failed workers
    failed_workers = stage.run_attention_checks(hits)
    sucessful_results, approvals_list = utils.filter_out_failed_workers(hits, failed_workers)
    print('%d out of %d results sucessful' % (len(sucessful_results), sum(assignments)))

    # Update the knowledge for each image
    knowledge_file = utils.get_knowledge_file(args)
    for result in sucessful_results:
        for output in result['output']:
            image_name = output['url'].split('/')[-1]

            image_knowledge = knowledge_file.get(image_name, {})
            stage_knowledge = image_knowledge.get('stage_'+str(args.stage), {})

            updated_stage_knowledge = update_knowledge(stage, stage_knowledge, output, result['worker_id'], result['hit_id'])
            image_knowledge['stage_'+str(args.stage)] = updated_stage_knowledge
            knowledge_file[image_name] = image_knowledge

    utils.update_most_recent_launch_with_approvals(approvals_list, args)
    utils.mark_most_recent_launch_as_known(args)
    utils.save_knowledge_file(knowledge_file, args)

if __name__ == '__main__':
    args = utils.parse_args()
    main(args)
