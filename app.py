import re
import streamlit as st
from datetime import date

st.set_page_config(page_title="KDPEasy Clipart & Mockup Kit", page_icon="\U0001F3A8", layout="centered")

# ----------------------------------------------------------------------------
# Access. v1 = single tier, no OTOs yet - the funnel split is still being
# decided. Add more entries here later the same way Storybook Prompt Kit's
# PASSWORDS dict does. "expires": None = permanent, or a datetime.date for a
# trial password.
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

NO_EDIT_LINE = ("Draw this as a brand-new image from the brief below - not an edit of any "
                "image already in this chat, and no uploaded reference picture is needed either.")

CLIPART_STYLES = {
    "Flat vector": ("flat vector clipart: solid flat colors, clean even outlines, "
                     "no gradients, no texture, no shadow"),
    "Soft watercolor": ("soft watercolor clipart: painted texture with visible brush edges, "
                         "gentle color bleed, a faint natural shadow beneath the object"),
    "Hand-drawn digital": ("hand-drawn digital clipart: a loose sketchy outline, playful "
                            "uneven linework, flat color fill, no shadow"),
}

MOCKUP_STYLES = {
    "Flatlay": "a bright flatlay scene shot from directly above, soft natural light, a few simple props",
    "Lifestyle": "a lifestyle scene with the product shown in natural use, soft daylight, an uncluttered background",
    "Clean studio": "a clean studio product shot, plain seamless background, soft even lighting, no extra props",
}

PAPER_STYLES = {
    "Flat geometric": "flat geometric shapes in a bright, limited color palette, simple repeating motif",
    "Soft watercolor": "soft painted watercolor motifs with gentle color bleed and a light, airy feel",
    "Hand-drawn doodle": "playful hand-drawn doodle motifs, loose uneven linework, flat color fill",
}

STICKER_STYLES = {
    "Bold & cute": "bold, cheerful sticker art: thick clean outlines, bright flat colors, rounded friendly shapes",
    "Soft pastel": "soft pastel sticker art: gentle rounded shapes, muted colors, a light clean outline",
    "Hand-drawn": "hand-drawn sticker art: a loose sketchy outline, playful uneven linework, flat color fill",
}

DECOR_STYLES = {
    "Bold & bright": "bold classroom decor art: thick clean outlines, bright saturated flat colors, easy to read from across a room",
    "Soft pastel": "soft pastel classroom decor art: gentle rounded shapes, light muted colors, a clean simple outline",
    "Chalkboard": "a chalkboard-style look: clean white or pastel chalk-line art on a solid dark background",
}

BG_OPTIONS = {
    "Transparent": "a fully transparent background (PNG-ready, nothing behind the object)",
    "Plain white": "a plain solid white background",
}

# Settings shared by the generic (non-mockup, non-mascot) modes: UI labels,
# the count field, the style menu, and how background is handled.
#   bg: "choose"  -> customer picks Transparent / Plain white
#       "forced_transparent" / "forced_white" -> fixed, no selector shown
#       "none" -> no background line at all (pattern fills the whole canvas)
MODE_UI = {
    "Clipart set": {
        "count_label": "Number of elements",
        "count_default": 12, "count_min": 4, "count_max": 40,
        "styles": CLIPART_STYLES,
        "bg": "choose",
    },
    "Listing mockup scenes": {
        "count_label": "Number of mockup scenes",
        "count_default": 6, "count_min": 3, "count_max": 12,
        "styles": MOCKUP_STYLES,
        "bg": "none",
    },
    "Digital paper pack": {
        "count_label": "Number of pattern designs",
        "count_default": 8, "count_min": 4, "count_max": 20,
        "styles": PAPER_STYLES,
        "bg": "none",
    },
    "Planner stickers": {
        "count_label": "Number of stickers",
        "count_default": 16, "count_min": 4, "count_max": 40,
        "styles": STICKER_STYLES,
        "bg": "forced_transparent",
    },
    "Classroom decor set": {
        "count_label": "Number of decor elements",
        "count_default": 10, "count_min": 4, "count_max": 30,
        "styles": DECOR_STYLES,
        "bg": "forced_white",
    },
}
MASCOT_MODE = "Mascot pose pack"
MODES = list(MODE_UI.keys()) + [MASCOT_MODE]

