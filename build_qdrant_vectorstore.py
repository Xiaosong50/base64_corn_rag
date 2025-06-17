import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

# 载入嵌入模型
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")

# 连接Qdrant，启用gRPC
qdrant = QdrantClient(
    host="localhost",
    grpc_port=6334,   # 关键切换点
    prefer_grpc=True, # 启用 gRPC
    timeout=600.0
)

collection = "corn_base64_knowledge"

# 删除旧collection
if qdrant.collection_exists(collection):
    qdrant.delete_collection(collection)

# 创建新的 collection
qdrant.create_collection(
    collection_name=collection,
    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
)

# 读取数据
with open("data/structured_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts, payloads = [], []

# 病虫害部分
for record in data["pests"]:
    full_text = f"{record['title']}\n{record['symptom_field']}：{record['symptom_content']}\n{record['rule_field']}：{record['rule_content']}\n{record['control_field']}：{record['control_content']}"
    texts.append(full_text)
    payloads.append(record)

# 杂草防除部分
weed = data["weed"]
texts.append(weed["content"])
payloads.append(weed)

# 批量嵌入（本地化预处理加速）
vectors = model.encode(texts, batch_size=32, show_progress_bar=True)

# 批量 upsert
batch_size = 20
total = len(vectors)

for i in range(0, total, batch_size):
    end_idx = min(i + batch_size, total)
    batch_points = [
        models.PointStruct(
            id=idx,
            vector=vectors[idx].tolist(),
            payload=payloads[idx]
        )
        for idx in range(i, end_idx)
    ]

    if batch_points:
        qdrant.upsert(collection_name=collection, points=batch_points)
        print(f"✅ 已入库 {end_idx} / {total} 条")

print("✅ Qdrant图文混合高速建库（gRPC）完成 ✅")