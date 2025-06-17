import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

# 载入本地嵌入模型
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")

# 连接本地 Qdrant
qdrant = QdrantClient("localhost", port=6333)
collection = "corn_base64_knowledge"

while True:
    query = input("\n请输入你的问题（输入exit退出）：").strip()
    if query.lower() in ['exit', 'quit']:
        break

    query_vector = model.encode(query)

    hits = qdrant.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=3,
        with_payload=True
    )

    if not hits:
        print("⚠ 未召回到任何结果。")
        continue

    print("\n召回结果：")
    for i, point in enumerate(hits):
        payload = point.payload
        print(f"\n结果 {i+1}：")
        print(f"标题：{payload['title']}")
        print(f"类型：{payload.get('type','')}")
        
        if payload['type'] == '病虫害':
            print(f"{payload['symptom_field']}：{payload['symptom_content']}")
            print(f"{payload['rule_field']}：{payload['rule_content']}")
            print(f"{payload['control_field']}：{payload['control_content']}")
        elif payload['type'] == '杂草防除':
            print(f"内容：{payload['content']}")
        
        print("图片文件：")
        for img in payload['images']:
            print(f" - {img['filename']}")