MARKERS = {
    "Clipart set": "ITEM",
    "Listing mockup scenes": "SCENE",
    "Digital paper pack": "PATTERN",
    "Planner stickers": "STICKER",
    "Classroom decor set": "ITEM",
    MASCOT_MODE: "POSE",
}

OPENER = {
    "Clipart set": "a themed clipart set",
    "Listing mockup scenes": "listing preview images for a product",
    "Digital paper pack": "a themed digital paper (pattern) pack",
    "Planner stickers": "a themed planner sticker pack",
    "Classroom decor set": "a themed classroom decor set",
}

NOUNS = {
    "Clipart set": "individual clipart elements",
    "Listing mockup scenes": "different mockup scene ideas",
    "Digital paper pack": "pattern designs",
    "Planner stickers": "individual sticker ideas",
    "Classroom decor set": "individual decor elements",
}

ITEM_GUIDANCE = {
    "Clipart set": "Each one should be simple and recognizable on its own, not a busy scene.",
    "Listing mockup scenes": "Each scene should be a different setting or angle, not a repeat of the same idea.",
    "Digital paper pack": "Each one should be a distinct color-and-motif combination that could repeat seamlessly as a background pattern.",
    "Planner stickers": "Each one should be a single simple icon, tracker, or short-phrase idea - the kind of small sticker someone adds to a planner page.",
    "Classroom decor set": "Each one should be a distinct, simple decor piece (a label, a border motif, a small graphic), not a busy scene.",
}

DESC_GUIDANCE = {
    "Clipart set": "one plain sentence describing what it looks like (shape, pose, key details only)",
    "Listing mockup scenes": "one plain sentence describing the setting, props, and camera angle (do not mention the product itself - that gets added separately)",
    "Digital paper pack": 'one plain sentence describing the color palette and motif (for example, "mustard and cream, small falling leaves")',
    "Planner stickers": "one plain sentence describing the icon and any short text on it",
    "Classroom decor set": "one plain sentence describing what it looks like and what it is for (border strip, label, banner piece, and so on)",
}

CLOSING_LINE = {
    "Clipart set": ("One isolated object, centered in the frame. No shadow, no text, no border, "
                     "no extra scenery. Match the line weight and color palette used for the "
                     "rest of this set."),
    "Digital paper pack": ("Make this a seamless, tileable pattern - the design must repeat edge "
                            "to edge with no visible seam, no single focal point, flat even "
                            "coverage across the whole canvas."),
    "Planner stickers": ("One isolated sticker, centered in the frame, with a clean white border "
                          "about 2 to 3 mm wide outlining its shape like a die-cut line. No "
                          "background scenery."),
    "Classroom decor set": ("One isolated decor element, centered in the frame, bold and simple "
                             "enough to read from across a room. Sized to print, cut out, and "
                             "laminate."),
}


def marker_for(mode: str) -> str:
    return MARKERS[mode]


def build_shotlist_prompt(mode: str, theme: str, count: int, style_desc: str, bg_desc) -> str:
    marker = marker_for(mode)
    last = f"{marker} {count:02d}"
    theme_word = "PRODUCT OR THEME" if mode == "Listing mockup scenes" else "THEME"
    style_line = f"Style for reference (do not repeat this in the list): {style_desc}"
    style_line += f", on {bg_desc}." if bg_desc else "."
    return (
        f"You are helping me plan {OPENER[mode]}.\n\n"
        f"{theme_word}: {theme}\n\n"
        f"Give me a shot list of {count} {NOUNS[mode]} that fit this. {ITEM_GUIDANCE[mode]}\n\n"
        f"Output format, exactly like this for every item:\n"
        f"=== {marker} 01 ===\n"
        f"NAME: short name\n"
        f"DESCRIPTION: {DESC_GUIDANCE[mode]}\n"
        f"=== {marker} 02 ===\n"
        f"...continue through {last}\n\n"
        f"{style_line}\n"
        f"Keep descriptions concrete and visual. No mood, lighting, or rendering language. "
        f"Avoid near-duplicate items."
    )


