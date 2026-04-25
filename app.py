"""
gui/app.py
----------
Tkinter-based GUI for the Battle Cats Save Editor.
Launch with: python main.py --gui
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


class SaveEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐱 Battle Cats Save Editor")
        self.resizable(True, True)
        self.configure(bg="#1a1a2e")
        self.minsize(750, 600)

        self._save = None
        self._res = None
        self._eyes = None
        self._units = None
        self._stages = None

        self._build_ui()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg="#16213e", pady=12)
        hdr.pack(fill="x")
        tk.Label(
            hdr, text="🐱  Battle Cats Save Editor",
            font=("Courier", 18, "bold"),
            fg="#e94560", bg="#16213e",
        ).pack()
        tk.Label(
            hdr, text="v1.0.0  |  Always back up your save first!",
            font=("Courier", 9), fg="#888", bg="#16213e",
        ).pack()

        # ── File loader ──
        file_frame = tk.Frame(self, bg="#1a1a2e", pady=8, padx=16)
        file_frame.pack(fill="x")

        tk.Label(file_frame, text="Save File:", fg="#ccc", bg="#1a1a2e",
                 font=("Courier", 10)).grid(row=0, column=0, sticky="w")

        self._save_path_var = tk.StringVar(value="No file loaded")
        tk.Label(file_frame, textvariable=self._save_path_var,
                 fg="#4ec9b0", bg="#1a1a2e", font=("Courier", 10),
                 wraplength=500, justify="left").grid(row=0, column=1, sticky="w", padx=8)

        self._region_var = tk.StringVar(value="en")
        region_menu = ttk.Combobox(file_frame, textvariable=self._region_var,
                                   values=["en","jp","kr","tw"], width=5, state="readonly")
        region_menu.grid(row=0, column=2, padx=4)

        btn_style = {"font": ("Courier", 9, "bold"), "relief": "flat",
                     "padx": 10, "pady": 4, "cursor": "hand2"}
        tk.Button(file_frame, text="📂 Browse", bg="#0f3460", fg="white",
                  command=self._browse_save, **btn_style).grid(row=0, column=3, padx=4)
        tk.Button(file_frame, text="🔓 Load & Decrypt", bg="#533483", fg="white",
                  command=self._load_save, **btn_style).grid(row=0, column=4, padx=4)
        tk.Button(file_frame, text="💾 Save", bg="#1b6ca8", fg="white",
                  command=self._save_file, **btn_style).grid(row=0, column=5, padx=4)

        # ── Tabs ──
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#16213e", foreground="#ccc",
                        font=("Courier", 10, "bold"), padding=(12, 6))
        style.map("TNotebook.Tab", background=[("selected","#0f3460")],
                  foreground=[("selected","#e94560")])

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        self._tab_resources(tabs)
        self._tab_catseyes(tabs)
        self._tab_units(tabs)
        self._tab_stages(tabs)

        # ── Status bar ──
        self._status_var = tk.StringVar(value="Ready. Load a save file to begin.")
        tk.Label(self, textvariable=self._status_var, fg="#4ec9b0",
                 bg="#16213e", font=("Courier", 9), anchor="w",
                 pady=4, padx=16).pack(fill="x", side="bottom")

    def _tab_resources(self, nb):
        frame = self._make_tab(nb, "🍖 Resources")
        FIELDS = [
            ("Cat Food",         "catfood",          99999),
            ("XP",               "xp",               9999999),
            ("Rare Tickets",     "rare_tickets",      9999),
            ("Platinum Tickets", "platinum_tickets",  999),
            ("Leadership",       "leadership",        9999),
            ("Platinum Shards",  "platinum_shards",   9999),
            ("Cat Energy",       "cat_energy",        999),
        ]
        self._res_vars = {}
        for i, (label, key, max_val) in enumerate(FIELDS):
            tk.Label(frame, text=label+":", fg="#ccc", bg="#16213e",
                     font=("Courier", 10), anchor="e", width=20).grid(
                row=i, column=0, sticky="e", padx=8, pady=6)
            var = tk.StringVar(value="—")
            self._res_vars[key] = var
            tk.Entry(frame, textvariable=var, width=14,
                     bg="#0f3460", fg="white", insertbackground="white",
                     font=("Courier", 11), relief="flat").grid(
                row=i, column=1, sticky="w", padx=4)
            tk.Label(frame, text=f"max {max_val:,}", fg="#555",
                     bg="#16213e", font=("Courier", 8)).grid(
                row=i, column=2, sticky="w", padx=4)

        tk.Button(frame, text="✅ Apply Resources", bg="#e94560", fg="white",
                  font=("Courier", 10, "bold"), relief="flat", padx=12, pady=6,
                  command=self._apply_resources, cursor="hand2").grid(
            row=len(FIELDS)+1, column=0, columnspan=3, pady=16)

    def _tab_catseyes(self, nb):
        frame = self._make_tab(nb, "👁 Catseyes")
        RARITIES = [
            ("🔵 Basic",       "basic"),
            ("🟢 Special",     "special"),
            ("🟡 Rare",        "rare"),
            ("🟠 Super Rare",  "super_rare"),
            ("🔴 Uber Rare",   "uber_rare"),
            ("🌈 Legend Rare", "legend_rare"),
        ]
        self._eye_vars = {}
        for i, (label, key) in enumerate(RARITIES):
            tk.Label(frame, text=label+":", fg="#ccc", bg="#16213e",
                     font=("Courier", 10), anchor="e", width=18).grid(
                row=i, column=0, sticky="e", padx=8, pady=6)
            var = tk.StringVar(value="—")
            self._eye_vars[key] = var
            tk.Entry(frame, textvariable=var, width=10,
                     bg="#0f3460", fg="white", insertbackground="white",
                     font=("Courier", 11), relief="flat").grid(
                row=i, column=1, sticky="w", padx=4)

        tk.Button(frame, text="✅ Apply Catseyes", bg="#e94560", fg="white",
                  font=("Courier", 10, "bold"), relief="flat", padx=12, pady=6,
                  command=self._apply_catseyes, cursor="hand2").grid(
            row=len(RARITIES)+1, column=0, columnspan=2, pady=16)
        tk.Button(frame, text="🌈 Max All", bg="#533483", fg="white",
                  font=("Courier", 10, "bold"), relief="flat", padx=12, pady=6,
                  command=self._max_catseyes, cursor="hand2").grid(
            row=len(RARITIES)+2, column=0, columnspan=2, pady=4)

    def _tab_units(self, nb):
        frame = self._make_tab(nb, "🐱 Units")
        # Row 0: unlock by ID
        tk.Label(frame, text="Cat ID to unlock:", fg="#ccc", bg="#16213e",
                 font=("Courier", 10)).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self._unlock_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self._unlock_id_var, width=8,
                 bg="#0f3460", fg="white", insertbackground="white",
                 font=("Courier", 11), relief="flat").grid(row=0, column=1, sticky="w")
        tk.Button(frame, text="Unlock", bg="#1b6ca8", fg="white",
                  font=("Courier", 9, "bold"), relief="flat", padx=8, pady=3,
                  command=self._unlock_cat_by_id, cursor="hand2").grid(row=0, column=2, padx=8)

        # Row 1: level
        tk.Label(frame, text="Set level (ID):", fg="#ccc", bg="#16213e",
                 font=("Courier", 10)).grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self._level_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self._level_id_var, width=8,
                 bg="#0f3460", fg="white", insertbackground="white",
                 font=("Courier", 11), relief="flat").grid(row=1, column=1, sticky="w")
        self._level_lv_var = tk.StringVar(value="30")
        tk.Entry(frame, textvariable=self._level_lv_var, width=5,
                 bg="#0f3460", fg="white", insertbackground="white",
                 font=("Courier", 11), relief="flat").grid(row=1, column=2)
        tk.Label(frame, text="+", fg="#ccc", bg="#16213e",
                 font=("Courier", 10)).grid(row=1, column=3)
        self._level_plus_var = tk.StringVar(value="90")
        tk.Entry(frame, textvariable=self._level_plus_var, width=5,
                 bg="#0f3460", fg="white", insertbackground="white",
                 font=("Courier", 11), relief="flat").grid(row=1, column=4)
        tk.Button(frame, text="Set Level", bg="#1b6ca8", fg="white",
                  font=("Courier", 9, "bold"), relief="flat", padx=8, pady=3,
                  command=self._set_cat_level, cursor="hand2").grid(row=1, column=5, padx=8)

        sep = ttk.Separator(frame, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=6, sticky="ew", pady=12)

        # Bulk operations
        bulk_ops = [
            ("🐱 Unlock All Basic Cats",  self._unlock_basic),
            ("⬆️  Max All Unlocked Cats",  self._max_all_unlocked),
        ]
        for i, (label, cmd) in enumerate(bulk_ops):
            tk.Button(frame, text=label, bg="#0f3460", fg="white",
                      font=("Courier", 10, "bold"), relief="flat", padx=14, pady=8,
                      command=cmd, cursor="hand2").grid(
                row=3+i, column=0, columnspan=3, sticky="w", padx=8, pady=4)

    def _tab_stages(self, nb):
        frame = self._make_tab(nb, "🗺 Stages")
        ops = [
            ("Complete All Empire of Cats",      lambda: self._stages_op("eoc")),
            ("Complete All Into the Future",     lambda: self._stages_op("itf")),
            ("Complete All Cats of the Cosmos",  lambda: self._stages_op("cotc")),
            ("Complete All Stories of Legend",   lambda: self._stages_op("sol")),
            ("Complete ALL Story Chapters 🎉",   lambda: self._stages_op("all")),
        ]
        for i, (label, cmd) in enumerate(ops):
            tk.Button(frame, text=label, bg="#0f3460", fg="white",
                      font=("Courier", 10, "bold"), relief="flat", padx=14, pady=10,
                      command=cmd, cursor="hand2", width=40).pack(pady=6)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _make_tab(self, nb, label):
        outer = tk.Frame(nb, bg="#16213e")
        nb.add(outer, text=label)
        inner = tk.Frame(outer, bg="#16213e", padx=24, pady=20)
        inner.pack(fill="both", expand=True)
        return inner

    def _require_save(self) -> bool:
        if self._save is None:
            messagebox.showwarning("No save loaded", "Please load a save file first.")
            return False
        return True

    def _browse_save(self):
        path = filedialog.askopenfilename(title="Select SAVE_DATA file")
        if path:
            self._save_path_var.set(path)

    def _load_save(self):
        from editor.save_file import SaveFile
        from editor.resources import ResourceEditor
        from editor.catseyes import CatseyeEditor
        from editor.units import UnitEditor
        from editor.stages import StageEditor

        path = self._save_path_var.get()
        if not path or path == "No file loaded":
            messagebox.showwarning("No file", "Please select a SAVE_DATA file first.")
            return
        try:
            self._save   = SaveFile(path, region=self._region_var.get())
            self._save.decrypt()
            self._res    = ResourceEditor(self._save)
            self._eyes   = CatseyeEditor(self._save)
            self._units  = UnitEditor(self._save)
            self._stages = StageEditor(self._save)
            self._populate_fields()
            self._status("✅ Save loaded and decrypted successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _populate_fields(self):
        """Fill UI fields with current save values."""
        if not self._res:
            return
        for key, var in self._res_vars.items():
            try:
                var.set(str(getattr(self._res, f"get_{key}")()))
            except Exception:
                pass
        for key, var in self._eye_vars.items():
            try:
                var.set(str(self._eyes.get(key)))
            except Exception:
                pass

    def _apply_resources(self):
        if not self._require_save(): return
        try:
            for key, var in self._res_vars.items():
                val = var.get().strip()
                if val and val != "—":
                    getattr(self._res, f"set_{key}")(int(val))
            self._status("✅ Resources applied.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_catseyes(self):
        if not self._require_save(): return
        try:
            for key, var in self._eye_vars.items():
                val = var.get().strip()
                if val and val != "—":
                    self._eyes.set(key, int(val))
            self._status("✅ Catseyes applied.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _max_catseyes(self):
        if not self._require_save(): return
        self._eyes.max_all()
        self._populate_fields()
        self._status("🌈 All catseyes maxed!")

    def _unlock_cat_by_id(self):
        if not self._require_save(): return
        try:
            self._units.unlock_cat(int(self._unlock_id_var.get()))
            self._status(f"✅ Cat {self._unlock_id_var.get()} unlocked.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _set_cat_level(self):
        if not self._require_save(): return
        try:
            self._units.set_cat_level(
                int(self._level_id_var.get()),
                int(self._level_lv_var.get()),
                int(self._level_plus_var.get()),
            )
            self._status(f"✅ Cat level set.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _unlock_basic(self):
        if not self._require_save(): return
        self._units.unlock_all_basic_cats()
        self._status("🐱 All basic cats unlocked!")

    def _max_all_unlocked(self):
        if not self._require_save(): return
        self._units.max_all_unlocked()
        self._status("⬆️ All unlocked cats maxed!")

    def _stages_op(self, op: str):
        if not self._require_save(): return
        ops = {
            "eoc":  self._stages.complete_all_empire_of_cats,
            "itf":  self._stages.complete_all_into_the_future,
            "cotc": self._stages.complete_all_cats_of_the_cosmos,
            "sol":  lambda: self._stages.complete_all_stories_of_legend(stars=1),
            "all":  self._stages.complete_all,
        }
        ops[op]()
        self._status("✅ Stages completed!")

    def _save_file(self):
        if not self._require_save(): return
        path = filedialog.asksaveasfilename(
            title="Save edited file",
            initialfile="SAVE_DATA_EDITED",
        )
        if not path:
            return
        try:
            self._save.encrypt()
            self._save.write(path)
            self._status(f"💾 Saved to: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _status(self, msg: str):
        self._status_var.set(msg)
        self.update_idletasks()


def launch_gui():
    app = SaveEditorApp()
    app.mainloop()
