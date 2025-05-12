import random
from pathlib import Path
import shutil
from collections import defaultdict

def split_val(base_dir, val_ratio=0.05):
    # group by scenarios
    # caluculate its percent
    sensors = ["GS_RGB", "GS_SWIR", "GS_Therm", "GS_UV","UAV_RGB","UAV_Therm"]

    for sensor in sensors:
        print(f"\n📂 Processing sensor: {sensor}")
        img_dir = Path(base_dir) / sensor / "train" / "images"
        lbl_dir = Path(base_dir) / sensor / "train" / "labels"
        val_img_dir = Path(base_dir) / sensor / "val" / "images"
        val_lbl_dir = Path(base_dir) / sensor / "val" / "labels"

        val_img_dir.mkdir(parents=True, exist_ok=True)
        val_lbl_dir.mkdir(parents=True, exist_ok=True)

        # Group image files by scenario
        scenario_groups = defaultdict(list)
        for img_file in img_dir.glob("*.jpg"):
            parts = img_file.stem.split("_", 2)
            if len(parts) >= 2:
                scenario = parts[0]
                scenario_groups[scenario].append(img_file)

        moved_count = 0
        for scenario, files in scenario_groups.items():
            if not files:
                continue
            val_count = max(1, int(len(files) * val_ratio))
            sampled_files = random.sample(files, val_count)

            for img_file in sampled_files:
                label_file = lbl_dir / (img_file.stem + ".txt")
                shutil.move(str(img_file), str(val_img_dir / img_file.name))
                if label_file.exists():
                    shutil.move(str(label_file), str(val_lbl_dir / label_file.name))
                moved_count += 1

        print(f"✅ Moved {moved_count} validation samples for sensor {sensor}, across {len(scenario_groups)} scenarios.")

# Usage
split_val("G:\\GRADUATE\\lab\\Yolov11\\v3")