def build_mascot_shotlist_prompt(character_desc: str, count: int, style_desc: str) -> str:
    marker = marker_for(MASCOT_MODE)
    return (
        f"You are helping me plan a consistent mascot character for reuse across many images.\n\n"
        f"CHARACTER: {character_desc}\n\n"
        f"First, write a short CHARACTER BIBLE that fixes the parts of this character that must "
        f"never change: species or type, body shape, face, colors, and any clothing or "
        f"accessories. Output it between these markers:\n"
        f"=== CHARACTER BIBLE START ===\n"
        f"(the bible, 3 to 5 sentences)\n"
        f"=== CHARACTER BIBLE END ===\n\n"
        f"Then give me a shot list of {count} different poses, expressions, or simple actions "
        f"for this same character - things that CAN change from image to image (pose, "
        f"expression, gesture, camera angle). Do not change anything listed in the Character "
        f"Bible.\n\n"
        f"Output format, exactly like this for every pose:\n"
        f"=== {marker} 01 ===\n"
        f"NAME: short name for the pose\n"
        f"DESCRIPTION: one plain sentence describing the pose, expression, or action only (do "
        f"not repeat the character's fixed appearance)\n"
        f"=== {marker} 02 ===\n"
        f"...continue through {marker} {count:02d}\n\n"
        f"Style for reference (do not repeat this in the list): {style_desc}, on a transparent "
        f"background.\n"
        f"Keep poses concrete and visual. Avoid near-duplicate poses."
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


def parse_mascot_bible(raw: str) -> str:
    m = re.search(r'CHARACTER BIBLE START\s*=*\s*(.*?)\s*=*\s*CHARACTER BIBLE END',
                  raw, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def build_item_prompt(mode: str, name: str, desc: str, style_desc: str, bg_desc) -> str:
    bg_line = f"BACKGROUND: {bg_desc}.\n" if bg_desc else ""
    return (
        f"{NO_EDIT_LINE}\n\n"
        f"STYLE: {style_desc}.\n"
        f"{bg_line}"
        f"SUBJECT: {name} - {desc}\n\n"
        f"{CLOSING_LINE[mode]}"
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


def build_mascot_pose_prompt(bible: str, name: str, desc: str, style_desc: str) -> str:
    return (
        f"{NO_EDIT_LINE}\n\n"
        f"CHARACTER (keep exactly as described, do not change): {bible}\n\n"
        f"STYLE: {style_desc}.\n"
        f"BACKGROUND: {BG_OPTIONS['Transparent']}.\n"
        f"POSE: {name} - {desc}\n\n"
        f"Give this image its own fresh pose and expression as described above - do not reuse "
        f"the pose or expression from another image. One isolated character, centered in the "
        f"frame. No shadow, no text, no border, no extra scenery."
    )


def build_collection_cover_prompt(mode: str, items, style_desc: str, bg_desc, title: str,
                                   character_bible: str = "") -> str:
    """One listing/cover photo showing the whole set together - the main thumbnail
    buyers see on Etsy or TPT before they open the listing."""
    noun = "poses" if mode == MASCOT_MODE else NOUNS.get(mode, "items")
    listing = "\n".join(f"- {name}: {desc}" for name, desc in items)
    bg_line = f"BACKGROUND: {bg_desc}.\n" if bg_desc else ""
    bible_line = (f"CHARACTER (keep exactly as described): {character_bible}\n\n"
                  if character_bible else "")
    title_line = (
        f'Add the text "{title}" as a small, clean label near the top of the image.\n'
        if title.strip() else ""
    )
    return (
        f"Create ONE image that works as a single cover/preview photo for this set - the main "
        f"thumbnail a shopper sees before opening the listing.\n\n"
        f"{bible_line}"
        f"Arrange all {len(items)} {noun} below together in a tidy grid or flat-lay layout, each "
        f"one fully visible, evenly spaced, not overlapping or cropped.\n\n"
        f"ITEMS:\n{listing}\n\n"
        f"STYLE: {style_desc}.\n"
        f"{bg_line}"
        f"{title_line}"
        f"Keep every item in the same consistent style and proportion as the rest."
    )


# ----------------------------------------------------------------------------
# Mode suggestion. Plain keyword matching, no API call - keeps the whole tool
# zero-cost. It is a pointer, not a verdict: ties and near-misses are common,
# so the UI always lets the customer pick manually too.
# ----------------------------------------------------------------------------
MODE_KEYWORDS = {
    "Clipart set": ["template", "canva", "design", "plr", "graphic", "scrapbook",
                    "card making", "craft", "svg", "decorate", "diy", "resell", "mrr"],
    "Listing mockup scenes": ["pdf", "ebook", "e-book", "worksheet", "workbook", "course",
                               "guide", "listing", "etsy", "tpt", "digital download", "printable"],
    "Digital paper pack": ["pattern", "scrapbook", "card making", "background",
                            "paper craft", "digital paper"],
    "Planner stickers": ["planner", "goodnotes", "notability", "digital planner",
                          "bullet journal", "productivity", "sticker"],
    "Classroom decor set": ["classroom", "teacher", "bulletin board", "school",
                             "student", "teaching", "homeschool"],
    MASCOT_MODE: ["mascot", "character", "brand", "logo", "avatar", "consistent character"],
}

MODE_REASON = {
    "Clipart set": "fits products buyers use as raw material to build their own designs.",
    "Listing mockup scenes": "fits any finished digital download that needs a professional listing photo.",
    "Digital paper pack": "fits scrapbook, card-making, or craft-style products - usually paired with a clipart set.",
    "Planner stickers": "fits planner, productivity, or bullet-journal products.",
    "Classroom decor set": "fits classroom or homeschool-teaching products - the most TPT-native use case.",
    MASCOT_MODE: "fits a product that needs a consistent recurring character or brand mascot.",
}

# What picking this mode actually gets the buyer, in plain terms - shown so
# the person choosing a bonus can see the payoff, not just "this fits".
MODE_BENEFIT = {
    "Clipart set": ("Buyers get themed graphics they can drop straight into their own designs - "
                     "no design skill needed. Best when they'll keep customizing what they bought "
                     "(templates, workbooks, print-on-demand items)."),
    "Listing mockup scenes": ("Buyers get ready-made prompts to turn their own product pages into "
                               "professional Etsy or TPT listing photos. Most useful when they plan "
                               "to resell or list what they just bought (PLR, templates, planners)."),
    "Digital paper pack": ("Buyers get matching background patterns to pair with their own layouts "
                            "- a natural add-on for scrapbook, card-making, or paper-craft products, "
                            "not a strong standalone draw by itself."),
    "Planner stickers": ("Buyers get a themed sticker set to use inside their own planner or "
                          "productivity product - a direct companion to anything in the planner or "
                          "bullet-journal niche."),
    "Classroom decor set": ("Buyers get ready classroom decor - labels, banners, borders - that "
                             "matches their teaching materials. Strong fit when the core product is "
                             "itself used in a classroom or homeschool setting."),
    MASCOT_MODE: ("Buyers get one consistent character they can reuse across their own branding or "
                  "materials - useful when a recognizable recurring mascot adds value (a class "
                  "mascot, a shop mascot)."),
}


def suggest_modes(description: str):
    text = description.lower()
    scores = []
    for mode, keywords in MODE_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in text]
        if matched:
            scores.append((mode, len(matched), matched))
    scores.sort(key=lambda row: -row[1])
    return scores


def build_explain_prompt(description: str, mode: str) -> str:
    """The keyword matcher above only sees words, not what the product actually
    does - it can suggest a bonus that is secretly redundant with something the
    product already includes. This hands that judgement to ChatGPT, which can
    actually read the pasted description."""
    return (
        f"Here is a product description or sales page:\n\n"
        f"{description.strip()}\n\n"
        f'I am considering offering "{mode}" as a free bonus to buyers of this product. '
        f"{mode} {MODE_REASON[mode]}\n\n"
        f"In 2 to 3 sentences, explain specifically how this bonus would help someone who buys "
        f"the product described above. Be honest: if this bonus would be redundant with "
        f"something the product already includes, say so plainly instead of forcing a fit."
    )


# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------
if not check_password():
    st.stop()

st.title("\U0001F3A8 KDPEasy Clipart & Mockup Kit")
st.caption(
    "Type a theme, get a prompt for ChatGPT. Paste its reply back, get one ready-to-run "
    "image prompt per item."
)

use_mode = st.radio(
    "I'm building this to:",
    ["Sell as a product", "Use as a promo bonus"],
    horizontal=True,
)
if use_mode == "Use as a promo bonus":
    theme_label = "Product or niche you are promoting"
    theme_help = "The affiliate offer's theme - the set is built to match it, ready to hand out as a bonus."
else:
    theme_label = "Theme"
    theme_help = 'What the whole set is about. Keep it specific - "Cozy Autumn Harvest" beats "Fall".'

st.subheader("Not sure which type to use?")
promo_desc = st.text_area(
    "Describe what you're promoting (product name, niche, what it includes - "
    "pasting the whole sales page works too)",
    height=160,
    placeholder='e.g. "A PLR bundle of 50 Canva planner templates for busy moms"',
)
if st.button("Suggest a bonus type"):
    _stash("suggestions", promo_desc, suggest_modes(promo_desc))

suggestions = _recall("suggestions", promo_desc)
if suggestions is not None:
    if not suggestions:
        st.info(
            "No strong match found. \"Listing mockup scenes\" is the safest default - it fits "
            "almost any finished digital product. Pick a mode manually below if you have a "
            "more specific idea."
        )
    else:
        for i, (sugg_mode, score, matched) in enumerate(suggestions[:3]):
            col_text, col_btn = st.columns([4, 1])
            with col_text:
                st.markdown(f"**{i+1}. {sugg_mode}** - {MODE_REASON[sugg_mode]}")
                st.caption("Matched words: " + ", ".join(matched))
                st.markdown(f"_If you pick this: {MODE_BENEFIT[sugg_mode]}_")
                with st.expander("Explain this for my specific product (ask ChatGPT)"):
                    st.caption(
                        "The matching above only looks at words. Paste this into ChatGPT to "
                        "get a real answer for your product - including whether this bonus "
                        "would actually be redundant with something it already includes."
                    )
                    explain_prompt = build_explain_prompt(promo_desc, sugg_mode)
                    st.code(explain_prompt, language=None)
                    st.download_button(
                        "Download this prompt (.txt)", explain_prompt,
                        file_name=f"explain_{sugg_mode.lower().replace(' ', '_')}.txt",
                        key=f"dl_explain_{i}",
                    )
            with col_btn:
                if st.button("Use this", key=f"use_suggestion_{i}"):
                    st.session_state["mode_radio"] = sugg_mode
                    st.rerun()
    st.caption(
        "This is simple keyword matching, not real judgement - treat it as a starting point, "
        "not a final answer."
    )

st.divider()
mode = st.radio("What do you want to create?", MODES, key="mode_radio")

if mode == MASCOT_MODE:
    theme_label = "Character description"
    theme_help = ('Describe the character\'s fixed look: species, colors, outfit, any '
                  'accessories. Example: "a friendly orange fox with a round body, big eyes, '
                  'and a green knit scarf".')

with st.expander("How this kit works"):
    st.markdown(
        "1. Fill in the fields below and build the Step 1 prompt.\n"
        "2. Paste that prompt into ChatGPT. It replies with a numbered list.\n"
        "3. Paste that reply into Step 2. The kit turns every line into its own image prompt, "
        "already locked to one consistent style.\n"
        "4. Run each Step 2 prompt in the same ChatGPT chat so everything matches.\n"
        "5. Step 3 builds one more prompt: a single cover photo showing the whole set together "
        "- the main listing thumbnail for Etsy or TPT.\n\n"
        "**Clipart set** - isolated objects, transparent or white background.\n\n"
        "**Listing mockup scenes** - upload a real screenshot or page of your product first; "
        "each prompt places it into a styled scene for an Etsy or TPT listing photo. ChatGPT "
        "does not always keep the uploaded content perfectly untouched - check each result.\n\n"
        "**Digital paper pack** - seamless tileable background patterns, usually sold alongside "
        "a matching clipart set.\n\n"
        "**Planner stickers** - transparent die-cut-style stickers for digital or printed "
        "planners.\n\n"
        "**Classroom decor set** - bulletin board and labeling graphics, printed and laminated.\n\n"
        "**Mascot pose pack** - one consistent character in many poses, for a recurring brand "
        "or classroom mascot. Step 1 also writes a Character Bible that every pose reuses so "
        "the character does not drift.\n\n"
        "**About the Step 3 cover:** it draws a brand-new illustration of the whole set "
        "together, so it may look slightly different from the individual images from Step 2. "
        "It is a fast way to get a listing photo. For a pixel-exact thumbnail, arrange your "
        "finished Step 2 images yourself in Canva or a similar tool instead."
    )

tab1, tab2, tab3 = st.tabs(["Step 1 - Shot list", "Step 2 - Image prompts", "Step 3 - Collection cover"])

with tab1:
    theme = st.text_input(theme_label, help=theme_help)

    if mode == MASCOT_MODE:
        count = st.number_input("Number of poses", min_value=4, max_value=30, value=10)
        style_name = st.selectbox("Style", list(CLIPART_STYLES.keys()))
        style_desc = CLIPART_STYLES[style_name]
        bg_desc = BG_OPTIONS["Transparent"]
        st.caption("Background: transparent (fixed, so the character drops into anything).")
    else:
        cfg = MODE_UI[mode]
        count = st.number_input(cfg["count_label"], min_value=cfg["count_min"],
                                 max_value=cfg["count_max"], value=cfg["count_default"])
        style_name = st.selectbox("Style", list(cfg["styles"].keys()))
        style_desc = cfg["styles"][style_name]
        if cfg["bg"] == "choose":
            bg_name = st.selectbox("Background", list(BG_OPTIONS.keys()))
            bg_desc = BG_OPTIONS[bg_name]
        elif cfg["bg"] == "forced_transparent":
            bg_desc = BG_OPTIONS["Transparent"]
            st.caption("Background: transparent (fixed for stickers).")
        elif cfg["bg"] == "forced_white":
            bg_desc = BG_OPTIONS["Plain white"]
            st.caption("Background: plain white (fixed for easy cutting and laminating).")
        else:
            bg_desc = None

    sig1 = (mode, theme, count, style_name)
    if st.button("Build Step 1 prompt"):
        if not theme.strip():
            st.warning("Fill in the field above first.")
        elif mode == MASCOT_MODE:
            _stash("shotlist_prompt", sig1, build_mascot_shotlist_prompt(theme.strip(), int(count), style_desc))
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
        elif mode == MASCOT_MODE:
            bible = parse_mascot_bible(shotlist)
            if not bible:
                st.warning(
                    "Could not find the Character Bible block. Make sure the pasted text "
                    "still has the '=== CHARACTER BIBLE START/END ===' markers."
                )
            else:
                prompts = [build_mascot_pose_prompt(bible, n, d, style_desc) for n, d in items]
                _stash("item_prompts", sig2, list(zip([n for n, d in items], prompts)))
        elif mode == "Listing mockup scenes":
            prompts = [build_mockup_item_prompt(n, d, style_desc) for n, d in items]
            _stash("item_prompts", sig2, list(zip([n for n, d in items], prompts)))
        else:
            prompts = [build_item_prompt(mode, n, d, style_desc, bg_desc) for n, d in items]
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
            bible = parse_mascot_bible(shotlist) if mode == MASCOT_MODE else ""
            _stash(
                "cover_prompt", sig3,
                build_collection_cover_prompt(mode, cover_items, style_desc, bg_desc, cover_title, bible),
            )

    out3 = _recall("cover_prompt", sig3)
    if out3:
        st.code(out3, language=None)
        st.download_button("Download this prompt (.txt)", out3, file_name="step3_cover_prompt.txt")
    else:
        st.caption("Fill in Step 2's shot list first, then click \"Build collection cover prompt\".")

st.divider()
st.caption("KDPEasy Studio - kdpeasy.studio")
