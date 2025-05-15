import os
import xml.etree.ElementTree as ET
from PIL import Image
from pathlib import Path
from collections import defaultdict

classes=['person','vessel', 'vehicle']

def get_file_list(dir, files, ext=None):
    """
    get all files with specific extension under a directory
    dir: drectory
    files: file list
    """
    newDir = dir
    if os.path.isfile(dir):
        if ext is None:
            files.append(dir)
        else:
            if ext in dir:
                files.append(dir)
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            new_dir = os.path.join(dir,s)
            get_file_list(new_dir, files, ext)


def convert(size, box):
    dw = 1.0/size[0]
    dh = 1.0/size[1]
    x = (box[0]+box[1])/2.0
    y = (box[2]+box[3])/2.0
    w = box[1]-box[0]
    h = box[3]-box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return [x,y,w,h]

def convert_xml_to_txt(xml_dir):
    xml_files = []
    # get All xml annotation files
    get_file_list(xml_dir, xml_files, '.xml')
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for image in root.findall('image'):
            image_name = image.get('name')
            image_width = float(image.get('width'))
            image_height = float(image.get('height'))

            output_lines = []
            for box in image.findall('box'):
                label = box.get('label')
                if label not in classes:
                    classes.append(label)
                    print(f'{label} not in classes')
                class_id = classes.index(label)
                xtl = float(box.get("xtl"))
                ytl = float(box.get("ytl"))
                xbr = float(box.get("xbr"))
                ybr = float(box.get("ybr"))
                bdx = convert((image_width, image_height), (xtl, xbr, ytl, ybr))
                # YOLO format <class_id> <center_x> <center_y> <width> <height>
                oline = f"{class_id} {' '.join(str(a) for a in bdx)}"
                output_lines.append(oline)
            label_file = os.path.join(os.path.dirname(xml_file), 'labels', os.path.splitext(image_name)[0] +'.txt')
            label_dir = os.path.dirname(label_file)
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)
            with open(label_file, 'a') as f:
                f.write('\n'.join(output_lines))
                f.close()
        with open('classes.txt', 'a') as f:
            f.write('\n'.join(classes))
            f.close()

# Group data by (scenario, sensor)
grouped_predictions = defaultdict(list)
def convert_txt_to_xml(image_dir, output_dir):

    for image_file in image_dir.glob("*.jpg"):
        image = Image.open(image_file)
        w,h = image.size
        # split file name to get scenario, sensor, and image real name(with suffix)
        parts = str(image_file.stem).split("_", 3)
        scenario = parts[0]
        sensor = "_".join(parts[1:3])
        _ = parts[3]
        label_file = image_dir / "labels" / (image_file.stem+'.txt')
        if not label_file.exists():
            continue
        # open txt file
        with open(label_file, "r") as f:
            boxes = []
            for line in f:
                parts = line.strip().split()
                # center of bounding box, width and height of bounding box
                class_id, xc, yc, bw, bh = map(float, parts)
                abs_xc, abs_yc = xc * w, yc * h
                abs_bw, abs_bh = bw * w, bh * h
                xtl = abs_xc - abs_bw / 2
                ytl = abs_yc - abs_bh / 2
                xbr = abs_xc + abs_bw / 2
                ybr = abs_yc + abs_bh / 2
                boxes.append({
                    "label": classes[int(class_id)],
                    "xtl": xtl,
                    "ytl": ytl,
                    "xbr": xbr,
                    "ybr": ybr
                })
            grouped_predictions[(scenario, sensor)].append({
                "image_name": _,
                "width": w,
                "height": h,
                "boxes": boxes
            })
        
    for (scenario, sensor), images in grouped_predictions.items():
        root = ET.Element("predictions")
        for idx, img_data in enumerate(images):
            image_elem = ET.SubElement(root, "image", {
                "id": str(idx),
                "name": img_data["image_name"],
                "width": str(img_data["width"]),
                "height": str(img_data["height"])
            })
            object_id = 1
            for box in img_data["boxes"]:
                box_elem = ET.SubElement(image_elem, "box", {
                    "label": box["label"],
                    "xtl": f"{box['xtl']:.2f}",
                    "ytl": f"{box['ytl']:.2f}",
                    "xbr": f"{box['xbr']:.2f}",
                    "ybr": f"{box['ybr']:.2f}"
                })
                ET.SubElement(box_elem, "attribute", {"name": "ID"}).text = str(object_id)
                object_id+=1
        # make a new directory in different scenarios
        output_path = output_dir / scenario / sensor
        output_path.mkdir(parents=True, exist_ok=True)
        tree = ET.ElementTree(root)
        tree.write(output_path /"predictions.xml", encoding="utf-8", xml_declaration=True)
        print(f"Saved: {output_path / 'predictions.xml'}")

if __name__ == '__main__':
    # the directory to save images
    img_dir = ''
    xml_dir = ''
    # xml_dir = ''
    # label_dir = '' # new directory to save labels txt

    convert_xml_to_txt(xml_dir)
    # convert_txt_to_xml(
    #     Path(""),
    #     Path("")
    # )
