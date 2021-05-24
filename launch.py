import stages
import utils

from easyturk import interface

def main(args):
    # Get launch stage
    if args.stage == 1: stage = stages.stage1
    elif args.stage == 2: stage = stages.stage2

    # Get HITs, rewards, and assignments
    if args.initial_launch:
        hits, rewards, assignments = stages.initial_launch.prepare_launch(args)
    elif args.disagreement_launch:
        hits, rewards, assignments = stages.disagreement_launch.prepare_launch(args)

    # Check that there's enough money
    cost = sum([r*a for r, a in zip(rewards, assignments)])
    assert interface.get_account_balance(args.sandbox) >= cost, 'Insufficient funds'

    # Confirm launch
    print('Total cost for %d assignments across %d HITs: %0.2f' % (sum(assignments), len(hits), cost))
    print('Launch to %s?' % ('sandbox' if args.sandbox else 'production'))
    assert input() == 'y', 'Aborting'

    # Launch the HITs
    hit_ids = stage.launch(hits, rewards, assignments, args.sandbox)
    print('HIT IDs: %s' % str(hit_ids))

    # Save the HIT IDs
    utils.save_launch_to_launch_file(hit_ids, assignments, cost, args)

if __name__ == '__main__':
    args = utils.parse_args(launch=True)
    main(args)
