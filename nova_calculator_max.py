import ast, math, operator, random, statistics, tkinter as tk, csv, json, urllib.request, urllib.parse, webbrowser, os
from datetime import datetime
from tkinter import ttk, filedialog, messagebox

PALETTES={
    'Neonowy niebieski': {'BG':'#10141f','PANEL':'#1a2130','BTN':'#29354a','BLUE':'#5b8cff','FG':'#f1f5ff','OUT':'#9abaff'},
    'Jasny': {'BG':'#f2f5fb','PANEL':'#ffffff','BTN':'#dce5f5','BLUE':'#2563eb','FG':'#172033','OUT':'#1d4ed8'},
    'Neonowy zielony': {'BG':'#0b1713','PANEL':'#14271f','BTN':'#214234','BLUE':'#22c55e','FG':'#effff5','OUT':'#86efac'},
    'Fioletowy': {'BG':'#171024','PANEL':'#251a38','BTN':'#3b2a55','BLUE':'#a855f7','FG':'#faf5ff','OUT':'#d8b4fe'},
}
APP_DIR=os.path.join(os.path.expanduser('~'), 'Documents', 'NovaCalculatorMAX')
MEMORIES_DIR=os.path.join(APP_DIR, 'Pamieci')
os.makedirs(MEMORIES_DIR, exist_ok=True)
SETTINGS_FILE=os.path.join(APP_DIR, 'settings.json')
HISTORY_FILE=os.path.join(MEMORIES_DIR, 'historia.json')
TUTORIAL_FILE=os.path.join(APP_DIR, 'samouczek_widziany.txt')
try:
    with open(SETTINGS_FILE, encoding='utf-8') as f: SETTINGS=json.load(f)
except Exception: SETTINGS={}
THEME_NAME=SETTINGS.get('theme','Neonowy niebieski')
if THEME_NAME not in PALETTES: THEME_NAME='Neonowy niebieski'
BG=PALETTES[THEME_NAME]['BG']; PANEL=PALETTES[THEME_NAME]['PANEL']; BTN=PALETTES[THEME_NAME]['BTN']; BLUE=PALETTES[THEME_NAME]['BLUE']; FG=PALETTES[THEME_NAME]['FG']; OUT=PALETTES[THEME_NAME]['OUT']
try:
    with open(HISTORY_FILE, encoding='utf-8') as f: HISTORY=json.load(f)
    if not isinstance(HISTORY,list): HISTORY=[]
except Exception: HISTORY=[]
HISTORY=HISTORY[-500:]
MEMORY=float(SETTINGS.get('memory',0.0) or 0.0)
LAST_NUMERIC_RESULT=None

def save_settings():
    try:
        with open(SETTINGS_FILE,'w',encoding='utf-8') as f:
            json.dump({'theme':THEME_NAME,'memory':MEMORY},f,ensure_ascii=False,indent=2)
    except Exception: pass

def save_history():
    try:
        with open(HISTORY_FILE,'w',encoding='utf-8') as f: json.dump(HISTORY[-500:],f,ensure_ascii=False,indent=2)
    except Exception: pass

def reload_all_memories():
    # Ponownie odczytuje wszystkie pliki JSON z folderu Pamieci.
    global HISTORY
    items=[]
    try:
        for name in os.listdir(MEMORIES_DIR):
            if not name.lower().endswith('.json'): continue
            try:
                with open(os.path.join(MEMORIES_DIR,name),encoding='utf-8') as f: data=json.load(f)
                if isinstance(data,list): items.extend(str(x) for x in data)
            except Exception: continue
        HISTORY=items[-500:]
        save_history()
    except Exception: pass
OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow,ast.Mod:operator.mod,ast.FloorDiv:operator.floordiv}
FUN={'sqrt':math.sqrt,'abs':abs,'round':round,'floor':math.floor,'ceil':math.ceil,'sin':math.sin,'cos':math.cos,'tan':math.tan,'asin':math.asin,'acos':math.acos,'atan':math.atan,'ln':math.log,'log':math.log10,'exp':math.exp,'factorial':math.factorial,'degrees':math.degrees,'radians':math.radians,'sinh':math.sinh,'cosh':math.cosh,'tanh':math.tanh,'pi':math.pi,'e':math.e}
def calc(s, extra=None):
    tree=ast.parse(s.replace('^','**').replace('×','*').replace('÷','/'),mode='eval'); names=dict(FUN); names.update(extra or {})
    def ev(n):
        if isinstance(n,ast.Expression): return ev(n.body)
        if isinstance(n,ast.Constant) and type(n.value) in (int,float): return n.value
        if isinstance(n,ast.Name) and n.id in names: return names[n.id]
        if isinstance(n,ast.BinOp) and type(n.op) in OPS:
            a,b=ev(n.left),ev(n.right)
            if isinstance(n.op,ast.Pow) and abs(b)>1000: raise ValueError('Za duży wykładnik')
            return OPS[type(n.op)](a,b)
        if isinstance(n,ast.UnaryOp):
            v=ev(n.operand)
            if isinstance(n.op,ast.USub): return -v
            if isinstance(n.op,ast.UAdd): return v
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and callable(names.get(n.func.id)) and n.func.id not in ('pi','e'): return names[n.func.id](*(ev(a) for a in n.args))
        raise ValueError('Nieobsługiwane wyrażenie')
    out=ev(tree)
    if isinstance(out,complex) or isinstance(out,float) and not math.isfinite(out): raise ValueError('Wynik poza zakresem')
    return out
UNITS={
'Długość':{'mm':.001,'cm':.01,'m':1,'km':1000,'cale':.0254,'stopy':.3048,'mile':1609.344},
'Powierzchnia':{'cm²':.0001,'m²':1,'km²':1e6,'hektary':10000},
'Objętość':{'ml':1e-6,'l':.001,'m³':1,'cm³':1e-6,'galon US':.003785411784},
'Masa':{'mg':1e-6,'g':.001,'kg':1,'tona':1000,'funt':.45359237,'uncja':.0283495},
'Czas':{'ms':.001,'sekundy':1,'minuty':60,'godziny':3600,'dni':86400},
'Prędkość':{'m/s':1,'km/h':1/3.6,'mph':.44704,'węzły':.514444},
'Ciśnienie':{'Pa':1,'kPa':1000,'MPa':1e6,'bar':100000,'atm':101325,'psi':6894.757},
'Energia':{'J':1,'kJ':1000,'MJ':1e6,'Wh':3600,'kWh':3600000,'cal':4.184,'kcal':4184},
'Moc':{'W':1,'kW':1000,'MW':1e6,'KM':735.499,'hp':745.7},
'Dane komputerowe':{'bit':1,'bajt':8,'KB':8000,'MB':8e6,'GB':8e9,'TB':8e12,'KiB':8192,'MiB':8388608,'GiB':8589934592},
'Kąt':{'stopnie':1,'radiany':180/math.pi,'grady':.9},'Przyspieszenie':{'m/s²':1,'g ziemskie':9.80665},
'Częstotliwość':{'Hz':1,'kHz':1000,'MHz':1e6,'GHz':1e9},'Siła':{'N':1,'kN':1000,'kgf':9.80665,'lbf':4.44822}}
def convert(cat,v,a,b):
    if cat=='Temperatura':
        c=v if a=='°C' else (v-32)*5/9 if a=='°F' else v-273.15
        return c if b=='°C' else c*9/5+32 if b=='°F' else c+273.15
    if cat=='Zużycie paliwa':
        if v<=0: raise ValueError('Wartość musi być dodatnia')
        return v if a==b else 100/v
    return v*UNITS[cat][a]/UNITS[cat][b]
root=tk.Tk(); root.title('Nova Calculator MAX'); root.geometry('1050x740'); root.minsize(850,600); root.configure(bg=BG)
try:
    root.iconbitmap(os.path.join(os.path.dirname(__file__), 'nova_icon.ico'))
