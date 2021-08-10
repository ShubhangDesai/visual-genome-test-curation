import utils
import io
from PIL import Image, ImageTk
import numpy as np
import PySimpleGUI as sg

def create_window(cursor, imgs, relationships):
    layout = [
        [sg.Image(key='-IMAGE-')],
        [sg.Text(relationships[cursor])],
        [sg.Button('All relationships')] + [sg.Button('Relationship ' + str(i)) for i in range(1, len(imgs[cursor]))],
        [sg.Button('Prev'), sg.Button('Next')],
    ]

    window = sg.Window(
        'VG Viz',
        layout,
        location=(0, 0),
        finalize=True,
        element_justification='center',
        font='Helvetica 18',
    )

    window['-IMAGE-'].update(data=ImageTk.PhotoImage(imgs[cursor][0]))

    return window

def main(args):
    knowledge_file = utils.get_knowledge_file(args)

    imgs, relationships = [], []
    for image_name, image_knowledge in knowledge_file.items():
        img = Image.open(image_name.replace('jpg', 'jpeg'))

        stage_1_knowledge  = image_knowledge['stage_1']
        for relationship in utils.get_relationships(stage_1_knowledge):
            imgs.append([])
            relationships.append(relationship)

            subjects, objects = utils.get_subjects_and_objects(relationship, stage_1_knowledge)

            all_rels_img = utils.draw_rects(img.copy(), subjects, 'red')
            all_rels_img = utils.draw_rects(all_rels_img, objects, 'green')
            imgs[-1].append(all_rels_img)

            stage_3_knowledge = image_knowledge['stage_3']
            for i, subject in enumerate(subjects):
                for j, object in enumerate(objects):
                    task_name = '_'.join([relationship, str(i), str(j)])
                    if not stage_3_knowledge[task_name]['final_answer']: continue

                    rel_img = utils.draw_rects(img.copy(), [subject], 'red')
                    rel_img = utils.draw_rects(rel_img, [object], 'green')
                    imgs[-1].append(rel_img)

    cursor = 0
    window = create_window(cursor, imgs, relationships)
    while True:
        event, values = window.read()
        if 'Relationship ' in event or 'All' in event:
            rel = int(event.split(' ')[-1]) if 'Relationship ' in event else 0
            window['-IMAGE-'].update(data=ImageTk.PhotoImage(imgs[cursor][rel]))
        elif event == 'Next' or event == 'Prev':
            cursor = min(cursor+1, len(imgs)-1) if event == 'Next' else max(cursor-1, 0)
            window.close()
            window = create_window(cursor, imgs, relationships)
        elif event == sg.WIN_CLOSE:
            break

    window.close()

if __name__ == '__main__':
    args = utils.parse_args()
    main(args)
