import utils

import os
from easyturk import interface

def main(args):
    hit_ids, assignments = utils.get_most_recent_hit_ids_and_assignments(args)
    results = interface.fetch_completed_hits(hit_ids, sandbox=args.sandbox, approve=False)

    dump = utils.get_dump_file(args)
    incomplete_hits = sum(assignments)

    for hit_id, assignment in zip(hit_ids, assignments):
        if hit_id not in results: 
            continue

        hit_results = results[hit_id]
        if args.sandbox and assignment == 2: hit_results.append(hit_results[0])

        completed_assignments = len(hit_results)

        incomplete_hits -= completed_assignments
        if hit_id in dump: # If hit already added
            continue

        if completed_assignments == assignment: # Only update if the HIT is completed for all assignments
            dump[hit_id] = hit_results

    if incomplete_hits == 0:
        utils.mark_most_recent_launch_as_done(args)
        print('HITs completed')
    else:
        print('There are %d HITs still incomplete' % incomplete_hits)

    utils.save_dump_file(dump, args)

if __name__ == '__main__':
    args = utils.parse_args()
    main(args)