except Exception: pass
st=ttk.Style(); st.theme_use('clam'); st.configure('TNotebook',background=BG,borderwidth=0); st.configure('TNotebook.Tab',background=PANEL,foreground=FG,padding=(11,8)); st.map('TNotebook.Tab',background=[('selected',BLUE)]); st.configure('TLabel',background=BG,foreground=FG); st.configure('TCombobox',fieldbackground=PANEL,background=PANEL,foreground=FG); st.configure('TNotebook.Tab',background=PANEL,foreground=FG)
nb=ttk.Notebook(root); nb.pack(fill='both',expand=True,padx=10,pady=10)
def tab(name):
 f=tk.Frame(nb,bg=BG); nb.add(f,text=name); return f
def heading(p,s): tk.Label(p,text=s,bg=BG,fg=FG,font=('Segoe UI',18,'bold')).pack(pady=(12,8))
def ent(p,s='',w=38):
 e=tk.Entry(p,width=w,font=('Segoe UI',12),bg=PANEL,fg=FG,insertbackground=FG,relief='flat'); e.insert(0,s); e.pack(padx=8,pady=4,ipady=5); return e
def out(p):
 x=tk.Label(p,text='',bg=BG,fg=OUT,font=('Segoe UI',12),wraplength=900,justify='left'); x.pack(pady=5); return x
def btn(p,s,fn): return tk.Button(p,text=s,command=fn,bg=BLUE,fg='white',activebackground='#7da2ff',relief='flat',padx=10,pady=5,font=('Segoe UI',10,'bold'))
def log(s):
 HISTORY.append(f'[{datetime.now():%Y-%m-%d %H:%M:%S}] {s}'); del HISTORY[:-500]; save_history()

# Kalkulator
t=tab('Kalkulator'); heading(t,'Nova Calculator MAX'); mode=tk.StringVar(value='Normalny'); ttk.Combobox(t,textvariable=mode,values=['Normalny','Porównawczy','Naukowy','Programistyczny'],state='readonly',width=22).pack(pady=3)
expr=ent(t,'2+2',45); calc_out=out(t)
memrow=tk.Frame(t,bg=BG); memrow.pack(pady=3)
memlabel=tk.Label(memrow,text='Pamięć: 0',bg=BG,fg=OUT,font=('Segoe UI',10,'bold')); memlabel.pack(side='left',padx=5)
def update_memory_label(): memlabel.config(text=f'Pamięć: {MEMORY:g}')
def memory_add():
 global MEMORY
 if LAST_NUMERIC_RESULT is None: calc_out.config(text='Najpierw wykonaj działanie dające wynik liczbowy.'); return
 MEMORY+=LAST_NUMERIC_RESULT; save_settings(); update_memory_label(); calc_out.config(text=f'Dodano {LAST_NUMERIC_RESULT:g} do pamięci. Pamięć = {MEMORY:g}')
def memory_subtract():
 global MEMORY
 if LAST_NUMERIC_RESULT is None: calc_out.config(text='Najpierw wykonaj działanie dające wynik liczbowy.'); return
 MEMORY-=LAST_NUMERIC_RESULT; save_settings(); update_memory_label(); calc_out.config(text=f'Odjęto {LAST_NUMERIC_RESULT:g} od pamięci. Pamięć = {MEMORY:g}')
def memory_recall():
 expr.delete(0,'end'); expr.insert(0,f'{MEMORY:g}'); calc_out.config(text=f'Przywrócono z pamięci: {MEMORY:g}')
def memory_clear():
 global MEMORY
 MEMORY=0.0; save_settings(); update_memory_label(); calc_out.config(text='Pamięć wyczyszczona.')
