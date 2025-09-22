import faiss
import pickle
import numpy as np
from transformers import TextIteratorStreamer, GenerationConfig
from threading import Thread
import consts
import settings

def load_embedding_and_chunks():
    """
    Load FAISS index và chunks từ file đã lưu
    """
    try:
        # Load FAISS index
        if settings.FAISS_PATH.exists():
            faiss_index = faiss.read_index(str(settings.FAISS_PATH))
        else:
            print(f"⚠️  File FAISS không tồn tại: {settings.FAISS_PATH}")
            return None, []
        
        # Load chunks
        if settings.PICKLE_PATH.exists():
            with open(settings.PICKLE_PATH, "rb") as f:
                data = pickle.load(f)
            all_chunks = []
            for item in data:
                if isinstance(item, dict) and "chunks" in item:
                    all_chunks.extend(item["chunks"])
                elif isinstance(item, list):
                    all_chunks.extend(item)
            
            return faiss_index, all_chunks
        else:
            print(f"⚠️  File pickle không tồn tại: {settings.PICKLE_PATH}")
            return faiss_index, []
            
    except Exception as e:
        print(f"❌ Lỗi khi load embedding và chunks: {e}")
        return None, []

def get_relevant_chunks(
    query,
    faiss_index,
    chunks,
    top_k=3,
    max_tokens_per_chunk=5120,
):
    """
    Tìm các đoạn văn bản liên quan nhất với câu hỏi
    """
    try:
        if consts.embedding_model is None:
            print("❌ Embedding model chưa được load")
            return []
            
        query_vector = consts.embedding_model.encode([query])
        D, I = faiss_index.search(np.array(query_vector).astype("float32"), top_k)

        context_chunks = []
        for i in I[0]:
            if i < len(chunks):
                chunk = chunks[i]
                tokens = consts.llm_tokenizer.tokenize(chunk)
                if len(tokens) > max_tokens_per_chunk:
                    tokens = tokens[:max_tokens_per_chunk]
                    chunk = consts.llm_tokenizer.convert_tokens_to_string(tokens)
                context_chunks.append(chunk.strip())

        return context_chunks
    except Exception as e:
        print(f"❌ Lỗi khi tìm chunks liên quan: {e}")
        return []

def build_prompt(context_chunks, question):
    """
    Tạo prompt cho mô hình với context và câu hỏi
    """
    context = "\n---\n".join(context_chunks)
    return f"""<|im_start|>system
Bạn là một trợ lý AI chuyên về an toàn thông tin tại Việt Nam. Chỉ trả lời người dùng dựa trên thông tin được cung cấp dưới đây về luật pháp, quy định và tiêu chuẩn an toàn thông tin Việt Nam. Nếu không có thông tin phù hợp, hãy trả lời: "Tôi không có thông tin về câu hỏi này trong cơ sở dữ liệu hiện tại." Không được bịa đặt thông tin.
<|im_end|>
<|im_start|>user
Thông tin tham khảo:
{context}

Câu hỏi: {question}
<|im_end|>
<|im_start|>assistant
"""

def configure_generation(max_tokens=256, temperature=0.7, top_k=50, top_p=0.95):
    """
    Cấu hình generation cho mô hình
    """
    generation_config = GenerationConfig(
        max_new_tokens=max_tokens,
        do_sample=True,
        num_return_sequences=1,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        pad_token_id=consts.llm_tokenizer.eos_token_id,
    )
    return generation_config

def generate_answer(prompt, max_tokens=256, temperature=0.7, top_k=50, top_p=0.95):
    """
    Sinh câu trả lời từ mô hình
    """
    try:
        if consts.llm_model is None or consts.llm_tokenizer is None:
            return "❌ LLM model chưa được load"
            
        # Tokenize và đưa lên thiết bị
        encoding = consts.llm_tokenizer(prompt, return_tensors="pt")
        input_ids = encoding["input_ids"].to(consts.llm_model.device)
        attention_mask = encoding["attention_mask"].to(consts.llm_model.device)

        # Sinh văn bản
        outputs = consts.llm_model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            generation_config=configure_generation(max_tokens, temperature, top_k, top_p),
        )

        # Lấy phần model vừa sinh (bỏ phần input gốc)
        generated_only_ids = outputs[0][input_ids.shape[1]:]
        return consts.llm_tokenizer.decode(generated_only_ids, skip_special_tokens=True)
        
    except Exception as e:
        print(f"❌ Lỗi khi sinh câu trả lời: {e}")
        return "❌ Đã xảy ra lỗi trong quá trình sinh câu trả lời."

