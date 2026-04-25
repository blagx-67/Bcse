#  Battle Cats Save Editor

A powerful, community-built save file editor for **The Battle Cats** (にゃんこ大戦争). Edit your save file to add cat food, tickets, catseyes, unlock units, complete stages, and much more.

> **Disclaimer**: This tool is for personal, educational use only. Use at your own risk. Always back up your save file before editing. This project is not affiliated with PONOS Corporation.

---

## Features

| Feature | Description |
|---|---|
| **Cat Food** | Set any amount of cat food |
| **Tickets** | Rare tickets, platinum tickets, event tickets |
| **XP** | Set your current XP amount |
| **Units** | Unlock cats, set levels & plus levels |
| **Stages** | Mark any stage as cleared |
| **Catseyes** | Add basic, special, rare, super rare, uber & legend catseyes |
| **Leadership** | Edit leadership points |
| **Platinum Shards** | Edit platinum shard count |

---

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Quick Start

### CLI Mode

```bash
# Run the interactive CLI editor
python main.py

# Or load a save file directly
python main.py --save path/to/SAVE_DATA

# Apply a specific edit
python main.py --save SAVE_DATA --catfood 99999
python main.py --save SAVE_DATA --tickets rare=99 platinum=10
python main.py --save SAVE_DATA --xp 9999999
```

### GUI Mode

```bash
python main.py --gui
```

---

## Project Structure

```
battle-cats-save-editor/
├── main.py                  # Entry point (CLI + GUI launcher)
├── requirements.txt
├── .gitignore
│
├── editor/
│   ├── __init__.py
│   ├── save_file.py         # Core save file loader/saver
│   ├── crypto.py            # AES decryption/encryption
│   ├── resources.py         # Cat food, tickets, XP editor
│   ├── units.py             # Cat unit unlock/level editor
│   ├── stages.py            # Stage completion editor
│   └── catseyes.py          # Catseye resource editor
│
├── data/
│   ├── units.json           # All cat unit IDs and names
│   ├── stages.json          # All stage IDs and names
│   └── offsets.json         # Save file byte offsets by version
│
├── gui/
│   ├── __init__.py
│   └── app.py               # Tkinter GUI application
│
└── tests/
    ├── test_crypto.py
    ├── test_resources.py
    └── test_units.py
```

---

## How It Works

Battle Cats saves your progress in a binary file called `SAVE_DATA`. On Android this is located at:

```
/data/data/jp.co.ponos.battlecatsen/files/SAVE_DATA
```

On iOS it can be extracted via iTunes backup or jailbreak tools.

The save file is **AES-128 encrypted** in CBC mode. This editor:
1. Decrypts the save file
2. Parses the binary data using known byte offsets
3. Applies your edits
4. Re-encrypts and writes the modified file

---

## Usage Examples

### Python API

```python
from editor.save_file import SaveFile
from editor.resources import ResourceEditor
from editor.units import UnitEditor
from editor.stages import StageEditor
from editor.catseyes import CatseyeEditor

# Load save
save = SaveFile("SAVE_DATA")
save.decrypt()

# Edit resources
res = ResourceEditor(save)
res.set_catfood(99999)
res.set_xp(9999999)
res.set_rare_tickets(99)
res.set_platinum_tickets(10)
res.set_leadership(9999)

# Edit catseyes
eyes = CatseyeEditor(save)
eyes.set_basic_catseyes(99)
eyes.set_rare_catseyes(99)
eyes.set_super_rare_catseyes(99)
eyes.set_uber_rare_catseyes(99)
eyes.set_legend_rare_catseyes(99)

# Unlock and level up a cat
units = UnitEditor(save)
units.unlock_cat(cat_id=25)          # e.g., Bahamut Cat
units.set_cat_level(cat_id=25, level=30, plus_level=90)
units.unlock_all_basic_cats()

# Complete stages
stages = StageEditor(save)
stages.complete_stage(chapter=1, stage_id=47)   # ITF Ch1 Moon
stages.complete_all_empire_of_cats()
stages.complete_all_into_the_future()

# Save
save.encrypt()
save.write("SAVE_DATA_EDITED")
print("Save file written!")
```

---

## Cat IDs (Examples)

| ID | Cat Name |
|---|---|
| 0 | Cat |
| 1 | Tank Cat |
| 2 | Axe Cat |
| 25 | Bahamut Cat |
| 36 | Valkyrie Cat |
| ... | See `data/units.json` for full list |

---

##  Stage IDs

Stages are organized by chapter and map:

- `chapter=0` → Empire of Cats
- `chapter=1` → Into the Future
- `chapter=2` → Cats of the Cosmos
- `chapter=3+` → Stories of Legend / Collaboration stages

---

## Known Limitations

- Save file format may differ between **JP**, **EN**, **KR**, and **TW** versions
- Game version updates may shift byte offsets — check `data/offsets.json`
- Editing cat levels beyond what's normally achievable may cause crashes
- Some stage flags are interdependent (you may need to clear prerequisite stages)

---

##  Contributing

PRs are welcome! If you've found a new offset or want to add a feature:

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Credits

- Battle Cats community on Reddit ([r/battlecats](https://reddit.com/r/battlecats)) for save format research
- PONOS Corporation for making a fantastic game
ddit ([r/battlecats](https://reddit.com/r/battlecats)) for save format research
- PONOS Corporation for making a fantastic game