for label,fn in [('M+',memory_add),('M−',memory_subtract),('MR',memory_recall),('MC',memory_clear)]: btn(memrow,label,fn).pack(side='left',padx=3)
update_memory_label()
hist=tk.Text(t,height=4,bg=PANEL,fg=FG,relief='flat'); hist.pack(fill='x',padx=16,pady=5)
def calculate():
 global LAST_NUMERIC_RESULT
 try:
  s=expr.get().strip()
  if mode.get()=='Porównawczy':
   p=s.split(';')
   if len(p)!=2: raise ValueError('Podaj dwa wyrażenia rozdzielone średnikiem, np. 5+2;8')
   a,b=calc(p[0]),calc(p[1]); rel='jest równe' if a==b else 'jest większe od' if a>b else 'jest mniejsze od'; ans=f'{a} {rel} {b}'
  elif mode.get()=='Programistyczny':
   n=int(calc(s)); ans=f'Dziesięcznie: {n}\nBinarnie: {bin(n)}\nÓsemkowo: {oct(n)}\nSzesnastkowo: {hex(n)}'
  else: ans=str(calc(s))
  if mode.get()!='Programistyczny' and mode.get()!='Porównawczy':
   try: LAST_NUMERIC_RESULT=float(ans)
   except Exception: LAST_NUMERIC_RESULT=None
  else: LAST_NUMERIC_RESULT=None
  calc_out.config(text='Wynik: '+ans); log(f'{s} = {ans}'); hist.config(state='normal'); hist.insert('end',f'{s} = {ans}\n'); hist.see('end'); hist.config(state='disabled')
 except Exception as e: calc_out.config(text='Błąd: '+str(e))
