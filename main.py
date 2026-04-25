#!/usr/bin/env python3
"""
main.py
-------
Battle Cats Save Editor — entry point.

Usage:
  python main.py                         # Interactive CLI menu
  python main.py --gui                   # Launch GUI
  python main.py --save SAVE_DATA        # Load a specific save file
  python main.py --save SAVE_DATA --catfood 99999
  python main.py --save SAVE_DATA --maxall
"""

import argparse
import sys
import os

# ── Colorama for cross-platform color ─────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    C = {
        "title":   Fore.CYAN + Style.BRIGHT,
        "ok":      Fore.GREEN,
        "warn":    Fore.YELLOW,
        "err":     Fore.RED,
        "reset":   Style.RESET_ALL,
        "bold":    Style.BRIGHT,
        "cat":     Fore.MAGENTA + Style.BRIGHT,
    }
except ImportError:
    C = {k: "" for k in ("title","ok","warn","err","reset","bold","cat")}


BANNER = f"""
{C['cat']}
  ██████╗  █████╗ ████████╗████████╗██╗     ███████╗
  ██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝██║     ██╔════╝
  ██████╔╝███████║   ██║      ██║   ██║     █████╗  
  ██╔══██╗██╔══██║   ██║      ██║   ██║     ██╔══╝  
  ██████╔╝██║  ██║   ██║      ██║   ███████╗███████╗
  ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝
  {C['title']}CATS  SAVE  EDITOR  🐱  v1.0.0{C['reset']}
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Battle Cats Save File Editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--save", metavar="PATH", help="Path to SAVE_DATA file")
    p.add_argument("--region", default="en", choices=["en","jp","kr","tw"],
                   help="Game region (default: en)")
    p.add_argument("--gui", action="store_true", help="Launch GUI mode")
    p.add_argument("--output", metavar="PATH", help="Output path (default: overwrites input)")

    # Quick edit flags
    edit = p.add_argument_group("Quick Edits")
    edit.add_argument("--catfood", type=int, metavar="N")
    edit.add_argument("--xp", type=int, metavar="N")
    edit.add_argument("--rare-tickets", type=int, metavar="N")
    edit.add_argument("--platinum-tickets", type=int, metavar="N")
    edit.add_argument("--leadership", type=int, metavar="N")
    edit.add_argument("--catseyes", metavar="RARITY=N",
                      help="e.g. --catseyes uber_rare=99")
    edit.add_argument("--unlock-cat", type=int, metavar="ID",
                      help="Unlock a cat by ID")
    edit.add_argument("--max-cat", type=int, metavar="ID",
                      help="Max level a cat by ID")
    edit.add_argument("--complete-all-eoc", action="store_true")
    edit.add_argument("--complete-all-itf", action="store_true")
    edit.add_argument("--complete-all-cotc", action="store_true")
    edit.add_argument("--maxall", action="store_true",
                      help="Max all resources, catseyes, and unlock all basic cats")
    return p


def run_cli_args(save_path: str, args, region: str):
    """Apply edits specified via command-line flags."""
    from editor.save_file import SaveFile
    from editor.resources import ResourceEditor
    from editor.catseyes import CatseyeEditor
    from editor.units import UnitEditor
    from editor.stages import StageEditor

    save = SaveFile(save_path, region=region)
    save.decrypt()

    res = ResourceEditor(save)
    eyes = CatseyeEditor(save)
    units = UnitEditor(save)
    stages = StageEditor(save)

    changed = False

    if args.maxall:
        res.max_resources()
        eyes.max_all()
        units.unlock_all_basic_cats()
        changed = True

    if args.catfood is not None:
        res.set_catfood(args.catfood); changed = True
    if args.xp is not None:
        res.set_xp(args.xp); changed = True
    if args.rare_tickets is not None:
        res.set_rare_tickets(args.rare_tickets); changed = True
    if args.platinum_tickets is not None:
        res.set_platinum_tickets(args.platinum_tickets); changed = True
    if args.leadership is not None:
        res.set_leadership(args.leadership); changed = True

    if args.catseyes:
        rarity, _, val = args.catseyes.partition("=")
        eyes.set(rarity.strip(), int(val.strip())); changed = True

    if args.unlock_cat is not None:
        units.unlock_cat(args.unlock_cat); changed = True
    if args.max_cat is not None:
        units.max_cat_level(args.max_cat); changed = True

    if args.complete_all_eoc:
        stages.complete_all_empire_of_cats(); changed = True
    if args.complete_all_itf:
        stages.complete_all_into_the_future(); changed = True
    if args.complete_all_cotc:
        stages.complete_all_cats_of_the_cosmos(); changed = True

    if changed:
        save.encrypt()
        save.write(args.output or save_path)
    else:
        print(f"{C['warn']}No edits specified. Run without flags for interactive mode.{C['reset']}")


def run_interactive(save_path: str, region: str):
    """Full interactive CLI menu."""
    from editor.save_file import SaveFile
    from editor.resources import ResourceEditor
    from editor.catseyes import CatseyeEditor
    from editor.units import UnitEditor
    from editor.stages import StageEditor

    print(BANNER)
    save = SaveFile(save_path, region=region)
    save.decrypt()

    res   = ResourceEditor(save)
    eyes  = CatseyeEditor(save)
    units = UnitEditor(save)
    stages = StageEditor(save)

    MENU = f"""
{C['bold']}┌─────────────────────────────────┐
│       What do you want to edit? │
├─────────────────────────────────┤
│  [1] Resources (cat food, XP…)  │
│  [2] Tickets                    │
│  [3] Catseyes                   │
│  [4] Units / Cats               │
│  [5] Stages                     │
│  [6] Battle Items               │
│  [7] Show current summary       │
│  [8] MAX EVERYTHING 🐱          │
│  [9] Save & exit                │
│  [0] Exit WITHOUT saving        │
└─────────────────────────────────┘{C['reset']}
"""

    modified = False

    while True:
        print(MENU)
        choice = input("  › ").strip()

        if choice == "1":
            print("\n" + res.summary())
            cf = input("  New cat food (blank=skip): ").strip()
            if cf: res.set_catfood(int(cf)); modified = True
            xp = input("  New XP (blank=skip): ").strip()
            if xp: res.set_xp(int(xp)); modified = True
            lead = input("  New leadership (blank=skip): ").strip()
            if lead: res.set_leadership(int(lead)); modified = True

        elif choice == "2":
            print(f"\n  Rare tickets: {res.get_rare_tickets()}")
            print(f"  Platinum tickets: {res.get_platinum_tickets()}")
            rt = input("  New rare tickets (blank=skip): ").strip()
            if rt: res.set_rare_tickets(int(rt)); modified = True
            pt = input("  New platinum tickets (blank=skip): ").strip()
            if pt: res.set_platinum_tickets(int(pt)); modified = True

        elif choice == "3":
            print("\n" + eyes.summary())
            for rarity in ["basic","special","rare","super_rare","uber_rare","legend_rare"]:
                val = input(f"  {rarity} catseyes (blank=skip): ").strip()
                if val: eyes.set(rarity, int(val)); modified = True

        elif choice == "4":
            sub = input(
                "\n  [a] Unlock cat by ID\n"
                "  [b] Set cat level\n"
                "  [c] Unlock all basic cats\n"
                "  [d] Unlock all cats\n"
                "  [e] Max all unlocked cats\n"
                "  › "
            ).strip().lower()
            if sub == "a":
                cid = int(input("  Cat ID: "))
                units.unlock_cat(cid); modified = True
            elif sub == "b":
                cid = int(input("  Cat ID: "))
                lv  = int(input("  Level (1–30): "))
                plus= int(input("  Plus level (0–90): ") or "0")
                units.set_cat_level(cid, lv, plus); modified = True
            elif sub == "c":
                units.unlock_all_basic_cats(); modified = True
            elif sub == "d":
                confirm = input("  ⚠️  Unlock ALL cats? [y/N] ").strip().lower()
                if confirm == "y":
                    units.unlock_all_cats(); modified = True
            elif sub == "e":
                units.max_all_unlocked(); modified = True

        elif choice == "5":
            sub = input(
                "\n  [1] Complete all EoC\n"
                "  [2] Complete all ItF\n"
                "  [3] Complete all CotC\n"
                "  [4] Complete all SoL (1★)\n"
                "  [5] Complete ALL\n"
                "  [6] Complete specific stage\n"
                "  › "
            ).strip()
            if sub == "1": stages.complete_all_empire_of_cats(); modified = True
            elif sub == "2": stages.complete_all_into_the_future(); modified = True
            elif sub == "3": stages.complete_all_cats_of_the_cosmos(); modified = True
            elif sub == "4": stages.complete_all_stories_of_legend(stars=1); modified = True
            elif sub == "5": stages.complete_all(); modified = True
            elif sub == "6":
                chapter = input("  Chapter (empire_of_cats/into_the_future/cats_of_the_cosmos): ")
                sub_ch  = int(input("  Sub-chapter (0/1/2): "))
                stage   = int(input("  Stage ID (0-based): "))
                stages._complete(chapter, sub_ch, stage); modified = True

        elif choice == "6":
            from editor.resources import BATTLE_ITEM_NAMES
            for i, name in enumerate(BATTLE_ITEM_NAMES):
                cur = res.get_battle_item(i)
                val = input(f"  {name} (current: {cur}, blank=skip): ").strip()
                if val: res.set_battle_item(i, int(val)); modified = True

        elif choice == "7":
            print("\n" + res.summary())
            print(eyes.summary())
            print(stages.summary())

        elif choice == "8":
            res.max_resources()
            eyes.max_all()
            units.unlock_all_basic_cats()
            modified = True
            print(f"\n{C['ok']}🎉 Everything maxed!{C['reset']}")

        elif choice == "9":
            if modified:
                out = input(f"  Output path (blank=overwrite {save_path}): ").strip()
                save.encrypt()
                save.write(out or save_path)
            else:
                print("  No changes made.")
            sys.exit(0)

        elif choice == "0":
            print(f"{C['warn']}Exiting without saving.{C['reset']}")
            sys.exit(0)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.gui:
        from gui.app import launch_gui
        launch_gui()
        return

    if args.save is None:
        # Prompt for a save file path
        print(BANNER)
        args.save = input("  Enter path to SAVE_DATA file: ").strip()
        if not args.save:
            parser.print_help()
            sys.exit(1)

    # Check if any quick-edit flags were provided
    quick_flags = [
        args.catfood, args.xp, args.rare_tickets, args.platinum_tickets,
        args.leadership, args.catseyes, args.unlock_cat, args.max_cat,
        args.complete_all_eoc, args.complete_all_itf, args.complete_all_cotc,
        args.maxall,
    ]

    if any(f is not None and f is not False for f in quick_flags):
        run_cli_args(args.save, args, region=args.region)
    else:
        run_interactive(args.save, region=args.region)


if __name__ == "__main__":
    main()
