# 🤖 AI UNKLAB Assistant

A modern AI chatbot web interface for university assistance, focused on answering questions from PDF documents and official website data.

---

## ✨ Features

- **Modern UI**: Clean, professional interface similar to ChatGPT/Notion AI
- **RAG Technology**: Retrieval-Augmented Generation using Google Gemini
- **Multi-source Knowledge**: PDF documents + website data
- **Real-time Chat**: Smooth animations and typing indicators
- **Sources Display**: Clickable sources under each AI response
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Works on desktop and mobile devices

---

## 📁 Project Structure

```
expert-system/
├── app.py                        ← Flask backend application
├── requirements.txt              ← Python dependencies
├── README.md                     ← This file
├── templates/
│   └── index.html               ← Main web interface
├── static/
│   ├── styles.css               ← Modern CSS styling
│   └── script.js                ← Frontend JavaScript
├── BUKU-PANDUAN-UNKLAB-2024.pdf  ← University guide PDF
└── jesa_cache_unklab.json        ← Cached embeddings
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Google Gemini API Key

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Place PDF File
Ensure `BUKU-PANDUAN-UNKLAB-2024.pdf` is in the root directory.

### 4. Get API Key
1. Visit https://aistudio.google.com/app/apikey
2. Create a new API key
3. Copy the key

### 5. Run the Application
```bash
python app.py
```

### 6. Open Browser
Navigate to: **http://localhost:5000**

---

## 🎨 UI Features

### Layout
- **Left Sidebar**: Navigation, logo, loaded data sources
- **Main Chat Area**: Chat bubbles with smooth animations
- **Top Bar**: Title and status indicator
- **Input Area**: Rounded input with send button

### Advanced Features
- **Sources Modal**: View detailed sources for each response
- **PDF Toggle**: Switch between PDF-only or all knowledge
- **Typing Indicator**: Shows when AI is processing
- **Chat History**: Access previous conversations
- **Settings Panel**: Dark mode and other preferences

### Design Highlights
- Clean, minimal aesthetic
- Soft shadows and rounded corners (16px+ border-radius)
- Modern color palette (white, light gray, blue/green accents)
- Inter/Poppins typography
- Smooth 0.2-0.3s transitions
- Hover effects and micro-interactions

---

## 🔧 API Endpoints

- `GET /` - Main web interface
- `POST /chat` - Send chat message
- `POST /initialize` - Initialize with API key

---

## 🛠️ Development

### Adding New Features
1. Backend logic in `app.py`
2. Frontend updates in `templates/index.html`
3. Styling in `static/styles.css`
4. Interactions in `static/script.js`

### Customization
- Modify color variables in `styles.css`
- Update layout in `index.html`
- Add new routes in `app.py`

---

## 📝 Notes

- First initialization takes several minutes to process the PDF
- Embeddings are cached for faster subsequent runs
- Supports both PDF documents and website data
- Mobile-responsive design

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 🧠 Cara Kerja (RAG)

```
PDF ──► Ekstraksi Teks ──► Chunking ──► Embedding (Gemini)
                                              │
Pertanyaan ──► Embedding ──► Cosine Similarity Search
                                              │
                              Top-5 Chunk Relevan
                                              │
                         Gemini 1.5 Flash ──► Jawaban
```

1. **Ekstraksi**: Teks dari 351 halaman PDF diekstrak
2. **Chunking**: Dipecah menjadi potongan ~600 kata dengan overlap 80 kata
3. **Embedding**: Setiap chunk diubah menjadi vektor menggunakan `text-embedding-004`
4. **Retrieval**: Saat ada pertanyaan, 5 chunk paling relevan diambil via cosine similarity
5. **Generation**: Gemini 1.5 Flash menjawab berdasarkan konteks yang ditemukan

---

## ⚙️ Konfigurasi (opsional)

Edit bagian ini di `app.py` untuk menyesuaikan:

```python
CHUNK_SIZE    = 600   # kata per chunk (lebih besar = konteks lebih panjang)
CHUNK_OVERLAP = 80    # overlap antar chunk (cegah potongan informasi)
TOP_K         = 30     # jumlah chunk yang diambil per pertanyaan
```

---

## 📝 Catatan

- Jawaban hanya berdasarkan isi Buku Panduan UNKLAB 2024
- Tidak memerlukan internet setelah inisialisasi (kecuali Gemini API)
- Riwayat chat tidak disimpan permanen
- Untuk informasi terkini, hubungi bagian akademik UNKLAB