keys=['7','8','9','/','sqrt(','sin(','4','5','6','*','^','cos(','1','2','3','-','(', 'tan(','0','.','(',')','+','pi','ln(','log(','factorial(','abs(','e','Wyczyść']
kb=tk.Frame(t,bg=BG); kb.pack()
for i,k in enumerate(keys):
 def act(v=k): expr.delete(0,'end') if v=='Wyczyść' else expr.insert('end',v)
 tk.Button(kb,text=k,command=act,bg=BTN,fg=FG,relief='flat',width=9).grid(row=i//6,column=i%6,padx=2,pady=2)
btn(t,'OBLICZ',calculate).pack(pady=5)

# Konwerter
t=tab('Konwerter'); heading(t,'Konwerter jednostek'); cats=list(UNITS)+['Temperatura','Zużycie paliwa']; cv=tk.StringVar(value='Długość'); sv=tk.StringVar(); dv=tk.StringVar(); ttk.Label(t,text='Rodzaj wielkości').pack(); cb=ttk.Combobox(t,textvariable=cv,values=cats,state='readonly',width=28); cb.pack(pady=3); tk.Label(t,text='Wartość').pack(); ve=ent(t,'100',20); tk.Label(t,text='Z jednostki').pack(); sb=ttk.Combobox(t,textvariable=sv,state='readonly',width=28); sb.pack(pady=3); tk.Label(t,text='Na jednostkę').pack(); db=ttk.Combobox(t,textvariable=dv,state='readonly',width=28); db.pack(pady=3); co=out(t)
def refresh(*_):
 u=['°C','°F','K'] if cv.get()=='Temperatura' else ['l/100 km','km/l'] if cv.get()=='Zużycie paliwa' else list(UNITS[cv.get()]); sb['values']=u; db['values']=u; sv.set(u[0]); dv.set(u[1] if len(u)>1 else u[0])
def do_convert():
 try:
  v=float(ve.get().replace(',','.')); a=convert(cv.get(),v,sv.get(),dv.get()); co.config(text=f'{v:g} {sv.get()} = {a:.10g} {dv.get()}'); log(co.cget('text'))
 except Exception as e: co.config(text='Błąd: '+str(e))
cb.bind('<<ComboboxSelected>>',refresh); refresh(); btn(t,'PRZELICZ',do_convert).pack(pady=5)

# Dane i pliki
t=tab('Dane i pliki'); heading(t,'Analiza danych i otwieranie plików'); din=ent(t,'10, 20, 30, 40, 50',45); dout=out(t)
def analyze():
 try:
  ns=[float(x) for x in din.get().replace(',',' ').replace(';',' ').split()];
  if not ns: raise ValueError('Wpisz liczby')
  s=f'Liczba: {len(ns)}\nSuma: {sum(ns):g}\nŚrednia: {statistics.mean(ns):g}\nMediana: {statistics.median(ns):g}\nMin: {min(ns):g}\nMax: {max(ns):g}'; s+=f'\nOdchylenie standardowe: {statistics.stdev(ns):g}' if len(ns)>1 else ''; dout.config(text=s); log(s)
 except Exception as e: dout.config(text='Błąd: '+str(e))
btn(t,'ANALIZUJ LICZBY',analyze).pack(pady=3); fileview=tk.Text(t,height=12,bg=PANEL,fg=FG,wrap='word',relief='flat'); fileview.pack(fill='both',expand=True,padx=14,pady=5)
def openfile():
 p=filedialog.askopenfilename(filetypes=[('Dane','*.csv *.txt *.xlsx'),('Wszystkie pliki','*.*')]);
 if not p:return
 try:
  if p.lower().endswith('.xlsx'):
   import openpyxl
   wb=openpyxl.load_workbook(p,read_only=True,data_only=True); rows=list(wb.active.iter_rows(values_only=True))[:100]; text='\n'.join(' | '.join('' if v is None else str(v) for v in r) for r in rows); wb.close()
  elif p.lower().endswith('.csv'):
   with open(p,encoding='utf-8-sig',newline='') as f: text='\n'.join(' | '.join(r) for r in list(csv.reader(f))[:200])
  else:
   with open(p,encoding='utf-8-sig') as f: text=f.read(30000)
  fileview.delete('1.0','end'); fileview.insert('end',text); log('Otwarto plik '+p)
 except ImportError: messagebox.showerror('Brak biblioteki','Do Excela zainstaluj: py -m pip install openpyxl')
 except Exception as e: messagebox.showerror('Błąd pliku',str(e))
btn(t,'OTWÓRZ CSV / EXCEL / TXT',openfile).pack(pady=3)

# Wykresy
t=tab('Wykresy'); heading(t,'Rysowanie wykresów'); gi=ent(t,'x**2',30); gout=out(t)
def graph():
 try:
  import numpy as np, matplotlib.pyplot as plt
  xs=np.linspace(-10,10,500); ys=[]
  for x in xs:
   try: ys.append(float(calc(gi.get(),{'x':float(x)})))
   except Exception: ys.append(float('nan'))
  plt.figure('Nova Calculator MAX'); plt.plot(xs,ys,label='y = '+gi.get()); plt.axhline(0,linewidth=.7); plt.axvline(0,linewidth=.7); plt.grid(True); plt.legend(); plt.show(); gout.config(text='Wykres otworzono w osobnym oknie.')
 except Exception as e: gout.config(text='Błąd: '+str(e)+'; zainstaluj numpy i matplotlib.')
btn(t,'RYSUJ WYKRES',graph).pack(pady=5)

# Równania
t=tab('Równania'); heading(t,'Rozwiązywanie równań')
tk.Label(t,text='Równanie liniowe w postaci wyrażenie = wyrażenie (użyj x), np. 2*x+4=10',bg=BG,fg=FG,wraplength=850).pack()
eqin=ent(t,'2*x+4=10',35); eqout=out(t)
def solve_equation():
 try:
  parts=eqin.get().replace('−','-').split('=')
  if len(parts)!=2: raise ValueError('Wpisz dokładnie jeden znak =, np. 2*x+4=10')
  left,right=[x.strip() for x in parts]
  def f(x): return float(calc(left,{'x':x}))-float(calc(right,{'x':x}))
  y0,y1,y2=f(0),f(1),f(2); a=y1-y0
  if abs(a)<1e-12:
   if abs(y0)<1e-12: result='Równanie ma nieskończenie wiele rozwiązań (w sprawdzonym zakresie).'
   else: result='Brak rozwiązań.'
  else:
   x=-y0/a
   if abs(f(2)-(y0+2*a))>1e-7*max(1,abs(y2)): raise ValueError('To nie wygląda na równanie liniowe. Użyj niżej kalkulatora równań kwadratowych.')
   result=f'x = {x:g}'
  eqout.config(text=result); log('Równanie '+eqin.get()+' → '+result)
 except Exception as e: eqout.config(text='Błąd: '+str(e))
btn(t,'ROZWIĄŻ RÓWNANIE',solve_equation).pack(pady=3)
tk.Label(t,text='Liniowe współczynnikami: a*x + b = 0',bg=BG,fg=FG).pack(pady=(10,0)); ea=ent(t,'2',15); eb=ent(t,'5',15); eo=out(t)
def linear():
 try:
  a=float(ea.get().replace(',','.')); b=float(eb.get().replace(',','.')); s=('Brak rozwiązań' if b else 'Nieskończenie wiele rozwiązań') if a==0 else f'x = {-b/a:g}'; eo.config(text=s); log(s)
 except Exception as e: eo.config(text=str(e))
btn(t,'ROZWIĄŻ LINIOWE',linear).pack(pady=3); tk.Label(t,text='Kwadratowe: a*x² + b*x + c = 0',bg=BG,fg=FG).pack(pady=(10,2)); qa=ent(t,'1',15); qb=ent(t,'-3',15); qc=ent(t,'2',15); qo=out(t)
def quadratic():
 try:
  a,b,c=[float(e.get().replace(',','.')) for e in (qa,qb,qc)]
  if a==0: raise ValueError('a nie może być zerem')
  d=b*b-4*a*c; s=f'Delta = {d:g}\n'
  if d<0:s+='Brak rozwiązań rzeczywistych'
  elif d==0:s+=f'x = {-b/(2*a):g}'
  else:s+=f'x₁ = {(-b-math.sqrt(d))/(2*a):g}\nx₂ = {(-b+math.sqrt(d))/(2*a):g}'
  qo.config(text=s); log(s)
 except Exception as e: qo.config(text='Błąd: '+str(e))
btn(t,'ROZWIĄŻ KWADRATOWE',quadratic).pack(pady=3)

# Fizyka i elektryczność
t=tab('Fizyka i prąd'); heading(t,'Fizyka i elektryczność'); pm=tk.StringVar(value='Prawo Ohma'); ttk.Combobox(t,textvariable=pm,values=['Prawo Ohma','Moc elektryczna','Energia elektryczna','Siła','Ciśnienie','Gęstość','Prędkość'],state='readonly',width=25).pack(pady=4); tk.Label(t,text='Wartości A i B — opisy jednostek pojawią się w wyniku.',bg=BG,fg=FG).pack(); pa=ent(t,'12',18); pb=ent(t,'2',18); po=out(t)
def physics():
 try:
  a=float(pa.get().replace(',','.')); b=float(pb.get().replace(',','.')); m=pm.get()
  if m=='Prawo Ohma':
   if b==0: raise ValueError('Opór nie może być zerem')
   s=f'I = U/R = {a/b:g} A (A=napięcie V, B=opór Ω)'
  elif m=='Moc elektryczna': s=f'P = U·I = {a*b:g} W (A=napięcie V, B=prąd A)'
  elif m=='Energia elektryczna': s=f'E = P·t = {a*b:g} Wh (A=moc W, B=czas h)'
  elif m=='Siła': s=f'F = m·a = {a*b:g} N (A=masa kg, B=przyspieszenie m/s²)'
  elif m=='Ciśnienie':
   if b==0: raise ValueError('Pole nie może być zerem')
   s=f'p = F/S = {a/b:g} Pa (A=siła N, B=pole m²)'
  elif m=='Gęstość':
   if b==0: raise ValueError('Objętość nie może być zerem')
   s=f'ρ = m/V = {a/b:g} kg/m³ (A=masa kg, B=objętość m³)'
  else:
   if b==0: raise ValueError('Czas nie może być zerem')
   s=f'v = s/t = {a/b:g} m/s (A=droga m, B=czas s)'
  po.config(text=s); log(s)
 except Exception as e: po.config(text='Błąd: '+str(e))
btn(t,'OBLICZ',physics).pack(pady=5)

# Internet i waluty
t=tab('Internet i waluty'); heading(t,'Google, odczyt stron i kursy walut'); qi=ent(t,'kurs euro PLN',40)
def google():
 if qi.get().strip(): webbrowser.open('https://www.google.com/search?q='+urllib.parse.quote(qi.get().strip()))
btn(t,'SZUKAJ W GOOGLE',google).pack(pady=3); tk.Label(t,text='Kursy online (Frankfurter API)',bg=BG,fg=FG).pack(pady=(8,2)); cf=tk.StringVar(value='EUR'); ct=tk.StringVar(value='PLN'); row=tk.Frame(t,bg=BG); row.pack(); vals=['PLN','EUR','USD','GBP','CHF','CZK','UAH','JPY']
for var in (cf,ct): ttk.Combobox(row,textvariable=var,values=vals,state='readonly',width=8).pack(side='left',padx=4)
amount=ent(t,'1',15); currencyout=out(t)
def rate():
 try:
  a,b=cf.get(),ct.get()
  if a==b: currencyout.config(text=f'1 {a} = 1 {b}'); return
  url=f'https://api.frankfurter.app/latest?from={a}&to={b}'
  with urllib.request.urlopen(url,timeout=8) as r: d=json.loads(r.read().decode())
  n=float(amount.get().replace(',','.')); k=d['rates'][b]; s=f'Data kursu: {d["date"]}\n1 {a} = {k:g} {b}\n{n:g} {a} = {n*k:.6g} {b}'; currencyout.config(text=s); log(s)
 except Exception as e: currencyout.config(text='Nie udało się pobrać kursu. Sprawdź internet. '+str(e))
btn(t,'POBIERZ KURS I PRZELICZ',rate).pack(pady=3); tk.Label(t,text='Adres strony do odczytania tekstu:',bg=BG,fg=FG).pack(pady=(7,1)); urlin=ent(t,'https://example.com',45); page=tk.Text(t,height=8,bg=PANEL,fg=FG,wrap='word',relief='flat'); page.pack(fill='both',expand=True,padx=12,pady=5)
def readpage():
 try:
  u=urlin.get().strip(); p=urllib.parse.urlparse(u)
  if p.scheme not in ('http','https') or not p.netloc: raise ValueError('Wpisz pełny adres https://')
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=10) as r: s=r.read(1000000).decode('utf-8',errors='replace')
  import re
  s=re.sub(r'(?is)<(script|style).*?>.*?</\1>',' ',s); s=re.sub(r'(?s)<[^>]+>',' ',s); s=re.sub(r'\s+',' ',s)
  page.delete('1.0','end'); page.insert('end',s[:10000])
 except Exception as e: page.delete('1.0','end'); page.insert('end','Nie udało się odczytać strony: '+str(e))
