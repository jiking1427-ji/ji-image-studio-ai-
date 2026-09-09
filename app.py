import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import urllib.parse

# 1. Page Config with Logo Favicon
try:
    logo_img = Image.open("logo.png")
    st.set_page_config(
        page_title="Ji Image Studio AI",
        page_icon=logo_img,
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    st.set_page_config(
        page_title="Ji Image Studio AI",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# 2. SEO Meta Tags & ChatGPT Dark Theme CSS
st.markdown("""
    <head>
        <meta property="og:site_name" content="Ji Image Studio AI">
        <meta name="description" content="Ji Image Studio AI - Convert Images to AI Prompts and generate custom AI photos seamlessly.">
        <link rel="icon" type="image/png" href="logo.png">
        <script type="application/ld+json">
        {
          "@context" : "https://schema.org",
          "@type" : "WebSite",
          "name" : "Ji Image Studio AI",
          "url" : "https://ji-image-studio-ai.onrender.com/"
        }
        </script>
    </head>
    
    <style>
    /* Dark Theme Setup */
    .stApp {
        background-color: #0E0E10 !important;
        color: #ECECF1 !important;
    }
    
    /* Typography */
    h1, h2, h3, h4, label, p, span {
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2A2A2A !important;
    }
    
    /* Buttons Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Text Inputs & Dropzone */
    textarea, input, section[data-testid="stFileUploadDropzone"] {
        background-color: #171717 !important;
        border: 1px solid #2A2A2A !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    /* Mobile Responsiveness */
    @media only screen and (max-width: 768px) {
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 20px;
        }
        .stButton > button {
            padding: 14px !important;
            font-size: 16px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Main Brand Header with Logo Display
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    try:
        st.image("logo.png", width=120)
    except Exception:
        pass
    st.markdown("<h1 style='text-align: center; color: #3B82F6; margin-top: -10px;'>Ji Image Studio AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF;'>உங்களுக்குப் பிடித்த புகைப்படத்தின் பிராம்ட்டை எடுத்து, அதே ஸ்டைலில் புதிய படத்தை உருவாக்குங்கள்.</p>", unsafe_allow_html=True)

st.divider()

# Sidebar Setup
with st.sidebar:
    try:
        st.image("logo.png", width=80)
    except Exception:
        pass
    st.title("Ji Image Studio AI")
    st.write("---")
    api_key = st.text_input("Gemini API Key உள்ளிடவும்:", type="password")
    st.caption("உங்கள் API தகவல்கள் பாதுகாப்பாகப் பராமரிக்கப்படும்.")

if api_key:
    genai.configure(api_key=api_key)

# Main Application Layout
col1, col2 = st.columns(2)

# Step 1: Image to Prompt
with col1:
    st.markdown("### 1️⃣ Step 1: Image to Prompt")
    ref_file = st.file_uploader("ரெஃபரன்ஸ் போட்டோ அப்லோட் செய்க:", type=["jpg", "jpeg", "png"], key="ref")
    
    extracted_prompt = ""
    if ref_file:
        ref_img = Image.open(ref_file)
        st.image(ref_img, caption="Reference Image", use_container_width=True)
        
        if st.button("✨ Extract Prompt") and api_key:
            with st.spinner("AI பிராம்ட்டை உருவாக்குகிறது..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt_req = "Analyze this image and create a detailed photo prompt describing lighting, costume, pose, and background style."
                    res = model.generate_content([prompt_req, ref_img])
                    extracted_prompt = res.text
                    st.success("பிராம்ட் தயார்!")
                except Exception:
                    st.error("பிழை ஏற்பட்டது. API Key-ஐ சரிபார்க்கவும்.")
                    
    prompt_box = st.text_area("Extracted AI Prompt:", value=extracted_prompt, height=120, placeholder="பிராம்ட் இங்கு தோன்றும்...")

# Step 2: AI Photo Generator
with col2:
    st.markdown("### 2️⃣ Step 2: AI Photo Generator")
    user_file = st.file_uploader("உங்கள் போட்டோவை அப்லோட் செய்க:", type=["jpg", "jpeg", "png"], key="user")
    
    if user_file:
        u_img = Image.open(user_file)
        st.image(u_img, caption="Your Image", width=200)
        
    final_prompt = st.text_area("AI Prompt (Auto-filled):", value=prompt_box, height=100)
    gen_btn = st.button("🚀 Generate My AI Photo")
    
    if gen_btn and final_prompt:
        with st.spinner("உங்கள் புதிய AI புகைப்படம் உருவாகிறது..."):
            try:
                encoded = urllib.parse.quote(final_prompt + ", photorealistic 8k, face accuracy")
                img_url = f"https://pollinations.ai/p/{encoded}?width=1024&height=1024&seed=42"
                res = requests.get(img_url)
                if res.status_code == 200:
                    out_img = Image.open(io.BytesIO(res.content))
                    st.image(out_img, caption="Generated AI Photo", use_container_width=True)
                    st.download_button("📥 Download Photo", data=res.content, file_name="Ji_Image_Studio_Photo.jpg", mime="image/jpeg")
                else:
                    st.error("இமேஜ் உருவாக்க முடியவில்லை.")
            except Exception:
                st.error("தொழில்நுட்பப் பிழை ஏற்பட்டது.")
