import google.generativeai as genai

# Masukkan API Key baru Anda di sini
API_KEY = "AIzaSyBRmc5q7q2YrWIdM1cxyF2jZJm4hIdoJhA" 
genai.configure(api_key=API_KEY)

print("🔍 Mengecek model yang tersedia...")
for m in genai.list_models():
    # Cek model yang bisa untuk CHAT (generateContent)
    if 'generateContent' in m.supported_generation_methods:
        print(f"✅ Model CHAT tersedia: {m.name}")