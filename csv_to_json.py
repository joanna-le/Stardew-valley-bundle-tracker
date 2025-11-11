import csv
import json

# Helper functions
def str_to_bool(s):
    if s is None:
        return False
    s = str(s).strip().lower()
    return s in ("1", "true", "yes", "y", "t")

def parse_seasons(s):
    if not s:
        return []
    return [part.strip() for part in s.split(",") if part.strip()]

# Conversion function
def csv_to_nested_json(csv_file, json_file):
    data = {}

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Check that required columns exist
        required_cols = {"Area", "Bundle Name", "Item Name", "Seasons", "Source", "Collected", "Image Path", "Required Count"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        for row in reader:
            room = row["Area"].strip()
            bundle = row["Bundle Name"].strip()
            item = row["Item Name"].strip()

            # Read required count
            required_count_raw = row.get("Required Count", "").strip()
            try:
                required_count = int(required_count_raw) if required_count_raw else None
            except ValueError:
                required_count = None

            seasons = parse_seasons(row.get("Seasons", ""))
            source = row.get("Source", "").strip()
            icon = row.get("Image Path", "").strip()
            collected = str_to_bool(row.get("Collected", "False"))

            # Build JSON hierarchy
            room_data = data.setdefault(room, {})
            bundle_data = room_data.setdefault(bundle, {"items": {}, "required_count": required_count})

            # If we see a required_count again for the same bundle, only set if missing
            if bundle_data.get("required_count") is None and required_count is not None:
                bundle_data["required_count"] = required_count

            bundle_data["items"][item] = {
                "collected": collected,
                "seasons": seasons,
                "source": source,
                "icon": icon
            }

    # Write JSON file
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully created '{json_file}' from '{csv_file}'")

# Run the converter
if __name__ == "__main__":
    csv_to_nested_json("bundles.csv", "bundles.json")

