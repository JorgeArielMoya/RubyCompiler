import re
import tkinter as tk
from tkinter import messagebox
import threading
from main import run_interpreter

#INTERFAZ GRAFICA
EXAMPLES = {
    "Tipos de datos": 'entero = Integer("10")\ndecimal = Float("3.14")\ntexto = String("hola")\nputs entero\nputs decimal\nputs texto',
    "Cadenas": 'nombre = "Jorge"\napellido = "Moya"\ncompleto = nombre + " " + apellido\nputs completo',
    "Operaciones básicas": 'a = 10\nb = 3\nsuma = a + b\nresta = a - b\nmultiplicacion = a * b\ndivision = a / b\nputs suma\nputs resta\nputs multiplicacion\nputs division',
    "Condicionales": 'nota = 85\nif nota >= 90\n  puts "A"\nelsif nota >= 80\n  puts "B"\nelsif nota >= 70\n  puts "C"\nelse\n  puts("Reprobado")\nend',
    "Bucle For": 'for i in 1..5\n  puts i\nend',
    "Bucle While": 'i = 1\nwhile i <= 5\n  puts i\n  i = i + 1\nend'
}

TOKEN_COLORS = {
    "KEYWORD":    "#c792ea",
    "IDENTIFIER": "#82aaff",
    "NUMBER":     "#f78c6c",
    "STRING":     "#c3e88d",
    "OPERATOR":   "#89ddff",
    "RANGE":      "#ffcb6b",
    "DOT":        "#89ddff",
    "PAREN":      "#ffcb6b",
}

KEYWORD_COLORS = {
    "if": "#c792ea", "elsif": "#c792ea", "else": "#c792ea",
    "end": "#c792ea", "while": "#c792ea", "for": "#c792ea", "in": "#c792ea",
}

BG         = "#1e1e2e"
BG2        = "#181825"
BG3        = "#313244"
ACCENT     = "#cba6f7"
ACCENT2    = "#89dceb"
TEXT       = "#cdd6f4"
TEXT2      = "#a6adc8"
TEXT3      = "#585b70"
RED        = "#f38ba8"
GREEN      = "#a6e3a1"
YELLOW     = "#f9e2af"
MONO_FONT  = ("Consolas", 13)
MONO_FONT2 = ("Consolas", 11)
UI_FONT    = ("Segoe UI", 11)
UI_FONT_B  = ("Segoe UI", 11, "bold")

class RubyIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Intérprete Ruby")
        self.configure(bg=BG2)
        self.geometry("1100x680")
        self.minsize(800, 500)
        self._build_ui()
        self._apply_syntax_highlight()
        self.editor.bind("<KeyRelease>", self._on_key)
        self.editor.bind("<Tab>", self._insert_tab)
        self._highlight_job = None

    def _build_ui(self):
        self._build_toolbar()
        self._build_panes()
        self._build_statusbar()

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG, height=44)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)

        tk.Label(bar, text="\u25c6 Intérprete Ruby", bg=BG,
                 fg=ACCENT, font=("Segoe UI", 12, "bold")).pack(side="left", padx=16)

        self.btn_run = tk.Button(
            bar, text="\u25b6  Ejecutar (F5)",
            bg=ACCENT, fg=BG2, font=UI_FONT_B,
            relief="flat", padx=14, pady=4,
            activebackground="#b4a0e0", activeforeground=BG2,
            cursor="hand2", command=self._run)
        self.btn_run.pack(side="left", padx=(4, 6), pady=6)

        self.ex_var = tk.StringVar(value="Ejemplos \u25be")
        ex_btn = tk.Menubutton(
            bar, textvariable=self.ex_var,
            bg=BG3, fg=ACCENT2, font=UI_FONT,
            relief="flat", padx=10, pady=4,
            activebackground="#45475a", cursor="hand2")
        ex_menu = tk.Menu(ex_btn, bg=BG, fg=TEXT, activebackground=BG3,
                          activeforeground=TEXT, tearoff=False)
        for name in EXAMPLES:
            ex_menu.add_command(label=name,
                                command=lambda n=name: self._load_example(n))
        ex_btn["menu"] = ex_menu
        ex_btn.pack(side="left", padx=6, pady=6)

        self.bind_all("<F5>", lambda e: self._run())

    def _build_panes(self):
        pw = tk.PanedWindow(self, orient="horizontal", bg=BG2,
                            sashwidth=5, sashrelief="flat",
                            handlepad=0, handlesize=0)
        pw.pack(fill="both", expand=True)

        left = tk.Frame(pw, bg=BG2)
        pw.add(left, minsize=300)

        lbl_ed = tk.Frame(left, bg=BG, height=30)
        lbl_ed.pack(fill="x")
        lbl_ed.pack_propagate(False)
        tk.Label(lbl_ed, text="  EDITOR  ", bg=BG, fg=TEXT3,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=8, pady=5)

        ed_frame = tk.Frame(left, bg=BG2)
        ed_frame.pack(fill="both", expand=True)

        self.ln_canvas = tk.Canvas(ed_frame, width=42, bg=BG2,
                                   highlightthickness=0)
        self.ln_canvas.pack(side="left", fill="y")

        vsb = tk.Scrollbar(ed_frame, orient="vertical", bg=BG3,
                           troughcolor=BG2, width=10)
        vsb.pack(side="right", fill="y")

        self.editor = tk.Text(
            ed_frame, bg=BG2, fg=TEXT, insertbackground=ACCENT,
            font=MONO_FONT, relief="flat", padx=10, pady=10,
            undo=True, wrap="none",
            yscrollcommand=self._sync_scroll,
            selectbackground=BG3, selectforeground=TEXT,
            highlightthickness=0, borderwidth=0)
        self.editor.pack(fill="both", expand=True)
        vsb.config(command=self._editor_yview)

        self._setup_highlight_tags()
        self._ln_update()
        self.editor.bind("<Configure>", lambda e: self._ln_update())

        right = tk.Frame(pw, bg=BG2)
        pw.add(right, minsize=280)

        tab_bar = tk.Frame(right, bg=BG, height=30)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        self._tabs = {}
        self._active_tab = tk.StringVar(value="output")
        for tid, tlabel in [("output", "SALIDA"), ("errors", "ERRORES"), ("tokens", "TOKENS")]:
            btn = tk.Button(tab_bar, text=tlabel,
                            bg=BG, fg=TEXT3, font=("Segoe UI", 9, "bold"),
                            relief="flat", padx=12,
                            activebackground=BG, activeforeground=ACCENT,
                            cursor="hand2",
                            command=lambda t=tid: self._switch_tab(t))
            btn.pack(side="left", pady=4)
            self._tabs[tid] = btn

        self._panels = {}
        container = tk.Frame(right, bg=BG2)
        container.pack(fill="both", expand=True)

        for tid in ("output", "errors", "tokens"):
            f = tk.Frame(container, bg=BG2)
            f.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._panels[tid] = f

        self._build_output_panel()
        self._build_errors_panel()
        self._build_tokens_panel()

        self._switch_tab("output")

    def _build_output_panel(self):
        p = self._panels["output"]
        vsb = tk.Scrollbar(p, bg=BG3, troughcolor=BG2, width=10)
        vsb.pack(side="right", fill="y")
        self.out_text = tk.Text(
            p, bg=BG2, fg=GREEN, font=MONO_FONT,
            relief="flat", padx=14, pady=10,
            state="disabled", wrap="word",
            yscrollcommand=vsb.set,
            selectbackground=BG3, highlightthickness=0)
        self.out_text.pack(fill="both", expand=True)
        vsb.config(command=self.out_text.yview)
        self.out_text.tag_configure("prompt", foreground=TEXT3)
        self.out_text.tag_configure("out",    foreground=GREEN)
        self.out_text.tag_configure("info",   foreground=ACCENT2)

    def _build_errors_panel(self):
        p = self._panels["errors"]
        vsb = tk.Scrollbar(p, bg=BG3, troughcolor=BG2, width=10)
        vsb.pack(side="right", fill="y")
        self.err_text = tk.Text(
            p, bg=BG2, fg=RED, font=MONO_FONT2,
            relief="flat", padx=14, pady=10,
            state="disabled", wrap="word",
            yscrollcommand=vsb.set,
            selectbackground=BG3, highlightthickness=0)
        self.err_text.pack(fill="both", expand=True)
        vsb.config(command=self.err_text.yview)
        self.err_text.tag_configure("header", foreground=YELLOW, font=("Segoe UI", 10, "bold"))
        self.err_text.tag_configure("err",    foreground=RED)
        self.err_text.tag_configure("ok",     foreground=GREEN)

    def _build_tokens_panel(self):
        p = self._panels["tokens"]
        vsb = tk.Scrollbar(p, bg=BG3, troughcolor=BG2, width=10)
        vsb.pack(side="right", fill="y")
        self.tok_text = tk.Text(
            p, bg=BG2, fg=TEXT, font=MONO_FONT2,
            relief="flat", padx=14, pady=10,
            state="disabled", wrap="word",
            yscrollcommand=vsb.set,
            selectbackground=BG3, highlightthickness=0)
        self.tok_text.pack(fill="both", expand=True)
        vsb.config(command=self.tok_text.yview)
        for ttype, color in TOKEN_COLORS.items():
            self.tok_text.tag_configure(f"tok_{ttype}", foreground=color)
        self.tok_text.tag_configure("line_label", foreground=TEXT3)
        self.tok_text.tag_configure("header",     foreground=ACCENT2,
                                    font=("Segoe UI", 10, "bold"))

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=BG, height=26)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Listo")
        self.status_lbl = tk.Label(bar, textvariable=self.status_var,
                                   bg=BG, fg=TEXT2, font=("Segoe UI", 9),
                                   anchor="w")
        self.status_lbl.pack(side="left", padx=12)

        self.cur_lbl = tk.Label(bar, text="Ln 1, Col 1",
                                bg=BG, fg=TEXT3, font=("Segoe UI", 9))
        self.cur_lbl.pack(side="right", padx=12)

        self.editor.bind("<KeyRelease>", self._update_cursor)
        self.editor.bind("<ButtonRelease>", self._update_cursor)

    def _switch_tab(self, tab_id):
        self._active_tab.set(tab_id)
        for tid, btn in self._tabs.items():
            if tid == tab_id:
                btn.config(fg=ACCENT, bg=BG3)
            else:
                btn.config(fg=TEXT3, bg=BG)
        self._panels[tab_id].lift()

    def _sync_scroll(self, *args):
        self._ln_update()

    def _editor_yview(self, *args):
        self.editor.yview(*args)
        self._ln_update()

    def _ln_update(self):
        self.ln_canvas.delete("all")
        i = self.editor.index("@0,0")
        while True:
            dline = self.editor.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = int(i.split(".")[0])
            self.ln_canvas.create_text(36, y + 2, anchor="ne",
                                       text=str(linenum),
                                       fill=TEXT3,
                                       font=MONO_FONT2)
            i = self.editor.index(f"{i}+1line")
            if self.editor.compare(i, "==", "end"):
                break

    def _setup_highlight_tags(self):
        self.editor.tag_configure("kw",  foreground="#c792ea")
        self.editor.tag_configure("str", foreground="#c3e88d")
        self.editor.tag_configure("num", foreground="#f78c6c")
        self.editor.tag_configure("id",  foreground=TEXT)
        self.editor.tag_configure("op",  foreground="#89ddff")
        self.editor.tag_configure("bi",  foreground="#82aaff")
        self.editor.tag_configure("conv",foreground="#ffcb6b")  

    def _apply_syntax_highlight(self):
        code = self.editor.get("1.0", "end-1c")
        for tag in ("kw", "str", "num", "id", "op", "bi", "conv"):
            self.editor.tag_remove(tag, "1.0", "end")

        patterns = [
            ("str",  r'".*?"'),
            ("kw",   r'\b(if|elsif|else|end|while|for|in)\b'),
            ("conv", r'\b(Integer|Float|String)\b'),
            ("bi",   r'\b(print|puts)\b'),
            ("num",  r'\b\d+\.?\d*\b'),
            ("op",   r'==|!=|<=|>=|[+\-*/=<>!]|\.\.'),
        ]
        for tag, pat in patterns:
            for m in re.finditer(pat, code):
                start = f"1.0+{m.start()}c"
                end   = f"1.0+{m.end()}c"
                self.editor.tag_add(tag, start, end)

    def _on_key(self, event=None):
        self._ln_update()
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(150, self._apply_syntax_highlight)
        self._update_cursor()

    def _insert_tab(self, event):
        self.editor.insert("insert", "  ")
        return "break"

    def _update_cursor(self, event=None):
        pos = self.editor.index("insert")
        ln, col = pos.split(".")
        self.cur_lbl.config(text=f"Ln {ln}, Col {int(col)+1}")

    def _new_file(self):
        if messagebox.askyesno("Nuevo", "¿Descartar el código actual?", parent=self):
            self.editor.delete("1.0", "end")
            self._clear_output()
            self._apply_syntax_highlight()

    def _load_example(self, name):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", EXAMPLES[name])
        self._apply_syntax_highlight()
        self._ln_update()
        self.status_var.set(f"Ejemplo cargado: {name}")
        self.ex_var.set("Ejemplos ▾")

    def _clear_output(self):
        for widget in (self.out_text, self.err_text, self.tok_text):
            widget.config(state="normal")
            widget.delete("1.0", "end")
            widget.config(state="disabled")
        self.status_var.set("Salida limpiada")

    def _run(self):
        code = self.editor.get("1.0", "end-1c").strip()
        if not code:
            self.status_var.set("Sin código para ejecutar")
            return

        self.btn_run.config(state="disabled", text="⏳ Ejecutando…")
        self.status_var.set("Ejecutando…")
        self._clear_output()

        def worker():
            try:
                output_lines, errors, tokens = run_interpreter(code)
            except Exception as e:
                output_lines, errors, tokens = [], [f"Error interno: {e}"], []
            self.after(0, lambda: self._show_results(output_lines, errors, tokens))

        threading.Thread(target=worker, daemon=True).start()

    def _show_results(self, output_lines, errors, tokens):
        self.btn_run.config(state="normal", text="▶  Ejecutar (F5)")

        self.out_text.config(state="normal")
        if errors:
            self.out_text.insert("end", "✗ El programa contiene errores.\n", "info")
            self.out_text.insert("end", "  Revisa la pestaña ERRORES para más detalles.\n", "prompt")
        elif not output_lines:
            self.out_text.insert("end", "(sin salida)\n", "prompt")
        else:
            buf = ""
            for kind, val in output_lines:
                if kind == "puts":
                    buf += val + "\n"
                else:
                    buf += val
            self.out_text.insert("end", buf, "out")
        self.out_text.config(state="disabled")

        self.err_text.config(state="normal")
        if errors:
            self.err_text.insert("end", f"  {len(errors)} error(es) encontrado(s)\n\n", "header")
            for i, err in enumerate(errors, 1):
                self.err_text.insert("end", f"  {i}. {err}\n", "err")
        else:
            self.err_text.insert("end", "✓  Sin errores detectados\n", "ok")
        self.err_text.config(state="disabled")

        self.tok_text.config(state="normal")
        self.tok_text.insert("end", f"  {len(tokens)} token(s) generados\n\n", "header")
        last_line = None
        for ttype, tval, tline in tokens:
            if tline != last_line:
                self.tok_text.insert("end", f"\n  ── Línea {tline} ──\n", "line_label")
                last_line = tline
            color_tag = f"tok_{ttype}"
            self.tok_text.insert("end", f"    [{ttype:12s}]  ", color_tag)
            self.tok_text.insert("end", f"{repr(tval)}\n", color_tag)
        self.tok_text.config(state="disabled")

        if errors:
            self.status_var.set(f"✗ {len(errors)} error(es)  —  ver pestaña ERRORES")
            self._switch_tab("errors")
            self.status_lbl.config(fg=RED)
        else:
            self.status_var.set(f"✓ Ejecutado correctamente  —  {len(output_lines)} línea(s) de salida")
            self._switch_tab("output")
            self.status_lbl.config(fg=GREEN)

if __name__ == "__main__":
    app = RubyIDE()
    app.mainloop()