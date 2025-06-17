import json
from qdrant_client import QdrantClient

qdrant = QdrantClient("localhost", port=6333)
collection = "corn_base64_knowledge"

all_points = []
scroll_offset = None

while True:
    scroll_result = qdrant.scroll(collection_name=collection, limit=100, offset=scroll_offset)
    batch, scroll_offset = scroll_result
    if not batch:
        break
    all_points.extend(batch)

exported_data = []
for point in all_points:
    exported_data.append({
        "id": point.id,
        "vector": point.vector,
        "payload": point.payload
    })

with open("exported_knowledge.json", "w", encoding="utf-8") as f:
    json.dump(exported_data, f, ensure_ascii=False, indent=2)

print("✅ 知识库已导出")