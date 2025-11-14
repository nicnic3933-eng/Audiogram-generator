# app.py
# Audiogram Generator – High-Res 1060x674 @ 96 dpi
# Copy-paste = Drag PNG size in Word | Unmasked BC sync

import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import io

# ================================
# CONFIG
# ================================

GRID_FILE = "dual_audiogram_grid.png"  # ← 1060x674 @ 96 dpi
AC_FREQS = [250, 500, 1000, 2000, 3000, 4000, 6000, 8000]
BC_FREQS = [500, 1000, 2000, 4000]

# === HARD-CODED X-COORDINATES (for 1060x674 image) ===
RIGHT_X = {250: 218, 500: 262, 1000: 317, 2000: 375, 3000: 399, 4000: 432, 6000: 456, 8000: 489}
LEFT_X  = {250: 752, 500: 798, 1000: 855, 2000: 911, 3000: 935, 4000: 969, 6000: 992, 8000: 1029}

# === HARD-CODED Y-COORDINATES ===
Y_START = 53
Y_SCALE = 2.33
Y_PIX = {db: round(Y_START + (db + 10) * Y_SCALE) for db in range(-10, 126, 5)}

# === MASKED BC OFFSET ===
MASKED_OFFSET = 13

# Load image
try:
    bg = Image.open(GRID_FILE)
    width, height = bg.size
    if (width, height) != (1060, 674):
        st.warning(f"Image size is {width}x{height}, expected 1060x674.")
except:
    st.error(f"Image not found: {GRID_FILE}")
    st.stop()

# ================================
# PAGE
# ================================

st.set_page_config(page_title="Audiogram Generator", layout="wide")
st.title("Audiogram Generator")

# ================================
# COLOR SCHEME
# ================================

color_scheme = st.selectbox("Color Scheme", ["Red & Blue (Default)", "Black"], index=0)
use_black = (color_scheme == "Black")

# ================================
# UNMASKED BC SYNC
# ================================

if "bc_u" not in st.session_state:
    st.session_state.bc_u = {f: 10 for f in BC_FREQS}
if "bc_u_last" not in st.session_state:
    st.session_state.bc_u_last = {f: 10 for f in BC_FREQS}

# ================================
# INPUTS
# ================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Right Ear")
    right_ac = {f: st.number_input(f"AC {f} Hz", -10, 120, 20, 5, key=f"r_ac_{f}") for f in AC_FREQS}
    st.write("**BC**")
    right_bc_u = {}
    right_bc_m = {}
    for f in BC_FREQS:
        c1, c2 = st.columns(2)
        with c1:
            val = st.number_input(f"unmasked {f} Hz", -10, 120, st.session_state.bc_u[f], 5, key=f"r_u_{f}")
            if val != st.session_state.bc_u_last[f]:
                st.session_state.bc_u[f] = val
                st.session_state.bc_u_last[f] = val
                st.rerun()
            right_bc_u[f] = val
        with c2:
            right_bc_m[f] = st.number_input(f"masked {f} Hz", -10, 120, None, 5, key=f"r_m_{f}")

with col2:
    st.subheader("Left Ear")
    left_ac = {f: st.number_input(f"AC {f} Hz", -10, 120, 20, 5, key=f"l_ac_{f}") for f in AC_FREQS}
    st.write("**BC**")
    left_bc_u = {}
    left_bc_m = {}
    for f in BC_FREQS:
        c1, c2 = st.columns(2)
        with c1:
            val = st.number_input(f"unmasked {f} Hz", -10, 120, st.session_state.bc_u[f], 5, key=f"l_u_{f}")
            if val != st.session_state.bc_u_last[f]:
                st.session_state.bc_u[f] = val
                st.session_state.bc_u_last[f] = val
                st.rerun()
            left_bc_u[f] = val
        with c2:
            left_bc_m[f] = st.number_input(f"masked {f} Hz", -10, 120, None, 5, key=f"l_m_{f}")

# ================================
# PLOT – EXACT SIZE FOR COPY-PASTE
# ================================

fig, ax = plt.subplots(
    figsize=(width / 96, height / 96),  # 1060/96 ≈ 11.04", 674/96 ≈ 7.02"
    dpi=96
)

ax.imshow(bg)
ax.set_xlim(0, width)
ax.set_ylim(height, 0)
ax.axis('off')

def coord(ear, f, db):
    return (RIGHT_X if ear == "right" else LEFT_X)[f], Y_PIX[db]

right_color = "black" if use_black else "red"
left_color  = "black" if use_black else "blue"

# AC
for ear, ac, color, symbol in [("right", right_ac, right_color, "o"), ("left", left_ac, left_color, "x")]:
    xs = [coord(ear, f, ac[f])[0] for f in AC_FREQS if ac[f] is not None]
    ys = [coord(ear, f, ac[f])[1] for f in AC_FREQS if ac[f] is not None]
    if xs:
        ax.plot(xs, ys, symbol, color=color, ms=8, mfc="none", mew=1.2)
        ax.plot(xs, ys, "-", color=color, lw=1.0)

# BC
for f in BC_FREQS:
    # Right
    rm = right_bc_m.get(f)
    ru = right_bc_u.get(f) if rm is None else None
    rval = rm or ru
    if rval is not None:
        x, y = RIGHT_X[f], Y_PIX[rval]
        if rm is not None:
            ax.text(x - MASKED_OFFSET, y, "[", color=right_color, fontsize=12, ha="center", va="center")
        else:
            ax.plot(x, y, "^", color=right_color, ms=9, mew=1.5, mfc="none")

    # Left
    lm = left_bc_m.get(f)
    lu = left_bc_u.get(f) if lm is None else None
    lval = lm or lu
    if lval is not None:
        x, y = LEFT_X[f], Y_PIX[lval]
        if lm is not None:
            ax.text(x + MASKED_OFFSET, y, "]", color=left_color, fontsize=12, ha="center", va="center")
        else:
            ax.plot(x, y, "^", color=left_color, ms=9, mew=1.5, mfc="none")

# Display without scaling
st.pyplot(fig, use_container_width=False)

# ================================
# DOWNLOAD – PNG WITH 96 DPI
# ================================

# PNG with 96 DPI
final_png = io.BytesIO()
pil_img = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
pil_img.save(final_png, format='PNG', dpi=(96, 96))
final_png.seek(0)

st.download_button(
    "Download PNG (Same Size in Word)",
    final_png.getvalue(),
    "audiogram.png",
    "image/png"
)

# PDF
buf_pdf = io.BytesIO()
fig.savefig(buf_pdf, format='pdf', bbox_inches='tight', pad_inches=0)
buf_pdf.seek(0)
st.download_button("Download PDF", buf_pdf.getvalue(), "audiogram.pdf", "application/pdf")

st.success("Copy-paste or drag PNG → same size in Word.")
