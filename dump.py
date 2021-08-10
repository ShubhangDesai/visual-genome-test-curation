import utils

import os
from easyturk import interface

def main(args):
    hit_ids, assignments = utils.get_most_recent_hit_ids_and_assignments(args)
    results = interface.fetch_completed_hits(hit_ids, sandbox=args.sandbox, approve=False)

    dump = utils.get_dump_file(args)
    incomplete_assignments = sum(assignments)
    for hit_id, assignment in zip(hit_ids, assignments):
        if hit_id not in results: continue

        hit_results = results[hit_id]
        if args.sandbox and assignment == 2: hit_results.append(hit_results[0])

        completed_assignments = len(hit_results)

        incomplete_assignments -= completed_assignments
        if hit_id in dump: continue

        if completed_assignments == assignment: dump[hit_id] = hit_results

    if incomplete_assignments == 0:
        utils.mark_most_recent_launch_as_done(args)
        print('All assignments completed')
    else:
        print('There are %d assignments still incomplete' % incomplete_assignments)

    utils.save_dump_file(dump, args)

if __name__ == '__main__':
    args = utils.parse_args()
    main(args)