btn(t,'ODCZYTAJ STRONĘ',readpage).pack(pady=3)

# Narzędzia
t=tab('Narzędzia'); heading(t,'Procenty, losowanie i daty'); tk.Label(t,text='Procent z liczby: procent oraz liczba',bg=BG,fg=FG).pack(); pct=ent(t,'15',15); base=ent(t,'200',15); pco=out(t)
def percent():
 try:
  s=f'{float(pct.get().replace(",",".")):g}% z {float(base.get().replace(",",".")):g} = {float(pct.get().replace(",","."))*float(base.get().replace(",","."))/100:g}'; pco.config(text=s); log(s)
 except Exception as e:pco.config(text=str(e))
btn(t,'OBLICZ PROCENT',percent).pack(pady=3); tk.Label(t,text='Losuj liczbę całkowitą',bg=BG,fg=FG).pack(pady=(8,1)); rmin=ent(t,'1',15); rmax=ent(t,'100',15); ro=out(t)
def rand():
 try:
  a,b=int(rmin.get()),int(rmax.get())
  if a>b: raise ValueError('Początek zakresu jest większy niż koniec')
  s=f'Wylosowano: {random.randint(a,b)}'; ro.config(text=s); log(s)
 except Exception as e:ro.config(text=str(e))
btn(t,'LOSUJ',rand).pack(pady=3); tk.Label(t,text='Różnica między datami (format RRRR-MM-DD)',bg=BG,fg=FG).pack(pady=(8,1)); d1=ent(t,datetime.now().strftime('%Y-%m-%d'),18); d2=ent(t,datetime.now().strftime('%Y-%m-%d'),18); do=out(t)
def dates():
 try:
  a=datetime.strptime(d1.get(),'%Y-%m-%d').date(); b=datetime.strptime(d2.get(),'%Y-%m-%d').date(); s=f'Różnica: {abs((b-a).days)} dni'; do.config(text=s); log(s)
 except Exception:do.config(text='Wpisz daty jako RRRR-MM-DD')
