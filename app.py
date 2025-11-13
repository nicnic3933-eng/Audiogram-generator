# app.py
# Audiogram Generator – Web App
# Masked BC: 8px offset | 250/500/1k AC: 3px left shift

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

# X-AXIS: Base positions
RIGHT_X_BASE = {250: 133, 500: 160, 1000: 193, 2000: 228, 3000: 243, 4000: 263, 6000: 277, 8000: 298}
LEFT_X_BASE  = {250: 458, 500: 485, 1000: 520, 2000: 554, 3000: 569, 4000: 590, 6000: 604, 8000: 626}

# Apply 3px left shift to 250, 500, 1000 Hz for both ears
SHIFT_FREQ = {250, 500, 1000}
X_SHIFT = -3

RIGHT_X = {f: RIGHT_X_BASE[f] + (X_SHIFT if f in SHIFT_FREQ else 0) for f in AC_FREQS}
LEFT_X  = {f: LEFT_X_BASE[f]  + (X_SHIFT if f in SHIFT_FREQ else 0) for f in AC_FREQS}

# Y-AXIS
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
# COLOR SCHEME
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

with col1:
    st.subheader("Right Ear")
    right_ac = {f: st.number_input(f"AC {f} Hz", -10, 120
