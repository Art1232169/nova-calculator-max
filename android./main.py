__version__ = "1.2.0-android"

import ast, json, math, os
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

APP_NAME = "Nova Calculator MAX"

class SafeMath:
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
               ast.Pow, ast.USub, ast.UAdd, ast.Load, ast.Call, ast.Name)
    funcs = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
             "tan": math.tan, "log": math.log10, "ln": math.log,
             "abs": abs, "round": round, "pi": math.pi, "e": math.e}
    @classmethod
    def calc(cls, expr):
        expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, cls.allowed):
                raise ValueError("Niedozwolone działanie")
            if isinstance(node, ast.Name) and node.id not in cls.funcs:
                raise ValueError("Nieznana funkcja: " + node.id)
            if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or node.func.id not in cls.funcs):
                raise ValueError("Niedozwolona funkcja")
        return eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, cls.funcs)

class NovaAndroid(App):
    def build(self):
        self.title = APP_NAME
        self.data_dir = self.user_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.state_path = os.path.join(self.data_dir, "state.json")
        self.state = {"memory": 0.0, "history": [], "theme": "Jasny", "tutorial_seen": False}
        self.load_state()
        self.colors = {
            "Jasny": ("#f5f7fb", "#ffffff", "#172033", "#dce3ef", "#2764d8"),
            "Ciemny": ("#171923", "#252938", "#f4f5f7", "#42495b", "#8aa9ff"),
            "Miętowy": ("#e9f8f1", "#ffffff", "#173d31", "#c5e7d8", "#198765"),
        }
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.apply_colors()
        self.tabs = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(5))
        for name in ["Kalkulator", "Historia", "Przelicznik", "Równania", "Motyw"]:
            b = Button(text=name, font_size=dp(13), background_normal="", background_color=self.accent)
            b.bind(on_release=lambda btn, n=name: self.show_page(n))
            self.tabs.add_widget(b)
        self.root_box.add_widget(self.tabs)
        self.content = BoxLayout(orientation="vertical", spacing=dp(8))
        self.root_box.add_widget(self.content)
        self.show_page("Kalkulator")
        if not self.state.get("tutorial_seen"):
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.show_tutorial(), 0.5)
        return self.root_box

    def load_state(self):
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                self.state.update(json.load(f))
        except (OSError, ValueError):
            pass

    def save_state(self):
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def apply_colors(self):
        bg, panel, fg, border, accent = self.colors[self.state.get("theme", "Jasny")]
        self.bg, self.panel, self.fg, self.border, self.accent = bg, panel, fg, border, accent
        Window.clearcolor = self.hex_rgba(bg)

    def hex_rgba(self, value):
        value = value.lstrip("#")
        return tuple(int(value[i:i+2], 16)/255 for i in (0,2,4)) + (1,)

    def label(self, text, size=16, height=None):
        return Label(text=text, color=self.hex_rgba(self.fg), font_size=dp(size),
                     size_hint_y=None if height else 1, height=dp(height) if height else None)

    def button(self, text, callback, height=44):
        b = Button(text=text, size_hint_y=None, height=dp(height), font_size=dp(16),
                   background_normal="", background_color=self.hex_rgba(self.accent),
                   color=(1,1,1,1))
        b.bind(on_release=callback)
        return b

    def textinput(self, hint="", text="", multiline=False, height=48):
        return TextInput(hint_text=hint, text=text, multiline=multiline,
                         size_hint_y=None, height=dp(height), font_size=dp(18),
                         foreground_color=self.hex_rgba(self.fg),
                         background_color=self.hex_rgba(self.panel),
                         cursor_color=self.hex_rgba(self.accent))

    def clear_content(self):
        self.content.clear_widgets()
        self.apply_colors()

    def show_page(self, page):
        self.clear_content()
        if page == "Kalkulator": self.page_calc()
        elif page == "Historia": self.page_history()
        elif page == "Przelicznik": self.page_converter()
        elif page == "Równania": self.page_equations()
        elif page == "Motyw": self.page_theme()

    def page_calc(self):
        self.expr = self.textinput("Wpisz działanie, np. 12*(3+4)")
        self.content.add_widget(self.label("Nova Calculator MAX", 22, 36))
        self.content.add_widget(self.expr)
        self.result = self.label("Wynik: —", 20, 40)
        self.content.add_widget(self.result)
        mem = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))
        for t, cb in [("M+", self.mem_add), ("M−", self.mem_sub), ("MR", self.mem_recall), ("MC", self.mem_clear)]:
            mem.add_widget(self.button(t, cb, 44))
        self.content.add_widget(mem)
        grid = GridLayout(cols=4, spacing=dp(5), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        keys = ["7","8","9","÷","4","5","6","×","1","2","3","−","0",".","(",")","C","⌫","^","+","sqrt(","pi","=","/"]
        for key in keys:
            grid.add_widget(self.button(key, lambda btn, k=key: self.key_press(k), 48))
        sv = ScrollView()
        sv.add_widget(grid)
        self.content.add_widget(sv)

    def key_press(self, key):
        if key == "C": self.expr.text = ""; self.result.text = "Wynik: —"
        elif key == "⌫": self.expr.text = self.expr.text[:-1]
        elif key == "=": self.calculate()
        else: self.expr.text += key

    def calculate(self):
        try:
            val = SafeMath.calc(self.expr.text)
            if not math.isfinite(float(val)): raise ValueError("Wynik nie jest liczbą skończoną")
            self.result.text = "Wynik: " + str(val)
            self.state["history"].insert(0, {"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "expression": self.expr.text, "result": str(val)})
            self.state["history"] = self.state["history"][:200]
            self.save_state()
        except Exception as e:
            self.result.text = "Błąd: " + str(e)

    def current_number(self):
        try:
            return float(SafeMath.calc(self.expr.text))
        except Exception:
            try: return float(self.result.text.split("Wynik: ",1)[1])
            except Exception: return 0.0

    def mem_add(self, *_): self.state["memory"] = float(self.state.get("memory",0)) + self.current_number(); self.save_state(); self.toast("Dodano do pamięci")
    def mem_sub(self, *_): self.state["memory"] = float(self.state.get("memory",0)) - self.current_number(); self.save_state(); self.toast("Odjęto od pamięci")
    def mem_recall(self, *_):
        self.show_page("Kalkulator")
        self.expr.text = str(self.state.get("memory",0))
    def mem_clear(self, *_): self.state["memory"] = 0.0; self.save_state(); self.toast("Pamięć wyczyszczona")

    def toast(self, message):
        p = Popup(title="Nova Calculator MAX", content=Label(text=message), size_hint=(.8,.25))
        p.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: p.dismiss(), 1.2)

    def page_history(self):
        self.content.add_widget(self.label("Historia obliczeń", 22, 40))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row.add_widget(self.button("Wyczyść historię", self.clear_history))
        row.add_widget(self.button("Odśwież", lambda *_: self.show_page("Historia")))
        self.content.add_widget(row)
        scroll = ScrollView()
        items = BoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None)
        items.bind(minimum_height=items.setter("height"))
        for item in self.state.get("history", []):
            items.add_widget(self.label(f"{item.get('time','')}\\n{item.get('expression','')} = {item.get('result','')}", 15, 54))
        scroll.add_widget(items)
        self.content.add_widget(scroll)

    def clear_history(self, *_):
        self.state["history"] = []; self.save_state(); self.show_page("Historia")

    def page_converter(self):
        self.content.add_widget(self.label("Przelicznik jednostek", 22, 40))
        self.unit_kind = Spinner(text="Długość", values=("Długość","Masa","Temperatura"), size_hint_y=None, height=dp(46))
        self.content.add_widget(self.unit_kind)
        self.amount = self.textinput("Wartość", "1")
        self.content.add_widget(self.amount)
        self.from_unit = Spinner(text="km", values=("mm","cm","m","km","g","kg","mg","°C","°F"), size_hint_y=None, height=dp(46))
        self.to_unit = Spinner(text="m", values=("mm","cm","m","km","g","kg","mg","°C","°F"), size_hint_y=None, height=dp(46))
        self.content.add_widget(self.from_unit); self.content.add_widget(self.to_unit)
        self.conv_result = self.label("Wynik: —", 20, 42); self.content.add_widget(self.conv_result)
        self.content.add_widget(self.button("Przelicz", self.convert_units))
        self.content.add_widget(self.label("Wersja Android 1.2.0 zawiera przelicznik jednostek offline. Kursy walut nie należą do zakresu wydania 1.2.0.", 13, 75))

    def convert_units(self, *_):
        try:
            x = float(self.amount.text.replace(",", "."))
            a, b = self.from_unit.text, self.to_unit.text
            factors = {"mm":.001,"cm":.01,"m":1,"km":1000,"mg":.001,"g":1,"kg":1000}
            if a in factors and b in factors and ((a in ("mm","cm","m","km") and b in ("mm","cm","m","km")) or (a in ("mg","g","kg") and b in ("mg","g","kg"))):
                y = x * factors[a] / factors[b]
            elif a == "°C" and b == "°F": y = x*9/5+32
            elif a == "°F" and b == "°C": y = (x-32)*5/9
            elif a == b: y = x
            else: raise ValueError("Wybierz zgodne jednostki")
            self.conv_result.text = f"Wynik: {y:g} {b}"
        except Exception as e: self.conv_result.text = "Błąd: " + str(e)

    def page_equations(self):
        self.content.add_widget(self.label("Rozwiązywanie równań", 22, 40))
        self.content.add_widget(self.label("Równanie liniowe: ax + b = 0", 16, 32))
        self.a1 = self.textinput("a", "2"); self.b1 = self.textinput("b", "-8")
        self.content.add_widget(self.a1); self.content.add_widget(self.b1)
        self.linear_result = self.label("Wynik: —", 18, 42); self.content.add_widget(self.linear_result)
        self.content.add_widget(self.button("Rozwiąż liniowe", self.solve_linear))
        self.content.add_widget(self.label("Równanie kwadratowe: ax² + bx + c = 0", 16, 32))
        self.a2 = self.textinput("a", "1"); self.b2 = self.textinput("b", "-3"); self.c2 = self.textinput("c", "2")
        self.content.add_widget(self.a2); self.content.add_widget(self.b2); self.content.add_widget(self.c2)
        self.quad_result = self.label("Wynik: —", 18, 64); self.content.add_widget(self.quad_result)
        self.content.add_widget(self.button("Rozwiąż kwadratowe", self.solve_quadratic))

    def solve_linear(self, *_):
        try:
            a,b=float(self.a1.text),float(self.b1.text)
            if a == 0: ans = "Nieskończenie wiele rozwiązań" if b == 0 else "Brak rozwiązań"
            else: ans = f"x = {-b/a:g}"
            self.linear_result.text = ans
        except Exception: self.linear_result.text = "Podaj poprawne liczby"

    def solve_quadratic(self, *_):
        try:
            a,b,c=float(self.a2.text),float(self.b2.text),float(self.c2.text)
            if a == 0: self.quad_result.text = "a = 0: użyj równania liniowego"; return
            d=b*b-4*a*c
            if d < 0: ans = "Brak rozwiązań rzeczywistych"
            elif d == 0: ans = f"x = {-b/(2*a):g}"
            else: ans = f"x₁ = {(-b-math.sqrt(d))/(2*a):g}, x₂ = {(-b+math.sqrt(d))/(2*a):g}"
            self.quad_result.text = ans
        except Exception: self.quad_result.text = "Podaj poprawne liczby"

    def page_theme(self):
        self.content.add_widget(self.label("Wygląd aplikacji", 22, 40))
        spinner = Spinner(text=self.state.get("theme","Jasny"), values=("Jasny","Ciemny","Miętowy"), size_hint_y=None, height=dp(48))
        self.content.add_widget(spinner)
        self.content.add_widget(self.button("Zastosuj motyw", lambda *_: self.set_theme(spinner.text)))
        self.content.add_widget(self.label("Motyw zapisuje się i pozostaje po ponownym uruchomieniu.", 15, 45))

    def set_theme(self, theme):
        self.state["theme"] = theme; self.save_state(); self.apply_colors(); self.show_page("Motyw")

    def show_tutorial(self):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        box.add_widget(Label(text="Witaj w Nova Calculator MAX!\\n\\nWpisz działanie i naciśnij =. Użyj M+, M−, MR i MC do pamięci. Historia, motywy, przelicznik i równania są dostępne na górnych kartach.", halign="left"))
        p = Popup(title="Pierwsze uruchomienie", content=box, size_hint=(.9,.55), auto_dismiss=False)
        box.add_widget(self.button("Zaczynamy", lambda *_: self.finish_tutorial(p)))
        p.open()

    def finish_tutorial(self, popup):
        self.state["tutorial_seen"] = True; self.save_state(); popup.dismiss()

if __name__ == "__main__":
    NovaAndroid().run()
