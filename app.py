import hashlib
import json
import os
import random
import re
import time
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Fiyat Avcısı", page_icon="🫰", layout="wide")

ROBOT_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:transparent;overflow:hidden;display:flex;justify-content:center}
svg{width:100%;max-width:320px;height:auto}
#robot{animation:floaty 3s ease-in-out infinite}
.fa{transform-box:fill-box;transform-origin:50% 100%;animation:snapA __DUR__ ease-in-out __ITER__ forwards}
.fb{transform-box:fill-box;transform-origin:50% 100%;animation:snapB __DUR__ ease-in-out __ITER__ forwards}
.burst{transform-box:fill-box;transform-origin:center;opacity:0;animation:burst __DUR__ ease-out __ITER__ forwards}
.pop{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop __DUR__ ease-out __ITER__ forwards}
.eye{transform-box:fill-box;transform-origin:center;animation:blink 3s infinite}
.ball{animation:glow 1s ease-in-out infinite alternate}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes snapA{0%,38%{transform:rotate(-22deg)}44%,60%{transform:rotate(6deg)}75%,100%{transform:rotate(-22deg)}}
@keyframes snapB{0%,38%{transform:rotate(22deg)}44%,60%{transform:rotate(-6deg)}75%,100%{transform:rotate(22deg)}}
@keyframes burst{0%,42%{transform:scale(0);opacity:0}48%{opacity:1}100%{transform:scale(2.4);opacity:0}}
@keyframes pop{0%,44%{opacity:0;transform:scale(.5)}52%{opacity:1;transform:scale(1.2)}80%,100%{opacity:0;transform:scale(1)}}
@keyframes blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}
@keyframes glow{from{opacity:.6}to{opacity:1}}
</style></head><body>
<svg viewBox="0 0 340 290" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="150" cy="276" rx="42" ry="6" fill="rgba(0,0,0,.28)"/>
<g id="robot">
  <line x1="150" y1="40" x2="150" y2="62" stroke="#94a3b8" stroke-width="4"/>
  <circle class="ball" cx="150" cy="34" r="8" fill="#fb923c"/>
  <rect x="122" y="238" width="22" height="30" rx="8" fill="#0f766e"/>
  <rect x="156" y="238" width="22" height="30" rx="8" fill="#0f766e"/>
  <rect x="110" y="148" width="80" height="94" rx="20" fill="#5eead4" stroke="#0f766e" stroke-width="4"/>
  <circle cx="150" cy="192" r="14" fill="#fb923c" stroke="#c2410c" stroke-width="3"/>
  <rect x="84" y="158" width="22" height="60" rx="11" fill="#2dd4bf" stroke="#0f766e" stroke-width="3"/>
  <circle cx="95" cy="226" r="12" fill="#5eead4" stroke="#0f766e" stroke-width="3"/>
  <rect x="100" y="62" width="100" height="80" rx="22" fill="#2dd4bf" stroke="#0f766e" stroke-width="4"/>
  <g class="eye"><circle cx="128" cy="96" r="13" fill="#fff"/><circle cx="130" cy="98" r="6" fill="#0f172a"/></g>
  <g class="eye"><circle cx="172" cy="96" r="13" fill="#fff"/><circle cx="174" cy="98" r="6" fill="#0f172a"/></g>
  <path d="M132 122 Q150 134 168 122" stroke="#0f172a" stroke-width="4" fill="none" stroke-linecap="round"/>
  <line x1="188" y1="170" x2="234" y2="112" stroke="#0f766e" stroke-width="26" stroke-linecap="round"/>
  <line x1="188" y1="170" x2="234" y2="112" stroke="#2dd4bf" stroke-width="18" stroke-linecap="round"/>
  <g transform="translate(238 100)">
    <rect class="fa" x="-11" y="-36" width="9" height="28" rx="4.5" fill="#5eead4" stroke="#0f766e" stroke-width="2.5"/>
    <rect class="fb" x="2" y="-36" width="9" height="28" rx="4.5" fill="#5eead4" stroke="#0f766e" stroke-width="2.5"/>
    <circle r="15" fill="#5eead4" stroke="#0f766e" stroke-width="3"/>
  </g>
  <g transform="translate(238 62)">
    <g class="burst" stroke="#fbbf24" stroke-width="4" stroke-linecap="round">
      <line x1="0" y1="-10" x2="0" y2="-24"/>
      <line x1="0" y1="-10" x2="0" y2="-24" transform="rotate(45)"/>
      <line x1="0" y1="-10" x2="0" y2="-24" transform="rotate(90)"/>
      <line x1="0" y1="-10" x2="0" y2="-24" transform="rotate(135)"/>
      <line x1="0" y1="-10" x2="0" y2="-24" transform="rotate(180)"/>
      <line x1="0" y1="-10" x2="0" y2="-24" transform="rotate(225)"/>
      <line x1="0" y1="-10" x2="0" y2="-24" transform="rotate(270)"/>
      <line x1="0" y1="-10" x2="0" y2="-24" transform="rotate(315)"/>
    </g>
  </g>
  <text class="pop" x="252" y="38" font-family="Arial Black,Arial,sans-serif" font-size="20" font-weight="900" fill="#fbbf24">SNAP!</text>
