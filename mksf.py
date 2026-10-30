import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import re
import json


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_FONT = r"C:\Windows\Fonts\times.ttf"

DEFAULT_FONT_SIZE = 55
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 150

DEFAULT_OUTPUT = "output"

SETTINGS_FILE = "settings.json"


# ============================================================
# HELPERS
# ============================================================

def clean_filename(text):
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', '_', text.strip())
    return text


def load_settings():

    if not os.path.exists(SETTINGS_FILE):
        return {}

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return {}


def save_settings(data):

    try:
        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    except Exception:
        pass


def get_font(draw, text, max_width, font_path, font_size):
    """
    Font size foydalanuvchi tomonidan berilgan.
    Agar Auto Fit yoqilgan bo'lsa, avtomatik kichrayadi.
    """

    try:
        font = ImageFont.truetype(
            font_path,
            font_size
        )

    except Exception:

        font = ImageFont.truetype(
            DEFAULT_FONT,
            font_size
        )

    box = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    width = box[2] - box[0]

    return font


def get_auto_fit_font(
    draw,
    text,
    max_width,
    font_path,
    start_size,
    min_size
):

    for size in range(
        start_size,
        min_size - 1,
        -1
    ):

        try:

            font = ImageFont.truetype(
                font_path,
                size
            )

        except Exception:

            font = ImageFont.truetype(
                DEFAULT_FONT,
                size
            )

        box = draw.textbbox(
            (0, 0),
            text,
            font=font
        )

        width = (
            box[2] - box[0]
        )

        if width <= max_width:

            return font

    return ImageFont.truetype(
        font_path,
        min_size
    )


# ============================================================
# MAIN APP
# ============================================================

class CertificateApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Auto Certificate Generator"
        )

        self.root.geometry(
            "1350x850"
        )

        self.root.minsize(
            1100,
            700
        )

        # ----------------------------------------------------
        # SETTINGS
        # ----------------------------------------------------

        self.saved_settings = load_settings()

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        self.template_path = None
        self.names_path = None

        self.output_dir = self.saved_settings.get(
            "output_dir",
            DEFAULT_OUTPUT
        )

        self.font_path = self.saved_settings.get(
            "font_path",
            DEFAULT_FONT
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        self.original_image = None
        self.preview_image = None
        self.tk_image = None

        self.display_scale = 1

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        self.names = []

        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

        self.line_x1 = 250
        self.line_x2 = 1050
        self.text_y = 610

        # ----------------------------------------------------
        # MOUSE
        # ----------------------------------------------------

        self.drag_mode = None

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.create_ui()


    # ========================================================
    # UI
    # ========================================================

    def create_ui(self):

        # ====================================================
        # TOP BAR
        # ====================================================

        top = tk.Frame(
            self.root,
            padx=10,
            pady=10
        )

        top.pack(
            fill="x"
        )

        tk.Button(
            top,
            text="📄 Sertifikat",
            command=self.select_template,
            width=18
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            top,
            text="📋 Names.txt",
            command=self.select_names,
            width=18
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            top,
            text="🔤 Font",
            command=self.select_font,
            width=14
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            top,
            text="📁 Output",
            command=self.select_output,
            width=14
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            top,
            text="🔄 Preview",
            command=self.update_preview,
            width=14
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            top,
            text="🚀 GENERATE",
            command=self.generate_certificates,
            bg="#198754",
            fg="white",
            width=18,
            height=2
        ).pack(
            side="right",
            padx=4
        )


        # ====================================================
        # MAIN
        # ====================================================

        main = tk.Frame(
            self.root
        )

        main.pack(
            fill="both",
            expand=True
        )


        # ====================================================
        # PREVIEW
        # ====================================================

        preview_frame = tk.Frame(
            main,
            bg="#202020"
        )

        preview_frame.pack(
            side="left",
            fill="both",
            expand=True
        )


        self.canvas = tk.Canvas(
            preview_frame,
            bg="#202020",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )


        self.canvas.bind(
            "<Button-1>",
            self.canvas_click
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.canvas_drag
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.canvas_release
        )


        # Keyboard
        self.root.bind(
            "<Left>",
            lambda e: self.move_position(-1, 0)
        )

        self.root.bind(
            "<Right>",
            lambda e: self.move_position(1, 0)
        )

        self.root.bind(
            "<Up>",
            lambda e: self.move_position(0, -1)
        )

        self.root.bind(
            "<Down>",
            lambda e: self.move_position(0, 1)
        )


        # ====================================================
        # RIGHT PANEL
        # ====================================================

        panel = tk.Frame(
            main,
            width=330,
            padx=15,
            pady=15
        )

        panel.pack(
            side="right",
            fill="y"
        )

        panel.pack_propagate(
            False
        )


        tk.Label(
            panel,
            text="CERTIFICATE SETTINGS",
            font=(
                "Segoe UI",
                15,
                "bold"
            )
        ).pack(
            pady=(0, 15)
        )


        # ====================================================
        # NAME
        # ====================================================

        tk.Label(
            panel,
            text="Preview ism:"
        ).pack(
            anchor="w"
        )

        self.name_var = tk.StringVar(
            value="Abbosbek"
        )

        self.name_entry = tk.Entry(
            panel,
            textvariable=self.name_var,
            font=(
                "Segoe UI",
                11
            )
        )

        self.name_entry.pack(
            fill="x",
            pady=(4, 15)
        )

        self.name_entry.bind(
            "<KeyRelease>",
            lambda e: self.update_preview()
        )


        # ====================================================
        # FONT SIZE
        # ====================================================

        tk.Label(
            panel,
            text="Font Size:"
        ).pack(
            anchor="w"
        )

        font_size_frame = tk.Frame(
            panel
        )

        font_size_frame.pack(
            fill="x",
            pady=(3, 10)
        )

        self.font_size_var = tk.IntVar(
            value=self.saved_settings.get(
                "font_size",
                DEFAULT_FONT_SIZE
            )
        )

        self.font_size_entry = tk.Spinbox(
            font_size_frame,
            from_=MIN_FONT_SIZE,
            to=MAX_FONT_SIZE,
            textvariable=self.font_size_var,
            width=8,
            command=self.update_preview
        )

        self.font_size_entry.pack(
            side="left"
        )

        tk.Button(
            font_size_frame,
            text="Apply",
            command=self.update_preview
        ).pack(
            side="left",
            padx=5
        )


        # ====================================================
        # AUTO FIT
        # ====================================================

        self.auto_fit_var = tk.BooleanVar(
            value=True
        )

        tk.Checkbutton(
            panel,
            text="🤖 Auto Fit Font",
            variable=self.auto_fit_var,
            command=self.update_preview
        ).pack(
            anchor="w",
            pady=(0, 15)
        )


        # ====================================================
        # X1
        # ====================================================

        tk.Label(
            panel,
            text="LINE X1 — chap chegara"
        ).pack(
            anchor="w"
        )

        self.x1_var = tk.IntVar(
            value=self.saved_settings.get(
                "x1",
                250
            )
        )

        self.x1_scale = tk.Scale(
            panel,
            from_=0,
            to=3000,
            orient="horizontal",
            variable=self.x1_var,
            command=self.slider_changed
        )

        self.x1_scale.pack(
            fill="x"
        )


        # ====================================================
        # X2
        # ====================================================

        tk.Label(
            panel,
            text="LINE X2 — o'ng chegara"
        ).pack(
            anchor="w"
        )

        self.x2_var = tk.IntVar(
            value=self.saved_settings.get(
                "x2",
                1050
            )
        )

        self.x2_scale = tk.Scale(
            panel,
            from_=0,
            to=3000,
            orient="horizontal",
            variable=self.x2_var,
            command=self.slider_changed
        )

        self.x2_scale.pack(
            fill="x"
        )


        # ====================================================
        # Y
        # ====================================================

        tk.Label(
            panel,
            text="TEXT Y — vertikal markaz"
        ).pack(
            anchor="w"
        )

        self.y_var = tk.IntVar(
            value=self.saved_settings.get(
                "y",
                610
            )
        )

        self.y_scale = tk.Scale(
            panel,
            from_=0,
            to=3000,
            orient="horizontal",
            variable=self.y_var,
            command=self.slider_changed
        )

        self.y_scale.pack(
            fill="x"
        )


        # ====================================================
        # AUTO DETECT
        # ====================================================

        tk.Button(
            panel,
            text="🔍 Avtomatik aniqlash",
            command=self.auto_detect_line,
            height=2
        ).pack(
            fill="x",
            pady=(15, 5)
        )


        # ====================================================
        # FONT INFO
        # ====================================================

        self.font_label = tk.Label(
            panel,
            text="Font: " + self.font_path,
            justify="left",
            wraplength=290,
            fg="#555"
        )

        self.font_label.pack(
            anchor="w",
            pady=5
        )


        # ====================================================
        # OUTPUT INFO
        # ====================================================

        self.output_label = tk.Label(
            panel,
            text="Output:\n" + os.path.abspath(
                self.output_dir
            ),
            justify="left",
            wraplength=290,
            fg="#555"
        )

        self.output_label.pack(
            anchor="w",
            pady=5
        )


        # ====================================================
        # STATUS
        # ====================================================

        self.status_var = tk.StringVar(
            value="Sertifikat shablonini tanlang..."
        )

        tk.Label(
            panel,
            textvariable=self.status_var,
            justify="left",
            wraplength=290
        ).pack(
            anchor="w",
            pady=10
        )


    # ========================================================
    # TEMPLATE
    # ========================================================

    def select_template(self):

        path = filedialog.askopenfilename(
            title="Sertifikat shablonini tanlang",
            filetypes=[
                (
                    "Images",
                    "*.jpg *.jpeg *.png *.webp"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        try:

            image = Image.open(
                path
            ).convert("RGB")

            self.template_path = path
            self.original_image = image

            # Sliderlarni image o'lchamiga moslash
            self.x1_scale.config(
                to=image.width
            )

            self.x2_scale.config(
                to=image.width
            )

            self.y_scale.config(
                to=image.height
            )

            # Agar settings yo'q bo'lsa,
            # default joylashtiramiz

            if "x1" not in self.saved_settings:

                self.x1_var.set(
                    int(image.width * 0.20)
                )

                self.x2_var.set(
                    int(image.width * 0.80)
                )

                self.y_var.set(
                    int(image.height * 0.50)
                )

            self.status_var.set(
                f"Shablon yuklandi.\n"
                f"{image.width} × {image.height}"
            )

            self.update_preview()

        except Exception as e:

            messagebox.showerror(
                "Xatolik",
                str(e)
            )


    # ========================================================
    # NAMES
    # ========================================================

    def select_names(self):

        path = filedialog.askopenfilename(
            title="names.txt tanlang",
            filetypes=[
                (
                    "Text",
                    "*.txt"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        try:

            with open(
                path,
                "r",
                encoding="utf-8-sig"
            ) as f:

                self.names = [
                    line.strip()
                    for line in f
                    if line.strip()
                ]

            self.names_path = path

            if self.names:

                self.name_var.set(
                    self.names[0]
                )

            self.status_var.set(
                f"📋 {len(self.names)} ta ism yuklandi."
            )

            self.update_preview()

        except Exception as e:

            messagebox.showerror(
                "Xatolik",
                str(e)
            )


    # ========================================================
    # FONT
    # ========================================================

    def select_font(self):

        path = filedialog.askopenfilename(
            title="Font tanlang",
            filetypes=[
                (
                    "TrueType Font",
                    "*.ttf"
                ),
                (
                    "OpenType Font",
                    "*.otf"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        try:

            # Fontni test qilib ko'ramiz
            ImageFont.truetype(
                path,
                30
            )

            self.font_path = path

            self.font_label.config(
                text="Font:\n" + path
            )

            self.update_preview()

        except Exception as e:

            messagebox.showerror(
                "Font xatosi",
                str(e)
            )


    # ========================================================
    # OUTPUT
    # ========================================================

    def select_output(self):

        path = filedialog.askdirectory(
            title="Sertifikatlar saqlanadigan papkani tanlang"
        )

        if not path:
            return

        self.output_dir = path

        self.output_label.config(
            text="Output:\n" + path
        )

        self.status_var.set(
            "Output papka tanlandi."
        )


    # ========================================================
    # PREVIEW
    # ========================================================

    def update_preview(self, *args):

        if self.original_image is None:
            return

        self.line_x1 = self.x1_var.get()
        self.line_x2 = self.x2_var.get()
        self.text_y = self.y_var.get()

        name = self.name_var.get().strip()

        if not name:
            name = "F.I.SH."

        try:

            font_size = int(
                self.font_size_var.get()
            )

        except Exception:

            font_size = DEFAULT_FONT_SIZE

        img = self.original_image.copy()

        draw = ImageDraw.Draw(
            img
        )

        line_width = max(
            1,
            self.line_x2 - self.line_x1
        )

        # ----------------------------------------------------
        # FONT
        # ----------------------------------------------------

        if self.auto_fit_var.get():

            font = get_auto_fit_font(
                draw,
                name,
                line_width,
                self.font_path,
                font_size,
                MIN_FONT_SIZE
            )

        else:

            font = get_font(
                draw,
                name,
                line_width,
                self.font_path,
                font_size
            )


        # ----------------------------------------------------
        # TEXT BOX
        # ----------------------------------------------------

        box = draw.textbbox(
            (0, 0),
            name,
            font=font
        )

        text_width = (
            box[2] - box[0]
        )

        text_height = (
            box[3] - box[1]
        )


        # ----------------------------------------------------
        # CENTER
        # ----------------------------------------------------

        x = (
            self.line_x1
            + (
                line_width
                - text_width
            ) / 2
        )

        y = (
            self.text_y
            - (
                text_height / 2
            )
            - box[1]
        )


        # ----------------------------------------------------
        # DRAW TEXT
        # ----------------------------------------------------

        draw.text(
            (x, y),
            name,
            font=font,
            fill="black"
        )


        # ----------------------------------------------------
        # GUIDE LINE
        # ----------------------------------------------------

        draw.line(
            (
                self.line_x1,
                self.text_y,
                self.line_x2,
                self.text_y
            ),
            fill="red",
            width=2
        )


        # X1
        draw.ellipse(
            (
                self.line_x1 - 8,
                self.text_y - 8,
                self.line_x1 + 8,
                self.text_y + 8
            ),
            fill="red"
        )


        # X2
        draw.ellipse(
            (
                self.line_x2 - 8,
                self.text_y - 8,
                self.line_x2 + 8,
                self.text_y + 8
            ),
            fill="red"
        )


        # Center
        center_x = (
            self.line_x1
            + self.line_x2
        ) / 2

        draw.ellipse(
            (
                center_x - 7,
                self.text_y - 7,
                center_x + 7,
                self.text_y + 7
            ),
            fill="blue"
        )


        self.preview_image = img

        self.show_on_canvas()


    # ========================================================
    # SHOW PREVIEW
    # ========================================================

    def show_on_canvas(self):

        if self.preview_image is None:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 100:
            canvas_w = 900

        if canvas_h < 100:
            canvas_h = 600

        img = self.preview_image.copy()

        scale = min(
            canvas_w / img.width,
            canvas_h / img.height
        )

        new_size = (
            int(img.width * scale),
            int(img.height * scale)
        )

        img = img.resize(
            new_size,
            Image.Resampling.LANCZOS
        )

        self.display_scale = scale

        self.tk_image = ImageTk.PhotoImage(
            img
        )

        self.canvas.delete(
            "all"
        )

        self.canvas.create_image(
            canvas_w // 2,
            canvas_h // 2,
            image=self.tk_image,
            anchor="center"
        )


    # ========================================================
    # SLIDER
    # ========================================================

    def slider_changed(self, value):

        self.update_preview()


    # ========================================================
    # CANVAS COORDINATES
    # ========================================================

    def canvas_to_image(self, x, y):

        if self.original_image is None:
            return None, None

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        img_w = self.original_image.width
        img_h = self.original_image.height

        scale = min(
            canvas_w / img_w,
            canvas_h / img_h
        )

        display_w = img_w * scale
        display_h = img_h * scale

        offset_x = (
            canvas_w - display_w
        ) / 2

        offset_y = (
            canvas_h - display_h
        ) / 2

        image_x = (
            x - offset_x
        ) / scale

        image_y = (
            y - offset_y
        ) / scale

        return image_x, image_y


    # ========================================================
    # MOUSE CLICK
    # ========================================================

    def canvas_click(self, event):

        x, y = self.canvas_to_image(
            event.x,
            event.y
        )

        if x is None:
            return

        # X1
        if abs(x - self.line_x1) < 40:

            self.drag_mode = "x1"

        # X2
        elif abs(x - self.line_x2) < 40:

            self.drag_mode = "x2"

        # Center
        elif (
            self.line_x1 <= x <= self.line_x2
            and abs(y - self.text_y) < 50
        ):

            self.drag_mode = "center"

        else:

            self.drag_mode = None


    # ========================================================
    # MOUSE DRAG
    # ========================================================

    def canvas_drag(self, event):

        if self.drag_mode is None:
            return

        x, y = self.canvas_to_image(
            event.x,
            event.y
        )

        if x is None:
            return

        if self.drag_mode == "x1":

            self.x1_var.set(
                int(max(0, x))
            )

        elif self.drag_mode == "x2":

            self.x2_var.set(
                int(max(0, x))
            )

        elif self.drag_mode == "center":

            center_x = (
                self.line_x1
                + self.line_x2
            ) / 2

            dx = x - center_x

            new_x1 = (
                self.line_x1
                + dx
            )

            new_x2 = (
                self.line_x2
                + dx
            )

            self.x1_var.set(
                int(max(0, new_x1))
            )

            self.x2_var.set(
                int(max(0, new_x2))
            )

            self.y_var.set(
                int(max(0, y))
            )

        self.update_preview()


    def canvas_release(self, event):

        self.drag_mode = None


    # ========================================================
    # KEYBOARD
    # ========================================================

    def move_position(self, dx, dy):

        if self.original_image is None:
            return

        self.x1_var.set(
            max(
                0,
                self.x1_var.get() + dx
            )
        )

        self.x2_var.set(
            max(
                0,
                self.x2_var.get() + dx
            )
        )

        self.y_var.set(
            max(
                0,
                self.y_var.get() + dy
            )
        )

        self.update_preview()


    # ========================================================
    # AUTO DETECT
    # ========================================================

    def auto_detect_line(self):

        if self.original_image is None:

            messagebox.showwarning(
                "Ogohlantirish",
                "Avval sertifikat tanlang."
            )

            return

        img = self.original_image.convert(
            "L"
        )

        width, height = img.size

        max_width = 1200

        scale = min(
            1,
            max_width / width
        )

        if scale < 1:

            small = img.resize(
                (
                    int(width * scale),
                    int(height * scale)
                )
            )

        else:

            small = img

        sw, sh = small.size

        candidates = []

        for y in range(
            int(sh * 0.10),
            int(sh * 0.90)
        ):

            dark_count = 0

            for x in range(
                0,
                sw,
                3
            ):

                pixel = small.getpixel(
                    (x, y)
                )

                if pixel < 100:
                    dark_count += 1

            candidates.append(
                (
                    dark_count,
                    y
                )
            )

        if not candidates:

            messagebox.showinfo(
                "Natija",
                "Chiziq topilmadi."
            )

            return

        candidates.sort(
            reverse=True
        )

        best_count, best_y = candidates[0]

        detected_y = int(
            best_y / scale
        )

        xs = []

        for x in range(sw):

            pixel = small.getpixel(
                (x, best_y)
            )

            if pixel < 100:
                xs.append(x)

        if xs:

            detected_x1 = int(
                min(xs) / scale
            )

            detected_x2 = int(
                max(xs) / scale
            )

        else:

            detected_x1 = int(
                width * 0.20
            )

            detected_x2 = int(
                width * 0.80
            )

        # Juda qisqa natijani qabul qilmaymiz
        if (
            detected_x2
            - detected_x1
            < width * 0.25
        ):

            detected_x1 = int(
                width * 0.20
            )

            detected_x2 = int(
                width * 0.80
            )

        self.x1_var.set(
            detected_x1
        )

        self.x2_var.set(
            detected_x2
        )

        self.y_var.set(
            detected_y
        )

        self.update_preview()

        messagebox.showinfo(
            "Avtomatik aniqlash",
            f"Chiziq aniqlandi:\n\n"
            f"X1 = {detected_x1}\n"
            f"X2 = {detected_x2}\n"
            f"Y  = {detected_y}"
        )


    # ========================================================
    # SAVE SETTINGS
    # ========================================================

    def save_current_settings(self):

        data = {
            "font_path": self.font_path,
            "font_size": self.font_size_var.get(),
            "output_dir": self.output_dir,
            "x1": self.x1_var.get(),
            "x2": self.x2_var.get(),
            "y": self.y_var.get(),
            "auto_fit": self.auto_fit_var.get()
        }

        save_settings(
            data
        )


    # ========================================================
    # GENERATE
    # ========================================================

    def generate_certificates(self):

        if self.original_image is None:

            messagebox.showwarning(
                "Ogohlantirish",
                "Sertifikat shablonini tanlang."
            )

            return

        if not self.names:

            messagebox.showwarning(
                "Ogohlantirish",
                "Names.txt faylini tanlang."
            )

            return

        # Output folder
        try:

            os.makedirs(
                self.output_dir,
                exist_ok=True
            )

        except Exception as e:

            messagebox.showerror(
                "Output xatosi",
                str(e)
            )

            return


        # Settings save
        self.save_current_settings()


        total = len(
            self.names
        )

        for index, name in enumerate(
            self.names,
            1
        ):

            img = self.original_image.copy()

            draw = ImageDraw.Draw(
                img
            )

            line_width = (
                self.line_x2
                - self.line_x1
            )

            try:

                font_size = int(
                    self.font_size_var.get()
                )

            except Exception:

                font_size = DEFAULT_FONT_SIZE


            # ------------------------------------------------
            # FONT
            # ------------------------------------------------

            if self.auto_fit_var.get():

                font = get_auto_fit_font(
                    draw,
                    name,
                    line_width,
                    self.font_path,
                    font_size,
                    MIN_FONT_SIZE
                )

            else:

                font = get_font(
                    draw,
                    name,
                    line_width,
                    self.font_path,
                    font_size
                )


            # ------------------------------------------------
            # TEXT
            # ------------------------------------------------

            box = draw.textbbox(
                (0, 0),
                name,
                font=font
            )

            text_width = (
                box[2] - box[0]
            )

            text_height = (
                box[3] - box[1]
            )


            x = (
                self.line_x1
                + (
                    line_width
                    - text_width
                ) / 2
            )

            y = (
                self.text_y
                - (
                    text_height / 2
                )
                - box[1]
            )


            draw.text(
                (x, y),
                name,
                font=font,
                fill="black"
            )


            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            filename = (
                f"{index:03d}_"
                f"{clean_filename(name)}.jpg"
            )

            output_path = os.path.join(
                self.output_dir,
                filename
            )

            img.save(
                output_path,
                quality=95
            )


            self.status_var.set(
                f"🚀 Yaratilmoqda...\n\n"
                f"{index} / {total}\n"
                f"{name}"
            )

            self.root.update_idletasks()


        messagebox.showinfo(
            "Tayyor!",
            f"{total} ta sertifikat tayyor!\n\n"
            f"Saqlangan joy:\n"
            f"{self.output_dir}"
        )


        self.status_var.set(
            f"✅ {total} ta sertifikat tayyor."
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CertificateApp(
        root
    )

    root.mainloop()