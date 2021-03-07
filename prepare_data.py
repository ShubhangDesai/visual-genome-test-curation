import os, json, argparse, datetime
import stage1, stage2, stage3
import utils

from easyturk import interface

# Parse VG-formatted data, gather unique relationships for stage_1, and output initial_data.json file
# Currently only works for 4 hits right now, but can easily specify
def main(args):
    input_file = args.input
    output_file = args.output
    if args.directory: # If director location given for both input and output
        input_file = args.directory + "/" + input_file
        output_file = args.directory + "/" + output_file

    curated_test_data = utils.read_json(input_file)

    formatted_data = []
    lower_lim, upper_lim = 5, 15
    num_rels = 0
    # for i in range(len(curated_test_data)):
    for i in range(lower_lim, upper_lim):
        img_url = curated_test_data[i]['url']
        img_objects = curated_test_data[i]['objects']

        # Get relationships in image
        img_rels = set()
        for rel in curated_test_data[i]['relationships']:
            sub = img_objects[rel['subject']]['name']
            obj = img_objects[rel['object']]['name']
            pred = rel['predicate']
            rel = (sub, pred, obj)
            img_rels.add(rel)

        # Format relationships in image according to data reading
        for rel in img_rels:
            sub_dict = {"name": rel[0]}
            obj_dict = {"name": rel[2]}
            entry = {"url": img_url, "predicate": rel[1], "subject": sub_dict, "object": obj_dict}
            formatted_data.append(entry)
            num_rels += 1

    # Save and provide output
    print("Number of relationships to verify: ", num_rels)
    utils.write_json(formatted_data, output_file)
    # print("Saved data with [{}] tasks".format(len(formatted_data)))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--directory', type=str, required=False)
    # parser.add_argument('--num_batches', type=int, required=False)
    # parser.add_argument('--stage', type=int, required=True, choices=[1,2,3])

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)






