import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import urllib.parse
import os

# 1. API Key Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        pass

# Initialize Session State
if "extracted_prompt" not in st.session_state:
    st.session_state["extracted_prompt"] = ""

# 2. Page Config
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

# 3. Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E0E10 !important;
        color: #ECECF1 !important;
    }
    h1, h2, h3, h4, label, p, span {
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2A2A2A !important;
    }
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
    textarea, input, section[data-testid="stFileUploadDropzone"] {
        background-color: #171717 !important;
        border: 1px solid #2A2A2A !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main Brand Header
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
    st.info("✨ AI Image & Prompt Studio")

# Main Application Layout
col1, col2 = st.columns(2)

# Step 1: Image to Prompt
with col1:
    st.markdown("### 1️⃣ Step 1: Image to Prompt")
    ref_file = st.file_uploader("ரெஃபரன்ஸ் போட்டோ அப்லோட் செய்க:", type=["jpg", "jpeg", "png"], key="ref")
    
    if ref_file:
        ref_img = Image.open(ref_file)
        st.image(ref_img, caption="Reference Image", use_container_width=True)
        
        if st.button("✨ Extract Prompt"):
            if not GEMINI_API_KEY:
                st.error("⚠️ Gemini API Key Render-ல் அமைக்கப்படவில்லை!")
            else:
                with st.spinner("AI பிராம்ட்டை உருவாக்குகிறது..."):
                    try:
                        model = genai.GenerativeModel('gemini-3.6-flash')
                        prompt_req = "Analyze this image and create a detailed photo prompt describing lighting, costume, pose, and background style."
                        res = model.generate_content([prompt_req, ref_img])
                        st.session_state["extracted_prompt"] = res.text
                        st.success("பிராம்ட் தயார்!")
                    except Exception as e:
                        st.error(f"பிராம்ட் உருவாக்க முடியவில்லை: {str(e)}")
                    
    prompt_box = st.text_area(
        "Extracted AI Prompt:", 
        value=st.session_state["extracted_prompt"], 
        height=120, 
        placeholder="பிராம்ட் இங்கு தோன்றும்..."
    )

# Step 2: AI Photo Generator
with col2:
    st.markdown("### 2️⃣ Step 2: AI Photo Generator")
    user_file = st.file_uploader("உங்கள் போட்டோவை அப்லோட் செய்க:", type=["jpg", "jpeg", "png"], key="user")
    
    if user_file:
        u_img = Image.open(user_file)
        st.image(u_img, caption="Your Image", width=200)
        
    final_prompt = st.text_area("AI Prompt (Auto-filled):", value=prompt_box, height=100)
    gen_btn = st.button("🚀 Generate My AI Photo")
    
    if gen_btn:
        if not final_prompt:
            st.warning("தயவுசெய்து பிராம்ட்டை உள்ளிடவும்!")
        else:
            with st.spinner("உங்கள் புதிய AI புகைப்படம் உருவாகிறது..."):
                try:
                    encoded = urllib.parse.quote(final_prompt + ", photorealistic 8k, sharp focus")
                    img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&seed=42&nologo=true&model=flux"
                    
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    res = requests.get(img_url, headers=headers, timeout=45)
                    
                    if res.status_code == 200:
                        out_img = Image.open(io.BytesIO(res.content))
                        st.image(out_img, caption="Generated AI Photo", use_container_width=True)
                        st.download_button("📥 Download Photo", data=res.content, file_name="Ji_Image_Studio_Photo.jpg", mime="image/jpeg")
                    else:
                        st.warning("⚠️ இமேஜ் சர்வர் பிஸியாக உள்ளது. 10 வினாடிகள் கழித்து மீண்டும் அழுத்தவும்.")
                except Exception:
                    st.warning("⚠️ AI இமேஜ் உருவாக்கத்தில் சிறிய தாமதம் ஏற்படுகிறது. 10 வினாடிகள் கழித்து மீண்டும் 'Generate' பட்டனை அழுத்தவும்.")
