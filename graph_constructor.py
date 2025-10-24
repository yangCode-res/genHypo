from numpy import full
from pydantic_core import to_json
from api import generate_text,conversation_history
import nltk
import fitz  # PyMuPDF
from HG.BERN2.bern2.bern2 import annotate_text

def split_text(text, chunk_size):#数据分块
    chunks=[]
    current_chunk=""
    sentences = nltk.sent_tokenize(text)
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        elif current_chunk!="":
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks
    
def extract_causal_kg(fulltext, chunk_size=600):#抽取json格式的三元组
    chunks = split_text(fulltext, chunk_size)
    kg_triples = []
    for chunk in chunks[:1]:
    # Step 1: 识别⽂本中存在的因果类型
        causal_types=set()
        type_prompt = f"""
        识别⽂本中存在的因果关系类型:
        {chunk}
        输出因果类型列表(如:基因调控,信号通路,环境因素)，如果没有这种因果类型，返回空，不然用逗号隔开返回给我，不需要额外进行解释。
        """
        c_types=set(generate_text(type_prompt).split(","))
        for ctype in c_types:
            causal_types.add(ctype.strip())
        conversation_history.pop()  # 清除对话历史，防止上下文干扰
    # Step 2: 对每种类型分别抽取实例
        for ctype in causal_types:
            instance_prompt = f"""
            抽取{ctype}的因果实例:
            ⽂本: {chunk}
            输出格式(JSON):
            {{
            "subject": "原因实体",
            "subject_state": "baseline/upregulated/downregulated/activated/inhibited",
            "predicate": "具体因果关系(如upregulates, activates, inhibits)",
            "object": "结果实体",
            "object_state_change": "状态变化⽅向",
            "temporal_info": "时间信息(if any)",
            "mechanism": "机制描述(50-100词)",
            "evidence_strength": "strong/moderate/weak",
            "source_sentence": "原始句⼦"
            }}
            """
            instances = generate_text(instance_prompt)
            kg_triples.append(instances)
            conversation_history.pop()  # 清除对话历史，防止上下文干扰
    return kg_triples

def transPDF2Text(pdf_path):#将pdf转换为文本
    doc = fitz.open(pdf_path)
    fulltext = ""
    for page in range(doc.page_count):
        page= doc.load_page(page)
        fulltext += page.get_text()
    return fulltext


if __name__ == "__main__":
    pdf_path="/home/nas3/biod/dongkun/HG/test.pdf"
    fulltext=transPDF2Text(pdf_path)
    kg_triples=extract_causal_kg(fulltext)
    print(kg_triples)