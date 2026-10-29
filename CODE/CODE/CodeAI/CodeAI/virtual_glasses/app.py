import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import os, math, random, base64, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# 1. PAGE CONFIG & GLOBAL STYLES
# ============================================================
st.set_page_config(page_title="LensAI – Virtual Try-On", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box}
html,body{overflow-x:hidden}
:root{
  --blue:#00b8fc;
  --blue2:#009fd9;
  --blue-light:#e8f8ff;
  --blue-soft:#b8e8fc;
  --bg:#f4f7fa;
  --white:#ffffff;
  --ink:#0d1b2a;
  --muted:#6b7a8d;
  --border:#dde4ec;
  --r:18px;
  --pink:#ff4d7e;
  --green:#00c48c;
  --gold:#f5a623;
}
.stApp{background:var(--bg);font-family:'Inter',sans-serif;color:var(--ink)}
h1,h2,h3,h4{font-family:'Nunito',sans-serif}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:1.2rem 2rem 0 2rem !important}

/* ── BRAND ── */
.brand{display:flex;align-items:center;gap:12px;margin-bottom:6px;padding:4px 0}
.brand-logo{font-family:'Nunito',sans-serif;font-size:32px;font-weight:900;color:var(--ink)}
.brand-logo span{color:var(--blue)}
.brand-pill{background:linear-gradient(135deg,var(--blue),var(--blue2));color:#fff;
  font-size:10px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;
  padding:4px 14px;border-radius:30px;box-shadow:0 2px 8px rgba(0,184,252,.35)}

/* ── NAV BUTTONS ── */
div.stButton>button{
  font-family:'Nunito',sans-serif;font-weight:800;font-size:15px;letter-spacing:.3px;
  border-radius:12px;height:44px;border:2px solid var(--border);
  background:var(--white);color:var(--muted);cursor:pointer;
  transition:all .2s;width:100%;box-shadow:0 1px 4px rgba(0,0,0,.06)
}
div.stButton>button:hover{
  border-color:var(--blue);color:var(--blue);
  background:var(--blue-light);box-shadow:0 4px 12px rgba(0,184,252,.2)
}
div.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,var(--blue),var(--blue2)) !important;
  color:#fff !important;border:none !important;
  box-shadow:0 4px 16px rgba(0,184,252,.4) !important
}

/* ── PAGE TITLE ── */
.page-title{font-family:'Nunito',sans-serif;font-size:34px;font-weight:900;color:var(--ink);margin-bottom:8px}
.page-sub{font-size:17px;color:var(--muted);margin-bottom:24px;letter-spacing:.2px}

/* ── PRODUCT CARD ── */
.pc{
  background:var(--white);
  border-radius:var(--r);
  border:2px solid var(--border);
  overflow:hidden;
  transition:transform .28s cubic-bezier(.34,1.56,.64,1),box-shadow .28s,border-color .2s;
  box-shadow:0 2px 10px rgba(0,0,0,.06);
  position:relative;
  margin-bottom:4px;
}
.pc:hover{
  transform:translateY(-7px) scale(1.012);
  box-shadow:0 20px 48px rgba(0,184,252,.18),0 6px 20px rgba(0,0,0,.1);
  border-color:var(--blue);
  z-index:10;
}
.pc.sel{border-color:var(--blue);box-shadow:0 0 0 4px rgba(0,184,252,.15),0 12px 32px rgba(0,184,252,.2)}
.pc.fav{border-color:var(--pink);box-shadow:0 0 0 4px rgba(255,77,126,.12),0 8px 24px rgba(255,77,126,.15)}

