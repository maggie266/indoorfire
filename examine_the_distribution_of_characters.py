import os, re
from collections import Counter
img_dir = r"D:\Fire_Project\FireDataset_new2\test\images"
scenes = ("bedroom","livingroom","living_room","kitchen","office","diningroom","dining_room","corridor")
actions = ("injured_run","slow_run","injured_walk_backwards","sit_to_stand","standing_yell",
           "fall_flat","hit_to_side_of_body","crawling","sitting_idle","standing_idle")
c = Counter()
for f in os.listdir(img_dir):
    s = re.sub(r"^\d+_", "", os.path.splitext(f)[0].lower())
    for sc in scenes:
        if s.startswith(sc + "_"): s = s[len(sc)+1:]; break
    victim = s
    for a in actions:
        i = s.find("_" + a)
        if i > 0: victim = s[:i]; break
    else:
        victim = re.sub(r"_(horlook|overlook).*$", "", s)
    c[victim] += 1
for k, v in c.most_common(40): print(f"{v:5d}  {k}")