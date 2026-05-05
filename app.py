"""
JESA (Jarvis Environmental System Academic) - UNKLAB
Modern Web Chatbot RAG dengan PyMuPDF & Tagging Sumber
"""

import os
import re
import json
import time
import math
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import fitz  # Menggunakan PyMuPDF pengganti pypdf

app = Flask(__name__)

# ==========================================
# 1. KONFIGURASI SISTEM
# ==========================================
PDF_PATH = "BUKU-PANDUAN-UNKLAB-2024.pdf"
CACHE_FILE = "jesa_cache_unklab.json"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K = 30 

EMBED_MODEL = "models/gemini-embedding-2"
CHAT_MODEL = "models/gemini-flash-latest" # Menggunakan 1.5 flash yang lebih pintar

WEB_URLS = [
    "https://filkom.unklab.ac.id/",
    "https://www.unklab.ac.id",
    "https://www.unklab.ac.id/fakultas-ilmu-komputer/"
]

# ==========================================
# 2. EKSTRAKSI & CHUNKING (PyMuPDF + TAGGING)
# ==========================================

def split_into_chunks_with_tag(text: str, tag: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_text = " ".join(words[start:end])
        if chunk_text.strip():
            chunks.append(f"{tag}\n{chunk_text}")
        if end >= len(words):
            break
    return chunks

def get_all_chunks() -> list[str]:
    all_chunks = []
    
    # 1. Proses PDF dengan PyMuPDF (Jauh lebih pintar membaca tabel/spasi)
    print("📄 Membaca PDF Buku Panduan dengan PyMuPDF...")
    try:
        doc = fitz.open(PDF_PATH)
        for i, page in enumerate(doc):
            text = page.get_text("text") or ""
            text = re.sub(r'\.{3,}', ' ', text).strip()
            text = re.sub(r'\n+', '\n', text)
            if len(text) > 30:
                tag = f"[Halaman {i+1}]"
                page_chunks = split_into_chunks_with_tag(text, tag)
                all_chunks.extend(page_chunks)
        doc.close()
    except Exception as e:
        print(f"❌ Error saat membaca PDF: {e}")

    # 2. Proses Website
    for url in WEB_URLS:
        print(f"🌐 Mengambil data dari web: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.extract()
                
            text = soup.get_text(separator='\n', strip=True)
            text = re.sub(r'\n+', '\n', text).strip()
            
            if len(text) > 50:
                tag = f"[Sumber Web: {url}]"
                web_chunks = split_into_chunks_with_tag(text, tag)
                all_chunks.extend(web_chunks)
        except Exception as e:
            print(f"❌ Error saat mengambil web {url}: {e}")

    return all_chunks

# ==========================================
# 3. VECTOR STORE
# ==========================================

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

class VectorStore:
    def __init__(self):
        self.chunks: list[str] = []
        self.embeddings: list[list[float]] = []

    def add(self, chunks: list[str]):
        print(f"⚙️ Membuat embedding untuk {len(chunks)} chunk...")
        for i, chunk in enumerate(chunks):
            result = genai.embed_content(
                model=EMBED_MODEL,
                content=chunk,
                task_type="retrieval_document"
            )
            self.embeddings.append(result['embedding'])
            self.chunks.append(chunk)
            print(f"  ➢ Selesai memproses chunk {i+1}/{len(chunks)}")
            time.sleep(4)

    def search(self, query: str, top_k: int = TOP_K):
        result = genai.embed_content(
            model=EMBED_MODEL,
            content=query,
            task_type="retrieval_query"
        )
        q_emb = result['embedding']
        scores = [
            (cosine_similarity(q_emb, emb), chunk)
            for emb, chunk in zip(self.embeddings, self.chunks)
        ]
        scores.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scores[:top_k]]

# ==========================================
# 4. INISIALISASI
# ==========================================

vector_store = VectorStore()
init_status = {"done": False, "error": None}

def initialize(api_key: str):
    global init_status

    if not api_key.strip():
        return "❌ API Key tidak boleh kosong."
    if not os.path.exists(PDF_PATH):
        return f"❌ File PDF tidak ditemukan: {PDF_PATH}"

    try:
        genai.configure(api_key=api_key.strip())

        if os.path.exists(CACHE_FILE):
            print("✅ Membaca data JESA dari cache lokal...")
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                vector_store.chunks = data["chunks"]
                vector_store.embeddings = data["embeddings"]

            init_status = {"done": True, "error": None}
            return f"JESA Siap! {len(vector_store.chunks)} referensi dimuat dari cache."

        print("⚠️ Memproses Knowledge Base (Buku Panduan & Website). Mohon tunggu sebentar...")
        
        chunks = get_all_chunks()

        if not chunks:
            return "❌ Gagal mengekstrak teks dari PDF maupun Web."

        vector_store.chunks = []
        vector_store.embeddings = []
        vector_store.add(chunks)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "chunks": vector_store.chunks,
                "embeddings": vector_store.embeddings
            }, f)

        init_status = {"done": True, "error": None}
        return f"Berhasil! Referensi sistem JESA telah siap dengan total {len(chunks)} chunks."

    except Exception as e:
        init_status = {"done": False, "error": str(e)}
        return f"Error Inisialisasi: {str(e)}"

