# app.py
# Audiogram Generator – Web App
# With color scheme, Hz labels, unmasked/masked

import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import io

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

try:
    bg = Image.open(GRID_FILE)
    width, height = bg.size
except:
    st.error(f"Image not found: {GRID_FILE}")
    st.stop()

# ================================
# PAGE
# ================================

st.set_page_config(page_title="Audiogram Generator", layout="wide")
st.title("Audiogram Generator")

# ================================
# COLOR SCHEME DROPDOWN
# ================================

color_scheme = st.selectbox(
    "Color Scheme",
    ["Red & Blue (Default)", "Black"],
    index=0
)

use_black = (color_scheme == "Black")

# ================================
# INPUTS
# ================================

col1, col2 = st.columns(2)

# --- RIGHT EAR ---
with col1:
    st.subheader("Right Ear")
    
    # AC with Hz
    right_ac = {
        f: st.number_input(f"AC {f} Hz", -10, 120, 20, 5, key=f"r_ac_{f}") 
        for f in AC_FREQS
    }
    
    st.write("**BC**")
    right_bc_u = {}
    right_bc_m = {}
    for f in BC_FREQS:
        c1, c2 = st.columns(2)
        with c1: 
            right_bc_u[f] = st.number_input(f"unmasked {f} Hz", -10, 120, 10, 5, key=f"r_u_{f}")
        with c2: 
            right_bc_m[f] = st.number_input(f"masked {f} Hz", -10, 120, None, 5, key=f"r_m_{f}")

# --- LEFT EAR ---
with col2:
    st.subheader("Left Ear")
    
    # AC with Hz
    left_ac = {
        f: st.number_input(f"AC {f} Hz", -10, 120, 20, 5, key=f"l_ac_{f}") 
        for f in AC_FREQS
    }
    
    st.write("**BC**")
    left_bc_u = {}
    left_bc_m = {}
    for f in BC_FREQS:
        c1, c2 = st.columns(2)
        with c1: 
            left_bc_u[f] = st.number_input(f"unmasked {f} Hz", -10, 120, 10, 5, key=f"l_u_{f}")
        with c2: 
            left_bc_m[f] = st.number_input(f"masked {f} Hz", -10, 120, None, 5, key=f"l_m_{f}")

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

# Determine colors
right_color = 'black' if use_black else 'red'
left_color  = 'black' if use_black else 'blue'

# AC
for ear, ac, color, symbol in [
    ('right', right_ac, right_color, 'o'),
    ('left',  left_ac,  left_color,  'x')
]:
    xs = [coord(ear, f, ac[f])[0] for f in AC_FREQS if ac[f] is not None]
    ys = [coord(ear, f, ac[f])[1] for f in AC_FREQS if ac[f] is not None]
    if xs:
        ax.plot(xs, ys, symbol, color=color, ms=8, mfc='none', mew=1.2)
        ax.plot(xs, ys, '-', color=color, lw=1.0)

# BC
for f in BC_FREQS:
    # Right
    rm = right_bc_m[f]; ru = right_bc_u[f] if rm is None else None; rval = rm or ru
    if rval is not None:
        x, y = RIGHT_X[f], Y_PIX[rval]
        if rm is not None:
            ax.text(x - 5, y, '[', color=right_color, fontsize=12, ha='center', va='center')
        else:
            ax.plot(x, y, '^', color=right_color, ms=9, mew=1.5, mfc='none')
    
    # Left
    lm = left_bc_m[f]; lu = left_bc_u[f] if lm is None else None; lval = lm or lu
    if lval is not None:
        x, y = LEFT_X[f], Y_PIX[lval]
        if lm is not None:
            ax.text(x + 5, y, ']', color=left_color, fontsize=12, ha='center', va='center')
        else:
            ax.plot(x, y, '^', color=left_color, ms=9, mew=1.5, mfc='none')

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

st.success("Ready! Use buttons to download.")