btn(t,'OBLICZ DNI',dates).pack(pady=3)

# Historia
t=tab('Historia'); heading(t,'Historia i zapisywanie wyników'); hv=tk.Text(t,bg=PANEL,fg=FG,wrap='word',relief='flat'); hv.pack(fill='both',expand=True,padx=12,pady=7)
def showhist():
 reload_all_memories(); hv.delete('1.0','end'); hv.insert('end','\n'.join(HISTORY) if HISTORY else 'Historia jest pusta.')
def savehist():
 reload_all_memories()
 save_history()
 messagebox.showinfo('Zapisano',f'Historia jest zapisana automatycznie w folderze:\n{MEMORIES_DIR}')
showhist()
btn(t,'ODŚWIEŻ HISTORIĘ',showhist).pack(side='left',padx=15,pady=6); btn(t,'ZAPISZ HISTORIĘ',savehist).pack(side='left',padx=5,pady=6)
# Motywy i kolory

def apply_theme(name):
 global THEME_NAME, BG, PANEL, BTN, BLUE, FG, OUT
 if name not in PALETTES: return
 THEME_NAME=name; pal=PALETTES[name]; BG=pal['BG']; PANEL=pal['PANEL']; BTN=pal['BTN']; BLUE=pal['BLUE']; FG=pal['FG']; OUT=pal['OUT']
 root.configure(bg=BG)
 st.configure('TNotebook',background=BG); st.configure('TNotebook.Tab',background=PANEL,foreground=FG,padding=(11,8)); st.map('TNotebook.Tab',background=[('selected',BLUE)],foreground=[('selected',FG)])
 st.configure('TLabel',background=BG,foreground=FG); st.configure('TCombobox',fieldbackground=PANEL,background=PANEL,foreground=FG)
 def recolor(w):
  try:
   if isinstance(w,tk.Frame): w.configure(bg=BG)
   elif isinstance(w,tk.Label): w.configure(bg=BG,fg=OUT if w.cget('font') and 'bold' in str(w.cget('font')) else FG)
   elif isinstance(w,tk.Entry): w.configure(bg=PANEL,fg=FG,insertbackground=FG)
   elif isinstance(w,tk.Text): w.configure(bg=PANEL,fg=FG,insertbackground=FG)
   elif isinstance(w,tk.Button): w.configure(bg=BLUE if w.cget('command') else BTN,fg='white' if name!='Jasny' else '#ffffff',activebackground=BTN)
  except tk.TclError: pass
  for child in w.winfo_children(): recolor(child)
 recolor(root); save_settings()

