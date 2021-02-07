import stage1, stage2, stage3
import utils

def main(args):
    # Get launch stage
    if args.stage == 1: stage = stage1
    elif args.stage == 2: stage = stage2
    elif args.stage == 3: stage = stage3

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
        output = result['output'][0]
        image_name = output['url'].split('/')[-1]

        image_knowledge = knowledge_file.get(image_name, {})
        stage_knowledge = image_knowledge.get('stage_'+str(args.stage), {'hit_ids': []})
        stage_knowledge['hit_ids'].append(result['hit_id'])

        updated_stage_knowledge = stage.update_knowledge(stage_knowledge, result['worker_id'], output)

        image_knowledge['stage_'+str(args.stage)] = updated_stage_knowledge
        knowledge_file[image_name] = image_knowledge

    utils.update_most_recent_launch_with_approvals(approvals_list, args)
    utils.mark_most_recent_launch_as_known(args)
    utils.save_knowledge_file(knowledge_file, args)

if __name__ == '__main__':
    args = utils.parse_args()
    main(args)