/* Image zone */
.pc-img{
  background:linear-gradient(145deg,#f0f8ff,#e4f4fd);
  height:200px;
  display:flex;align-items:center;justify-content:center;
  position:relative;overflow:hidden;
  padding:16px;
}
.pc-img img{
  max-height:155px;max-width:92%;width:auto;height:auto;
  object-fit:contain;display:block;margin:0 auto;
  transition:transform .3s cubic-bezier(.34,1.56,.64,1);
  filter:drop-shadow(0 6px 16px rgba(0,0,0,.18));
}
.pc:hover .pc-img img{transform:scale(1.07) translateY(-4px)}

/* Badges */
.badge-sel{
  position:absolute;top:10px;right:10px;
  background:linear-gradient(135deg,var(--blue),var(--blue2));
  color:#fff;width:28px;height:28px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-weight:900;font-size:13px;box-shadow:0 2px 8px rgba(0,184,252,.5);z-index:3
}
.badge-fav{
  position:absolute;top:10px;left:10px;
  background:rgba(255,77,126,.12);border:2px solid var(--pink);
  color:var(--pink);width:28px;height:28px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:12px;z-index:3
}

/* Body */
.pc-body{padding:12px 14px 12px;border-top:1px solid #f0f4f8}
.pc-name{
  font-family:'Nunito',sans-serif;font-weight:900;font-size:18px;color:var(--ink);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:4px;
}
.pc-type{font-size:13px;color:var(--muted);letter-spacing:.5px;text-transform:uppercase;margin-bottom:10px}

/* Color dots */
.pc-colors{display:flex;align-items:center;gap:4px;margin-bottom:8px}
.pcs{
  width:13px;height:13px;border-radius:50%;
  border:2px solid rgba(255,255,255,.8);
  box-shadow:0 0 0 1.5px rgba(0,0,0,.12);
  flex-shrink:0;display:inline-block
}
.pc-colors-lbl{font-size:13px;color:var(--muted);margin-left:3px;font-weight:600}

/* Score chip */
.pc-sc{
  display:inline-flex;align-items:center;gap:3px;
  border-radius:20px;padding:4px 10px;font-size:13px;font-weight:800;
  font-family:'Nunito',sans-serif
}

/* Price row */
.pc-pr{display:flex;align-items:center;justify-content:space-between}
.pc-price{font-family:'Nunito',sans-serif;font-weight:900;font-size:20px;color:var(--blue2)}

/* ── BUTTON VARIANTS ── */
.btn-blue div.stButton>button{
  background:linear-gradient(135deg,var(--blue),var(--blue2)) !important;
  color:#fff !important;border:none !important;
  box-shadow:0 3px 10px rgba(0,184,252,.35) !important;height:42px !important;
  font-size:14px !important
}
.btn-pink div.stButton>button{
  background:rgba(255,77,126,.08) !important;color:var(--pink) !important;
  border:2px solid var(--pink) !important;height:42px !important;font-size:14px !important
}
.btn-pink div.stButton>button:hover{background:rgba(255,77,126,.18) !important}
.btn-outline div.stButton>button{
  background:var(--blue-light) !important;color:var(--blue2) !important;
  border:2px solid var(--blue-soft) !important;height:42px !important;font-size:14px !important
}

/* Filter */
div[data-baseweb="select"]>div{
  border-radius:10px !important;border-color:var(--border) !important;
  background:var(--white) !important;
}

/* Sticky bar */
.sticky-bar{
  position:sticky;bottom:0;background:rgba(244,247,250,.97);
  backdrop-filter:blur(12px);border-top:2px solid var(--border);
  padding:12px 0;margin-top:16px;z-index:100
}
.sel-label{font-family:'Nunito',sans-serif;font-weight:800;font-size:16px;color:var(--blue2)}

/* Try-on panels */
.panel{
  background:var(--white);border-radius:var(--r);
  border:1.5px solid var(--border);padding:16px 18px;margin-bottom:12px;
  box-shadow:0 1px 6px rgba(0,0,0,.04)
}
.panel-title{
  font-family:'Nunito',sans-serif;font-size:14px;font-weight:800;
  letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin-bottom:10px
}
.video-wrap{background:#0d0d0d;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,.25)}
.hint-pill{
  display:inline-flex;align-items:center;gap:6px;
  background:linear-gradient(135deg,var(--blue),var(--blue2));color:#fff;
  border-radius:30px;padding:7px 16px;font-family:'Nunito',sans-serif;
  font-size:15px;font-weight:800;margin-right:8px;margin-bottom:8px;
  box-shadow:0 3px 12px rgba(0,184,252,.35);
  animation:pp 2.2s ease-in-out infinite
}
.hint-pill.r{
  background:linear-gradient(135deg,var(--pink),#ff2060);
  box-shadow:0 3px 12px rgba(255,77,126,.35);animation-delay:.5s
}
@keyframes pp{0%,100%{transform:scale(1)}50%{transform:scale(1.04)}}

.ai-box{border-radius:16px;padding:18px;margin-bottom:12px;color:#fff}
.ai-num{font-family:'Nunito',sans-serif;font-size:52px;font-weight:900;line-height:1}
.ai-lbl{font-size:18px;font-weight:600;opacity:.9;margin-top:4px}
.ai-rsn{font-size:14px;opacity:.82;margin-top:6px;line-height:1.5}

.score-bar-bg{height:6px;background:var(--border);border-radius:10px;margin-top:4px;overflow:hidden}
.score-bar-fg{height:100%;border-radius:10px;transition:width .5s}
.rec-row{display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--border)}
.rec-row:last-child{border-bottom:none}

.swatch-row{display:flex;gap:7px;flex-wrap:wrap;margin-top:8px}
.swatch{width:30px;height:30px;border-radius:50%;border:3px solid transparent;
  cursor:pointer;transition:transform .18s,border-color .18s;box-shadow:0 2px 6px rgba(0,0,0,.2)}
.swatch.active{border-color:var(--blue);transform:scale(1.22)}

hr{border-color:var(--border) !important;margin:10px 0 16px !important}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:10px}

/* Upload */
.upload-tip{background:var(--blue-light);border:1.5px solid var(--blue-soft);border-radius:14px;padding:16px 20px;margin-bottom:20px}
.btn-upload div.stButton>button{
  background:linear-gradient(135deg,#7B4FFF,#9B6FFF) !important;
  color:#fff !important;border:none !important;box-shadow:0 4px 16px rgba(123,79,255,.35) !important
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. SESSION STATE - KHỞI TẠO ĐÚNG CÁCH
# ============================================================
if 'glasses_idx' not in st.session_state:
    st.session_state.glasses_idx = 0
if 'color_idx' not in st.session_state:
    st.session_state.color_idx = 0
if 'cam_on' not in st.session_state:
    st.session_state.cam_on = False
if 'scores' not in st.session_state:
    st.session_state.scores = {}
if 'phase' not in st.session_state:
    st.session_state.phase = 'tryon'
if 'ai_score' not in st.session_state:
    st.session_state.ai_score = None
if 'ai_reason' not in st.session_state:
    st.session_state.ai_reason = ''
if 'face_data' not in st.session_state:
    st.session_state.face_data = {}
if 'page' not in st.session_state:
    st.session_state.page = 'catalog'
if 'selected_glasses' not in st.session_state:
    st.session_state.selected_glasses = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'admin_verified' not in st.session_state:
    st.session_state.admin_verified = False

# ============================================================
# 3. DATA
# ============================================================
COLORS = [
    {"name": "Đen", "hex": "#1A1A1A"},
    {"name": "Nâu", "hex": "#7B4F2E"},
    {"name": "Vàng", "hex": "#C9A227"},
    {"name": "Bạc", "hex": "#9EB4C8"},
    {"name": "Xanh", "hex": "#00b8fc"},
    {"name": "Hồng", "hex": "#FF6B8A"},
]

PRODUCT_META = {
    "round": {"type": "Tròn", "price": "600.000₫", "style": "Retro"},
    "square": {"type": "Vuông", "price": "550.000₫", "style": "Classic"},
    "oval": {"type": "Oval", "price": "480.000₫", "style": "Everyday"},
    "aviator": {"type": "Aviator", "price": "300.000₫", "style": "Sport"},
    "cat": {"type": "Cat Eye", "price": "420.0000₫", "style": "Fashion"},
    "wayfarer": {"type": "Wayfarer", "price": "300.000₫", "style": "Streetwear"},
    "half": {"type": "Half-rim", "price": "300.000₫", "style": "Office"},
    "angular": {"type": "Angular", "price": "200.000₫", "style": "Bold"},
}
DEFAULT_META = {"type": "Thời Trang", "price": "350.000₫", "style": "Phổ Thông"}

IMG_DIR = "images"
os.makedirs(IMG_DIR, exist_ok=True)
META_FILE = "custom_meta.json"
import json


def load_custom_meta():
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}


def save_custom_meta(d):
    with open(META_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)


SKIN_COLOR_BONUS = {
    "trắng": {"Đen": 0.5, "Nâu": 0.3, "Vàng": 0.5, "Bạc": 0.8, "Xanh": 0.5, "Hồng": 0.4},
    "trung bình": {"Đen": 0.8, "Nâu": 0.8, "Vàng": 0.3, "Bạc": 0.3, "Xanh": 0.5, "Hồng": 0.5},
    "ngăm": {"Đen": 0.5, "Nâu": 0.8, "Vàng": 0.8, "Bạc": 0.5, "Xanh": 0.3, "Hồng": 0.3},
}


def get_glass_files():
    """Lấy tất cả file ảnh hỗ trợ (png, jpg, jpeg, webp, gif)"""
    supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    return sorted([f for f in os.listdir(IMG_DIR)
                   if f.lower().endswith(supported_formats)])


def glass_label(f):
    cm = load_custom_meta()
    if f in cm and "name" in cm[f]: return cm[f]["name"]
    return f.split('.')[0].replace('_', ' ').upper()


def get_meta(fname):
    cm = load_custom_meta()
    if fname in cm: return cm[fname]
    fl = fname.lower()
    for k, v in PRODUCT_META.items():
        if k in fl: return v
    return DEFAULT_META


def score_key():
    gf = get_glass_files();
    g = gf[st.session_state.glasses_idx] if gf else "none"
    return f"{g}|{COLORS[st.session_state.color_idx]['name']}"


def save_score(v): st.session_state.scores[score_key()] = round(v, 1)


# ============================================================
# HÀM VẼ CHỮ TIẾNG VIỆT TRÊN CAMERA
# ============================================================
def draw_vietnamese_text(frame, text, position, font_size=20, color=(255, 255, 255), bg_color=None):
    """
    Vẽ chữ tiếng Việt lên frame OpenCV sử dụng PIL
    """
    # Chuyển frame từ BGR sang RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(pil_img)

    # Tìm font hỗ trợ tiếng Việt
    font = None
    font_paths = [
        "arial.ttf",
        "Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\Arial.ttf",
        "/Library/Fonts/Arial.ttf"
    ]

    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue

    if font is None:
        font = ImageFont.load_default()

    # Vẽ background nếu có
    if bg_color:
        bbox = draw.textbbox((position[0], position[1]), text, font=font)
        draw.rectangle(bbox, fill=bg_color)

    # Vẽ text
    draw.text(position, text, font=font, fill=color)

    # Chuyển lại từ RGB sang BGR
    frame_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return frame_bgr


# ============================================================
# FIX: img_to_b64 - HỖ TRỢ NHIỀU ĐỊNH DẠNG
# ============================================================
@st.cache_data(show_spinner=False)
def img_to_b64(img_path: str) -> str:
    try:
        if not os.path.exists(img_path):
            return ""
        with Image.open(img_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img.thumbnail((220, 140), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/png;base64,{b64}"
    except Exception as e:
        print(f"Error converting {img_path}: {e}")
        return ""


# ============================================================
# 4. MEDIAPIPE
# ============================================================
@st.cache_resource
def load_face_model():
    import urllib.request, tempfile
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    p = os.path.join(tempfile.gettempdir(), "face_landmarker.task")
    if not os.path.exists(p): urllib.request.urlretrieve(url, p)
    return vision.FaceLandmarker.create_from_options(
        vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=p),
            num_faces=1, min_face_detection_confidence=0.5))


face_model = load_face_model()


# ============================================================
# 5. CV HELPERS
# ============================================================
def overlay_transparent(bg, ol, x, y):
    bh, bw = bg.shape[:2];
    oh, ow = ol.shape[:2]
    y1, y2 = max(0, y), min(bh, y + oh);
    x1, x2 = max(0, x), min(bw, x + ow)
    oy1, oy2 = max(0, -y), min(oh, bh - y);
    ox1, ox2 = max(0, -x), min(ow, bw - x)
    if y1 >= y2 or x1 >= x2: return bg
    alpha = ol[oy1:oy2, ox1:ox2, 3:4] / 255.0
    bg[y1:y2, x1:x2] = (alpha * ol[oy1:oy2, ox1:ox2, :3] + (1 - alpha) * bg[y1:y2, x1:x2]).astype(np.uint8)
    return bg


def tint_glasses(img, hex_color):
    h = hex_color.lstrip('#');
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    tint = np.zeros_like(img);
    tint[:, :, 0] = b;
    tint[:, :, 1] = g;
    tint[:, :, 2] = r;
    tint[:, :, 3] = img[:, :, 3]
    out = cv2.addWeighted(img, 0.55, tint, 0.45, 0);
    out[:, :, 3] = img[:, :, 3]
    return out


def rotate_glasses(img, angle_deg):
    if abs(angle_deg) < 0.8: return img
    h, w = img.shape[:2];
    cx, cy = w // 2, h // 2
    M = cv2.getRotationMatrix2D((cx, cy), angle_deg, 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1]);
    nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
    M[0, 2] += (nw / 2) - cx;
    M[1, 2] += (nh / 2) - cy
    return cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                          borderValue=(0, 0, 0, 0))


def place_glasses_on_face(frame, glass_img, lm, fw, fh):
    l_outer = (lm[33].x * fw, lm[33].y * fh);
    r_outer = (lm[263].x * fw, lm[263].y * fh)
    l_inner = (lm[133].x * fw, lm[133].y * fh);
    r_inner = (lm[362].x * fw, lm[362].y * fh)
    l_cx = (l_outer[0] + l_inner[0]) / 2;
    l_cy = (l_outer[1] + l_inner[1]) / 2
    r_cx = (r_outer[0] + r_inner[0]) / 2;
    r_cy = (r_outer[1] + r_inner[1]) / 2
    dx = r_cx - l_cx;
    dy = r_cy - l_cy;
    angle_deg = math.degrees(math.atan2(dy, dx))

    left_temple = (lm[234].x * fw, lm[234].y * fh)
    right_temple = (lm[454].x * fw, lm[454].y * fh)
    face_w = math.hypot(right_temple[0] - left_temple[0], right_temple[1] - left_temple[1])

    _x, _y, _w, _h = cv2.boundingRect(glass_img[:, :, 3]) if glass_img.shape[2] == 4 else (0, 0, glass_img.shape[1],
                                                                                           glass_img.shape[0])
    visible_ratio = glass_img.shape[1] / _w if _w > 0 else 1.0

    gw = max(int(face_w * 1.05 * visible_ratio), 10);
    gh = max(int(gw * glass_img.shape[0] / glass_img.shape[1]), 4)

    real_y = (lm[152].y - lm[10].y) * fh
    real_z = (lm[152].z - lm[10].z) * fw
    pitch_angle = math.atan2(real_z, real_y)

    squash_ratio = max(math.cos(pitch_angle), 0.5)
    gh = max(int(gh * squash_ratio), 4)

    resized = cv2.resize(glass_img, (gw, gh));
    rotated = rotate_glasses(resized, -angle_deg)

    nose_bridge = (lm[168].x * fw, lm[168].y * fh)
    cx = int(nose_bridge[0])

    pitch_offset = real_z * 0.45
    cy = int((l_cy + r_cy) / 2) + int(gh * 0.08) + int(pitch_offset)

    rh, rw = rotated.shape[:2]
    return overlay_transparent(frame, rotated, cx - rw // 2, cy - rh // 2)


def ear(lm, t, b, l, r, fw, fh):
    top = np.array([lm[t].x * fw, lm[t].y * fh]);
    bot = np.array([lm[b].x * fw, lm[b].y * fh])
    lft = np.array([lm[l].x * fw, lm[l].y * fh]);
    rgt = np.array([lm[r].x * fw, lm[r].y * fh])
    return np.linalg.norm(top - bot) / (np.linalg.norm(lft - rgt) + 1e-6)


def dist2d(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])


def lm_px(lm, idx, fw, fh): return (lm[idx].x * fw, lm[idx].y * fh)


# ============================================================
# 6. AI SCORING
# ============================================================
def detect_skin_tone(frame, lm, fw, fh):
    cheek = lm_px(lm, 330, fw, fh);
    x, y = int(cheek[0]), int(cheek[1])
    patch = frame[max(0, y - 15):y + 15, max(0, x - 15):x + 15]
    if patch.size == 0: return "trung bình"
    v = float(np.mean(cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)[:, :, 2]))
    return "trắng" if v > 165 else "trung bình" if v > 120 else "ngăm"


def compute_face_metrics(lm, fw, fh):
    face_w = dist2d(lm_px(lm, 234, fw, fh), lm_px(lm, 454, fw, fh))
    face_h = dist2d(lm_px(lm, 10, fw, fh), lm_px(lm, 152, fw, fh))
    if face_h == 0: return None
    jaw_w = dist2d(lm_px(lm, 172, fw, fh), lm_px(lm, 397, fw, fh))
    forehead_w = dist2d(lm_px(lm, 127, fw, fh), lm_px(lm, 356, fw, fh))
    eye_dist = dist2d(lm_px(lm, 133, fw, fh), lm_px(lm, 362, fw, fh))
    ewl = dist2d(lm_px(lm, 33, fw, fh), lm_px(lm, 133, fw, fh))
    ewr = dist2d(lm_px(lm, 362, fw, fh), lm_px(lm, 263, fw, fh))
    return {"face_ratio": face_w / face_h, "jaw_ratio": jaw_w / face_w,
            "forehead_ratio": forehead_w / face_w, "eye_dist_ratio": eye_dist / face_w,
            "eye_w_ratio": (ewl + ewr) / 2 / face_w}


GLASS_RULES = {
    "oval": {"round": 8.5, "square": 8.5, "oval": 8.5, "cat": 8.5, "half": 7.5, "aviator": 8.0, "wayfarer": 8.5,
             "default": 7.5},
    "round": {"square": 9.0, "angular": 9.0, "wayfarer": 8.5, "round": 5.5, "oval": 6.5, "half": 7.0, "default": 6.5},
    "square": {"round": 9.0, "oval": 8.5, "aviator": 8.0, "cat": 8.0, "square": 5.5, "angular": 5.5, "half": 7.0,
               "default": 7.0},
    "long": {"aviator": 8.5, "round": 8.5, "oval": 7.5, "cat": 8.0, "half": 7.0, "wayfarer": 8.0, "default": 7.0},
    "heart": {"aviator": 9.0, "round": 8.5, "oval": 8.5, "half": 7.5, "cat": 5.5, "wayfarer": 7.0, "default": 7.5},
}


def classify_face(m):
    r, j, f = m["face_ratio"], m["jaw_ratio"], m["forehead_ratio"]
    if r < 0.72: return "long"
    if r > 0.95: return "square" if j > 0.85 else "round"
    if f > 0.90 and j < 0.75: return "heart"
    return "oval"


def score_glass_face(glass_name, face_type, color_name, skin_tone, eye_dist_ratio):
    rules = GLASS_RULES.get(face_type, GLASS_RULES["oval"])
    gn = glass_name.lower();
    base = rules["default"];
    mk = "default"
    for k in rules:
        if k != "default" and k in gn: base = rules[k]; mk = k; break
    sb = SKIN_COLOR_BONUS.get(skin_tone, {}).get(color_name, 0.3)
    eb = 0.3 if eye_dist_ratio > 0.38 else 0.0
    total = min(10.0, max(1.0, base + sb + eb))
    fvn = {"oval": "oval", "round": "tròn", "square": "vuông", "long": "dài", "heart": "trái tim"}.get(face_type,
                                                                                                       "oval")
    stxt = {"trắng": "da sáng", "trung bình": "da trung bình", "ngăm": "da ngăm"}.get(skin_tone, "da trung bình")
    reason = f"Mặt {fvn} · {stxt} · kính {mk if mk != 'default' else glass_name.split('.')[0]} → {base:.1f}+{sb:.1f}"
    return round(total, 1), reason


# ============================================================
# 7. PRODUCT CARD
# ============================================================
def product_card_html(fname, is_sel, is_fav):
    meta = get_meta(fname)
    ai_sc = next((sc for k, sc in st.session_state.scores.items() if k.startswith(fname + "|")), None)
    if ai_sc is not None:
        sc_clr = "#00b8fc" if ai_sc >= 7.5 else ("#f5a623" if ai_sc >= 5.5 else "#ff4d7e")
        sc_html = f'<span class="pc-sc" style="background:{sc_clr}18;border:1.5px solid {sc_clr};color:{sc_clr}">★ {ai_sc:.1f}</span>'
    else:
        sc_html = '<span class="pc-sc" style="background:#f0f4f8;border:1.5px solid #dde4ec;color:#9aa3b0">Chưa thử</span>'

    card_cls = "pc" + (" sel" if is_sel else "") + (" fav" if is_fav else "")
    sel_badge = '<div class="badge-sel">✓</div>' if is_sel else ""
    fav_badge = '<div class="badge-fav">♥</div>' if is_fav else ""

    img_path = os.path.join(IMG_DIR, fname)
    b64 = img_to_b64(img_path)
    img_html = (f'<img src="{b64}" alt="{glass_label(fname)}">'
                if b64 else '<div style="font-size:44px;opacity:.2;text-align:center;padding:20px 0">🕶️</div>')

    swatches = "".join(f'<span class="pcs" style="background:{c["hex"]}" title="{c["name"]}"></span>'
                       for c in COLORS)

    return f"""
<div class="{card_cls}">
  <div class="pc-img">
    {sel_badge}{fav_badge}{img_html}
  </div>
  <div class="pc-body">
    <div class="pc-name">{glass_label(fname)}</div>
    <div class="pc-type">{meta['type']} · {meta['style']}</div>
    <div class="pc-colors">
      {swatches}
      <span class="pc-colors-lbl">{len(COLORS)} màu</span>
    </div>
    <div class="pc-pr">
      <div class="pc-price">{meta['price']}</div>
      {sc_html}
    </div>
  </div>
</div>"""


# ============================================================
# 8. HEADER + NAV
# ============================================================
glass_files = get_glass_files()

st.markdown("""
<div class="brand">
  <div class="brand-logo">Lens<span>AI</span></div>
  <div class="brand-pill">Virtual Try-On</div>
</div>""", unsafe_allow_html=True)

# Hiển thị trạng thái admin
status_col, spacer_col = st.columns([1, 10])
with status_col:
    if st.session_state.admin_verified:
        st.markdown("👑 **Admin**", unsafe_allow_html=True)
    else:
        st.markdown("👤 **Khách**", unsafe_allow_html=True)

c1, c2, c3, c4, _ = st.columns([2, 2, 2, 2, 6])
nav_items = [
    (c1, 'catalog', '🛍️ Cửa Hàng'),
    (c2, 'tryon',
     f'👓 Thử Kính' + (f' ({len(st.session_state.selected_glasses)})' if st.session_state.selected_glasses else '')),
    (c3, 'favorites',
     f'❤️ Yêu Thích' + (f' ({len(st.session_state.favorites)})' if st.session_state.favorites else '')),
    (c4, 'upload', '📤 Thêm Mẫu'),
]
for col, pg, label in nav_items:
    with col:
        if st.button(label, use_container_width=True,
                     type="primary" if st.session_state.page == pg else "secondary", key=f"nav_{pg}"):
            st.session_state.page = pg
            if pg == 'tryon' and st.session_state.selected_glasses:
                first = st.session_state.selected_glasses[0]
                if first in glass_files: st.session_state.glasses_idx = glass_files.index(first)
                st.session_state.phase = 'tryon'
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ============================================================
# 9. CATALOG PAGE
# ============================================================
if st.session_state.page == 'catalog':
    glass_files = get_glass_files()
    n_sel = len(st.session_state.selected_glasses)

    hc1, hc2 = st.columns([7, 3])
    with hc1:
        st.markdown(f"""
        <div class="page-title">🕶️ Bộ Sưu Tập Kính Mắt</div>
        <div class="page-sub">{len(glass_files)} sản phẩm · Chọn nhiều mẫu để thử cùng lúc</div>
        """, unsafe_allow_html=True)
    with hc2:
        if n_sel:
            st.markdown(f"""<div style="text-align:right;margin-top:10px">
              <span style="background:linear-gradient(135deg,var(--blue),var(--blue2));color:#fff;
                font-family:'Nunito',sans-serif;font-weight:800;font-size:15px;
                padding:7px 18px;border-radius:30px;box-shadow:0 3px 12px rgba(0,184,252,.4)">
                ✓ Đã chọn {n_sel} mẫu</span></div>""", unsafe_allow_html=True)

    all_types = sorted(set(get_meta(f)["type"] for f in glass_files)) if glass_files else []
    fc1, fc2, fc3, fc4 = st.columns([3, 1, 1, 1])
    with fc1:
        selected_filter = st.selectbox("", ["Tất cả"] + all_types, label_visibility="collapsed", key="cat_filter")
    with fc2:
        if st.button("✅ Tất cả", use_container_width=True):
            st.session_state.selected_glasses = glass_files.copy();
            st.rerun()
    with fc3:
        if st.button("❌ Bỏ chọn", use_container_width=True):
            st.session_state.selected_glasses = [];
            st.rerun()
    with fc4:
        if st.button("🔀 Ngẫu nhiên", use_container_width=True):
            pool = glass_files.copy();
            random.shuffle(pool)
            st.session_state.selected_glasses = pool[:min(3, len(pool))];
            st.rerun()
    st.write("")

    if not glass_files:
        st.markdown("""<div style="text-align:center;padding:80px 20px">
          <div style="font-size:72px;opacity:.2">🕶️</div>
          <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:24px;color:var(--ink);margin-top:12px">
            Chưa có sản phẩm nào</div>
          <div style="color:var(--muted);margin-top:6px;font-size:16px">Vào tab <b>📤 Thêm Mẫu</b> để upload ảnh kính (PNG, JPG, JPEG, WEBP, GIF)</div>
        </div>""", unsafe_allow_html=True)
    else:
        display_files = glass_files if selected_filter == "Tất cả" else [f for f in glass_files if
                                                                         get_meta(f)["type"] == selected_filter]
        if not display_files:
            st.info(f"Không tìm thấy sản phẩm loại '{selected_filter}'")
        else:
            COLS = 4
            for i in range(0, len(display_files), COLS):
                row = display_files[i:i + COLS]
                cols = st.columns(COLS)
                for j, fname in enumerate(row):
                    with cols[j]:
                        is_sel = fname in st.session_state.selected_glasses
                        is_fav = fname in st.session_state.favorites
                        st.markdown(product_card_html(fname, is_sel, is_fav), unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        with b1:
                            lbl = "✓ Đã chọn" if is_sel else "+ Chọn thử"
                            bt = "primary" if is_sel else "secondary"
                            if st.button(lbl, key=f"c_sel_{fname}", use_container_width=True, type=bt):
                                if is_sel:
                                    st.session_state.selected_glasses.remove(fname)
                                else:
                                    st.session_state.selected_glasses.append(fname)
                                st.rerun()
                        with b2:
                            flbl = "♥ Bỏ thích" if is_fav else "♡ Yêu thích"
                            if st.button(flbl, key=f"c_fav_{fname}", use_container_width=True):
                                if is_fav:
                                    st.session_state.favorites.remove(fname)
                                else:
                                    st.session_state.favorites.append(fname)
                                st.rerun()
                        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if st.session_state.selected_glasses:
        snames = ", ".join(glass_label(f) for f in st.session_state.selected_glasses[:3])
        if len(st.session_state.selected_glasses) > 3: snames += f" +{len(st.session_state.selected_glasses) - 3} nữa"
        st.markdown(f"""<div class="sticky-bar"><div style="margin:0">
          <div class="sel-label" style="margin-bottom:8px">📦 {len(st.session_state.selected_glasses)} mẫu: {snames}</div>
        </div></div>""", unsafe_allow_html=True)
        sg1, sg2 = st.columns(2)
        with sg1:
            if st.button(f"👓 Thử {len(st.session_state.selected_glasses)} mẫu →", use_container_width=True,
                         type="primary"):
                first = st.session_state.selected_glasses[0];
                glass_files = get_glass_files()
                if first in glass_files: st.session_state.glasses_idx = glass_files.index(first)
                st.session_state.page = 'tryon';
                st.session_state.phase = 'tryon';
                st.session_state.ai_score = None;
                st.rerun()
        with sg2:
            if st.button("🗑️ Xóa lựa chọn", use_container_width=True):
                st.session_state.selected_glasses = [];
                st.rerun()

# ============================================================
# 10. FAVORITES PAGE
# ============================================================
elif st.session_state.page == 'favorites':
    glass_files = get_glass_files()
    st.markdown("""<div class="page-title">❤️ Sản Phẩm <span style="color:var(--pink)">Yêu Thích</span></div>
    <div class="page-sub">Những mẫu kính bạn đã lưu lại</div>""", unsafe_allow_html=True)

    favs = [f for f in st.session_state.favorites if f in glass_files]
    if not favs:
        st.markdown("""<div style="text-align:center;padding:80px 20px">
          <div style="font-size:72px;opacity:.2">♡</div>
          <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:24px;color:var(--ink);margin-top:12px">
            Chưa có sản phẩm yêu thích</div>
          <div style="color:var(--muted);margin-top:6px;font-size:16px">Nhấn <b>♡ Yêu thích</b> trong Cửa Hàng để lưu mẫu</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="margin-bottom:16px">
          <span style="background:rgba(255,77,126,.1);border:2px solid var(--pink);color:var(--pink);
            font-family:'Nunito',sans-serif;font-weight:800;font-size:15px;
            padding:6px 18px;border-radius:30px">{len(favs)} sản phẩm yêu thích</span>
        </div>""", unsafe_allow_html=True)
        COLS = 4
        for i in range(0, len(favs), COLS):
            row = favs[i:i + COLS]
            cols = st.columns(COLS)
            for j, fname in enumerate(row):
                with cols[j]:
                    is_sel = fname in st.session_state.selected_glasses
                    st.markdown(product_card_html(fname, is_sel, True), unsafe_allow_html=True)
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("👓 Thử", key=f"f_try_{fname}", use_container_width=True):
                            if fname in glass_files: st.session_state.glasses_idx = glass_files.index(fname)
                            if fname not in st.session_state.selected_glasses:
                                st.session_state.selected_glasses.append(fname)
                            st.session_state.page = 'tryon';
                            st.session_state.phase = 'tryon';
                            st.session_state.ai_score = None;
                            st.rerun()
                    with b2:
                        lbl = "✓ Chọn" if is_sel else "+ Chọn"
                        bt = "primary" if is_sel else "secondary"
                        if st.button(lbl, key=f"f_sel_{fname}", use_container_width=True, type=bt):
                            if is_sel:
                                st.session_state.selected_glasses.remove(fname)
                            else:
                                st.session_state.selected_glasses.append(fname)
                            st.rerun()
                    with b3:
                        if st.button("♥ Bỏ", key=f"f_unfav_{fname}", use_container_width=True):
                            st.session_state.favorites.remove(fname);
                            st.rerun()
                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        st.write("")
        if st.button(f"👓 Thử tất cả {len(favs)} mẫu yêu thích", use_container_width=True, type="primary"):
            st.session_state.selected_glasses = favs.copy()
            if favs[0] in glass_files: st.session_state.glasses_idx = glass_files.index(favs[0])
            st.session_state.page = 'tryon';
            st.session_state.phase = 'tryon';
            st.session_state.ai_score = None;
            st.rerun()

# ============================================================
# 11. UPLOAD PAGE (CHỈ ADMIN - HỖ TRỢ NHIỀU ĐỊNH DẠNG ẢNH)
# ============================================================
elif st.session_state.page == 'upload':
    # KIỂM TRA QUYỀN ADMIN
    if not st.session_state.admin_verified:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px">
            <div style="font-size:72px;opacity:.2">🔒</div>
            <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:24px;color:var(--ink);margin-top:12px">
                Khu vực quản trị viên
            </div>
            <div style="color:var(--muted);margin-top:6px;font-size:16px">Vui lòng đăng nhập để thêm/xóa sản phẩm</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("admin_login_form"):
            st.markdown("### 🔐 Đăng nhập quản trị")
            admin_pass = st.text_input("Mật khẩu quản trị", type="password", placeholder="Nhập mật khẩu")
            submitted = st.form_submit_button("Đăng nhập", use_container_width=True, type="primary")

            if submitted:
                if admin_pass == "admin123":
                    st.session_state.admin_verified = True
                    st.success("✅ Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("❌ Mật khẩu không đúng!")
            st.stop()

    # ========== PHẦN NÀY CHỈ HIỂN THỊ KHI ĐÃ ĐĂNG NHẬP ADMIN ==========
    glass_files = get_glass_files()

    # Hiển thị banner admin
    st.markdown("""
    <div style="background:linear-gradient(135deg, #00b8fc, #009fd9); padding:12px 20px; border-radius:12px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center">
        <div style="color:white; font-weight:800; font-size:16px">👑 Chế độ quản trị viên</div>
        <div style="color:white; font-size:14px">Bạn có quyền thêm/xóa sản phẩm</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="page-title">📤 Thêm Mẫu Kính Mới</div>
    <div class="page-sub">Upload file ảnh nền trong suốt — hỗ trợ nhiều định dạng</div>""",
                unsafe_allow_html=True)
    st.markdown("""<div class="upload-tip">
      <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:16px;
        letter-spacing:1px;text-transform:uppercase;color:var(--blue2);margin-bottom:8px">💡 Hướng dẫn</div>
      <div style="font-size:16px;color:var(--ink);line-height:1.9">
        • Hỗ trợ các định dạng: <b>PNG, JPG, JPEG, WEBP, GIF</b><br>
        • Khuyến nghị dùng <b>PNG</b> với nền trong suốt (transparent) để có hiệu ứng tốt nhất<br>
        • Ảnh nền trắng hoặc có nền sẽ được xử lý tự động (nhưng khuyến nghị dùng nền trong suốt)<br>
        • Tên chứa loại kính để tự phân loại: <code>round</code>, <code>square</code>, <code>oval</code>, <code>aviator</code>, <code>cat</code>, <code>wayfarer</code>, <code>half</code>, <code>angular</code><br>
        • Ví dụ: <code>aviator_blue.png</code>, <code>cat_gold.jpg</code>, <code>wayfarer_black.webp</code>
      </div></div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader("Kéo thả hoặc click chọn file ảnh",
                                type=["png", "jpg", "jpeg", "webp", "gif"],
                                accept_multiple_files=True,
                                label_visibility="collapsed")

    if uploaded:
        prev_cols = st.columns(min(len(uploaded), 4))
        for pi, uf in enumerate(uploaded[:4]):
            with prev_cols[pi]:
                st.image(uf, caption=uf.name, use_container_width=True)
        st.write("")
        st.markdown("### 🏷️ Đặt tên & Giá")
        custom_names = {}
        custom_prices = {}
        for uf in uploaded:
            st.markdown(
                f"<div style='font-size:15px; font-weight:700; margin-bottom:4px; margin-top:8px'>🔹 {uf.name}</div>",
                unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            default_name = uf.name.split('.')[0].replace('_', ' ').upper()
            custom_names[uf.name] = c1.text_input("Tên kính", value="", key=f"n_{uf.name}",
                                                  label_visibility="collapsed", placeholder="Nhập tên sản phẩm")
            custom_prices[uf.name] = c2.text_input("Giá", value="", key=f"p_{uf.name}", label_visibility="collapsed",
                                                   placeholder="Nhập giá sản phẩm")

        st.markdown('<div class="btn-upload">', unsafe_allow_html=True)
        if st.button(f"⬆️ Upload {len(uploaded)} mẫu vào cửa hàng", use_container_width=True):
            saved, skipped, converted = [], [], []
            cm = load_custom_meta()
            for uf in uploaded:
                dest = os.path.join(IMG_DIR, uf.name)
                if os.path.exists(dest):
                    skipped.append(uf.name)
                else:
                    img = Image.open(uf)

                    if img.format != 'PNG' and img.mode != 'RGBA':
                        img = img.convert('RGBA')
                        new_filename = uf.name.rsplit('.', 1)[0] + '.png'
                        dest = os.path.join(IMG_DIR, new_filename)
                        img.save(dest, 'PNG')
                        converted.append(f"{uf.name} → {new_filename}")
                        saved_name = new_filename
                    else:
                        img.save(dest, img.format)
                        saved_name = uf.name
                        saved.append(uf.name)

                    fl = saved_name.lower()
                    m_type = "Thời Trang"
                    m_style = "Phổ Thông"
                    for k, v in PRODUCT_META.items():
                        if k in fl:
                            m_type = v["type"]
                            m_style = v["style"]
                            break

                    cm[saved_name] = {
                        "name": custom_names[uf.name].strip() or uf.name.split('.')[0].replace('_', ' ').upper(),
                        "type": m_type,
                        "style": m_style,
                        "price": custom_prices[uf.name].strip() or "750.000₫"
                    }
            save_custom_meta(cm)
            if saved: st.success(f"✅ Đã thêm {len(saved)} mẫu: {', '.join(saved)}")
            if converted: st.info(f"🔄 Đã chuyển đổi sang PNG: {', '.join(converted)}")
            if skipped: st.warning(f"⚠️ Bỏ qua {len(skipped)} file đã tồn tại")
            if saved or converted:
                st.balloons()
                st.info("💡 Vào **Cửa Hàng** để thấy mẫu mới!")
        st.markdown('</div>', unsafe_allow_html=True)

    glass_files = get_glass_files()
    st.write("");
    st.markdown("---")
    st.markdown(f"""<div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:22px;
      color:var(--ink);margin-bottom:12px">🗂️ Quản lý ({len(glass_files)} mẫu)</div>""", unsafe_allow_html=True)
    if not glass_files:
        st.markdown('<div style="color:var(--muted);padding:16px 0">Chưa có mẫu kính nào.</div>',
                    unsafe_allow_html=True)
    else:
        for fname in glass_files:
            mc1, mc2, mc3 = st.columns([5, 2, 1])
            with mc1:
                st.markdown(f"""<div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--border)">
                  <span style="font-size:26px">🕶️</span>
                  <div>
                    <div style="font-family:'Nunito',sans-serif;font-weight:700;font-size:17px;color:var(--ink)">{glass_label(fname)}</div>
                    <div style="font-size:14px;color:var(--muted)">{fname}</div>
                  </div></div>""", unsafe_allow_html=True)
            with mc2:
                meta = get_meta(fname)
                st.markdown(
                    f'<div style="padding:11px 0;font-size:16px;color:var(--muted)">{meta["type"]} · {meta["price"]}</div>',
                    unsafe_allow_html=True)
            with mc3:
                if st.button("🗑️", key=f"del_{fname}", help=f"Xóa {fname}"):
                    try:
                        os.remove(os.path.join(IMG_DIR, fname))
                        cm = load_custom_meta()
                        if fname in cm:
                            del cm[fname]
                            save_custom_meta(cm)
                        for lst in ['selected_glasses', 'favorites']:
                            if fname in st.session_state[lst]: st.session_state[lst].remove(fname)
                        st.success(f"Đã xóa {fname}");
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # Nút đăng xuất
    st.markdown("---")
    if st.button("🚪 Đăng xuất khỏi chế độ Admin", use_container_width=True):
        st.session_state.admin_verified = False
        st.rerun()

# ============================================================
# 12. TRY-ON PAGE
# ============================================================
elif st.session_state.page == 'tryon':
    glass_files = get_glass_files()
    active_glasses = st.session_state.selected_glasses if st.session_state.selected_glasses else glass_files
    if active_glasses:
        cur_glass = glass_files[st.session_state.glasses_idx] if glass_files else None
        if cur_glass not in active_glasses:
            cur_glass = active_glasses[0]
            if cur_glass in glass_files: st.session_state.glasses_idx = glass_files.index(cur_glass)

    if len(active_glasses) > 1:
        st.markdown("""<div style="background:var(--white);border-radius:14px;border:1.5px solid var(--border);
          padding:10px 16px;margin-bottom:12px;box-shadow:0 1px 6px rgba(0,0,0,.04)">
          <div style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:800;
            letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin-bottom:8px">Mẫu đang thử</div>""",
                    unsafe_allow_html=True)
        qcols = st.columns(min(len(active_glasses), 6))
        for qi, gf in enumerate(active_glasses[:6]):
            with qcols[qi]:
                is_cur = glass_files and gf == glass_files[st.session_state.glasses_idx]
                short = glass_label(gf)[:8] + ("…" if len(glass_label(gf)) > 8 else "")
                if st.button(short, key=f"q_{gf}", use_container_width=True, type="primary" if is_cur else "secondary"):
                    if gf in glass_files: st.session_state.glasses_idx = glass_files.index(
                        gf); st.session_state.ai_score = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([6, 4], gap="large")

    with right:
        if st.session_state.phase == 'tryon':
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Chọn mẫu kính</div>', unsafe_allow_html=True)
            if active_glasses:
                cur = glass_files[st.session_state.glasses_idx] if glass_files else None
                cur_in = cur if cur in active_glasses else active_glasses[0]
                aidx = active_glasses.index(cur_in)
                sel = st.selectbox("", active_glasses, index=aidx, format_func=glass_label,
                                   label_visibility="collapsed")
                nfi = glass_files.index(sel) if sel in glass_files else 0
                if nfi != st.session_state.glasses_idx: st.session_state.glasses_idx = nfi; st.session_state.ai_score = None
                if st.button("🔄 Thay đổi mẫu chọn", use_container_width=True):
                    st.session_state.page = 'catalog';
                    st.rerun()
            else:
                st.warning("Upload ảnh PNG vào tab 📤 Thêm Mẫu")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Màu gọng kính</div>', unsafe_allow_html=True)
            ccols = st.columns(len(COLORS))
            for i, c in enumerate(COLORS):
                with ccols[i]:
                    lbl = f"✓ {COLORS[i]['name']}" if i == st.session_state.color_idx else COLORS[i]['name']
                    if st.button(lbl, key=f"col_{i}", use_container_width=True):
                        st.session_state.color_idx = i;
                        st.session_state.ai_score = None;
                        st.rerun()
            sw = '<div class="swatch-row">'
            for i, c in enumerate(COLORS):
                cls = "active" if i == st.session_state.color_idx else ""
                sw += f'<div class="swatch {cls}" style="background:{c["hex"]}" title="{c["name"]}"></div>'
            sw += '</div>'
            st.markdown(sw, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            ai_sc = st.session_state.ai_score;
            ai_rsn = st.session_state.ai_reason
            if ai_sc is None:
                st.markdown("""<div class="panel" style="text-align:center;padding:26px">
                  <div style="font-size:40px;opacity:.25">🤖</div>
                  <div style="font-family:'Nunito',sans-serif;font-weight:700;font-size:14px;
                    color:var(--muted);margin-top:10px">Bật camera để AI<br>phân tích & chấm điểm</div>
                </div>""", unsafe_allow_html=True)
            else:
                sc_clr = "#00b8fc" if ai_sc >= 7.5 else ("#f5a623" if ai_sc >= 5.5 else "#ff4d7e")
                lbl = (
                    "Rất phù hợp 🔥" if ai_sc >= 8.5 else "Phù hợp 👍" if ai_sc >= 7.0 else "Tạm được 😐" if ai_sc >= 5.5 else "Không hợp 😕")
                st.markdown(f"""<div class="ai-box" style="background:linear-gradient(135deg,{sc_clr},{sc_clr}bb)">
                  <div style="font-size:10px;font-weight:700;letter-spacing:1.5px;opacity:.85;text-transform:uppercase">🤖 AI Score</div>
                  <div style="display:flex;align-items:baseline;gap:6px;margin-top:4px">
                    <div class="ai-num">{ai_sc:.1f}</div>
                    <div style="font-size:15px;font-weight:700;opacity:.8">/ 10</div>
                  </div>
                  <div class="ai-lbl">{lbl}</div>
                  <div style="height:6px;background:rgba(255,255,255,.25);border-radius:10px;margin-top:10px;overflow:hidden">
                    <div style="height:100%;width:{int(ai_sc * 10)}%;background:rgba(255,255,255,.8);border-radius:10px;transition:width .5s"></div>
                  </div>
                  <div class="ai-rsn">{ai_rsn}</div>
                </div>""", unsafe_allow_html=True)
                save_score(ai_sc)

            fd = st.session_state.face_data
            if fd:
                st.markdown(f"""<div class="panel" style="padding:12px 16px">
                  <div class="panel-title" style="margin-bottom:7px">📐 Phân tích khuôn mặt</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;font-size:13px;color:var(--ink)">
                    <div>Loại mặt: <b>{fd.get('face_type', '–')}</b></div>
                    <div>Tông da: <b>{fd.get('skin_tone', '–')}</b></div>
                    <div>Tỉ lệ W/H: <b>{fd.get('ratio', 0):.2f}</b></div>
                    <div>Khoảng mắt: <b>{fd.get('eye_dist_ratio', 0):.2f}</b></div>
                  </div></div>""", unsafe_allow_html=True)

            if glass_files:
                cur_fname = glass_files[st.session_state.glasses_idx]
                is_fav_cur = cur_fname in st.session_state.favorites
                fa1, fa2, fa3 = st.columns(3)
                with fa1:
                    st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
                    if st.button("🛒 Giỏ hàng", use_container_width=True):
                        st.toast(f"✅ Đã thêm {glass_label(cur_fname)}", icon="🛍️")
                    st.markdown('</div>', unsafe_allow_html=True)
                with fa2:
                    st.markdown('<div class="btn-pink">', unsafe_allow_html=True)
                    if st.button("♥ Đã lưu" if is_fav_cur else "♡ Yêu thích", use_container_width=True,
                                 key="tryon_fav"):
                        if is_fav_cur:
                            st.session_state.favorites.remove(cur_fname)
                        else:
                            st.session_state.favorites.append(cur_fname)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with fa3:
                    st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
                    if st.button("✨ Mua ngay", use_container_width=True):
                        st.balloons();
                        st.toast("🚀 Đang chuyển thanh toán...", icon="💳")
                    st.markdown('</div>', unsafe_allow_html=True)
            st.write("")
            if st.button("📊 Xem đề xuất tốt nhất →", use_container_width=True, type="primary"):
                st.session_state.phase = 'recommend';
                st.rerun()

        else:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">🏆 Xếp hạng phù hợp nhất</div>', unsafe_allow_html=True)
            if st.session_state.scores:
                active_set = set(active_glasses)
                fs = {k: v for k, v in st.session_state.scores.items() if
                      k.split("|")[0] in active_set} or st.session_state.scores
                ranked = sorted(fs.items(), key=lambda x: -x[1])
                medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                for i, (key, val) in enumerate(ranked[:5]):
                    parts = key.split("|");
                    gn = glass_label(parts[0]) if parts else "?";
                    cn = parts[1] if len(parts) > 1 else "?"
                    clr = "#00b8fc" if val >= 7.5 else ("#f5a623" if val >= 5.5 else "#ff4d7e")
                    st.markdown(f"""<div class="rec-row">
                      <div style="font-size:22px;min-width:34px">{medals[i]}</div>
                      <div style="flex:1">
                        <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:14px;color:var(--ink)">{gn}</div>
                        <div style="font-size:12px;color:var(--muted)">Màu: {cn}</div>
                        <div class="score-bar-bg"><div class="score-bar-fg" style="width:{int(val * 10)}%;background:{clr}"></div></div>
                      </div>
                      <div style="font-family:'Nunito',sans-serif;font-weight:900;font-size:18px;color:{clr}">{val:.1f}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Bật camera và thử từng mẫu để AI chấm điểm!")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.session_state.scores:
                best = max(st.session_state.scores, key=st.session_state.scores.get)
                bp = best.split("|");
                bname = glass_label(bp[0]);
                bcol = bp[1] if len(bp) > 1 else "?";
                bsc = st.session_state.scores[best]
                st.markdown(f"""<div class="panel" style="background:var(--blue-light);border-color:var(--blue-soft)">
                  <div style="font-family:'Nunito',sans-serif;font-weight:900;font-size:15px;color:var(--blue2)">✨ Đề xuất tốt nhất</div>
                  <div style="margin:6px 0 2px;font-size:15px;font-weight:700;color:var(--ink)">{bname}</div>
                  <div style="font-size:13px;color:var(--muted)">Màu: <b>{bcol}</b> · Điểm: <b>{bsc:.1f}/10</b></div>
                </div>""", unsafe_allow_html=True)
                st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
                if st.button("🔥 Mua mẫu tốt nhất", use_container_width=True):
                    st.balloons();
                    st.toast(f"🎉 {bname} màu {bcol}!", icon="✨")
                st.markdown('</div>', unsafe_allow_html=True)
            st.write("")
            if st.button("← Quay lại thử kính", use_container_width=True):
                st.session_state.phase = 'tryon';
                st.rerun()

    with left:
        st.markdown("""<div style="margin-bottom:10px">
          <span class="hint-pill">👁️ Nháy mắt → Đổi kính</span>
          <span class="hint-pill r">↔️ Nghiêng đầu → Đổi màu</span>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="video-wrap">', unsafe_allow_html=True)
        frame_win = st.empty()
        if not st.session_state.cam_on:
            frame_win.markdown("""<div style="height:450px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:14px;background:#000">
              <div style="color:#00b8fc;font-family:'Nunito',sans-serif;font-weight:900;font-size:26px;
                letter-spacing:3px;animation:pp 1.8s ease-in-out infinite;
                text-shadow:0 0 30px rgba(0,184,252,.7)">[ INITIALIZING AI ]</div>
              <div style="color:rgba(255,255,255,.5);font-family:'Inter',sans-serif;font-size:20px;letter-spacing:2px;color:#ffffff">
                KIẾN TẠO DIỆN MẠO - NÂNG TẦM PHONG CÁCH</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        cam_txt = "📷 Tắt camera" if st.session_state.cam_on else "📷 Bật camera"
        if st.button(cam_txt, use_container_width=True, type="primary"):
            st.session_state.cam_on = not st.session_state.cam_on;
            st.rerun()

    if st.session_state.cam_on and active_glasses:
        cap = cv2.VideoCapture(0)
        cur_glass_idx = st.session_state.glasses_idx;
        cur_color_idx = st.session_state.color_idx
        cur_gname = glass_files[cur_glass_idx] if glass_files else None
        cur_active_pos = active_glasses.index(cur_gname) if cur_gname in active_glasses else 0


        def load_glass(gi, ci):
            p = os.path.join(IMG_DIR, glass_files[gi])
            b = cv2.imread(p, cv2.IMREAD_UNCHANGED)
            if b is not None and b.ndim == 3 and b.shape[2] == 4: return tint_glasses(b.copy(), COLORS[ci]['hex'])
            return b


        glass_img = load_glass(cur_glass_idx, cur_color_idx)
        EAR_OPEN = 0.25;
        EAR_CLOSE = 0.18;
        BLINK_CONSEC = 2;
        TILT_THRESH = 0.05;
        TILT_CONSEC = 8;
        COOLDOWN_MAX = 25
        blink_cnt = 0;
        tilt_cnt = 0;
        cooldown = 0;
        eye_was_open = True;
        last_tilt = 0;
        frame_cnt = 0;
        SCORE_EVERY = 15

        while cap.isOpened() and st.session_state.cam_on:
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1);
            fh_f, fw_f = frame.shape[:2];
            frame_cnt += 1
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = face_model.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
            gesture_fired = False

            if res.face_landmarks:
                lm = res.face_landmarks[0]
                ear_l = ear(lm, 159, 145, 33, 133, fw_f, fh_f);
                ear_r = ear(lm, 386, 374, 362, 263, fw_f, fh_f)
                avg_ear = (ear_l + ear_r) / 2.0;
                nose_x = lm[1].x;
                chin_x = lm[152].x;
                tilt_val = nose_x - chin_x

                if cooldown > 0:
                    cooldown -= 1
                else:
                    eon = avg_ear >= EAR_OPEN;
                    ecn = avg_ear <= EAR_CLOSE
                    if ecn:
                        blink_cnt += 1;
                        eye_was_open = False
                    elif eon and not eye_was_open:
                        if blink_cnt >= BLINK_CONSEC:
                            cur_active_pos = (cur_active_pos + 1) % len(active_glasses)
                            ng = active_glasses[cur_active_pos]
                            if ng in glass_files: cur_glass_idx = glass_files.index(ng)
                            glass_img = load_glass(cur_glass_idx, cur_color_idx)
                            st.session_state.glasses_idx = cur_glass_idx;
                            st.session_state.ai_score = None
                            gesture_fired = True;
                            cooldown = COOLDOWN_MAX
                        blink_cnt = 0;
                        eye_was_open = True
                    else:
                        if eon: eye_was_open = True
                    if abs(tilt_val) > TILT_THRESH:
                        td = 1 if tilt_val > 0 else -1
                        if td == last_tilt:
                            tilt_cnt += 1
                        else:
                            tilt_cnt = 1;
                            last_tilt = td
                    else:
                        if tilt_cnt >= TILT_CONSEC:
                            cur_color_idx = (cur_color_idx + last_tilt) % len(COLORS)
                            glass_img = load_glass(cur_glass_idx, cur_color_idx)
                            st.session_state.color_idx = cur_color_idx;
                            st.session_state.ai_score = None
                            gesture_fired = True;
                            cooldown = COOLDOWN_MAX
                        tilt_cnt = 0;
                        last_tilt = 0

                if frame_cnt % SCORE_EVERY == 0:
                    m = compute_face_metrics(lm, fw_f, fh_f)
                    if m:
                        ft = classify_face(m);
                        st2 = detect_skin_tone(frame, lm, fw_f, fh_f)
                        gname = glass_files[cur_glass_idx];
                        cname = COLORS[cur_color_idx]['name']
                        sc, reason = score_glass_face(gname, ft, cname, st2, m["eye_dist_ratio"])
                        st.session_state.ai_score = sc;
                        st.session_state.ai_reason = reason
                        st.session_state.face_data = {
                            "face_type": {"oval": "Oval", "round": "Tròn", "square": "Vuông", "long": "Dài",
                                          "heart": "Trái Tim"}.get(ft, ft), "skin_tone": st2,
                            "ratio": round(m["face_ratio"], 2), "eye_dist_ratio": round(m["eye_dist_ratio"], 2)}
                        save_score(sc)

                if glass_img is not None: frame = place_glasses_on_face(frame, glass_img, lm, fw_f, fh_f)

                # PHẦN HIỂN THỊ SCORE - SỬ DỤNG PIL ĐỂ VẼ TIẾNG VIỆT
                sc_now = st.session_state.ai_score
                if sc_now is not None:
                    g_txt = glass_label(glass_files[cur_glass_idx])
                    c_txt = COLORS[cur_color_idx]['name']
                    text_line = f"{g_txt} [{c_txt}] Score: {sc_now:.1f}/10"

                    # Tạo background mờ cho text
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (0, fh_f - 52), (fw_f, fh_f), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

                    # Vẽ thanh score
                    bar_w = int(sc_now / 10 * (fw_f // 3))
                    cv2.rectangle(frame, (12, fh_f - 16), (12 + bar_w, fh_f - 6), (0, 184, 252), -1)

                    # Vẽ text tiếng Việt có dấu bằng PIL
                    frame = draw_vietnamese_text(frame, text_line, (12, fh_f - 48), font_size=18, color=(255, 255, 255))

                if gesture_fired:
                    ov = frame.copy();
                    cv2.rectangle(ov, (0, 0), (fw_f, fh_f), (0, 184, 252), -1)
                    cv2.addWeighted(ov, 0.15, frame, 0.85, 0, frame)

            frame_win.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
            if gesture_fired: cap.release(); st.rerun()
        cap.release()