# Osobna karta ustawień wyglądu
t=tab('Wygląd'); heading(t,'Motywy i kolory')
theme_row=tk.Frame(t,bg=BG); theme_row.pack(pady=(10,5))
tk.Label(theme_row,text='Motyw kolorystyczny:',bg=BG,fg=FG).pack(side='left',padx=5)
theme_var=tk.StringVar(value=THEME_NAME)
theme_box=ttk.Combobox(theme_row,textvariable=theme_var,values=list(PALETTES),state='readonly',width=22); theme_box.pack(side='left',padx=5)
theme_box.bind('<<ComboboxSelected>>',lambda _ : apply_theme(theme_var.get()))
def first_run_tutorial():
 if os.path.exists(TUTORIAL_FILE): return
 messagebox.showinfo('Witaj w Nova Calculator MAX', 'Witaj! To krótkie wprowadzenie do programu.\n\n• Kalkulator: wpisz działanie i kliknij OBLICZ.\n• M+, M−, MR, MC: pamięć wyniku.\n• Konwerter: wybierz jednostki i przelicz.\n• Równania: wpisz równanie i użyj narzędzi.\n• Historia: obliczenia zapisują się automatycznie. Kliknij ODŚWIEŻ HISTORIĘ, aby ponownie odczytać zapisane pliki.\n• Motywy: wybierz wygląd w zakładce ustawień.\n\nFolder pamięci: ' + MEMORIES_DIR)
 try:
  with open(TUTORIAL_FILE,'w',encoding='utf-8') as f: f.write('shown')
 except Exception: pass
root.after(500, first_run_tutorial)
root.mainloop()