def get_response(query: str, max_tokens=256, temperature=0.7, top_k=50, top_p=0.95):
    """
    Trả về câu trả lời cho câu hỏi
    """
    faiss_index, chunks = load_embedding_and_chunks()

    try:
        if faiss_index is None or len(chunks) == 0:
            return "❌ Không thể tải cơ sở dữ liệu. Vui lòng kiểm tra lại cấu hình."
        
        # Lấy các đoạn văn bản liên quan
        context_chunks = get_relevant_chunks(query, faiss_index, chunks)
        
        if not context_chunks:
            return "❌ Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."

        # Tạo prompt
        prompt = build_prompt(context_chunks, query)

        # Sinh câu trả lời
        full_output = generate_answer(prompt, max_tokens, temperature, top_k, top_p)

        return full_output.strip()

    except Exception as e:
        print(f"❌ Lỗi trong quá trình xử lý: {e}")
        return "❌ Đã xảy ra lỗi trong quá trình xử lý câu hỏi. Vui lòng thử lại sau."

def generate_answer_stream(prompt, max_tokens=256, temperature=0.7, top_k=50, top_p=0.95):
    """
    Sinh câu trả lời dưới dạng stream
    """
    try:
        if consts.llm_model is None or consts.llm_tokenizer is None:
            yield "❌ LLM model chưa được load"
            return
            
        # Tokenize và đưa lên GPU/CPU
        encoding = consts.llm_tokenizer(prompt, return_tensors="pt").to(consts.llm_model.device)

        # Tạo streamer để lấy token sinh ra
        streamer = TextIteratorStreamer(
            consts.llm_tokenizer,
            timeout=30,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        # Chạy sinh văn bản trong thread phụ
        generation_kwargs = {
            "input_ids": encoding.input_ids,
            "attention_mask": encoding.attention_mask,
            "generation_config": configure_generation(max_tokens, temperature, top_k, top_p),
            "streamer": streamer,
        }
        thread = Thread(target=consts.llm_model.generate, kwargs=generation_kwargs)
        thread.start()

        # Yield từng token với error handling
        try:
            for token in streamer:
                if token:  # Chỉ yield token không rỗng
                    yield token
        except Exception as e:
            yield f" [Lỗi streaming: {str(e)}]"
        finally:
            thread.join()  # Đảm bảo thread được join
            
    except Exception as e:
        print(f"❌ Lỗi trong generate_answer_stream: {e}")
        yield f"❌ Lỗi streaming: {str(e)}"

def get_response_stream(query: str, max_tokens=256, temperature=0.7, top_k=50, top_p=0.95):
    """
    Trả về câu trả lời dưới dạng stream
    """
    # Load dữ liệu
    faiss_index, chunks = load_embedding_and_chunks()

    try:
        if faiss_index is None or len(chunks) == 0:
            yield "❌ Không thể tải cơ sở dữ liệu. Vui lòng kiểm tra lại cấu hình."
            return
        
        # Lấy các đoạn ngữ cảnh liên quan
        context_chunks = get_relevant_chunks(query, faiss_index, chunks)
        
        if not context_chunks:
            yield "❌ Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
            return

        # Tạo prompt hội thoại đầy đủ
        prompt = build_prompt(context_chunks, query)

        # Trả về generator từ mô hình
        yield from generate_answer_stream(prompt, max_tokens, temperature, top_k, top_p)

    except Exception as e:
        print(f"❌ Lỗi trong get_response_stream: {e}")
        yield "❌ Lỗi xử lý câu hỏi."
