# Setup
import json
import re
from json import JSONDecodeError
from pathlib import Path
import streamlit as st

# Page titles
st.set_page_config(page_title="Stardew Bundle Tracker", layout="wide")
st.title("Stardew Bundle Tracker")

# UI to filter items by seasons
ENABLE_FILTER = st.checkbox("Enable season filter", value=False)
SELECTED_SEASONS = []
if ENABLE_FILTER:
    SELECTED_SEASONS = st.multiselect(
        "Show items available in these seasons:",
        ["Spring", "Summer", "Fall", "Winter"],
        default=["Spring"]
    )
st.markdown("---")

DATA_PATH = Path("bundles.json")

# Loading data path
def load_data(path: Path):
    if not path.exists():
        st.error(f"Missing data file: {path.resolve()}")
        st.stop()
    try:
        text = path.read_text(encoding="utf-8")
    except (PermissionError, OSError) as err:
        st.error(f"Cannot read {path}: {err}")
        st.stop()

    try:
        return json.loads(text)
    except JSONDecodeError as err:
        st.error(f"{path.name} is not valid JSON: {err}")
        st.stop()

data = load_data(DATA_PATH)

# Helpers
def make_key(*parts):
    """Streamlit widget key."""
    joined = "__".join(str(p) for p in parts)
    return re.sub(r"\W+", "_", joined).strip("_").lower()

def bundle_progress_stats(bundle_obj):
    """
    Returns: (counted, required, possible, pct_float)
    - counted = min(collected, required)
    - required = bundle.required_count (fallback to possible)
    """
    items = bundle_obj.get("items", {}) if isinstance(bundle_obj, dict) else {}
    possible = len(items)
    collected = sum(1 for v in items.values() if v.get("collected"))
    try:
        required = int(bundle_obj.get("required_count", possible))
    except (TypeError, ValueError):
        required = possible
    required = max(required, 1)
    counted = min(collected, required)
    return counted, required, possible, counted / required

# UI for a single bundle
def display_bundle(room_name, bundle_name, bundle_obj, filter_enabled=False, selected_seasons=None):
    if not isinstance(bundle_obj, dict):
        st.warning(f"Missing data for {bundle_name}")
        return

    bundle_obj.setdefault("items", {})
    bundle_obj.setdefault("required_count", len(bundle_obj["items"]))
    st.subheader(bundle_name)

    # Placeholders so progress sits near the top but reflects latest checkbox states
    progress_ph = st.empty()
    text_ph = st.empty()

    # Build filtered list for UI (but progress uses all items)
    items_all = list(bundle_obj["items"].items())
    if filter_enabled and selected_seasons:
        # rename loop variables to avoid shadowing warnings
        items_ui = [
            (item_label, meta)
            for item_label, meta in items_all
            if any(season in meta.get("seasons", []) for season in selected_seasons)
        ]
    else:
        items_ui = items_all

    # Fixed item layout with a 4 column grid (image on top, with checkbox/name underneath)
    items_ui = list(items_ui)
    num_cols = 4
    for i in range(0, len(items_ui), num_cols):
        row_items = items_ui[i:i + num_cols]
        cols = st.columns(num_cols)
        for col, (item_label, item_meta) in zip(cols, row_items):
            with col:
                icon_path = item_meta.get("icon", "")
                if icon_path:
                    try:
                        st.image(icon_path, width=64)
                    except (OSError, RuntimeError):
                        st.write("image")
                # Display for source of item when hovered over
                tooltip = f"Source: {item_meta.get('source','Unknown')}"
                key = make_key(room_name, bundle_name, item_label)
                checked = st.checkbox(
                    item_label,
                    value=item_meta.get("collected", False),
                    help=tooltip,
                    key=key
                )
                item_meta["collected"] = bool(checked)

    # Progress after checkboxes
    counted, required, possible, pct = bundle_progress_stats(bundle_obj)
    progress_ph.progress(pct)
    text_ph.write(
        f"**Progress:** {counted}/{required} required (from {possible} possible) — {int(pct*100)}%"
    )
    st.markdown("---")


# Crafts Room
with st.expander("Crafts Room", expanded=True):
    crafts_room = data.get("Crafts Room", {})
    for name in [
        "Spring Foraging Bundle",
        "Summer Foraging Bundle",
        "Fall Foraging Bundle",
        "Winter Foraging Bundle",
        "Construction Bundle",
        "Exotic Foraging Bundle",
    ]:
        b = crafts_room.get(name)
        if b:
            display_bundle("Crafts Room", name, b,
                           filter_enabled=ENABLE_FILTER,
                           selected_seasons=SELECTED_SEASONS)

# Pantry
with st.expander("Pantry", expanded=True):
    pantry = data.get("Pantry", {})
    for name in [
        "Spring Crops Bundle",
        "Summer Crops Bundle",
        "Fall Crops Bundle",
        "Quality Crops Bundle",
        "Animal Bundle",
        "Artisan Bundle",
    ]:
        b = pantry.get(name)
        if b:
            display_bundle("Pantry", name, b,
                           filter_enabled=ENABLE_FILTER,
                           selected_seasons=SELECTED_SEASONS)

# Fish Tank
with st.expander("Fish Tank", expanded=True):
    fish_tank = data.get("Fish Tank", {})
    for name in [
        "River Fish Bundle",
        "Lake Fish Bundle",
        "Ocean Fish Bundle",
        "Night Fishing Bundle",
        "Crab Pot Bundle",
        "Specialty Fish Bundle",
    ]:
        b = fish_tank.get(name)
        if b:
            display_bundle("Fish Tank", name, b,
                           filter_enabled=ENABLE_FILTER,
                           selected_seasons=SELECTED_SEASONS)

# Boiler Room
with st.expander("Boiler Room", expanded=True):
    boiler_room = data.get("Boiler Room", {})
    for name in [
        "Blacksmith's Bundle",
        "Geologist's Bundle",
        "Adventurer's Bundle",
    ]:
        b = boiler_room.get(name)
        if b:
            display_bundle("Boiler Room", name, b,
                           filter_enabled=ENABLE_FILTER,
                           selected_seasons=SELECTED_SEASONS)

# Bulletin Board
with st.expander("Bulletin Board", expanded=True):
    bulletin = data.get("Bulletin Board", {})
    for name in [
        "Dye Bundle",
        "Field Research Bundle",
        "Fodder Bundle",
        "Enchanter's Bundle",
    ]:
        b = bulletin.get(name)
        if b:
            display_bundle("Bulletin Board", name, b,
                           filter_enabled=ENABLE_FILTER,
                           selected_seasons=SELECTED_SEASONS)

# Vault
with st.expander("Vault", expanded=True):
    vault = data.get("Vault", {})
    for name in [
        "2500 Bundle",
        "5000 Bundle",
        "10000 Bundle",
        "25000 Bundle",
    ]:
        b = vault.get(name)
        if b:
            display_bundle("Vault", name, b,
                           filter_enabled=ENABLE_FILTER,
                           selected_seasons=SELECTED_SEASONS)


# Save
st.markdown("---")
if st.button("💾 Save progress"):
    try:
        DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        st.success("Progress saved to bundles.json")
    except Exception as e:
        st.error(f"Failed to save: {e}")
