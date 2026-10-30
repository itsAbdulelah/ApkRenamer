import os
import sys
import ctypes
import random
import string
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

import arabic_reshaper
from bidi.algorithm import get_display

try:
    from .runner import ApkRenamerRunner, check_java, get_core_dir
except ImportError:
    from runner import ApkRenamerRunner, check_java, get_core_dir


def load_bundled_fonts():
    """Register bundled fonts (e.g. Tajawal) into Windows GDI dynamically at runtime."""
    if sys.platform != "win32":
        return
    candidates = []
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "assets", "fonts"))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "assets", "fonts"))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(script_dir, "..", "assets", "fonts"))
    candidates.append(os.path.join(script_dir, "assets", "fonts"))

    FR_PRIVATE = 0x10
    for c in candidates:
        if os.path.isdir(c):
            for f in os.listdir(c):
                if f.lower().endswith((".ttf", ".otf")):
                    font_path = os.path.abspath(os.path.join(c, f))
                    try:
                        ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
                    except Exception:
                        pass
            break


# Load bundled fonts immediately on import
load_bundled_fonts()
APP_FONT = "Tajawal"


def get_font(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    """Helper to return Tajawal font consistently across the UI."""
    return ctk.CTkFont(family=APP_FONT, size=size, weight=weight)


def bidi_text(text: str) -> str:
    """Reshape and reorder Arabic text for LTR GUI engines (Tkinter/CustomTkinter).
    Ensures that sentences like 'ملف التطبيق الأساسي:' render in natural right-to-left
    word order rather than reversed 'الأساسي التطبيق ملف'.
    """
    if not text:
        return text
    if any("\u0600" <= c <= "\u06FF" for c in text):
        try:
            configuration = {
                "delete_harakat": False,
                "support_ligatures": True,
            }
            reshaper = arabic_reshaper.ArabicReshaper(configuration=configuration)
            reshaped = reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    return text


TRANSLATIONS = {
    "ar": {
        "app_title": "استوديو تعديل وتكرار التطبيقات",
        "app_subtitle": "تعديل، استنساخ، وتوقيع تطبيقات أندرويد بسهولة وبأعلى كفاءة",
        "config_card": "إعدادات وبيانات التطبيق",
        "src_apk": "ملف التطبيق الأساسي (APK):",
        "src_apk_ph": "اختر ملف التطبيق المراد تعديله (.apk)...",
        "out_apk": "مسار حفظ التطبيق الجديد (APK):",
        "out_apk_ph": "مسار وتسمية الملف المعدل الجديد...",
        "app_name": "اسم التطبيق الجديد:",
        "app_name_ph": "مثال: تطبيقي المعدل (أو اتركه فارغاً لعدم التغيير)",
        "pkg_id": "معرّف الحزمة الجديد (Package ID):",
        "pkg_id_ph": "مثال: com.company.app (مهم لتثبيت نسخة ثانية)",
        "random_btn": "🎲 عشوائي",
        "keep_icon": "استخدام الشعار الأصلي دون تغيير",
        "custom_icon": "شعار التطبيق المخصص (PNG):",
        "custom_icon_ph": "اختر صورة الأيقونة الجديدة بدقة مناسبة (.png)...",
        "browse": "استعراض...",
        "orig_badge": "[الأصلي]",
        "deep_rename": "تفعيل الاستنساخ الشامل وتغيير الحزمة (Deep Renaming):",
        "deep_rename_desc": "يستبدل معرّف الحزمة في كافة ملفات وشيفرات التطبيق لتثبيته كنسخة مكررة بجانب التطبيق الأصلي.",
        "adv_btn_closed": "▶ خيارات وإعدادات متقدمة (القاموس، وأوامر المعالجة)",
        "adv_btn_opened": "▼ إخفاء الإعدادات المتقدمة",
        "dict_lbl": "ملف قاموس استبدال النصوص (-r):",
        "dict_ph": "اختياري: ملف dictionary.txt لاستبدال الكلمات",
        "decode_lbl": "أوامر فك الحزم الإضافية (-da):",
        "decode_ph": "مثال: --keep-broken-res",
        "build_lbl": "أوامر إعادة البناء الإضافية (-ba):",
        "build_ph": "مثال: --use-aapt2",
        "start_btn": "🚀 بدء المعالجة والتعديل",
        "processing_btn": "⏳ جاري المعالجة...",
        "cancel_btn": "🛑 إلغاء",
        "open_folder": "📂 فتح مجلد الإخراج",
        "terminal_title": "سجل العمليات والمخرجات المباشر:",
        "copy_log": "نسخ",
        "clear_log": "مسح",
        "ready": "جاهز للبدء",
        "java_ok": "جافا: متوفر ومفعّل ✅",
        "java_fail": "جافا: غير مثبت بالنظام ❌",
        "copied": "تم نسخ السجل إلى الحافظة بنجاح!",
        "success_title": "اكتمل بنجاح",
        "success_msg": "تم تعديل وبناء وتوقيع التطبيق بنجاح!\nالمسار:\n",
        "err_title": "خطأ",
        "err_no_apk": "يرجى اختيار ملف تطبيق صالح وموجود.",
        "err_no_out": "يرجى تحديد مسار لحفظ التطبيق الناتج.",
        "confirm_title": "تنبيه",
        "confirm_msg": "لم تحدد اسماً جديداً أو معرّف حزمة أو شعاراً جديداً.\nهل ترغب بالاستمرار في استنساخ التطبيق بنفس الخصائص؟",
        "theme": "المظهر",
        "lang_switch_text": "English",
    },
    "en": {
        "app_title": "ApkRenamer Studio (Android Cloner)",
        "app_subtitle": "Customize, Clone, and Re-sign Android APKs with ease",
        "config_card": "Configuration & Parameters",
        "src_apk": "Source APK File:",
        "src_apk_ph": "Select target Android package (.apk)...",
        "out_apk": "Output APK Destination:",
        "out_apk_ph": "Location for the renamed .apk...",
        "app_name": "New App Name:",
        "app_name_ph": "e.g. My Cloned App (leave blank to keep unchanged)",
        "pkg_id": "New Package ID:",
        "pkg_id_ph": "e.g. com.company.app (needed for side-by-side install)",
        "random_btn": "🎲 Random",
        "keep_icon": "Keep Original APK Icon (No change)",
        "custom_icon": "Custom Icon (PNG):",
        "custom_icon_ph": "Select new .png icon...",
        "browse": "Browse...",
        "orig_badge": "[Original]",
        "deep_rename": "Enable Deep Renaming (-d) [Cloning Mode]:",
        "deep_rename_desc": "Replaces package name occurrences across all smali files & manifests for dual app installation.",
        "adv_btn_closed": "▶ Advanced Settings (Dictionary, Apktool flags)",
        "adv_btn_opened": "▼ Hide Advanced Settings",
        "dict_lbl": "Dictionary File (-r):",
        "dict_ph": "Optional: text replacement dictionary.txt",
        "decode_lbl": "Apktool Decode Flags (-da):",
        "decode_ph": "e.g. --keep-broken-res",
        "build_lbl": "Apktool Build Flags (-ba):",
        "build_ph": "e.g. --use-aapt2",
        "start_btn": "🚀 Start Processing",
        "processing_btn": "⏳ Processing...",
        "cancel_btn": "🛑 Cancel",
        "open_folder": "📂 Open Output Folder",
        "terminal_title": "Live Execution Terminal:",
        "copy_log": "Copy",
        "clear_log": "Clear",
        "ready": "Ready",
        "java_ok": "Java: Ready ✅",
        "java_fail": "Java: Missing! ❌",
        "copied": "Log contents copied to clipboard!",
        "success_title": "Success",
        "success_msg": "APK successfully customized, built, and signed!\nSaved to:\n",
        "err_title": "Error",
        "err_no_apk": "Please select a valid existing input .apk file.",
        "err_no_out": "Please specify the output .apk destination path.",
        "confirm_title": "Notice",
        "confirm_msg": "You haven't specified a new App Name or Package ID.\nDo you want to proceed with cloning/deep renaming anyway?",
        "theme": "Theme",
        "lang_switch_text": "العربية",
    }
}


class ApkRenamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("ApkRenamer Studio - Crystal Glass Edition")
        self.geometry("1020x820")
        self.minsize(880, 700)

        # Theme Colors (Obsidian / Crystal Glass)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Glass Styling Tokens
        self.glass_bg = ("#eef2f7", "#090c14")
        self.glass_card_bg = ("#ffffff", "#121726")
        self.glass_card_border = ("#d5dce6", "#222c44")
        self.glass_inner_bg = ("#f4f7fb", "#0c101c")
        self.glass_inner_border = ("#cbd5e1", "#283452")
        self.glass_header_bg = ("#fcfdff", "#0e1320")

        # State Variables
        self.current_lang = "ar"  # Default to Arabic (RTL)
        self.apk_in_var = ctk.StringVar()
        self.apk_out_var = ctk.StringVar()
        self.app_name_var = ctk.StringVar()
        self.package_name_var = ctk.StringVar()
        self.icon_path_var = ctk.StringVar()
        self.keep_original_icon_var = ctk.BooleanVar(value=True)
        self.dict_path_var = ctk.StringVar()
        self.deep_rename_var = ctk.BooleanVar(value=True)
        self.decode_args_var = ctk.StringVar()
        self.build_args_var = ctk.StringVar()

        self.adv_expanded = False
        self.icon_image_preview = None
        self.last_output_dir = None
        self.saved_logs = []

        # Configure root window background
        self.configure(fg_color=self.glass_bg)

        # Runner
        self.runner = ApkRenamerRunner(
            on_log=self.handle_log,
            on_finish=self.handle_finish,
            on_status=self.handle_status
        )

        self._build_interface()
        self._check_environment()

    def t(self, key: str) -> str:
        """Fetch translated text with full Arabic BiDi reshaping."""
        text = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["ar"]).get(key, key)
        if self.is_rtl():
            return bidi_text(text)
        return text

    def raw_t(self, key: str) -> str:
        """Fetch un-reshaped text for native Win32 dialogs (messagebox)."""
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["ar"]).get(key, key)

    def is_rtl(self) -> bool:
        return self.current_lang == "ar"

    def _toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        self._build_interface()
        self._toggle_icon_mode()
        self._check_environment(log=False)

    def _toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

    def _build_interface(self):
        # Save existing logs if rebuilding
        if hasattr(self, "console_box") and self.console_box.winfo_exists():
            self.saved_logs = self.console_box.get("1.0", "end-1c")

        # Clear existing children
        for widget in self.winfo_children():
            widget.destroy()

        rtl = self.is_rtl()
        label_anchor = "e" if rtl else "w"
        label_justify = "right" if rtl else "left"

        # Grid Configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 1. Frosted Glass Header ---
        header = ctk.CTkFrame(
            self,
            fg_color=self.glass_header_bg,
            border_color=self.glass_card_border,
            border_width=1,
            corner_radius=0,
            height=70
        )
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(1, weight=1)

        # Title Block
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_lbl = ctk.CTkLabel(
            title_frame,
            text=self.t("app_title"),
            font=get_font(20, "bold"),
            text_color=("#0f172a", "#f8fafc"),
            anchor=label_anchor
        )
        sub_lbl = ctk.CTkLabel(
            title_frame,
            text=self.t("app_subtitle"),
            font=get_font(11),
            text_color=("#64748b", "#94a3b8"),
            anchor=label_anchor,
            justify=label_justify
        )

        # Action badges block (Language, Theme, Java status)
        controls_frame = ctk.CTkFrame(header, fg_color="transparent")

        self.java_badge = ctk.CTkLabel(
            controls_frame,
            text="Checking Java...",
            font=get_font(12, "bold"),
            text_color="#888888"
        )
        self.java_badge.pack(side="left" if not rtl else "right", padx=10)

        theme_btn = ctk.CTkButton(
            controls_frame,
            text="🌓 " + self.t("theme"),
            width=85,
            height=30,
            corner_radius=10,
            font=get_font(12, "bold"),
            fg_color=("#e2e8f0", "#1e263d"),
            hover_color=("#cbd5e1", "#2b3656"),
            text_color=("#1e293b", "#e2e8f0"),
            border_color=self.glass_inner_border,
            border_width=1,
            command=self._toggle_theme
        )
        theme_btn.pack(side="left" if not rtl else "right", padx=6)

        lang_btn = ctk.CTkButton(
            controls_frame,
            text="🌐 " + self.t("lang_switch_text"),
            width=90,
            height=30,
            corner_radius=10,
            fg_color=("#0284c7", "#0369a1"),
            hover_color=("#0369a1", "#0284c7"),
            text_color="#ffffff",
            font=get_font(12, "bold"),
            command=self._toggle_language
        )
        lang_btn.pack(side="left" if not rtl else "right", padx=6)

        if rtl:
            title_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")
            title_lbl.pack(anchor="e")
            sub_lbl.pack(anchor="e")
            controls_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        else:
            title_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")
            title_lbl.pack(anchor="w")
            sub_lbl.pack(anchor="w")
            controls_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        # --- 2. Main Content Split ---
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=18, pady=(12, 16))
        content.grid_rowconfigure(0, weight=3)
        content.grid_rowconfigure(1, weight=2)
        content.grid_columnconfigure(0, weight=1)

        # Upper Card (Glass Form)
        upper_card = ctk.CTkFrame(
            content,
            fg_color=self.glass_card_bg,
            border_color=self.glass_card_border,
            border_width=1,
            corner_radius=16
        )
        upper_card.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 12))
        upper_card.grid_rowconfigure(1, weight=1)
        upper_card.grid_columnconfigure(0, weight=1)

        card_title = ctk.CTkLabel(
            upper_card,
            text=self.t("config_card"),
            font=get_font(14, "bold"),
            text_color=("#334155", "#94a3b8"),
            anchor=label_anchor
        )
        card_title.grid(row=0, column=0, sticky="e" if rtl else "w", padx=20, pady=(12, 4))

        top_scroll = ctk.CTkScrollableFrame(upper_card, fg_color="transparent")
        top_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        top_scroll.grid_columnconfigure(1, weight=1)

        col_label = 2 if rtl else 0
        col_input = 1
        col_action = 0 if rtl else 2
        label_sticky = "e" if rtl else "w"
        btn_sticky = "w" if rtl else "e"

        r = 0

        # --- Field 1: Source APK ---
        lbl_src = ctk.CTkLabel(top_scroll, text=self.t("src_apk"), font=get_font(13, "bold"), anchor=label_anchor)
        lbl_src.grid(row=r, column=col_label, padx=12, pady=6, sticky=label_sticky)

        self.apk_entry = ctk.CTkEntry(
            top_scroll,
            textvariable=self.apk_in_var,
            placeholder_text=self.t("src_apk_ph"),
            font=get_font(12),
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=10
        )
        self.apk_entry.grid(row=r, column=col_input, padx=8, pady=6, sticky="ew")

        btn_browse_apk = ctk.CTkButton(
            top_scroll,
            text=self.t("browse"),
            width=95,
            height=32,
            corner_radius=10,
            font=get_font(12, "bold"),
            fg_color=("#e2e8f0", "#1e263d"),
            hover_color=("#cbd5e1", "#2b3656"),
            text_color=("#0f172a", "#f1f5f9"),
            border_color=self.glass_inner_border,
            border_width=1,
            command=self._browse_apk_in
        )
        btn_browse_apk.grid(row=r, column=col_action, padx=8, pady=6, sticky=btn_sticky)
        r += 1

        # --- Field 2: Output APK ---
        lbl_out = ctk.CTkLabel(top_scroll, text=self.t("out_apk"), font=get_font(13, "bold"), anchor=label_anchor)
        lbl_out.grid(row=r, column=col_label, padx=12, pady=6, sticky=label_sticky)

        self.out_entry = ctk.CTkEntry(
            top_scroll,
            textvariable=self.apk_out_var,
            placeholder_text=self.t("out_apk_ph"),
            font=get_font(12),
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=10
        )
        self.out_entry.grid(row=r, column=col_input, padx=8, pady=6, sticky="ew")

        btn_browse_out = ctk.CTkButton(
            top_scroll,
            text=self.t("browse"),
            width=95,
            height=32,
            corner_radius=10,
            font=get_font(12, "bold"),
            fg_color=("#e2e8f0", "#1e263d"),
            hover_color=("#cbd5e1", "#2b3656"),
            text_color=("#0f172a", "#f1f5f9"),
            border_color=self.glass_inner_border,
            border_width=1,
            command=self._browse_apk_out
        )
        btn_browse_out.grid(row=r, column=col_action, padx=8, pady=6, sticky=btn_sticky)
        r += 1

        # --- Field 3: New App Name ---
        lbl_name = ctk.CTkLabel(top_scroll, text=self.t("app_name"), font=get_font(13, "bold"), anchor=label_anchor)
        lbl_name.grid(row=r, column=col_label, padx=12, pady=6, sticky=label_sticky)

        self.name_entry = ctk.CTkEntry(
            top_scroll,
            textvariable=self.app_name_var,
            placeholder_text=self.t("app_name_ph"),
            font=get_font(12),
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=10
        )
        if rtl:
            self.name_entry.grid(row=r, column=0, columnspan=2, padx=8, pady=6, sticky="ew")
        else:
            self.name_entry.grid(row=r, column=1, columnspan=2, padx=8, pady=6, sticky="ew")
        r += 1

        # --- Field 4: New Package ID & Random Button ---
        lbl_pkg = ctk.CTkLabel(top_scroll, text=self.t("pkg_id"), font=get_font(13, "bold"), anchor=label_anchor)
        lbl_pkg.grid(row=r, column=col_label, padx=12, pady=6, sticky=label_sticky)

        self.pack_entry = ctk.CTkEntry(
            top_scroll,
            textvariable=self.package_name_var,
            placeholder_text=self.t("pkg_id_ph"),
            font=get_font(12),
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=10
        )
        self.pack_entry.grid(row=r, column=col_input, padx=8, pady=6, sticky="ew")

        self.rand_btn = ctk.CTkButton(
            top_scroll,
            text=self.t("random_btn"),
            width=95,
            height=32,
            corner_radius=10,
            fg_color=("#4f46e5", "#4338ca"),
            hover_color=("#4338ca", "#3730a3"),
            text_color="#ffffff",
            font=get_font(12, "bold"),
            command=self._generate_random_package
        )
        self.rand_btn.grid(row=r, column=col_action, padx=8, pady=6, sticky=btn_sticky)
        r += 1

        # --- Field 5: Icon Management ---
        icon_frame = ctk.CTkFrame(top_scroll, fg_color="transparent")
        icon_frame.grid(row=r, column=0, columnspan=3, padx=12, pady=(6, 2), sticky="ew")

        self.keep_icon_switch = ctk.CTkSwitch(
            icon_frame,
            text=self.t("keep_icon"),
            variable=self.keep_original_icon_var,
            command=self._toggle_icon_mode,
            font=get_font(13, "bold"),
            progress_color="#0284c7"
        )
        self.keep_icon_switch.pack(side="right" if rtl else "left", padx=0, pady=2)
        r += 1

        # Custom Icon Row
        lbl_cicon = ctk.CTkLabel(top_scroll, text=self.t("custom_icon"), font=get_font(13, "bold"), anchor=label_anchor)
        lbl_cicon.grid(row=r, column=col_label, padx=12, pady=6, sticky=label_sticky)

        self.icon_entry = ctk.CTkEntry(
            top_scroll,
            textvariable=self.icon_path_var,
            placeholder_text=self.t("custom_icon_ph"),
            font=get_font(12),
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=10
        )
        self.icon_entry.grid(row=r, column=col_input, padx=8, pady=6, sticky="ew")

        icon_action_box = ctk.CTkFrame(top_scroll, fg_color="transparent")
        icon_action_box.grid(row=r, column=col_action, padx=8, pady=6, sticky=btn_sticky)

        self.icon_browse_btn = ctk.CTkButton(
            icon_action_box,
            text=self.t("browse"),
            width=95,
            height=32,
            corner_radius=10,
            font=get_font(12, "bold"),
            fg_color=("#e2e8f0", "#1e263d"),
            hover_color=("#cbd5e1", "#2b3656"),
            text_color=("#0f172a", "#f1f5f9"),
            border_color=self.glass_inner_border,
            border_width=1,
            command=self._browse_icon
        )
        self.preview_label = ctk.CTkLabel(icon_action_box, text=self.t("orig_badge"), font=get_font(11, "bold"), width=52, height=32)

        if rtl:
            self.preview_label.pack(side="left", padx=(0, 6))
            self.icon_browse_btn.pack(side="left")
        else:
            self.icon_browse_btn.pack(side="left")
            self.preview_label.pack(side="left", padx=(6, 0))
        r += 1

        # --- Field 6: Deep Rename Card ---
        deep_card = ctk.CTkFrame(
            top_scroll,
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=12
        )
        deep_card.grid(row=r, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.deep_switch = ctk.CTkSwitch(
            deep_card,
            text=self.t("deep_rename"),
            variable=self.deep_rename_var,
            font=get_font(13, "bold"),
            progress_color="#0284c7"
        )
        self.deep_switch.pack(anchor="e" if rtl else "w", padx=16, pady=(10, 4))

        lbl_deep_desc = ctk.CTkLabel(
            deep_card,
            text=self.t("deep_rename_desc"),
            font=get_font(11),
            text_color=("#64748b", "#94a3b8"),
            wraplength=700,
            justify=label_justify,
            anchor=label_anchor
        )
        lbl_deep_desc.pack(anchor="e" if rtl else "w", padx=16, pady=(0, 10))
        r += 1

        # --- Field 7: Advanced Options Collapsible ---
        self.adv_toggle_btn = ctk.CTkButton(
            top_scroll,
            text=self.t("adv_btn_opened" if self.adv_expanded else "adv_btn_closed"),
            fg_color="transparent",
            text_color=("#0284c7", "#38bdf8"),
            hover=False,
            anchor=label_anchor,
            font=get_font(12, "bold"),
            command=self._toggle_advanced
        )
        self.adv_toggle_btn.grid(row=r, column=0, columnspan=3, padx=12, pady=(4, 2), sticky="ew")
        r += 1

        self.adv_frame = ctk.CTkFrame(
            top_scroll,
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=12
        )
        self.adv_frame.grid_columnconfigure(1, weight=1)

        # Dictionary
        lbl_dict = ctk.CTkLabel(self.adv_frame, text=self.t("dict_lbl"), font=get_font(12, "bold"), anchor=label_anchor)
        lbl_dict.grid(row=0, column=col_label, padx=12, pady=6, sticky=label_sticky)
        ctk.CTkEntry(
            self.adv_frame,
            textvariable=self.dict_path_var,
            placeholder_text=self.t("dict_ph"),
            font=get_font(11),
            fg_color=self.glass_card_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=8
        ).grid(row=0, column=col_input, padx=6, pady=6, sticky="ew")
        ctk.CTkButton(
            self.adv_frame,
            text=self.t("browse"),
            width=80,
            height=28,
            corner_radius=8,
            font=get_font(11, "bold"),
            fg_color=("#e2e8f0", "#1e263d"),
            hover_color=("#cbd5e1", "#2b3656"),
            text_color=("#0f172a", "#f1f5f9"),
            border_color=self.glass_inner_border,
            border_width=1,
            command=self._browse_dict
        ).grid(row=0, column=col_action, padx=8, pady=6, sticky=btn_sticky)

        # Decode flags
        lbl_dec = ctk.CTkLabel(self.adv_frame, text=self.t("decode_lbl"), font=get_font(12, "bold"), anchor=label_anchor)
        lbl_dec.grid(row=1, column=col_label, padx=12, pady=6, sticky=label_sticky)
        dec_entry = ctk.CTkEntry(
            self.adv_frame,
            textvariable=self.decode_args_var,
            placeholder_text=self.t("decode_ph"),
            font=get_font(11),
            fg_color=self.glass_card_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=8
        )
        if rtl:
            dec_entry.grid(row=1, column=0, columnspan=2, padx=6, pady=6, sticky="ew")
        else:
            dec_entry.grid(row=1, column=1, columnspan=2, padx=6, pady=6, sticky="ew")

        # Build flags
        lbl_bld = ctk.CTkLabel(self.adv_frame, text=self.t("build_lbl"), font=get_font(12, "bold"), anchor=label_anchor)
        lbl_bld.grid(row=2, column=col_label, padx=12, pady=6, sticky=label_sticky)
        bld_entry = ctk.CTkEntry(
            self.adv_frame,
            textvariable=self.build_args_var,
            placeholder_text=self.t("build_ph"),
            font=get_font(11),
            fg_color=self.glass_card_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=8
        )
        if rtl:
            bld_entry.grid(row=2, column=0, columnspan=2, padx=6, pady=(6, 10), sticky="ew")
        else:
            bld_entry.grid(row=2, column=1, columnspan=2, padx=6, pady=(6, 10), sticky="ew")

        if self.adv_expanded:
            self.adv_frame.grid(row=r, column=0, columnspan=3, padx=10, pady=(2, 10), sticky="ew")
        r += 1

        # --- 3. Lower Glass Card (Actions & Terminal) ---
        lower_card = ctk.CTkFrame(
            content,
            fg_color=self.glass_card_bg,
            border_color=self.glass_card_border,
            border_width=1,
            corner_radius=16
        )
        lower_card.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        lower_card.grid_rowconfigure(3, weight=1)
        lower_card.grid_columnconfigure(0, weight=1)

        # Action Bar
        action_bar = ctk.CTkFrame(lower_card, fg_color="transparent")
        action_bar.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))

        self.start_btn = ctk.CTkButton(
            action_bar,
            text=self.t("start_btn"),
            font=get_font(14, "bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=40,
            width=170,
            corner_radius=12,
            command=self._start_process
        )

        self.cancel_btn = ctk.CTkButton(
            action_bar,
            text=self.t("cancel_btn"),
            font=get_font(13, "bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=40,
            width=110,
            corner_radius=12,
            state="disabled",
            command=self._cancel_process
        )

        self.open_out_btn = ctk.CTkButton(
            action_bar,
            text=self.t("open_folder"),
            height=40,
            corner_radius=12,
            font=get_font(12, "bold"),
            fg_color=("#10b981", "#059669"),
            hover_color=("#059669", "#047857"),
            text_color="#ffffff",
            state="disabled",
            command=self._open_output_folder
        )

        self.status_lbl = ctk.CTkLabel(
            action_bar,
            text=self.t("ready"),
            font=get_font(13, "bold"),
            text_color="#38bdf8",
            anchor=label_anchor
        )

        if rtl:
            self.start_btn.pack(side="right", padx=(8, 0))
            self.cancel_btn.pack(side="right", padx=(8, 0))
            self.open_out_btn.pack(side="right", padx=(8, 0))
            self.status_lbl.pack(side="left", padx=(0, 10))
        else:
            self.start_btn.pack(side="left", padx=(0, 8))
            self.cancel_btn.pack(side="left", padx=(0, 8))
            self.open_out_btn.pack(side="left", padx=(0, 8))
            self.status_lbl.pack(side="right", padx=(10, 0))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(lower_card, height=5, progress_color="#0284c7")
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 8))
        self.progress_bar.set(0)

        # Terminal Header Bar
        term_bar = ctk.CTkFrame(lower_card, fg_color="transparent")
        term_bar.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 4))

        lbl_terminal = ctk.CTkLabel(
            term_bar,
            text=self.t("terminal_title"),
            font=get_font(12, "bold"),
            text_color=("#475569", "#94a3b8"),
            anchor=label_anchor
        )

        btn_copy = ctk.CTkButton(
            term_bar,
            text=self.t("copy_log"),
            width=65,
            height=24,
            corner_radius=8,
            font=get_font(11, "bold"),
            fg_color=("#e2e8f0", "#1e263d"),
            hover_color=("#cbd5e1", "#2b3656"),
            text_color=("#0f172a", "#f1f5f9"),
            command=self._copy_log
        )
        btn_clear = ctk.CTkButton(
            term_bar,
            text=self.t("clear_log"),
            width=60,
            height=24,
            corner_radius=8,
            font=get_font(11, "bold"),
            fg_color=("#e2e8f0", "#1e263d"),
            hover_color=("#cbd5e1", "#2b3656"),
            text_color=("#0f172a", "#f1f5f9"),
            command=self._clear_log
        )

        if rtl:
            lbl_terminal.pack(side="right")
            btn_clear.pack(side="left", padx=(0, 4))
            btn_copy.pack(side="left")
        else:
            lbl_terminal.pack(side="left")
            btn_copy.pack(side="right", padx=(4, 0))
            btn_clear.pack(side="right")

        # Terminal Textbox
        self.console_box = ctk.CTkTextbox(
            lower_card,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=self.glass_inner_bg,
            border_color=self.glass_inner_border,
            border_width=1,
            corner_radius=12,
            wrap="word"
        )
        self.console_box.grid(row=3, column=0, sticky="nsew", padx=14, pady=(0, 12))
        self._setup_console_tags()

        # Restore saved logs if any
        if self.saved_logs:
            self.console_box.insert("end", self.saved_logs)
            self.console_box.see("end")

        self._toggle_icon_mode()

    def _setup_console_tags(self):
        tk_text = self.console_box._textbox
        tk_text.tag_config("info", foreground="#38bdf8")
        tk_text.tag_config("success", foreground="#34d399")
        tk_text.tag_config("warning", foreground="#fbbf24")
        tk_text.tag_config("error", foreground="#f87171")
        tk_text.tag_config("dim", foreground="#64748b")
        tk_text.tag_config("normal", foreground="#e2e8f0")

    def _check_environment(self, log: bool = True):
        has_java, info = check_java()
        if has_java:
            self.java_badge.configure(text=self.t("java_ok"), text_color="#34d399")
            if log:
                self.handle_log(f"Environment check: Java detected ({info})\n", "info")
        else:
            self.java_badge.configure(text=self.t("java_fail"), text_color="#f87171")
            if log:
                self.handle_log("Warning: Java JRE was not detected in system PATH.\n", "error")

        if log:
            core_dir = get_core_dir()
            jar_path = os.path.join(core_dir, "renamer.jar")
            if os.path.exists(jar_path):
                self.handle_log(f"Engine Core loaded: {jar_path}\nReady for operations.\n\n", "dim")
            else:
                self.handle_log(f"Warning: Core renamer.jar not found at {core_dir}\n", "error")

    def _toggle_advanced(self):
        self.adv_expanded = not self.adv_expanded
        self.adv_toggle_btn.configure(text=self.t("adv_btn_opened" if self.adv_expanded else "adv_btn_closed"))
        if self.adv_expanded:
            self.adv_frame.grid(row=8, column=0, columnspan=3, padx=10, pady=(2, 10), sticky="ew")
        else:
            self.adv_frame.grid_forget()

    def _generate_random_package(self):
        apk_path = self.apk_in_var.get().strip()
        base_hint = ""
        if apk_path:
            base_hint = os.path.splitext(os.path.basename(apk_path))[0]
        pkg = self._create_random_package_id(base_hint)
        self.package_name_var.set(pkg)
        self.handle_log(f"Generated Random Package ID: {pkg}\n", "info")

    def _create_random_package_id(self, base_hint: str = "") -> str:
        prefixes = ["com", "app", "net", "io", "org"]
        prefix = random.choice(prefixes)

        words = ["clone", "space", "dual", "multi", "plus", "mod", "apex", "swift", "nova", "prime", "echo", "hub"]
        clean_hint = "".join(c.lower() for c in base_hint if c.isalnum())
        if clean_hint and len(clean_hint) >= 3:
            mid = clean_hint[:10]
        else:
            mid = random.choice(words)

        suffix_chars = random.choices(string.ascii_lowercase + string.digits, k=5)
        if suffix_chars[0].isdigit():
            suffix_chars[0] = random.choice(string.ascii_lowercase)
        suffix = "".join(suffix_chars)

        return f"{prefix}.{mid}.{suffix}"

    def _toggle_icon_mode(self):
        keep_original = self.keep_original_icon_var.get()
        if keep_original:
            self.icon_entry.configure(state="disabled")
            self.icon_browse_btn.configure(state="disabled")
            self.preview_label.configure(image=None, text=self.t("orig_badge"))
        else:
            self.icon_entry.configure(state="normal")
            self.icon_browse_btn.configure(state="normal")
            if self.icon_path_var.get():
                self._update_icon_preview(self.icon_path_var.get())
            else:
                self.preview_label.configure(image=None, text="")

    # --- File Browsers ---
    def _browse_apk_in(self):
        file = filedialog.askopenfilename(
            title=self.raw_t("src_apk"),
            filetypes=[("Android Package (*.apk)", "*.apk"), ("All Files", "*.*")]
        )
        if file:
            self.apk_in_var.set(file)
            base_name = os.path.splitext(file)[0]
            dir_name = os.path.dirname(file)
            suggested_out = os.path.join(dir_name, f"{os.path.basename(base_name)}_renamed.apk")
            if not self.apk_out_var.get():
                self.apk_out_var.set(suggested_out)
            if not self.package_name_var.get():
                self._generate_random_package()

    def _browse_apk_out(self):
        file = filedialog.asksaveasfilename(
            title=self.raw_t("out_apk"),
            defaultextension=".apk",
            filetypes=[("Android Package (*.apk)", "*.apk")]
        )
        if file:
            self.apk_out_var.set(file)

    def _browse_icon(self):
        file = filedialog.askopenfilename(
            title=self.raw_t("custom_icon"),
            filetypes=[("PNG Images (*.png)", "*.png"), ("All Images", "*.png;*.jpg;*.jpeg")]
        )
        if file:
            self.icon_path_var.set(file)
            self._update_icon_preview(file)

    def _update_icon_preview(self, path: str):
        try:
            img = Image.open(path)
            img = img.resize((32, 32), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
            self.preview_label.configure(image=ctk_img, text="")
            self.icon_image_preview = ctk_img
        except Exception:
            self.preview_label.configure(image=None, text="⚠️")

    def _browse_dict(self):
        file = filedialog.askopenfilename(
            title=self.raw_t("dict_lbl"),
            filetypes=[("Text Files (*.txt)", "*.txt"), ("All Files", "*.*")]
        )
        if file:
            self.dict_path_var.set(file)

    # --- Execution ---
    def _start_process(self):
        apk_in = self.apk_in_var.get().strip()
        apk_out = self.apk_out_var.get().strip()
        app_name = self.app_name_var.get().strip()
        package_name = self.package_name_var.get().strip()
        icon = self.icon_path_var.get().strip()

        if not apk_in or not os.path.exists(apk_in):
            messagebox.showerror(self.raw_t("err_title"), self.raw_t("err_no_apk"))
            return

        if not apk_out:
            messagebox.showerror(self.raw_t("err_title"), self.raw_t("err_no_out"))
            return

        keep_orig_icon = self.keep_original_icon_var.get()
        effective_icon = "" if keep_orig_icon else icon

        if not app_name and not package_name and (keep_orig_icon or not effective_icon):
            confirm = messagebox.askyesno(self.raw_t("confirm_title"), self.raw_t("confirm_msg"))
            if not confirm:
                return

        self.start_btn.configure(state="disabled", text=self.t("processing_btn"))
        self.cancel_btn.configure(state="normal")
        self.open_out_btn.configure(state="disabled")
        self.progress_bar.start()

        params = {
            "apk_in": apk_in,
            "apk_out": apk_out,
            "app_name": app_name,
            "package_name": package_name,
            "icon_path": effective_icon,
            "keep_original_icon": keep_orig_icon,
            "dictionary_path": self.dict_path_var.get().strip(),
            "is_deep_rename": self.deep_rename_var.get(),
            "decode_args": self.decode_args_var.get().strip(),
            "build_args": self.build_args_var.get().strip(),
        }

        self.last_output_dir = os.path.dirname(os.path.abspath(apk_out))
        self.runner.run(params)

    def _cancel_process(self):
        self.runner.cancel()
        self.cancel_btn.configure(state="disabled")

    def _open_output_folder(self):
        target = self.last_output_dir or os.path.abspath("out")
        if os.path.exists(target):
            os.startfile(target)
        else:
            messagebox.showinfo(self.raw_t("open_folder"), f"Path not found: {target}")

    def _copy_log(self):
        content = self.console_box.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo(self.raw_t("copy_log"), self.raw_t("copied"))

    def _clear_log(self):
        self.console_box.delete("1.0", "end")

    # --- Callbacks ---
    def handle_log(self, text: str, line_type: str = "normal"):
        def _update():
            tk_text = self.console_box._textbox
            tk_text.insert("end", text, line_type)
            tk_text.see("end")
        self.after(0, _update)

    def handle_status(self, status: str):
        def _update():
            self.status_lbl.configure(text=status)
            if "success" in status.lower() or "finished" in status.lower():
                self.status_lbl.configure(text_color="#34d399")
            elif "error" in status.lower() or "fail" in status.lower():
                self.status_lbl.configure(text_color="#f87171")
            else:
                self.status_lbl.configure(text_color="#38bdf8")
        self.after(0, _update)

    def handle_finish(self, success: bool, message: str):
        def _update():
            self.progress_bar.stop()
            self.progress_bar.set(1.0 if success else 0)
            self.start_btn.configure(state="normal", text=self.t("start_btn"))
            self.cancel_btn.configure(state="disabled")

            if success:
                self.open_out_btn.configure(state="normal")
                messagebox.showinfo(self.raw_t("success_title"), f"{self.raw_t('success_msg')}{self.apk_out_var.get()}")
            else:
                messagebox.showwarning(self.raw_t("err_title"), f"Notice: {message}")

        self.after(0, _update)


def main():
    app = ApkRenamerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
