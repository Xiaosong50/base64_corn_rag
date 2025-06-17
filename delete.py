from qdrant_client import QdrantClient

qdrant = QdrantClient("localhost", port=6333)

# 删除整个 collection
qdrant.delete_collection(collection_name="corn_base64_knowledge")

print("已删除 collection：corn_base64_knowledge")