# ==========================================
# 5. RAG CHAT LOGIC
# ==========================================

SYSTEM_PROMPT = """Kamu adalah JESA (Jarvis Environmental System Academic), asisten akademik Universitas Klabat (UNKLAB).

Kamu secara resmi telah diberikan dua sumber pengetahuan utama di dalam ingatanmu:
1. BUKU PANDUAN UNKLAB 2024 (berisi peraturan akademik, kurikulum, fakultas, syarat kelulusan, dll).
2. Informasi dari Website Resmi UNKLAB.

ATURAN MENJAWAB:
- Jawablah secara akurat HANYA berdasarkan konteks yang diberikan di bawah ini.
- Jika pengguna bertanya "Apakah kamu tahu/memiliki buku panduan?", jawablah dengan yakin bahwa KAMU MEMILIKINYA.
- Berikan jawaban yang jelas dan natural tanpa menyebutkan halaman PDF atau sumber web secara eksplisit.
- Jika tidak ada di konteks, katakan bahwa kamu belum memiliki informasi tersebut.
"""

def clean_response_text(text: str) -> str:
    text = re.sub(r'\s*\[Halaman\s*\d+\]', '', text)
    text = re.sub(r'\s*\[Sumber Web:[^\]]+\]', '', text)
    text = re.sub(r'\s*\[Sumber Web\]', '', text)
    return text.strip()


def chat_response(message: str, use_pdf_only: bool = False):
    if not init_status["done"]:
        return {"error": "Sistem JESA belum diinisialisasi."}, None

    max_retries = 3
    for attempt in range(max_retries):
        try:
            relevant_chunks = vector_store.search(message)
            
            # --- MULAI KODE DEBUGGING ---
            print(f"\n[DEBUG] User bertanya: '{message}'")
            print("🔍 5 POTONGAN TEKS TERATAS YANG DITEMUKAN SISTEM:")
            for i, chunk in enumerate(relevant_chunks[:5]): # Tampilkan 5 teratas saja
                print(f"[{i+1}] {chunk[:150]}...") # Print 150 huruf pertama
            print("=============================================\n")
            # --- AKHIR KODE DEBUGGING ---

            context = "\n\n---\n\n".join(relevant_chunks)
            full_prompt = f"{SYSTEM_PROMPT}\n\nKONTEKS:\n{context}\n\nPertanyaan: {message}\nJawaban:"

            model = genai.GenerativeModel(CHAT_MODEL)
            response = model.generate_content(full_prompt)
            cleaned_response = clean_response_text(response.text)

            return {"response": cleaned_response, "sources": ""}, None
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                time.sleep(30)
            else:
                return {"error": str(e)}, None

# ==========================================
# 6. FLASK ROUTES
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    result, error = chat_response(message)
    if error:
        return jsonify(result), 500

    return jsonify(result)

@app.route('/initialize', methods=['POST'])
def initialize_route():
    data = request.get_json()
    api_key = data.get('api_key', '')

    status = initialize(api_key)
    return jsonify({"status": status, "initialized": init_status["done"]})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)