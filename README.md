# Fiyat Avcısı

Bir ürün yaz, Snappy robotu el şıklatsın, ekran beyazlasın ve sonuçlar en ucuzdan en pahalıya linkleriyle gelsin.

## Kurulum

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Gerçek fiyatlar

Uygulama önce `GEMINI_API_KEY` (Google AI Studio), yoksa `SERPAPI_KEY` arar. İkisi de yoksa demo verisi gösterir. Gemini sürümünde fiyatlar yapay zekayla bulunur, mağazada kontrol edilmelidir.

- Yerelde: `.streamlit/secrets.toml` dosyasına `GEMINI_API_KEY = "anahtarın"` yaz (bu dosyayı GitHub'a yükleme).
- Streamlit Community Cloud'da: App settings > Secrets bölümüne aynı satırı ekle.
- SerpApi kullanmak istersen aynı yere `SERPAPI_KEY = "anahtarın"` yaz.

## Karakter

Şıklatan robot (Snappy) kodun içinde SVG + CSS animasyonu olarak çizili, ayrı görsel dosyası gerekmez. `app.py` içindeki `ROBOT_TEMPLATE` bölümünden renkleri ve hızı değiştirebilirsin.

## GitHub ve yayınlama

1. Dosyaları bir GitHub reposuna yükle.
2. share.streamlit.io adresinden repoyu bağla, ana dosya olarak `app.py` seç.
