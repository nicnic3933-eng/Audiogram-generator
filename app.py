# app.py
# Web Audiogram – Runs locally OR online – NO GitHub needed

import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64

# ================================
# CONFIG
# ================================

GRID_FILE = "dual_audiogram_grid.png"

AC_FREQS = [250, 500, 1000, 2000, 3000, 4000, 6000, 8000]
BC_FREQS = [500, 1000, 2000, 4000]

RIGHT_X = {250: 133, 500: 160, 1000: 193, 2000: 228, 3000: 243, 4000: 263, 6000: 277, 8000: 298}
LEFT_X  = {250: 458, 500: 485, 1000: 520, 2000: 554, 3000: 569, 4000: 590, 6000: 604, 8000: 626}

Y_SCALE = 1.42
Y_START = 32
Y_PIX = {db: Y_START + (db + 10) * Y_SCALE for db in range(-10, 126, 5)}

# Load image
try:
    bg = Image.open(GRID_FILE)
    width, height = bg.size
except:
    st.error(f"Image not found: {GRID_FILE}")
    st.stop()

# ================================
# PAGE
# ================================

st.set_page_config(page_title="Audiogram", layout="wide")
st.title("Clinic Audiogram Generator")
st.markdown("**Enter thresholds → Download PNG/PDF**")

# ================================
# INPUT
# ================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Right Ear (Red)")
    right_ac = {f: st.number_input(f"AC {f}", -10, 120, None, 5, key=f"r_ac_{f}") for f in AC_FREQS}
    st.write("**BC**")
    right_bc_u = {}
    right_bc_m = {}
    for f in BC_FREQS:
        c1, c2 = st.columns(2)
        with c1: right_bc_u[f] = st.number_input(f"U {f}", -10, 120, None, 5, key=f"r_u_{f}")
        with c2: right_bc_m[f] = st.number_input(f"M {f}", -10, 120, None, 5, key=f"r_m_{f}")

with col2:
    st.subheader("Left Ear (Blue)")
    left_ac = {f: st.number_input(f"AC {f}", -10, 120, None, 5, key=f"l_ac_{f}") for f in AC_FREQS}
    st.write("**BC**")
    left_bc_u = {}
    left_bc_m = {}
    for f in BC_FREQS:
        c1, c2 = st.columns(2)
        with c1: left_bc_u[f] = st.number_input(f"U {f}", -10, 120, None, 5, key=f"l_u_{f}")
        with c2: left_bc_m[f] = st.number_input(f"M {f}", -10, 120, None, 5, key=f"l_m_{f}")

# ================================
# PLOT
# ================================

fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
ax.imshow(bg)
ax.set_xlim(0, width)
ax.set_ylim(height, 0)
ax.axis('off')

def coord(ear, f, db): 
    return (RIGHT_X if ear == 'right' else LEFT_X)[f], Y_PIX[db]

# Right AC
rx = [RIGHT_X[f] for f in AC_FREQS if right_ac[f] is not None]
ry = [Y_PIX[right_ac[f]] for f in AC_FREQS if right_ac[f] is not None]
if rx:
    ax.plot(rx, ry, 'o', color='red', ms=8, mfc='none', mew=1.2)
    ax.plot(rx, ry, '-', color='red', lw=1.0)

# Left AC
lx = [LEFT_X[f] for f in AC_FREQS if left_ac[f] is not None]
ly = [Y_PIX[left_ac[f]] for f in AC_FREQS if left_ac[f] is not None]
if lx:
    ax.plot(lx, ly, 'x', color='blue', ms=8, mew=1.2)
    ax.plot(lx, ly, '-', color='blue', lw=1.0)

# BC
for f in BC_FREQS:
    # Right
    rm = right_bc_m[f]; ru = right_bc_u[f] if rm is None else None; rval = rm if rm is not None else ru
    if rval is not None:
        x, y = RIGHT_X[f], Y_PIX[rval]
        if rm is not None:
            ax.text(x - 5, y, '[', color='red', fontsize=12, ha='center', va='center')
        else:
            ax.plot(x, y, '^', color='red', ms=9, mew=1.5, mfc='none')
    # Left
    lm = left_bc_m[f]; lu = left_bc_u[f] if lm is None else None; lval = lm if lm is not None else lu
    if lval is not None:
        x, y = LEFT_X[f], Y_PIX[lval]
        if lm is not None:
            ax.text(x + 5, y, ']', color='blue', fontsize=12, ha='center', va='center')
        else:
            ax.plot(x, y, '^', color='blue', ms=9, mew=1.5, mfc='none')

st.pyplot(fig)

# ================================
# DOWNLOAD
# ================================

buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
st.download_button("Download PNG", buf.getvalue(), "audiogram.png", "image/png")

buf_pdf = io.BytesIO()
fig.savefig(buf_pdf, format='pdf', bbox_inches='tight', pad_inches=0)
st.download_button("Download PDF", buf_pdf.getvalue(), "audiogram.pdf", "application/pdf")

st.success("Ready! Use buttons above to download.")