</g>
</svg></body></html>"""


def render_robot(loop: bool = False, height: int = 300):
    """Orijinal robot karakter (Snappy): el şıklatır, kıvılcım çıkar."""
    html = ROBOT_TEMPLATE.replace("__DUR__", "3s" if loop else "2.5s").replace(
        "__ITER__", "infinite" if loop else "1"
    )
    components.html(html, height=height)
SNAP_SECONDS = 2.5
FADE_SECONDS = 3.0

DARK_CSS = """
<style>
.stApp {background: radial-gradient(circle at 50% 0%, #3b1d6e 0%, #140a2b 60%, #07030f 100%);}
h1, h2, h3, p, label, span, div {color: #f3e8ff;}
.title {text-align:center; font-size:3rem; font-weight:800;
        background: linear-gradient(90deg,#f5c542,#ff7ae0,#7a5cff);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.sub {text-align:center; opacity:.8; margin-bottom:1.5rem;}
.snap-text {text-align:center; font-size:1.4rem; letter-spacing:.2em;
            animation: pulse 1s infinite alternate;}
@keyframes pulse {from{opacity:.4} to{opacity:1}}
</style>
"""

LIGHT_CSS = """
<style>
.stApp {background: #ffffff;}
h1, h2, h3, p, label, span, div {color: #1f2937;}
.title {text-align:center; font-size:2.6rem; font-weight:800;
        background: linear-gradient(90deg,#7a5cff,#ff7ae0);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.sub {text-align:center; color:#6b7280; margin-bottom:1rem;}
.card {border:1px solid #e5e7eb; border-radius:14px; padding:14px; margin-bottom:12px;
       box-shadow:0 2px 8px rgba(0,0,0,.05); background:#fff;}
.price {font-size:1.5rem; font-weight:800; color:#16a34a;}
.badge {background:#16a34a; color:#fff !important; padding:2px 10px; border-radius:999px;
        font-size:.75rem; font-weight:700;}
.badge-hot {background:#dc2626;}
.store {color:#6b7280; font-size:.85rem;}
</style>
"""

FADE_HTML = f"""
<style>
.white-fade {{position:fixed; inset:0; background:#fff; z-index:99999; opacity:0;
             pointer-events:none; animation: fadeToWhite {FADE_SECONDS}s ease-in forwards;}}
@keyframes fadeToWhite {{from{{opacity:0}} to{{opacity:1}}}}
</style>
<div class="white-fade"></div>
"""

STORES = [
    ("Trendyol", "https://www.trendyol.com/sr?q={q}"),
    ("Hepsiburada", "https://www.hepsiburada.com/ara?q={q}"),
    ("n11", "https://www.n11.com/arama?q={q}"),
    ("Amazon TR", "https://www.amazon.com.tr/s?k={q}"),
    ("Teknosa", "https://www.teknosa.com/arama/?s={q}"),
    ("Vatan Bilgisayar", "https://www.vatanbilgisayar.com/arama/{q}/"),
    ("MediaMarkt", "https://www.mediamarkt.com.tr/tr/search.html?query={q}"),
]


def get_secret(name: str):
    try:
        return st.secrets.get(name) or os.getenv(name)
    except Exception:
        return os.getenv(name)


@st.cache_data(ttl=3600, show_spinner=False)
def search_real(query: str, api_key: str):
    r = requests.get(
        "https://serpapi.com/search.json",
        params={"engine": "google_shopping", "q": query, "gl": "tr", "hl": "tr", "api_key": api_key},
        timeout=20,
    )
    r.raise_for_status()
    rows = []
    for it in r.json().get("shopping_results", []):
        price = it.get("extracted_price")
        link = it.get("product_link") or it.get("link")
        if price is None or not link:
            continue
        rows.append(
            {
                "Ürün": it.get("title", "-"),
                "Mağaza": it.get("source", "-"),
                "Fiyat": float(price),
                "Puan": it.get("rating"),
                "Teslimat": it.get("delivery", ""),
                "Görsel": it.get("thumbnail"),
                "Link": link,
            }
        )
    return rows


def parse_price(value):
    if isinstance(value, (int, float)):
        return float(value)
    s = re.sub(r"[^\d.,]", "", str(value))
    if not s:
        raise ValueError("fiyat yok")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[1]) == 3):
        s = s.replace(".", "")
    return float(s)


@st.cache_data(ttl=3600, show_spinner=False)
def search_gemini(query: str, api_key: str):
    """Gemini + Google Arama ile Türkiye'deki mağazalardan fiyat bulur."""
    prompt = (
        f"Türkiye'deki online mağazalarda '{query}' için şu an satılan farklı ürün ve fiyatları Google'da ara. "
        "En az 8 sonuç bul. Sadece geçerli bir JSON dizisi döndür, başka hiçbir açıklama yazma. "
        'Her eleman şu alanlara sahip olsun: {"urun": "ürün adı", "magaza": "mağaza adı", '
        '"fiyat": TL cinsinden sayı, "link": "ürün sayfasının tam https adresi", '
        '"puan": 5 üzerinden sayı ya da null, "teslimat": "kısa not ya da boş"}. '
        "Fiyatı bulamadığın ürünü ekleme, uydurma."
    )
    custom = get_secret("GEMINI_MODEL")
    models = ([custom] if custom else []) + ["gemini-flash-latest", "gemini-3-flash-preview", "gemini-2.5-flash"]
    r = None
    for model in models:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]},
            timeout=90,
        )
        if r.status_code != 404:  # 404 = bu model adı hesabında yok, sıradakini dene
            break
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts)
    data = json.loads(text[text.find("[") : text.rfind("]") + 1])

    rows = []
    for it in data:
        try:
            price = parse_price(it.get("fiyat"))
        except Exception:
            continue
        store = str(it.get("magaza") or "-")
        link = str(it.get("link") or "")
        if not link.startswith("http"):
            link = next(
                (u.format(q=quote_plus(query)) for n, u in STORES if n.lower() in store.lower()),
                f"https://www.google.com/search?tbm=shop&q={quote_plus(query)}",
            )
        rating = it.get("puan")
        rows.append(
            {
                "Ürün": str(it.get("urun") or query),
                "Mağaza": store,
                "Fiyat": price,
                "Puan": float(rating) if isinstance(rating, (int, float)) else None,
                "Teslimat": str(it.get("teslimat") or ""),
                "Görsel": None,
                "Link": link,
            }
        )
    return rows


def search_demo(query: str):
    """API anahtarı yokken sahte (demo) veri üretir."""
    rnd = random.Random(int(hashlib.md5(query.lower().encode()).hexdigest(), 16))
    base = rnd.randint(300, 5000)
    rows = []
    for name, url in STORES:
        rows.append(
            {
                "Ürün": f"{query.title()} - {rnd.choice(['Siyah', 'Beyaz', 'Mavi', 'Gri'])}",
                "Mağaza": name,
                "Fiyat": round(base * rnd.uniform(0.8, 1.35), 2),
                "Puan": round(rnd.uniform(3.6, 4.9), 1),
                "Teslimat": rnd.choice(["Ücretsiz kargo", "Yarın kargoda", "2-3 günde teslim", ""]),
                "Görsel": None,
                "Link": url.format(q=quote_plus(query)),
            }
        )
    return rows


def snap_animation(query: str):
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    stage = st.empty()
    with stage.container():
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            render_robot(loop=False, height=300)
        st.markdown(f"<p class='snap-text'>\"{query}\" aranıyor... Fiyatlar toplanıyor.</p>", unsafe_allow_html=True)
    time.sleep(SNAP_SECONDS)
    stage.markdown(FADE_HTML, unsafe_allow_html=True)
    time.sleep(FADE_SECONDS + 0.2)
    stage.empty()


def render_results(query: str, rows: list, demo: bool):
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)
    st.markdown("<div class='title'>Fiyat Avcısı</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>\"{query}\" için en ucuzdan en pahalıya</div>", unsafe_allow_html=True)

    if demo == "demo":
        st.warning("Demo modu: gösterilen fiyatlar örnektir. Gerçek fiyatlar için GEMINI_API_KEY ekle.")
    elif demo == "gemini":
        st.info("Fiyatlar yapay zeka ile bulundu. Satın almadan önce mağazadaki fiyatı kontrol et.")
    if not rows:
        st.info("Sonuç bulunamadı. Başka bir kelime dene.")
        return

    df = pd.DataFrame(rows).sort_values("Fiyat").reset_index(drop=True)

    with st.sidebar:
        st.header("Filtreler")
        lo, hi = float(df["Fiyat"].min()), float(df["Fiyat"].max())
        if lo < hi:
            rng = st.slider("Fiyat aralığı (₺)", lo, hi, (lo, hi))
            df = df[df["Fiyat"].between(*rng)]
        min_rating = st.slider("Minimum puan", 0.0, 5.0, 0.0, 0.1)
        if min_rating > 0:
            df = df[df["Puan"].fillna(0) >= min_rating]
        stores = st.multiselect("Mağaza", sorted(df["Mağaza"].unique()))
        if stores:
            df = df[df["Mağaza"].isin(stores)]

    if df.empty:
        st.info("Filtrelere uyan sonuç yok.")
        return

    cheapest, priciest = df["Fiyat"].min(), df["Fiyat"].max()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("En ucuz", f"{cheapest:,.0f} ₺")
    m2.metric("Ortalama", f"{df['Fiyat'].mean():,.0f} ₺")
    m3.metric("En pahalı", f"{priciest:,.0f} ₺")
    m4.metric("Sonuç sayısı", len(df))
    if cheapest > 0:
        st.success(f"En ucuzla en pahalı arasında {priciest - cheapest:,.0f} ₺ fark var (%{(priciest / cheapest - 1) * 100:.0f}).")

    if len(df) > 1:
        st.bar_chart(df.set_index(df["Mağaza"] + " #" + (df.index + 1).astype(str))["Fiyat"])

    st.subheader("Sıralama")
    for i, row in df.reset_index(drop=True).iterrows():
        left, mid, right = st.columns([1, 5, 2])
        with left:
            if row["Görsel"]:
                st.image(row["Görsel"], width=80)
            else:
                st.markdown("<div style='font-size:3rem'>📦</div>", unsafe_allow_html=True)
        with mid:
            badge = ""
            if i == 0:
                badge = "<span class='badge'>EN UCUZ</span> "
            elif i == len(df) - 1 and len(df) > 2:
                badge = "<span class='badge badge-hot'>EN PAHALI</span> "
            extra = f"⭐ {row['Puan']}  " if pd.notna(row["Puan"]) else ""
            st.markdown(
                f"<div class='card'>{badge}<b>{i + 1}. {row['Ürün']}</b><br>"
                f"<span class='store'>{row['Mağaza']} · {extra}{row['Teslimat']}</span></div>",
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(f"<div class='price'>{row['Fiyat']:,.2f} ₺</div>", unsafe_allow_html=True)
            st.link_button("Mağazaya git", row["Link"], use_container_width=True)

    st.download_button(
        "Sonuçları CSV indir",
        df.drop(columns=["Görsel"]).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{query}_fiyatlar.csv",
        mime="text/csv",
    )


def main():
    if "results" not in st.session_state:
        st.session_state.results = None

    if st.session_state.results is None:
        st.markdown(DARK_CSS, unsafe_allow_html=True)
        st.markdown("<div class='title'>Fiyat Avcısı</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>Ne aradığını yaz, gerisini Snappy halletsin.</div>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 3, 1])
        with mid:
            render_robot(loop=True, height=300)
            with st.form("arama"):
                q = st.text_input("Ne arıyorsun?", placeholder="kulaklık, powerbank, klavye...")
                go = st.form_submit_button("Ara", use_container_width=True)
        if go and q.strip():
            q = q.strip()
            snap_animation(q)
            gem_key = get_secret("GEMINI_API_KEY")
            serp_key = get_secret("SERPAPI_KEY")
            try:
                if gem_key:
                    rows, demo = search_gemini(q, gem_key), "gemini"
                elif serp_key:
                    rows, demo = search_real(q, serp_key), "serpapi"
                else:
                    rows, demo = search_demo(q), "demo"
            except Exception as e:
                st.error(f"Arama hatası: {e}")
                return
            st.session_state.results = (q, rows, demo)
            st.rerun()
    else:
        q, rows, demo = st.session_state.results
        render_results(q, rows, demo)
        if st.button("Yeni arama"):
            st.session_state.results = None
            st.rerun()


main()
