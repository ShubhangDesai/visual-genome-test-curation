import utils
from easyturk import EasyTurk

def main(args):
    launches = utils.get_launch_file(args)['launches']
    dump = utils.get_dump_file(args)

    et = EasyTurk(sandbox=args.sandbox)
    for launch in launches:
        for hit_id, approval in zip(launch['hit_ids'], launch['approvals']):
            for result, approved in zip(dump[hit_id], approval):
                assignment_id = result['assignment_id']
                if approved:
                    et.approve_assignment(assignment_id)
                else:
                    et.reject_assignment(assignment_id)

if __name__ == '__main__':
    args = utils.parse_args()
    main(args)
