import os, json, argparse, datetime
from easyturk import interface
import utils

def main(args):
	# et = interface.EasyTurk(args.sandbox)
	# deleted = et.delete_hit(hit_id=args.hit)
	hit_ids, assignments = utils.get_most_recent_hit_ids_and_assignments(args)
	results = interface.fetch_completed_hits(hit_ids, sandbox=args.sandbox, approve=False)
	print(hit_ids)
	for hit_id in hit_ids:
		for worker in results[hit_id]:
			print("Worker for HIT", hit_id)

	# print("Deleted HIT ID: {}, Status: {}".format(args.hit, deleted))


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--hit', type=str, required=True)
    parser.add_argument('--sandbox', action='store_true')
    parser.add_argument('--exp_name', type=str, required=True)
    parser.add_argument('--stage', type=int, required=True, choices=[1,2,3])
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
