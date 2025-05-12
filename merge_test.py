import os
import shutil
from pathlib import Path

# Set paths
root_dir = Path("G:\\downloads\\challenge1_challenge2\\test")
# output_images_dir = Path("G:\\GRADUATE\\lab\\Yolov11\\train\\images")
# output_labels_dir = Path("G:\\GRADUATE\\lab\\Yolov11")
output_base = Path("G:\\GRADUATE\\lab\\Yolov11\\v2_test")

# Create output folders
# output_images_dir.mkdir(parents=True, exist_ok=True)
# output_labels_dir.mkdir(parents=True, exist_ok=True)
# output_labels_dir.mkdir(parents=True, exist_ok=True)

# Scenarios and sensor types
# scenarios = ["bg11"]
scenarios = ["bg2", "bg6", "bg8","cy3"]
sensors = ["GS_RGB", "GS_SWIR", "GS_Therm", "GS_UV","UAV_RGB", "UAV_Therm"]

# Process each scenario and sensor
for scenario in scenarios:
    for sensor in sensors:
        img_folder = root_dir / scenario / sensor / "images"
        label_folder = root_dir / scenario / sensor / "labels"  # adjust if labels are elsewhere
        out_img_dir = output_base / sensor /"train"/ "images"
        out_lbl_dir = output_base / sensor /"train"/ "labels"
        out_img_dir.mkdir(parents=True, exist_ok=True)
        out_lbl_dir.mkdir(parents=True, exist_ok=True)
        if not img_folder.exists():
            continue  # skip if folder doesn't exist

        for img_file in img_folder.glob("*.jpg"):
            # Construct new filename: bg1_GS_RGB_0000.jpg
            new_name = f"{scenario}_{sensor}_{img_file.stem}{img_file.suffix}"
            shutil.copy(img_file, out_img_dir / new_name)
            
            # Look for corresponding label
            label_file = label_folder / f"{img_file.stem}.txt"
            if label_file.exists():
                new_label_name = f"{scenario}_{sensor}_{img_file.stem}.txt"
                shutil.copy(label_file, out_lbl_dir / new_label_name)

print("✅ Done moving and renaming files.")
