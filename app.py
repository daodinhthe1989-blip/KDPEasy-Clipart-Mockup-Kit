import re
import streamlit as st
from datetime import date

st.set_page_config(page_title="KDPEasy Clipart & Mockup Kit", page_icon="\U0001F3A8", layout="centered")

# ----------------------------------------------------------------------------
# Access. v1 = single tier, no OTOs yet - the funnel split (cleanup pass /
# matching paper / Etsy+TPT listing helper) is still being decided. Add more
# entries here later the same way Storybook Prompt Kit's PASSWORDS dict does.
# "expires": None = permanent, or a datetime.date for a trial password.
# ----------------------------------------------------------------------------
PASSWORDS = {
    "KDPCLIPART2026": {"expires": None},
}

CUSTOM_CSS = """
<style>
:root { color-scheme: light; }
.stApp { background: linear-gradient(160deg, #16302a 0%, #1f4a3e 55%, #275c4c 100%); }
.block-container, [data-testid="stMainBlockContainer"] {
    background: #fdfdfb;
    border-radius: 18px;
    padding-left: 3rem; padding-right: 3rem;
    margin-top: 1.5rem; margin-bottom: 3rem;
    box-shadow: 0 14px 44px rgba(10, 30, 24, 0.38);
}
h1, h2, h3 { color: #16302a; }
h1 { border-bottom: 3px solid #2f7d6b; padding-bottom: 0.3rem; }
a, a:visited { color: #1f4a3e; }
.stButton>button, .stDownloadButton>button {
    background-color: #2f7d6b; color: #ffffff; border-radius: 10px; border: none;
    padding: 0.6rem 1.4rem; font-weight: 600;
}
.stButton>button:hover, .stDownloadButton>button:hover { background-color: #1f4a3e; color: #ffffff; }
.kdp-card { display: none; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def check_password() -> bool:
    if st.session_state.get("authed"):
        return True
    st.markdown('<div class="kdp-card">', unsafe_allow_html=True)
    st.title("\U0001F3A8 KDPEasy Clipart & Mockup Kit")
    pw = st.text_input("Enter access password", type="password")
    if st.button("Unlock"):
        tier = PASSWORDS.get(pw)
        if tier is None:
            st.error("Incorrect password.")
        elif tier["expires"] is not None and date.today() > tier["expires"]:
            st.error("This trial password has expired. Please reach out to get full access.")
        else:
            st.session_state["authed"] = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    return False


# Streamlit reruns the whole script on every click, including download
# buttons - without this, a built prompt list disappears the moment someone
# clicks "Download". Stash keyed by the inputs that produced it; it keeps
# showing until an input actually changes.
def _stash(key, sig, value):
    st.session_state[key] = (sig, value)


def _recall(key, sig):
    got = st.session_state.get(key)
    return got[1] if got and got[0] == sig else None


# ----------------------------------------------------------------------------
# All text that ends up in a customer-facing prompt is plain ASCII on purpose -
# it gets pasted into ChatGPT, so no smart quotes / em dashes.
# ----------------------------------------------------------------------------

CLIPART_STYLES = {
    "Flat vector": ("flat vector clipart: solid flat colors, clean even outlines, "
                     "no gradients, no texture, no shadow"),
    "Soft watercolor": ("soft watercolor clipart: painted texture with visible brush edges, "
                         "gentle color bleed, a faint natural shadow beneath the object"),
    "Hand-drawn digital": ("hand-drawn digital clipart: a loose sketchy outline, playful "
                            "uneven linework, flat color fill, no shadow"),
}

BG_OPTIONS = {
    "Transparent": "a fully transparent background (PNG-ready, nothing behind the object)",
    "Plain white": "a plain solid white background",
}

MOCKUP_STYLES = {
    "Flatlay": "a bright flatlay scene shot from directly above, soft natural light, a few simple props",
    "Lifestyle": "a lifestyle scene with the product shown in natural use, soft daylight, an uncluttered background",
    "Clean studio": "a clean studio product shot, plain seamless background, soft even lighting, no extra props",
}

MODES = ["Clipart set", "Listing mockup scenes"]

NO_EDIT_LINE = ("Draw this as a brand-new image from the brief below - not an edit of any "
                "image already in this chat, and no uploaded reference picture is needed either.")

ITEM_MARKER = "ITEM"
SCENE_MARKER = "SCENE"


def marker_for(mode: str) -> str:
    return ITEM_MARKER if mode == "Clipart set" else SCENE_MARKER


def build_shotlist_prompt(mode: str, theme: str, count: int, style_desc: str, bg_desc) -> str:
    marker = marker_for(mode)
    last = f"{marker} {count:02d}"
    if mode == "Clipart set":
        return (
            f"You are helping me plan a themed clipart set.\n\n"
            f"THEME: {theme}\n\n"
            f"Give me a shot list of {count} individual clipart elements that fit this theme. "
            f"Each one should be simple and recognizable on its own, not a busy scene.\n\n"
            f"Output format, exactly like this for every item:\n"
            f"=== {marker} 01 ===\n"
            f"NAME: short name of the object\n"
            f"DESCRIPTION: one plain sentence describing what it looks like (shape, pose, key details only)\n"
            f"=== {marker} 02 ===\n"
            f"...continue through {last}\n\n"
            f"Style for reference (do not repeat this in the list): {style_desc}, on {bg_desc}.\n"
            f"Keep descriptions concrete and visual. No mood, lighting, or rendering language. "
            f"Avoid near-duplicate items."
        )
    else:
        return (
            f"You are helping me plan listing preview images for a product.\n\n"
            f"PRODUCT OR THEME: {theme}\n\n"
            f"Give me {count} different mockup scene ideas for showing this product in a product "
            f"listing photo. Each scene should be a different setting or angle, not a repeat of "
            f"the same idea.\n\n"
            f"Output format, exactly like this for every scene:\n"
            f"=== {marker} 01 ===\n"
            f"NAME: short name for the scene\n"
            f"DESCRIPTION: one plain sentence describing the setting, props, and camera angle "
            f"(do not mention the product itself - that gets added separately)\n"
            f"=== {marker} 02 ===\n"
            f"...continue through {last}\n\n"
            f"Style for reference (do not repeat this in the list): {style_desc}.\n"
            f"Keep each scene concrete and visual. Avoid near-duplicate scenes."
        )


def parse_items(raw: str, mode: str):
    marker = marker_for(mode)
    blocks = re.split(rf'=+\s*{marker}\s*\d+\s*=+', raw, flags=re.IGNORECASE)
    items = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        name_m = re.search(r'NAME\s*:\s*(.+)', block, re.IGNORECASE)
        desc_m = re.search(r'DESCRIPTION\s*:\s*(.+)', block, re.IGNORECASE)
        if name_m:
            name = name_m.group(1).strip()
            desc = desc_m.group(1).strip().split('\n')[0].strip() if desc_m else ""
            items.append((name, desc))
    return items


def build_clipart_item_prompt(name: str, desc: str, style_desc: str, bg_desc: str) -> str:
    return (
        f"{NO_EDIT_LINE}\n\n"
        f"STYLE: {style_desc}.\n"
        f"BACKGROUND: {bg_desc}.\n"
        f"SUBJECT: {name} - {desc}\n\n"
        f"One isolated object, centered in the frame. No shadow, no text, no border, no extra "
        f"scenery. Match the line weight and color palette used for the rest of this set."
    )


def build_mockup_item_prompt(name: str, desc: str, style_desc: str) -> str:
    return (
        f"Upload a screenshot or rendered page of your product before using this prompt.\n\n"
        f"Use the uploaded image as a fixed reference - do not redraw, alter, or reinterpret "
        f"what is on it.\n\n"
        f"SCENE: {name} - {desc}\n"
        f"STYLE: {style_desc}.\n\n"
        f"Place the uploaded image naturally into this scene, as if it were photographed there "
        f"for a product listing. Keep the uploaded content exactly as it is - only add the "
        f"surrounding scene around it."
    )


def build_collection_cover_prompt(mode: str, items, style_desc: str, bg_desc, title: str) -> str:
    """One listing/cover photo showing the whole set together - the main thumbnail
    buyers see on Etsy or TPT before they open the listing."""
    noun = "clipart elements" if mode == "Clipart set" else "scenes"
    listing = "\n".join(f"- {name}: {desc}" for name, desc in items)
    bg_line = f"BACKGROUND: {bg_desc}.\n" if bg_desc else ""
    title_line = (
        f'Add the text "{title}" as a small, clean label near the top of the image.\n'
        if title.strip() else ""
    )
    return (
        f"Create ONE image that works as a single cover/preview photo for this set - the main "
        f"thumbnail a shopper sees before opening the listing.\n\n"
        f"Arrange all {len(items)} {noun} below together in a tidy grid or flat-lay layout, each "
        f"one fully visible, evenly spaced, not overlapping or cropped.\n\n"
        f"ITEMS:\n{listing}\n\n"
        f"STYLE: {style_desc}.\n"
        f"{bg_line}"
        f"{title_line}"
        f"Keep every item in the same consistent style and proportion as the rest."
    )


# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------
if not check_password():
    st.stop()

st.title("\U0001F3A8 KDPEasy Clipart & Mockup Kit")
st.caption(
    "Type a theme, get a prompt for ChatGPT. Paste its reply back, get one ready-to-run "
    "image prompt per item - clipart elements or listing mockup scenes, your choice."
)

use_mode = st.radio(
    "I'm building this to:",
    ["Sell as a product", "Use as a promo bonus"],
    horizontal=True,
)
if use_mode == "Use as a promo bonus":
    theme_label = "Product or niche you are promoting"
    theme_help = "The affiliate offer's theme - the set is built to match it, ready to hand out as a bonus."
    theme_default = ""
else:
    theme_label = "Theme"
    theme_help = 'What the whole set is about. Keep it specific - "Cozy Autumn Harvest" beats "Fall".'
    theme_default = ""

mode = st.radio("What do you want to create?", MODES, horizontal=True)

with st.expander("How this kit works"):
    st.markdown(
        "1. Fill in the fields below and build the Step 1 prompt.\n"
        "2. Paste that prompt into ChatGPT. It replies with a numbered list.\n"
        "3. Paste that reply into Step 2. The kit turns every line into its own image prompt, "
        "already locked to one consistent style.\n"
        "4. Run each Step 2 prompt in the same ChatGPT chat so everything matches.\n"
        "5. Step 3 builds one more prompt: a single cover photo showing the whole set together "
        "- the main listing thumbnail for Etsy or TPT.\n\n"
        "**Clipart set** - isolated objects, transparent or white background, for a themed "
        "graphics pack.\n\n"
        "**Listing mockup scenes** - upload a real screenshot or page of your product first; "
        "each prompt places it into a styled scene for your Etsy or TPT listing photos. "
        "Note: ChatGPT does not always keep the uploaded content perfectly untouched - check "
        "each result before using it.\n\n"
        "**About the Step 3 cover:** it draws a brand-new illustration of the whole set "
        "together, so it may look slightly different from the individual images from Step 2. "
        "It is a fast way to get a listing photo. For a pixel-exact thumbnail, arrange your "
        "finished Step 2 images yourself in Canva or a similar tool instead."
    )

tab1, tab2, tab3 = st.tabs(["Step 1 - Shot list", "Step 2 - Image prompts", "Step 3 - Collection cover"])

with tab1:
    theme = st.text_input(theme_label, value=theme_default, help=theme_help)

    if mode == "Clipart set":
        count = st.number_input("Number of elements", min_value=4, max_value=40, value=12)
        style_name = st.selectbox("Style", list(CLIPART_STYLES.keys()))
        style_desc = CLIPART_STYLES[style_name]
        bg_name = st.selectbox("Background", list(BG_OPTIONS.keys()))
        bg_desc = BG_OPTIONS[bg_name]
    else:
        count = st.number_input("Number of mockup scenes", min_value=3, max_value=12, value=6)
        style_name = st.selectbox("Style", list(MOCKUP_STYLES.keys()))
        style_desc = MOCKUP_STYLES[style_name]
        bg_desc = None

    sig1 = (mode, theme, count, style_name)
    if st.button("Build Step 1 prompt"):
        if not theme.strip():
            st.warning("Enter a theme first.")
        else:
            _stash("shotlist_prompt", sig1, build_shotlist_prompt(mode, theme.strip(), int(count), style_desc, bg_desc))

    out1 = _recall("shotlist_prompt", sig1)
    if out1:
        st.code(out1, language=None)
        st.download_button("Download this prompt (.txt)", out1, file_name="step1_shotlist_prompt.txt")
    else:
        st.caption("Changed something above? Click \"Build Step 1 prompt\" again.")

with tab2:
    shotlist = st.text_area(
        "Paste ChatGPT's reply here",
        height=220,
        placeholder="=== %s 01 ===\nNAME: ...\nDESCRIPTION: ...\n=== %s 02 ===\n..." % (marker_for(mode), marker_for(mode)),
    )

    sig2 = (mode, shotlist, style_name, bg_desc)
    if st.button("Build Step 2 prompts"):
        items = parse_items(shotlist, mode)
        if not items:
            st.warning(
                "Could not find any items. Make sure the pasted text still has the "
                f"'=== {marker_for(mode)} 0X ===' markers with NAME: and DESCRIPTION: lines."
            )
        else:
            if mode == "Clipart set":
                prompts = [build_clipart_item_prompt(n, d, style_desc, bg_desc) for n, d in items]
            else:
                prompts = [build_mockup_item_prompt(n, d, style_desc) for n, d in items]
            _stash("item_prompts", sig2, list(zip([n for n, d in items], prompts)))

    built = _recall("item_prompts", sig2)
    if built:
        st.success(f"Built {len(built)} prompt(s).")
        all_text = "\n\n---\n\n".join(f"{i+1}. {name}\n\n{p}" for i, (name, p) in enumerate(built))
        st.download_button("Download all prompts (.txt)", all_text, file_name="step2_image_prompts.txt")
        for i, (name, p) in enumerate(built):
            st.markdown(f"**{i+1}. {name}**")
            st.code(p, language=None)
    else:
        st.caption("Paste a shot list above, then click \"Build Step 2 prompts\".")

with tab3:
    st.caption(
        "One extra prompt: a single cover photo showing every item in this set together - "
        "the main image buyers see on an Etsy or TPT listing before they click in."
    )
    cover_title = st.text_input(
        "Collection title to show on the cover (optional)",
        placeholder='e.g. "Cozy Autumn Harvest - 12 PNG Clipart Graphics"',
    )

    sig3 = (mode, shotlist, style_name, bg_desc, cover_title)
    if st.button("Build collection cover prompt"):
        cover_items = parse_items(shotlist, mode)
        if not cover_items:
            st.warning(
                "Could not find any items in Step 2's pasted text. Fill in Step 2 first, "
                "then come back here."
            )
        else:
            _stash(
                "cover_prompt", sig3,
                build_collection_cover_prompt(mode, cover_items, style_desc, bg_desc, cover_title),
            )

    out3 = _recall("cover_prompt", sig3)
    if out3:
        st.code(out3, language=None)
        st.download_button("Download this prompt (.txt)", out3, file_name="step3_cover_prompt.txt")
    else:
        st.caption("Fill in Step 2's shot list first, then click \"Build collection cover prompt\".")

st.divider()
st.caption("KDPEasy Studio - kdpeasy.studio")
