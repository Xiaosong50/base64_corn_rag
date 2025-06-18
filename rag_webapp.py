from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI



app = Flask(__name__)

# 嵌入模型
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")

# Qdrant客户端
# qdrant = QdrantClient("localhost", port=6333)
qdrant = QdrantClient(
    host="localhost",
    grpc_port=6334,   #  关键切换点
    prefer_grpc=True, #  启用 gRPC 
)
collection = "corn_base64_knowledge"

# LLM挂载
llm = ChatOpenAI(
    openai_api_key="sk-1bb535fafae7492b8e1ea724e4bade9c",
    openai_api_base="https://api.deepseek.com",
    model="deepseek-chat"
)

@app.route("/", methods=["GET", "POST"])
def index():
    answer, results = None, []
    if request.method == "POST":
        query = request.form["query"]
        query_vec = model.encode(query)
        
        # 向量召回
        hits = qdrant.search(collection_name=collection, query_vector=query_vec, limit=2, with_payload=True)
        
        context = ""
        for hit in hits:
            payload = hit.payload
            results.append(payload)
            
            # 构造召回内容上下文
            if payload.get('type') == '病虫害':
                context += f"【{payload['title']}】\n"
                if payload['symptom_content']:
                    context += f"{payload['symptom_field']}：{payload['symptom_content']}\n"
                if payload['rule_content']:
                    context += f"{payload['rule_field']}：{payload['rule_content']}\n"
                if payload['control_content']:
                    context += f"{payload['control_field']}：{payload['control_content']}\n"
                context += "\n"
            elif payload.get('type') == '杂草防除':
                context += f"【{payload['title']}】\n{payload['content']}\n\n"

            if payload.get("images"):
                for img in payload["images"]:
                    context += f"图片：{img['filename']}\n"

    context += "\n"
        # 给LLM的标准Prompt
        rag_prompt = f"""你是一位资深的农业知识助手，并喜欢完整的讲解用户的问题，请根据以下知识片段回答用户问题：
{context}
用户问题：{query}。"""

        response = llm.invoke(rag_prompt)
        answer = response.content
        
    return render_template("index.html", results=results, answer=answer)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)