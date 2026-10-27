# Nova Calculator MAX 1.2.0 — Android (projekt źródłowy)

To jest mobilna implementacja inspirowana zakresem funkcji wydania Windows 1.2.0:
- kalkulator z podstawowymi działaniami i bezpiecznym liczeniem wyrażeń,
- pamięć M+, M−, MR, MC,
- historia obliczeń zapisywana lokalnie,
- trzy motywy: jasny, ciemny i miętowy,
- przelicznik jednostek offline (długość, masa, temperatura),
- rozwiązywanie równań liniowych i kwadratowych,
- krótki samouczek przy pierwszym uruchomieniu.

## Ważne ograniczenie
Nie udało się pobrać źródeł repozytorium GitHub w środowisku tworzenia plików, więc ten projekt jest osobną implementacją mobilną opartą na opisie funkcji wydania v1.2.0, a nie bezpośrednią konwersją oryginalnego pliku Tkinter. Nie zbudowano ani nie przetestowano APK na urządzeniu Android w tym środowisku. Wydanie Windows 1.2.0 opisuje też konwerter jednostek, a nie walut.

## Budowanie APK w Windows przez WSL (Ubuntu)
Buildozer działa w Linux/macOS; w Windows użyj WSL2 z Ubuntu.

1. Zainstaluj WSL2 i Ubuntu (PowerShell jako administrator):
   `wsl --install -d Ubuntu`
   Uruchom Ubuntu z menu Start i dokończ konfigurację konta.
2. Skopiuj rozpakowany folder projektu do katalogu domowego Ubuntu, np. `~/NovaCalculatorMAX_Android`.
   Najlepiej nie budować bezpośrednio z `/mnt/c`, bo kompilacja może być wolniejsza.
3. W Ubuntu przejdź do folderu projektu:
   `cd ~/NovaCalculatorMAX_Android`
4. Zainstaluj wymagania systemowe:
   `sudo apt update`
   `sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-virtualenv \
     autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
     libtinfo6 cmake libffi-dev libssl-dev automake autopoint gettext`
5. Utwórz środowisko i zainstaluj Buildozer:
   `python3 -m venv .venv`
   `source .venv/bin/activate`
   `pip install --upgrade pip setuptools wheel`
   `pip install buildozer cython`
6. Sprawdź plik `buildozer.spec`, a potem uruchom:
   `buildozer -v android debug`
   Przy pierwszym uruchomieniu Buildozer pobierze Android SDK/NDK i inne narzędzia; może to potrwać długo i wymaga internetu.
7. Gotowy plik APK powinien pojawić się w katalogu `bin/`.
8. Skopiuj APK do Windows, np. przez Eksplorator plików do `\\wsl.localhost\Ubuntu\home\<twoj_uzytkownik>\NovaCalculatorMAX_Android\bin\`.
9. Przenieś APK na telefon i otwórz plik. Android może poprosić o zezwolenie na instalowanie aplikacji z danego źródła.

## Gdy kompilacja się nie uda
- Zapisz cały końcowy komunikat błędu z terminala.
- W przypadku błędu zależności sprawdź aktualne instrukcje: https://github.com/kivy/buildozer/blob/master/docs/source/installation.rst
- Oficjalny przewodnik Kivy: https://kivy.org/doc/stable/guide/packaging-android.html

## Testy ręczne po instalacji
1. Wpisz `12*(3+4)` i naciśnij `=`, wynik powinien być `84`.
2. Wpisz `10`, naciśnij M+, potem MC; pamięć powinna się wyzerować.
3. Oblicz kilka działań, otwórz Historię, zamknij i uruchom aplikację ponownie.
4. Zmień motyw na Ciemny i uruchom aplikację ponownie.
5. Przelicz `1 km` na `m`, a następnie sprawdź `0 °C` na `°F`.
6. Rozwiąż `2x - 8 = 0` (a=2, b=-8) i `x² - 3x + 2 = 0` (a=1, b=-3, c=2).

## Bezpieczeństwo
Kalkulator przyjmuje wyrażenia matematyczne przez ograniczony evaluator AST. Nie wykonuje dowolnego kodu Pythona.
