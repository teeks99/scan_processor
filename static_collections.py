import os
import json

collections = []
with open("collections.json", "r") as f:
    sc = json.load(f)
    collections = sc["collections"]

packets = {}
for collection in collections:
    entries = []
    with open(collection["index"], "r") as cf:
        entries = json.load(cf)
    output = open(collection["index"][:-4]+"html", "w")
    output.write("<html><body>")
    output.write("<h1>" + collection["name"] + "</h1>")
    for entry in entries:
        edir = entry["dir"]
        img_num = entry["img"]
        full_img = os.path.join(edir, img_num + ".jpg")
        if not entry["dir"] in packets:
            with open(os.path.join(edir, "data_" + edir + ".json"), "r") as df:
                data = json.load(df)
                packets[edir] = data
            comment = ""
            for img in packets[edir]["special_images"]:
                if img["number"] == img_num:
                    if "comment" in img:
                        comment = img["comment"]
                    break
        output.write("<p><a href=\"" + full_img + "\"><img src=\"" +
                     os.path.join(edir, "disp", img_num + ".jpg") + "\"><br>" +
                     comment + "</a></p>")
    output.write("</body></html>")

