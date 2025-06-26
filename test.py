import json




# from qdrant_client import QdrantClient

# qdrant = QdrantClient(
#     url="https://49e23577-2b75-49a0-ab71-2940f9ba2db9.eu-central-1-0.aws.cloud.qdrant.io:6333", 
#     api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Dw7SB1LmmftGmVd2ij61MjemAzu6A1_KMFQ67Ab5gbM",
#     timeout=600.0
# )

# print(qdrant_client.get_collections())


# 读取数据
with open("data/structured_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts, payloads = [], []

# 病虫害部分
for record in data["pests"]:
    full_text = f"{record['title']}\n"
    full_text += f"{record['symptom_field']}：{record['symptom_content']}\n"
    full_text += f"{record['rule_field']}：{record['rule_content']}\n"
    full_text += f"{record['control_field']}：{record['control_content']}\n"

    # 拼接图片名
    if record.get("images"):
        for img in record["images"]:
            full_text += f"图片：{img['filename']}\n"

    texts.append(full_text)
    payloads.append(record)

# 杂草防除部分
weed = data["weed"]
full_text = weed["content"] + "\n"

if weed.get("images"):
    for img in weed["images"]:
        full_text += f"图片：{img['filename']}\n"

texts.append(full_text)
payloads.append(weed)
i=0
for t in texts:
    print(t)
    print()
    i=i+1
    if i==3 :
        break

