# SuttaFlow 2.0.0 — proces tłumaczenia

Aktywna wersja Standardu. Zapis zgody: prace/20261021-wydanie-reczne/OWNER_APPROVAL.md.

Ten dokument powstaje z RULE_REGISTRY.json. Zmiany wprowadza się w rejestrze; nie utrzymuje się osobnych ręcznie redagowanych instrukcji.

## Przebieg w skrócie

1. Odczytaj stan zadania, właściwą kolejkę i istniejące produkty. Ustal źródło, zakres i wersję kontraktu. Nie powtarzaj ukończonych etapów.
2. Dla nowego Pali-first odczytaj całe Pali i utrwal R0 przed kontrolnymi przekładami. Zamówiona rewizja zachowuje istniejące R0 i ekspozycję, bez udawania nowego ślepego początku. EN→PL HH opiera się na konkretnym angielskim źródle i zachowuje jego przypisy; kontrola Pali ma jawny faktyczny zakres. Dla innej tradycji lub pośrednika ustal język, świadectwo i kontroluj właściwą podstawę zgodnie z SRC-001. Bramy wierności, źródeł, redakcji i recenzji pozostają, bez fikcyjnej etykiety Pali-first.
3. Autor sprawdza całe znaczenie względem właściwej podstawy i całą polszczyznę. Odrębny redaktor opracowuje tekst, a autor sprawdza proponowane zmiany względem rzeczywistego źródła.
4. Świeży recenzent najpierw ocenia czysty przekład. Po zamrożeniu CORE ocenia aparat. Kontrole interpretacyjne mają odrębne czyste wejścia i raporty.
5. Zamknięty tekst zapisuje się w Markdown z jawnymi przypisami, strofami i wyróżnieniami pali. Po zbudowaniu PDF kontroluje się jego tekst i wygląd.
6. Dostawa nie jest zgodą publikacyjną. Zweryfikuj aktualne produkty na Dysku, zapisz LOG i uzgodnij QUEUE. Pełne dowody przechowuj poza dokumentem czytelniczym.
7. Audio i nowa odrębna praca tematyczna wymagają właściwego zlecenia. Obowiązkowe sprawdzenie i uzupełnienie relewantnych istniejących dossier po DONE jest dokumentacją dostawy, nie nowym tłumaczeniem ani dowolną zmianą kolejki.
8. Dokładną wersję aktywuje jeden wykonawca po wymaganych dowodach, recenzjach i świadomej akceptacji właściciela; każdy zapis ma odczyt. Historię zachowuje się poza aktywnymi instrukcjami.

## 1. Start, zakres i wznowienie

Odczytaj stan zadania, właściwą kolejkę i istniejące produkty. Ustal źródło, zakres i wersję kontraktu. Nie powtarzaj ukończonych etapów.

**Odpowiedzialność:** Operator

**Wejście:** Zlecenie, aktywny kontrakt, bieżące QUEUE/LOG i istniejące wersje.

**Produkt i zakończenie:** Identyfikator, zakres, checkpoint i piny wejść.

**Zatrzymanie:** Sprzeczna kolejka lub nieustalona wersja: uzgodnić bez nadpisywania.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-GOV-001 — Wersja i odrębna aktywacja

Zakres: SUTTA, VINAYA.

Kontrakt 2.0.0 porządkuje proces tłumaczenia i dostawy sutt. Pierwsze wydanie stosuje kontrolowaną aktywację przez jednego wykonawcę; automatyczny koordynator Git/Docs pozostaje nieaktywny. Aktywacja wymaga świadomej akceptacji dokładnej wersji i zakresu zmian, zachowanego manifestu oraz odczytu po zapisach. Do potwierdzonej aktywacji obowiązuje Standard 1.13. Polecenie uproszczenia trybu wydania nie jest samo w sobie akceptacją nieprzedstawionego manifestu ani zgodą na publikację lub nagranie sutt.

### SF-RULE-GOV-002 — Zakres pierwszeństwa

Zakres: SUTTA, VINAYA.

Uwzględniać udokumentowane decyzje właściciela, rzeczywisty zamrożony kontrakt konkretnego zadania w jego zakresie i obowiązujący Standard. Nie tworzyć nowej, bezwarunkowej drabiny pierwszeństwa na podstawie projektu N2. Zatwierdzony K1 jest rozstrzygający w zakresie wyglądu, ról typograficznych i układu czytelniczego produktu. Konflikt decyzji z normą wymaga zapisania obu podstaw, zakresu i zależnego działania; wykonawca nie ustanawia wyjątku. Rzeczywisty kontrakt musi mieć dowód przyjęcia, zakres, identyfikator i zamrożoną rewizję; nie może służyć obejściu ochrony produktu.

### SF-RULE-GOV-003 — Ochrona wszystkich wcześniejszych wersji

Zakres: SUTTA, VINAYA.

Nie usuwać, nadpisywać, przenosić ani archiwizować istniejących wersji bez dokładnego upoważnienia. Zatwierdzone MN 41 RC2.1, Dhp 1–20 R3, K1, archiwalne raporty i historia logu pozostają nienaruszone. Nowa kontrola, korekta lub migracja jest osobnym datowanym zdarzeniem. Zachować pierwotne ukończenie, historyczne DONE i zakres dawnych PASS; nie certyfikować ich retrospektywnie i nie rozciągać na nową rewizję. Zmiany badać na kopiach i syntetycznych danych.

### SF-RULE-GOV-004 — Trwałe decyzje i rozdział identyfikatorów

Zakres: SUTTA, VINAYA.

Zatwierdzenie wymaga rzeczywistego świadectwa właściciela, daty i zakresu. Zastosowanie rozwiązania przez AI ani polecenie naprawy dokumentacji nie zatwierdza terminologii. Używać kwalifikowanego ID decyzji: OWNER-20261011-STANDARD15-D4 oznacza bramę MN 53; N2-PROPOSAL-D4 oznacza propozycję statusu terminologii. T-01, T-01-SCOPE i T-02 są odrębnymi wpisami. Zachować dosłowne źródło decyzji i historię korekt; nie tworzyć podpisu ani zgody za właściciela.

### SF-RULE-GOV-005 — Prawdziwość dowodów

Zakres: SUTTA, VINAYA.

Oświadczenie, licznik, hash, etykieta FROZEN, przygotowany prompt lub pobrany plik nie dowodzą rzeczywistej recenzji. Rozróżniać wykonano, przeanalizowano, nie wykonano i BLOCKED; podawać rzeczywisty zakres, wykonawcę, źródło i rewizję. Nie wymyślać testu, cytatu, SHA-256, revisionId, zewnętrznej kotwicy ani dostępu. Własny przegląd konstrukcyjny RC nie jest niezależnym audytem tego RC.

### SF-RULE-OPS-001 — Wyzwalacze i pełny zakres zadania

Zakres: SUTTA, VINAYA.

Sam numer sutty, np. MN 21, SN 22.59, AN 4.55 lub DN 2, uruchamia workflow SuttaFlow, o ile kontekst nie ogranicza zlecenia. Identyfikator Vinayi (np. Mv V.1, Cv lub konkretna reguła) uruchamia VinayaFlow. Nie wymagać przeniesienia do innej aplikacji, gdy pracę można wykonać w bieżącym czacie. Ustalić identyfikator, tytuł i cały zakres; odróżnić przekład, EN→PL HH, Themes i osobno zamówione audio.

### SF-RULE-OPS-002 — Start i wznowienie na realnym stanie

Zakres: SUTTA, VINAYA.

Przed startem odczytać aktualny Standard, QUEUE, relewantny LOG, rejestr terminologii i decyzji oraz sprawdzić istniejące dokumenty po identyfikatorze i zakresie. „Kontynuuj/kolejna” wznawia ACTIVE lub rozwiązuje blokującą BLOCKED. NEXT można rozpocząć tylko przy braku obu i otwartej bramie fazy. Nie wybierać na podstawie numeracji kanonu, nazw plików ani pamięci. Istniejący dokument o niepewnym ukończeniu wymaga uzgodnienia i BLOCKED, bez nadpisania.

### SF-RULE-OPS-003 — Foldery i rozdzielenie produktów

Zakres: SUTTA, VINAYA.

Produkty sutt: 01_Sutty i Kanon Palijski/{DN,MN,SN,AN,KN}; KN obejmuje Sutta Nipāta/StNp. Vinaya: folder Vinaya i odpowiednie części Mahāvagga, Suttavibhaṅga, Cullavagga, Mūlasarvāstivāda/Bhaiṣajyavastu; inne tradycje trzymać osobno. Themes: 04_SUTTAFLOW_THEMES · Zestawienia tematyczne. Pakiety recenzji, szkice i audyty umieszczać poza folderami produktów w 00_ARCHIWALNE_TŁUMACZENIA lub wskazanym katalogu. Release 2.0 ma osobną przestrzeń roboczą; nie przenosi istniejących produktów.

### SF-RULE-OPS-004 — Nazewnictwo i daty

Zakres: SUTTA, VINAYA.

Nazwa sutty: {NIKĀJA NR} · {Tytuł Pali} · {Tytuł polski} · [{konkretny tłumacz/model/narzędzie}, {RRRR-MM-DD}]. Dla Vinayi: {VINAYA REF} · {Tytuł Pali} · {Tytuł polski} · [{tłumacz/narzędzie}, {RRRR-MM-DD}]. Dopuszczalne „red. KR” i numer rewizji tego samego dnia. Dzień ukończenia liczyć w Europe/Warsaw, zgodnie w nazwie, metryce, natywnym elemencie daty i logu, także po eksporcie. Rewizja ma własną datę; modifiedTime nie rozstrzyga niejasności i nie ustanawia godziny ukończenia.

### SF-RULE-OPS-005 — QUEUE i bramy faz

Zakres: SUTTA, VINAYA.

Kanoniczny algorytm kolejki pozostaje w 01_SUTTAFLOW_QUEUE, „Zasady zarządzania kolejką”; reguły proceduralne są także w danych referencyjnych tego kontraktu; bieżący stan odczytać w QUEUE. Dopuszczalne statusy: NEXT, ACTIVE, QUEUED, DONE, BLOCKED, SKIPPED. Najwyżej jedna ACTIVE albo blokująca BLOCKED, przy niej zero NEXT. Bez obu, przy otwartej fazie, dokładnie jeden pierwszy NEXT. Po zamknięciu fazy zero NEXT i dalsze plany QUEUED, aż do upoważnionego przejścia. Pominięcie i zmiana kolejności wymagają decyzji użytkownika. Backlog tworzyć dopiero przy trwałym przekroczeniu około 20 oczekujących; QUEUE zachowuje około 10–20 najbliższych.

### SF-RULE-OPS-006 — Zakończenie i idempotentne uzgodnienie

Zakres: SUTTA, VINAYA.

Po wymaganych bramach tekstowych i FORMAT odczytać finalny PDF i jego wersję źródłową (w ścieżce historycznej także Doc), dopisać i odczytać sprawdzony wpis LOG z protokołem oraz trwałym PDF; następnie oznaczyć DONE i usunąć z QUEUE tylko szczegółowy wpis tej ukończonej pozycji, zachowując licznik fazy i link do historii. Rewizja jest nowym zdarzeniem logu, nie automatycznie nową suttą kolejki. Przerwany zapis uzgadniać po subject_id, zakresie, rewizji i istniejącym wpisie. Powtórzenie nie może tworzyć duplikatu ani usuwać historii. Kilka zapisów nie stanowi jednej transakcji. Na końcu przekazać w czacie działający link do produktu oraz krótką informację o rzeczywiście użytych źródłach, kontroli i ograniczeniach.

### SF-RULE-OPS-007 — Aktywna brama D4 / MN 53

Zakres: SUTTA, VINAYA.

Decyzja OWNER-20261011-STANDARD15-D4 nadal obowiązuje: MN 53 pozostaje NEXT w odczytanej kolejce. Przed rozpoczęciem należy uogólnić segmentację i mapowanie na dowolną suttę MN; wymagane są test niezmienności wyniku MN 41 i test MN 53. MN 53 ma być pierwszą suttą wykonaną od początku nową procedurą, z pełnym R0 zapisanym przed otwarciem przekładów EN. Gdy uogólnienie przekroczy jeden ograniczony etap, tylko właściciel wybiera oczekiwanie albo jawny wyjątek wykonania według 1.4 z rejestrem dowodów. RC nie otwiera tej bramy samym opisem.

### SF-RULE-OPS-008 — Checkpoint i rewind

Zakres: SUTTA, VINAYA.

Każdy etap zapisuje wejściowe rewizje i hashe, stan repo/dokumentów, otwarte problemy, faktyczne wyniki i następny atomowy krok. Po przerwaniu weryfikować piny przed wznowieniem. Rewind oznacza powrót do ostatniego udokumentowanego stanu kopii roboczej i ponowną kontrolę zależności; zachowuje późniejsze artefakty jako historię. Nie cofać cudzych zmian ani właścicielskich decyzji samowolnie. Opisać częściowy zapis i plan odtworzenia; nie obiecywać pracy poza aktywną sesją.

## 2. Pali, R0 i porównania

Dla nowego Pali-first odczytaj całe Pali i utrwal R0 przed kontrolnymi przekładami. Zamówiona rewizja zachowuje istniejące R0 i ekspozycję, bez udawania nowego ślepego początku. EN→PL HH opiera się na konkretnym angielskim źródle i zachowuje jego przypisy; kontrola Pali ma jawny faktyczny zakres. Dla innej tradycji lub pośrednika ustal język, świadectwo i kontroluj właściwą podstawę zgodnie z SRC-001. Bramy wierności, źródeł, redakcji i recenzji pozostają, bez fikcyjnej etykiety Pali-first.

**Odpowiedzialność:** Autor

**Wejście:** Pełna właściwa podstawa: Pali, zamówiony EN HH lub jawnie określony zachowany język/krytyczny pośrednik; dla rewizji istniejące wersje i ekspozycja.

**Produkt i zakończenie:** R0 nowego przebiegu lub zachowane R0 rewizji; prawdziwe porównania i mapa decyzji. EN→PL nie tworzy fikcyjnego R0 z Pali.

**Zatrzymanie:** Brak źródła/kontrolera: jawna kwerenda i wyjątek; brak dowodu nie daje zgodności.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-SRC-001 — SOURCE FIRST i kategorie pośrednie

Zakres: SUTTA, VINAYA.

Dla sutt i palijskiej Vinayi podstawą przekładu jest Pali. Dla innej tradycji ustalić właściwy język i najlepiej zachowane świadectwo. Gdy brak oryginału albo rzetelnego dostępu, można użyć krytycznego przekładu pośredniego, jawnie podając zachowany język, pośrednika i ograniczenie pewności; kontrolę wykonać wobec niego i dostępnych fragmentów oryginału. Nie nazywać takiego wyniku bezpośrednim przekładem z Pali, sanskrytu, chińskiego lub tybetańskiego. EN→PL HH ma własną kategorię i własną podstawę kontroli.

### SF-RULE-SRC-002 — Wydanie, autor i faktyczny nośnik

Zakres: SUTTA, VINAYA.

Manifest odróżnia wydanie tekstu, jego język, autora/redaktora/przekładowcę, platformę i faktyczny adres odczytu. SuttaCentral może służyć identyfikacji paralel, wariantów i dostępu do oznaczonego Pali przy nieskutecznym dostępie pierwotnym; podać cel i faktyczny zakres. Jeśli odczytano tam podstawę, tak to nazwać. Infrastruktura SuttaCentral nie czyni Sujato źródłem przekładu. Lustro, w tym A Buddhist View lub kopia książki, nie jest automatycznie oficjalnym wydawcą. We wszystkich zbiorach przekład Sujato może być wyłącznie dodatkowym weryfikatorem; nie używać go jako źródła sformułowań ani interpretacji, także poza 14 wzorcami terminologicznymi. Charakterystyczna terminologia wymaga osobnej decyzji. Zgodność liczyć według DEC-03, bez rozszerzania jego zakresu.

### SF-RULE-SRC-003 — R0 i dowód kolejności

Zakres: SUTTA, VINAYA.

Pełny R0 musi istnieć jako utrwalony artefakt o określonym zakresie, z rzeczywiście obliczonym SHA-256 surowych bajtów, datą/czasem i dowodem zapisania przed pierwszym odczytem przekładów kontrolnych. Odczytać i zweryfikować sam artefakt, a nie samą niepustą wartość hasha. Pusty zakres, niepełny R0, hash „x”, niezgodne bajty lub odwrócona kolejność nie uzasadniają B=PALI_FIRST_UDOKUMENTOWANY. Capture EN przed R0 jest dopuszczalnym technicznym zachowaniem bajtów tylko bez udostępnienia ich treści autorowi; faktyczne ekspozycje zapisać.

### SF-RULE-SRC-004 — Wcześniejsza ekspozycja i granice Pali-first

Zakres: SUTTA, VINAYA.

Udokumentowane Pali-first opisuje kolejność tego procesu, nie niezależność treningu modelu. Zapisać znaną wcześniejszą lekturę i kontekst przekładów. Brak R0 lub śladu kolejności oznacza PALI_FIRST_DEKLAROWANY albo NIEUSTALONE zgodnie z dowodami, bez wymyślania braku ekspozycji. W metodzie stosować neutralne określenie: „polskie opracowanie AI z odwołaniem do tekstu palijskiego; pełna niezależność metody nieudokumentowana”, gdy brak udokumentowanej kolejności. Nie mylić znanej ekspozycji z technicznym błędem hasha.

### SF-RULE-SRC-005 — Faktyczne odczyty i status źródła

Zakres: SUTTA, VINAYA.

CAPTURED jest zachowaniem bajtów, READ/ODCZYTANE rzeczywistą lekturą wskazanego zakresu. Wpis odczytu zawiera wykonawcę, czas, źródło, locator, zakres i dowód użycia w pracy; sam capture_log ani obecność na dysku nie wystarcza. Rozróżniać PEŁNY_ODCZYT, CZĘŚCIOWY_ODCZYT, BRAK_PRZEKŁADU_Z_KWERENDĄ, BRAK_DOSTĘPU_Z_KWERENDĄ i NIEZWERYFIKOWANE. Oryginalne nazwy statusów zachować wraz z semantyką i słownikiem adaptera. Brak odczytu nie może oznaczać zgodności ani nieistnienia utworu.

### SF-RULE-SRC-006 — Ścisła kolejność kontrolerów

Zakres: SUTTA, VINAYA.

Po R0 porównywać faktyczny zakres kolejno: HH/Anīgha (przekład lub bezpośrednio relewantne opracowanie), właściwy kontroler danego zbioru, następnie Ṭhānissaro. Dla MN właściwy jest Ñāṇamoli w redakcji Bodhiego/Bodhi; dla DN i KN obowiązuje pełen katalog danych referencyjnych tego kontraktu. Przekład i wykład/esej/glosariusz są różnymi dowodami. Gdy HH skraca lub nie obejmuje fragmentu, użyć kolejnego poziomu. Przy istotnej niejasności porównać wszystkie dodatkowo dostępne i sprawdzalne przekłady, zachowując kolejność; nie uśredniać ich.

### SF-RULE-SRC-007 — Kwerenda, brak i wyjątek kontrolny

Zakres: SUTTA, VINAYA.

Sprawdzić oficjalny indeks HH oraz relewantne znane studia/publikacje; dla EPUB podać nazwę, wydanie i rozdział. Dla każdego poziomu oddzielić odczytane, zidentyfikowane nieodczytane i nieznalezione po kwerendzie, z datą i zapytaniami. Brak w jednym indeksie nie dowodzi nieistnienia. Dostępne źródło najwyższego priorytetu porównać w zadeklarowanym zakresie. Niedostępność rozlicza tylko udokumentowany wyjątek z uzasadnieniem. Brak wszelkich porównań nie może dać wyniku dodatniego bez osobnej decyzji człowieka o ograniczeniach. Nie zastępować automatycznie brakującego kontrolera Sujato.

### SF-RULE-SRC-008 — Wykaz DN/KN i decyzje dla dalszych zbiorów

Zakres: SUTTA, VINAYA.

Pełny wykaz danych referencyjnych tego kontraktu jest normatywny: obejmuje DN z Bodhim/Walshe’em i listą 14 DN Ṭhānissaro; Sutta Nipāta; Udānę; Itivuttakę; Dhammapadę; Khuddakapāṭhę; Theragāthę i Therīgāthę, z kontrolerami filologicznymi. Zakresy indeksów z 2026-10-11 są zapisami odczytu, nie obietnicą aktualnej dostępności. Potwierdzić źródła przy pierwszej sutcie zbioru. Inne KN, np. Jātaka i Peṭavatthu, wymagają osobnej decyzji przy wejściu do kolejki. Proponowane minimum dwóch przekładów w KN nie zostaje aktywowane.

### SF-RULE-SRC-009 — VinayaFlow: kontrola i struktura

Zakres: SUTTA, VINAYA.

Zachować identyfikatory Mv/Cv i granice vatthu, narracji, historii reguły, reguły/zezwolenia, definicji, wyjątków i procedur wspólnotowych. Kontrolerzy: HH gdy bezpośrednio relewantny → Khematto dla dostępnej Mahāvaggi/Cullavaggi → Ṭhānissaro, Vinaya i BMC → Horner/PTS oraz Rhys Davids–Oldenberg → właściwe komentarze, wydania, słowniki i badania. Bodhi jest kontrolerem relewantnej sutty, nie domyślnym Vinayi. Nie mieszać tradycji ani przesądzać kierunku zależności paralel. Brahmali pozostaje propozycją.

### SF-RULE-SRC-010 — Słowniki i zakresy

Zakres: SUTTA, VINAYA.

Stosować pięć słowników z danych referencyjnych tego kontraktu: DPD; Cone A Dictionary of Pāli; PED Rhys Davids–Stede; CPD; DPPN Malalasekery. DPD służy najpierw morfologii, podstawom, rdzeniom, sandhi i złożeniom, z datą/wersją. Dla ważnego terminu dodatkowo odczytać właściwy słownik filologiczny. Cone obejmuje podany w źródle zakres A–Bh, CPD A–kāreti; poza nim NIEOBEJMUJE_ZAKRESU, a nie „brak terminu”. DPPN służy nazwom, nie rozstrzyganiu składni; nie przypisywać Malalasekerze nieoznaczonych dopisków redakcji elektronicznej.

### SF-RULE-SRC-011 — Protokół leksykalny

Zakres: SUTTA, VINAYA.

Dla istotnego, wieloznacznego lub niejasnego terminu zapisać całe zdanie Pali z lokatorem; formę powierzchniową, lemma/rdzeń i możliwe analizy; odczytane znaczenia DPD i właściwego Cone/PED/CPD; kontekst i wystąpienia kanoniczne; rzeczywistą kontrolę HH → właściwy kontroler → Ṭhānissaro; alternatywy PL, wybór i powody odrzucenia, niepewność i przypis. Niedostępny słownik: NIEODCZYTANO z datą i powodem. Dwie nieodczytane pozycje nie tworzą podwójnej kontroli. Składnię badać na poziomie zdania, nie przez sumowanie glos.

### SF-RULE-SRC-012 — Obowiązkowa kwerenda paralel

Zakres: SUTTA, VINAYA.

Przy każdej nowej sutcie i Vinayi sprawdzić paralele w Pali/Vinayi, chińskich Āgamach i Vinayach, zachowanym sanskrycie oraz relewantnych gāndhārskich, tybetańskich i innych wczesnych świadectwach. Zapisać wynik, zakres kwerendy i poziom lektury. Identyfikacja katalogowa nie jest analizą różnic. Materialne różnice wydarzeń, osób, liczb, kolejności, relacji przyczynowych lub doktryny ujawnić. Głównego przekładu nie kompilować po cichu z tradycji; ewentualny wpływ wariantu uzasadnić argumentem tekstualnym.

### SF-RULE-LEX-001 — Pełen rejestr terminologii i akceptacja

Zakres: SUTTA, VINAYA.

Rejestr terminologii w danych referencyjnych jest częścią kontraktu, nie nową kolejką. Każdy wpis zachowuje Pali, PL, zakres, wyjątki, uzasadnienie/źródło, status i historię. ZATWIERDZONE wymaga wyraźnej akceptacji w zakresie; ZATWIERDZONE POŚREDNIO obejmuje tylko przyjęte użycie w wskazanym wydaniu. ZASTOSOWANE, NIEPOTWIERDZONE nie tworzy nakazu; PROPOZYCJA nie obowiązuje, WYCOFANE przechowuje zastąpienie. Przed nową suttą odczytać relewantne formuły. Zmianę konwencji uzasadnić i wskazać możliwy wpływ na starsze teksty, bez ich automatycznej korekty.

### SF-RULE-LEX-002 — T-01, T-01-SCOPE i T-02

Zakres: SUTTA, VINAYA.

T-01: upapajjati → „pojawić się ponownie”, z naturalną fleksją; obejmuje czasownik i parafrazy w aparacie sutty, nie ogólną nazwę pojęcia „odrodzenie” w innych materiałach. Dla nowych przekładów i zamówionych rewizji: samādhi → „skomponowanie umysłu”, również w opisie, interpretacji i przypisach, z regułami form pochodnych i pierwszego objaśnienia EDIT-003. Dawna krótka glosa T-02 „skomponowanie” z 11.10.2026 i MN41 RC2.1 pozostają wyłącznie historią, bez globalnej zamiany. Celowy termin linii HH pressure → presja pozostaje w swoim zakresie. Nie tworzyć nowej glosy pali z angielskiej konwencji.

### SF-RULE-LEX-003 — HH–Sujato: komplet 14 sygnałów

Zakres: SUTTA, VINAYA.

Pełny rejestr HH–Sujato w przypiętym config/terminology_hh_sujato_v1.json zachowuje wszystkie 14 ID, regexy, wzorce Pali/EN/PL, segmenty i uwagi z zahaszowanego wejścia. Zgłoszenie polskiej formy jest REVIEW FLAG, nie automatycznym błędem; wymaga decyzji lub uzasadnionego pozostawienia. Przy każdym wykonaniu bramki ponownie weryfikować segmenty wobec przypiętych captures. Zakończenie z yogo karaṇīyo istnieje w Pali; spór dotyczy zawężenia do medytacji, nie dopisania całego zdania przez Sujato. Nie tworzyć z rejestru uniwersalnego glosariusza polskiego.

### SF-RULE-LEX-004 — DEC-03: dotychczasowy algorytm grup i osobna proweniencja

Zakres: SUTTA, VINAYA.

Zachować zatwierdzony algorytm: HH i Sujato identyczni w segmencie po normalizacji wielkości liter, interpunkcji i form ściągniętych tworzą jedną grupę; w pozostałych segmentach dwie. Ñāṇamoli/Bodhi i Ṭhānissaro są oddzielnymi grupami. Skrót HH nie jest pełnym drugim świadectwem; zgodna kompresja nie potwierdza pominiętego tekstu. Wynik algorytmu leksykalnego i rzeczywista proweniencja/niezależność tekstowa muszą mieć osobne pola. Różne słowa nie dowodzą niezależności. Liczba grup jest sygnałem, nie głosowaniem. Zmiana algorytmu wymaga decyzji właściciela. Raport podaje liczbę segmentów wspólnych i różnych HH–Sujato oraz rzeczywisty mianownik i zakres.

### SF-RULE-LEX-005 — Rozstrzygnięcie a zgodność tłumaczy

Zakres: SUTTA, VINAYA.

Rozstrzyga tekst Pali w kontekście i słowniki. Terminologię rozstrzyga HH po kontroli Pali i DPD w granicach zatwierdzonych decyzji; pierwszeństwo HH nie nadaje mu bezbłędności ani prawa do zmiany Pali. Gdy liczba grup i preferencja terminologiczna wskazują inne rozwiązania, zachować obie podstawy i uzasadnienie. Przy upoważnionym odstąpieniu od palisty AI dokumentuje miejsce, Pali, odczytania, słowniki, grupy za/przeciw, decyzję, pewność i regułę. Rekordy o średniej/niższej pewności mają pierwszeństwo przyszłej recenzji palisty.

### SF-RULE-LEX-006 — Kalki i zamrożone konwencje redakcyjne

Zakres: SUTTA, VINAYA.

Zgłaszać PL bez podstawy w Pali, obecne w angielskim przekładzie. Dotychczasowy sygnał porównuje odpowiednik EN u HH/Sujato w danym akapicie z glosami DPD jego słów Pali; każdy sygnał ma rozliczenie. Lista z MN 41 („innym”/to others, „naruszenie praw”/by law, „Przeciwnie”/Instead) jest ograniczona; brak sygnału nie dowodzi braku kalk. W EN→PL odniesieniem jest HH. DEC-07 zachowuje w MN 41 przyjęty stan nazw: Pali pozostaje Pali, przekład pozostaje przekładem; nie ujednolicać wstecz.

## 3. Pokrycie, dwie autokorekty i redakcja

Autor sprawdza całe znaczenie względem właściwej podstawy i całą polszczyznę. Odrębny redaktor opracowuje tekst, a autor sprawdza proponowane zmiany względem rzeczywistego źródła.

**Odpowiedzialność:** Autor i odrębny redaktor

**Wejście:** Przekład lub zamówiona rewizja, właściwa podstawa i aparat.

**Produkt i zakończenie:** Meaning, Polish, redakcja i rozliczony kandydat z pełnym pokryciem.

**Zatrzymanie:** Nierozstrzygnięty sens lub brak redaktora: nie zamykać etapu.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-MAP-001 — Pełny zakres, powtórzenia i peyyāla

Zakres: SUTTA, VINAYA.

Pełny przekład obejmuje cały zadeklarowany zakres, wszystkie zdania, strofy, klauzule, formuły, powtórzenia i kolofony obecne w podstawie. Nie zastępować własną kondensacją i nie nazywać jej bezwarunkowo pełnym przekładem. Źródłowe peyyāla zachować i jawnie oznaczyć. Redakcyjny skrót musi być widoczny w miejscu użycia oraz ograniczać deklarację kompletności. Każde wystąpienie formuły sprawdzić; próbka ani numer paragrafu nie zalicza całej jednostki.

### SF-RULE-MAP-002 — Segmentacja i mapowanie w obu kierunkach

Zakres: SUTTA, VINAYA.

Atomowe jednostki znaczeniowe właściwej podstawy źródłowej i PL otrzymują stałe ID i lokalizacje w konkretnych bajtach/rewizjach. Zachować wiele-do-jednego, gdy wymaga tego sens. Każda grupa ma niepuste rzeczywiste źródło i PL albo jawny typowany problem/wyjątek, z zakresem i oceną wpływu. Dwie jednostronne osierocone grupy nie mogą dać pełnej bramki mimo 100% sum liczników. Walidować obie strony, ID, kolejność, duplikaty i brak dopowiedzeń bez podstawy; nie dowodzić poprawności samej pary jej identyfikatorem.

### SF-RULE-MAP-003 — Mianownik, kotwice i odtwarzalność

Zakres: SUTTA, VINAYA.

Mianownik wynika z pełnego zamrożonego źródła i surowych bajtów, z odwracalnymi offsetami lub równoważnym dowodem zakresu. Przypiąć do realnych kotwic wydania: git blob na commicie, skrót wydania DPD lub niezależny snapshot, jeśli istnieją. Brak zewnętrznej kotwicy jest jawnym ograniczeniem; własny SHA jej nie zastępuje. Rejestr zmian pozwala deterministycznie odtworzyć kandydata. manifest_core_sha256 zachować poza pakietem, w upoważnionym prywatnym GitHub i raporcie Drive. Replay wymaga rzeczywistych wejść, nie samych ścieżek.

### SF-RULE-MAP-004 — Zamknięte statusy jednostek

Zakres: SUTTA, VINAYA.

Dopuszczalne wyniki jednostki 1.13: NIE_WYKONANO, W_TRAKCIE, WYMAGA_POPRAWKI, SPRAWDZONO_Z_UWAGĄ, SPRAWDZONO. Nieznany status, np. UNREVIEWED, pusta wartość, złe ID albo duplikat powodują walidacyjny HOLD z kodem przyczyny; nie są pomyślnym pokryciem. Status wynika z faktycznej pracy nad całą jednostką. Oryginalne wartości zachować w raw; techniczne adaptery muszą mieć wersjonowaną i testowaną mapę, bez samowolnego poszerzania enumów.

### SF-RULE-MAP-005 — Minimalny rekord dowodu

Zakres: SUTTA, VINAYA.

Rekord jednostki zawiera ID, wydanie i dokładną lokalizację źródła, odczytany krótki fragment właściwej podstawy źródłowej, PL i rewizję, osobne faktyczne zakresy kontrolerów, typ różnicy (pominięcie/dodatek/negacja/składnia/terminologia/wariant/interpretacja/paralela), wagę, rekomendację, decyzję z uzasadnieniem, status, wykonawcę i datę. Typ PRÓBKA jest odrębny od PEŁNA_JEDNOSTKA. Rejestr ma pełny zakres nowej sutty, link w zapleczu QA i LOG i nie kopiuje fikcyjnych wyników historycznego pilota.

### SF-RULE-MAP-006 — Problemy i invalidacja po każdej zmianie

Zakres: SUTTA, VINAYA.

Każda zmiana treści unieważnia użycie dawnych wyników dla nowej rewizji. Ponownie sprawdzić zmieniony fragment, kotwice i zależności; przepiąć hashe, pakiet i raport. Nie ograniczać tego do zmian uznanych za istotne. Rejestr problemu: ID, jednostka, dowody, wpływ, OTWARTA/W TOKU/ZAMKNIĘTA, działanie, poprawiona rewizja i dowód sprawdzenia. Samo issue ID nie zamyka OPEN/CRITICAL. Niezmienione historyczne raporty pozostają zapisem starego zakresu; nie nadpisywać ich.

### SF-RULE-QA-001 — Kontrola autora line-by-line

Zakres: SUTTA, VINAYA.

Autor wykonuje odrębny, pełny przebieg źródłowy, zestawiając każde zdanie, klauzulę, formułę i werset z PL. Sprawdza pominięcia/dodatki, podmiot/przedmiot, negację, przypadki i składnię, liczbę, imiona, liczebniki, czas, przyczynę, modalność, terminologię i powtórzenia. Zwykła lektura nie wystarcza. Raport wskazuje zakres, źródło, wersję Standardu, rewizję, rzeczywiste problemy/rozstrzygnięcia i ponowną kontrolę. Jeśli nie znaleziono problemu, tak zapisać; nie wymyślać korekt ani procentowej dokładności.

### SF-RULE-QA-002 — Semantyka wyniku kontroli

Zakres: SUTTA, VINAYA.

PASS oznacza rzeczywiście wykonane wymagane kontrole wskazanego zakresu i brak otwartych istotnych zastrzeżeń. PASS_WITH_NOTES oznacza kontrole wykonane z jawnym, uzasadnionym ograniczeniem nieblokującym; NEEDS_REVISION wymaga poprawy. Kontrola niewykonana, częściowa wobec wymaganego zakresu lub niemożliwa ma NIEWYKONANE albo ZABLOKOWANE, nigdy PASS. Raport etapu i finalna akceptacja są różnymi zdarzeniami. Wynik nie oznacza recenzji człowieka ani zezwolenia w E.

### SF-RULE-QA-003 — Akceptacja PASS_WITH_NOTES

Zakres: SUTTA, VINAYA.

Redaktor końcowy może przyjąć PASS_WITH_NOTES do finalizacji dopiero po sprawdzeniu podstawy i całego deklarowanego zakresu, braku kwestii mogącej istotnie zmienić sens i wykonaniu FORMAT. Każdą uwagę uzasadnić osobno, z osobą/rolą, datą, zakresem i oceną nieblokowania. Brak pomocniczego HH po kwerendzie lub nieodczytana paralela bez rozpoznanego wpływu mogą być uwagą, lecz sam brak dostępu nie dowodzi nieistotności. Ten sam model w trzech rolach musi być ujawniony; zmiana nazw ról nie tworzy niezależności.

### SF-RULE-QA-004 — Bezwzględne blokady finalizacji

Zakres: SUTTA, VINAYA.

Nie finalizować przy niezweryfikowanej podstawie, brakującym fragmencie, nierozstrzygniętej różnicy mogącej zmienić sens, podejrzeniu nieuprawnionego dodatku, nieaktualnej rewizji lub niewykonanym wymaganym QA. Nierozliczone CRITICAL/MAJOR blokują APARAT-GATE. Właściciel może świadomie przyjąć materiał roboczy albo ograniczony zakres, ale nie zmienia to niewykonanej kontroli w PASS, fragmentu w pełny przekład ani samokontroli w niezależną recenzję.

### SF-RULE-QA-005 — Granica Evidence QA i adapter zamknięcia

Zakres: SUTTA, VINAYA.

Evidence QA ocenia strukturę, spójność i gotowość dowodów. TECHNICAL_EVIDENCE_READY nie ustawia PASS, osi D/E, DONE ani ready_for_publication. Odrębny adapter zamknięcia wymaga realnych raportów autora i recenzentów, aktualnej rewizji, rozliczonych problemów, kompletnych bram APARAT, FORMAT i zakresowej decyzji właściciela dla E. Techniczne HUMAN_PALIST_REVIEW nie jest samo poświadczeniem lektury człowieka. Silnik nie orzeka o prawidłowym rozumieniu gramatyki Pali.

### SF-RULE-QA-006 — Błędy wejścia i wymagane negatywne próby

Zakres: SUTTA, VINAYA.

Brak capture_log, formuły, segmentu, PL, źródła, rewizji lub recenzenta daje ustrukturyzowany HOLD/BLOCKED z ID powodu, a nie crash ani wynik dodatni. Negatywnie sprawdzić każdą brakującą jednostkę, źródło bez wyjątku, problem istotny/krytyczny, brak fresh review, zły hash, stale PASS, APARAT przed CORE i brak FORMAT; SCRIPT QA tylko przy zamówionym audio. Dodatni wynik po WSTRZYMANO wymaga kontroli dowodów przez redaktora i nowego wpisu logu. Test syntetyczny nie certyfikuje sutty.

### SF-RULE-EDIT-001 — Dwie rzeczywiste autokorekty

Zakres: SUTTA, VINAYA.

Meaning obejmuje cały przekład względem pali: znaczenie, negacje, warunki, mówców, obrazy, formuły i powtórzenia. Polish zaczyna się ciągłą lekturą polszczyzny bez podglądania źródeł w tej części; po wskazaniu konkretnych wad autor wraca do pali i sprawdza skutki zmian. Są to autokorekty, nie niezależne recenzje. Wierność sensu zdania i naturalna polszczyzna mają pierwszeństwo przed mechanicznym tłumaczeniem glos. Nie dopisywać nauki, puenty ani techniki medytacji. Dla każdego akapitu lub strofy sprawdzić zrozumiałość i wszystkie formy wskazujące (tutaj, tam, to, ten, w obu miejscach; idha/ettha/tattha). Ustalić referent z pełnej klauzuli i sąsiadów; nie stosować jednej glosy ani automatycznego zakazu „tutaj”. Istotne doprecyzowanie zapisać z kotwicą źródła, podstawą i alternatywą. Chronić także zakres, wyjątki, modalność i rozróżnienia nauki. Osobny wynik odniesień i naturalności obejmuje cały tekst oraz konkretne decyzje i hash kandydata; sama deklaracja Polish PASS nie wystarcza. Dla EN→PL i pośrednika kontrolować rzeczywistą podstawę według zakresu, nie pozorować kontroli pełnego Pali.

### SF-RULE-EDIT-002 — Odrębny redaktor przed i po recenzji

Zakres: SUTTA, VINAYA.

Odrębny redaktor czyta cały polski tekst, Opis, Interpretację i przypisy przed świeżą recenzją. Autor rozlicza propozycje i sprawdza zmienione klauzule, sąsiadów i zależne formuły względem właściwej podstawy źródłowej. Dopiero wtedy zamraża kandydata. Ten sam redaktor po rozliczeniu uwag czyta całość końcowej wersji, sprawdza rytm, odniesienia, odmianę, spójność i aparat. Zmiana tekstu unieważnia zależne zamknięcie. Nie zastępować redaktora deklaracją autora. Redaktor jest odrębny od autora oraz od świeżego recenzenta, z odrębnym kontekstem; ten sam redaktor przygotowuje i zamyka tekst. Jego pierwsza ciągła polska lektura odbywa się bez podglądania Pali/EN w tej części, następnie propozycje sprawdza się w źródle. Nie oznacza to usunięcia pamięci wcześniejszych tekstów. Brak rzeczywistego redaktora pozostaje niewykonany; przygotować zamrożony pakiet i prompt do nowego czatu zamiast własnej deklaracji niezależności.

### SF-RULE-EDIT-003 — Aktualne konwencje i objaśnienia

Zakres: SUTTA, VINAYA.

Sati oddawać domyślnie jako pomność, z naturalnymi formami pomny, pamiętając lub mając na uwadze według kontekstu. Samādhi: skomponowanie umysłu; formy czasownikowe dobierać do zdania, bez podwajania umysłu przy citta. Przy pierwszym istotnym użyciu w przekładzie dodać krótkie kontekstowe objaśnienie: opanowanie i stabilność umysłu, z rzetelnym odwołaniem do odczytanego autora HH dla angielskiego composure. Polski zwrot jest konwencją SuttaFlow, nie słowami autora HH. Sprawdzić pełną kotwicę i treść przypisu w PDF. Nie wymuszać rzeczownika w każdym wystąpieniu ani ogólnej definicji niezależnie od sutty. Przy pierwszym objaśnieniu sati podać: „Pomność (sati) — przypominanie sobie i utrzymywanie w pamięci tego, co istotne dla bieżącej praktyki”. Nie dopisywać przedmiotu pamiętania, którego tekst nie ustala. Pamięć nie jest pełnym automatycznym zamiennikiem, pamiętliwość nie jest przyjętą glosą, pamiętność pozostaje niewybranym wariantem. Formy pokrewne, np. paṭissato, sprawdzać osobno w zdaniu; miejscowa korekta nie jest nową uniwersalną glosą.

## 4. Recenzja CORE, następnie aparatu

Świeży recenzent najpierw ocenia czysty przekład. Po zamrożeniu CORE ocenia aparat. Kontrole interpretacyjne mają odrębne czyste wejścia i raporty.

**Odpowiedzialność:** Świeży recenzent CORE/APARAT; odrębne IK/ID/IR; autor rozlicza

**Wejście:** Zamrożony czysty CORE; aparat udostępniony dopiero po raporcie CORE.

**Produkt i zakończenie:** Raporty i dyspozycje uwag przypięte do aktualnego tekstu.

**Zatrzymanie:** Brak rzeczywistej niezależnej kontroli lub otwarte uwagi: niewykonane; przygotować pakiet i prompt.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-CORE-001 — Czyste wejście CORE

Zakres: SUTTA, VINAYA.

Po kontroli autora recenzent dostaje kompletny zamrożony tekst źródłowy z kotwicami i odpowiadający PL, ID, wydanie, adres, revisionId, prawdziwe hashe/piny i manifest zakresu. Wykluczyć przypisy, paralele, opis, interpretację, wcześniejsze oceny, decyzje, propozycje, raport autora i historię toku powstawania. Nie udostępniać głównego Doc zawierającego te warstwy. Standardowo krótki prompt wskazuje jednoznaczne pliki/URL; przy niedostępnym zdalnym odczycie załączyć te same zamrożone pliki. Nie wklejać domyślnie całej sutty do promptu. Świeży recenzent po kontroli znaczenia wykonuje ciągłą polską lekturę całego CORE: naturalność, rytm, kalki i odniesienia. Jest odrębny od autora i redaktora; dokumentuje oba zakresy i konkretne uwagi.

### SF-RULE-CORE-002 — Wykonanie i zamrożenie przed APARAT

Zakres: SUTTA, VINAYA.

Fresh review jest rzeczywistą krytyczną lekturą całego zakresu przez wskazanego recenzenta, szukającą błędów, nadinterpretacji, wygładzenia i fałszywej pewności. Raport musi istnieć, wskazywać źródła, jednostki, problemy, zakres i werdykt; zamrozić go przed jakimkolwiek udostępnieniem APARAT. APARAT otwiera się dopiero po rzeczywistym zakończeniu i utrwaleniu CORE; sam manifest FROZEN nie spełnia tego warunku. Pierwszy raport pozostaje niezmienny. Późniejsze uwagi zapisuje się jako nowe, zakresowe ustalenia.

### SF-RULE-CORE-003 — Niezależność i brak narzędzia

Zakres: SUTTA, VINAYA.

Ten sam model w drugim przebiegu to odrębny przebieg AI; osobny kontekst dokumentuje izolację, nie niezależność treningu ani kompetencję palisty. Zapisać model/wykonawcę, kontekst, wcześniejszą ekspozycję i ograniczenia. Gdy nie da się uruchomić wymaganego kontekstu, przygotować samowystarczalny prompt CORE i czysty pakiet do nowego czatu. Prompt APARAT przygotować/dostarczyć dopiero po zwrocie zamrożonego CORE. Brak wykonanego raportu = NIE_WYKONANO/NIEWYKONANE, nie PASS. Nie fabrykować podpisu recenzenta.

### SF-RULE-CORE-004 — Długie teksty i pełna kontrola globalna

Zakres: SUTTA, VINAYA.

Dzielić deterministycznie po pełnych logicznych jednostkach; nie w środku zdania ani powiązania źródło–PL. Każda część ma source_ids, candidate_ids, kolejność, SHA i powiązania. Sąsiedni KONTEKST nie wchodzi ponownie do mianownika pokrycia. Jednostkę przekraczającą limit podzielić jawnie z nowym mapowaniem. Rozliczyć wszystkie części, przejścia, powtarzane formuły, ciągłość argumentu i pełną polską lekturę; brak realnej kontroli globalnej zaznaczyć. Automat odrzuca osierocone, zdublowane, przestawione jednostki i niezgodny manifest części.

### SF-RULE-APP-001 — Ogólny APARAT pozostaje obowiązkowy

Zakres: SUTTA, VINAYA.

Po zamrożonym CORE ten sam świeży recenzent otrzymuje oddzielny APARAT i tworzy oddzielny raport. Zakres: przypisy i ich kotwice, opis, interpretacja, paralele, źródła i rzeczywiste odczyty, metoda publiczna, decyzje tłumaczeniowe i metryka. Sprawdzać merytorycznie glosy, warianty, atrybucję, zakres dowodu i pełność bibliografii, nie tylko linki. Dodatkowe IK/ID/IR nie zastępują tego obowiązku. A0 jest nieaktywną propozycją reorganizacji; bez decyzji nie wolno usunąć ogólnego APARAT.

### SF-RULE-APP-002 — Przypisy i jawna niepewność

Zakres: SUTTA, VINAYA.

Aparat pomaga rozumieć tekst; nie dodawać ciekawostek bez funkcji objaśniającej. Przy ważnym terminie, składni, wariancie lub Vinayi w razie potrzeby podać formę, znaczenie i zakres, alternatywy, przyczynę wyboru i konsekwencję. Vinaya wymaga technicznego sensu prawno-monastycznego. Przy wariancie wskazać świadectwa. Krótkie proste noty są dopuszczalne. Fakty i stanowiska autora mają źródło; własną interpretację oznaczyć. Niepewności nie wygładzać: podać odczytania, podstawę, przypis, w razie potrzeby „tłumaczenie niepewne”.

### SF-RULE-APP-003 — Paralele i konflikt prezentacji

Zakres: SUTTA, VINAYA.

Istotne różnice paralel przedstawiać w sekcji K1 „Paralele kanoniczne”, z numerem tekstu, ustępu, krótkim opisem różnicy i pełnym źródłem. Przy odpowiednim fragmencie przekładu dać krótki przypis lub odsyłacz prowadzący do konkretnej różnicy. Ten przyjęty kierunek zastępuje konkurencyjny wymóg dodatkowego bloku bezpośrednio pod fragmentem. Ujawnić pośrednią translację i faktyczny zakres kontroli. Treści paraleli nie włączać po cichu do przekładu pali.

### SF-RULE-INT-001 — Trzy osobne kontrole interpretacyjne

Zakres: SUTTA, VINAYA.

Każdy nowy dokument i zamówiona merytoryczna rewizja Opisu/Interpretacji podlega po CORE trzem kontrolom: APARAT-IK (KANON), APARAT-ID (DOKTRYNA I PROWENIENCJA), APARAT-IR (REDAKCJA). Zakres obejmuje wszystkie zdania obydwu sekcji oraz relewantne twierdzenia przypisów i paralel. Wyniki i zakresy są osobne; łączny APARAT-GATE nie jest nazwą IK. Kontrole nie zastępują CORE, ogólnego APARAT, FORMAT ani decyzji właściciela.

### SF-RULE-INT-002 — Mapa 100% zdań i podtez

Zakres: SUTTA, VINAYA.

Zamrozić ID sutty, właściwą podstawę źródłową (Pali dla Pali-first), rewizję PL, całe Opis/Interpretację, przypisy oraz źródła i zakresy. Każde zdanie oznaczyć O01/I01 itd., wielotezowe podzielić na a/b. Mapa obejmuje 100% i rozróżnia K (wyrażone w kanonie), P (ostrożna parafraza), W (wniosek), T (stanowisko tradycji/autora), H (hipoteza). Każda teza ma konkretny locus; pojedynczy werset nie jest dowodem znacznie szerszego twierdzenia.

### SF-RULE-INT-003 — APARAT-IK

Zakres: SUTTA, VINAYA.

IK przypisuje każdemu istotnemu twierdzeniu werset/fragment właściwej podstawy kanonicznej i potrzebny kontekst lub paralelę; dla EN→PL wskazuje faktyczny zakres Pali, a przy pośredniku podaje zachowany język, pośrednictwo i ograniczenie pewności zamiast pozorowania odczytu oryginału. Sprawdza podmiot, kwantyfikatory, związek przyczynowy, dopowiedzenie, odwrócenie warunku, negację, terminy, alternatywy i zgodność z wybranym wariantem. Raportuje również poprawne jednostki. Nie powtarza mechanicznie line-by-line całego CORE, lecz musi pokryć wszystkie twierdzenia aparatu w swoim zakresie.

### SF-RULE-INT-004 — APARAT-ID

Zakres: SUTTA, VINAYA.

ID odróżnia literalny kanon, paralele, tradycyjny komentarz, HH, nowożytny przekład, słownik i syntezę autora. Kontroluje atrybucję, alternatywne interpretacje, pośrednictwo oraz zawężenie sensu ponad dowody. Wniosek nie może występować jako dosłowne zdanie Buddhy. Priorytet HH nie pozwala przypisać mu nieodczytanej tezy ani nadpisać Pali. Rejestr zawiera pochodzenie każdej ważnej tezy.

### SF-RULE-INT-005 — APARAT-IR

Zakres: SUTTA, VINAYA.

IR wykonuje całościową polską lekturę, osobno ocenia neutralność/zwięzłość Opisu i jasność/uczciwe oznaczenie Interpretacji. Sprawdza tytuły, terminy, relacje, powtórzenia, kalki, sztuczną naukowość, ozdobniki i ukryte tezy. Nie wolno dla płynności zmieniać sensu, usuwać atrybucji ani niepewności. Sugerowane brzmienie jest propozycją do rozliczenia, nie samoczynną edycją zatwierdzonego tekstu.

### SF-RULE-INT-006 — Niezależność IK/ID/IR

Zakres: SUTTA, VINAYA.

Każda kontrola otrzymuje odrębną instrukcję i czysty zamrożony pakiet bez wcześniejszych uwag, werdyktów i proponowanych korekt. Trzy raporty powstają i zamrażają się niezależnie przed zbiorczym rozliczeniem; preferować odrębne konteksty i dostępnych innych recenzentów/modeli/specjalistę. Trzy przebiegi jednego asystenta w jednym kontekście to samokontrola w trzech rolach, niezależność NIEWYKONANE. Gdy brak recenzenta, przygotować trzy prompty do NOWYCH CZATÓW; nie uznawać ich za wykonane recenzje.

### SF-RULE-INT-007 — Raporty, rozliczenie i APARAT-GATE

Zakres: SUTTA, VINAYA.

Każde ustalenie ma IK/ID/IR-ID, zdanie/podtezę, dokładne brzmienie, źródło/locus, rodzaj, wagę CRITICAL/MAJOR/MINOR/NOTE, propozycję, pewność, wykonawcę/model albo unknown, kontekst, datę i status. Redaktor rozlicza PRZYJĘTO/ODRZUCONO/ODROCZONO z uzasadnieniem na podstawie źródeł, nie głosowania. Zmienione zdania i zależności wracają do właściwych kontroli; zmiana sensu wymaga IK i ID. Brak wymaganej niezależności lub nierozliczona poprawka blokują nowy APARAT-GATE PASS. Zachować indywidualne wyniki i historyczne niezmienione CORE/FORMAT.

## 5. K1, metryka i PDF

Zamknięty tekst zapisuje się w Markdown z jawnymi przypisami, strofami i wyróżnieniami pali. Po zbudowaniu PDF kontroluje się jego tekst i wygląd.

**Odpowiedzialność:** Operator składu i wykonawca FORMAT

**Wejście:** Zamknięty tekst, wspólny CSS/fonty, noty i indeks form Pali.

**Produkt i zakończenie:** Źródło, PDF, kontrola tekstu/fontów/kotwic i oględziny wszystkich stron.

**Zatrzymanie:** Utrata tekstu, noty, kotwicy lub nieobejrzany PDF: bez FORMAT PASS.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-FMT-001 — Jedyny zatwierdzony K1

Zakres: SUTTA, VINAYA.

Zachować zatwierdzony wygląd K1: Merriweather, role i parametry wskazane w danych referencyjnych. Źródłowy K1 ma ID 1as-k0wrf_sXdXSTPPnoEmmx_fMfdn0C9H0HKO8JcmfY i pozostaje niezmieniony. Dla nowych dokumentów źródłem jest wersjonowany Markdown, wspólny CSS i przypięte fonty, a PDF powstaje przez Vivliostyle. Google Docs dawnych przekładów pozostają zachowane. Zmiana wyglądu poza przyjętą zawartością metryki wymaga konkretnej akceptacji.

### SF-RULE-FMT-002 — Pełna struktura nagłówków i dwa podziały

Zakres: SUTTA, VINAYA.

Dokument ma tytuł polski, podtytuł pali/zbiór/numer, sześć głównych sekcji: Opis, Interpretacja, Przekład, Jak powstało to tłumaczenie, Paralele kanoniczne i Źródła; podsekcję Decyzje tłumaczeniowe i końcową Metrykę przekładu. Metoda i metryka zaczynają nowe strony przez regułę podziału, nie puste akapity. Historyczne nagłówki „Dokumentacja pracy” i „Historia rewizji” nie są wymagane w nowych dokumentach czytelniczych: pełna dokumentacja trafia do repozytorium. Zachować pozostałe role typograficzne K1. Mapa semantyczna: polski tytuł = TITLE/HTML h1; podtytuł = SUBTITLE/p.subtitle; sześć wymienionych sekcji = HEADING_2/HTML h2; Decyzje tłumaczeniowe i Metryka przekładu = HEADING_3/HTML h3. Podgrupy źródeł także h3. Dwa historyczne H4 metryki nie są wymagane w nowych krótkich metrykach. Sprawdzić poziomy w skonwertowanym HTML, nie tylko rozmiary fontów.

### SF-RULE-FMT-003 — Tagi, dialog, gāthā i metryka

Zakres: SUTTA, VINAYA.

Używać rzeczywistego tekstu: proza, osobne akapity dialogu i jawne wersy/strofy. Nie pozostawiać demonstracji ani tagów szablonu. Metryka czytelnicza zawiera krótko wersję i datę, podstawę tekstową, udział AI, zakres kontroli i istotne ograniczenia oraz aktualny status. Nie zamieszczać w niej hashów, ścieżek, identyfikatorów przebiegów ani pełnych raportów. Te dowody pozostają w repozytorium, związane z suttą i rewizją. Osie A–E prowadzić w QA, bez dodatkowego bloku na pierwszej stronie.

### SF-RULE-FMT-004 — Natywne elementy i zwarty skład

Zakres: SUTTA, VINAYA.

PDF ma A4, marginesy 56,7 pt, rzeczywistą numerację stron i automatycznie numerowane przypisy u dołu strony. Zachować Merriweather: tytuł 24 pt, podtytuł 14 pt, tekst 12 pt, odstęp bazowych wierszy około 17,3466 pt, 0 pt przed i 4 pt po akapicie; strofy z wcięciem 18 pt bez dodatkowych odstępów między wersami; bibliografia i metryka 10 pt; przypisy 9,5 pt. Listy i linki pozostają semantycznymi elementami. Nie wpisywać numerów przypisów ręcznie. Długiej noty nie wolno ucinać: wymagane jest czytelne przeniesienie albo jawne zatrzymanie eksportu do korekty.

### SF-RULE-FMT-005 — Normalizacja po rzeczywistych zmianach

Zakres: SUTTA, VINAYA.

Po każdej zmianie tekstu lub noty ponownie zbudować dokument z aktualnego źródła i odtworzyć kotwice oraz mapę tekstu. Nie formatować według indeksów innej rewizji. W ścieżce historycznego Google Doc ponownie odczytać rzeczywistą strukturę i indeksy UTF-16; nie zastępować mechanizmu natywnego imitacją. W ścieżce Markdown sprawdzić wynik konwersji i zgodność bieżącego źródła, stylu, fontów oraz PDF. Puste akapity usuwać selektywnie, bez utraty granic strof i sekcji.

### SF-RULE-FMT-006 — Kursywa Pali w każdym przypisie

Zakres: SUTTA, VINAYA.

Wszystkie omawiane formy i cytaty palijskie w tekście oraz przypisach, także kolejne wystąpienia, warianty, fleksja i złożenia, oznaczać kursywą na podstawie rozpoznanego zakresu słów, a nie samych znaków diakrytycznych. Nie pochylać polskich objaśnień, numerów ani skrótów słowników; nazwę omawianą jako formę pali wyróżniać, nazwę osoby używaną po polsku pozostawiać zgodnie z funkcją. W Markdown używać właściwych znaczników, w definicjach not składni obsługiwanej przez VFM. W PDF sprawdzić faktyczny font Italic i kompletność. Indeks form właściwy danej sutcie nie jest uniwersalnym detektorem pali.

### SF-RULE-FMT-007 — Dwie osobne bramy Docs i PDF

Zakres: SUTTA, VINAYA.

Dwie osobne kontrole: najpierw struktura aktualnego źródła i wynik konwersji (role, listy, oba podziały, strofy, odwołania, kotwice, kursywa i linki), następnie końcowy PDF. W PDF sprawdzić pełny tekst i wszystkie noty oraz obejrzeć każdą stronę, anomalie w pełnej skali. Brak eksportu lub oględzin oznacza niewykonane/zablokowane, nigdy wynik dodatni. Dawny tryb Docs nadal wymaga rzeczywistego odczytu native i eksportu tej samej rewizji; nie przedstawiać Markdown jako natywnego Google Doc.

### SF-RULE-FMT-008 — Dowód FORMAT i DONE

Zakres: SUTTA, VINAYA.

FORMAT PASS wymaga wykonanych kontroli struktury, treści i wyglądu bez istotnych usterek. Zapis wskazuje ID sutty, rewizję i hash źródła, styl/fonty, końcowy PDF, liczbę stron, zakres oględzin, wykonawcę, poprawione wady i trwały link na Dysku. Dla historycznego eksportu Google zapisać ponadto Doc ID i revisionId. Po wymaganych bramach merytorycznych i FORMAT można zamknąć plik; zgoda publikacyjna pozostaje odrębna. Zmiana treści lub składu wymaga aktualizacji zależnych kontroli.

### SF-RULE-FMT-009 — Wariant VinayaFlow

Zakres: SUTTA, VINAYA.

Jeśli układ Vinayi mieści się w K1 bez utraty wymaganej struktury, zachować zatwierdzony wzorzec i udowodnić pełny zakres. Gdy potrzebuje innych ról, układu lub sekcji, przygotować odrębny wariant z dokładną mapą do K1, a jego aktywacja wymaga jawnej zgody właściciela. Nie rozszerzać szablonu przez domniemanie ani wciskać wyjątków, definicji i procedur w wariant usuwający granice tekstu. Kontrola numeracji i terminologii prawno-monastycznej pozostaje obowiązkowa.

## 6. Statusy, dostawa i dokumentacja

Dostawa nie jest zgodą publikacyjną. Zweryfikuj aktualne produkty na Dysku, zapisz LOG i uzgodnij QUEUE. Pełne dowody przechowuj poza dokumentem czytelniczym.

**Odpowiedzialność:** Operator; D/E tylko uprawnione osoby

**Wejście:** Aktualne produkty i dowody bram.

**Produkt i zakończenie:** Odczytane PDF/OPIS, wpis LOG i uzgodnione QUEUE; oddzielne osie.

**Zatrzymanie:** Niepewny zapis: najpierw readback po ID i wersji, bez ślepego ponowienia.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-STA-001 — Dokładne osie i zamknięte wartości

Zakres: SUTTA, VINAYA.

Pięć osi ustala się oddzielnie. A: ROBOCZY, UKOŃCZONY_PLIK. B: PALI_FIRST_UDOKUMENTOWANY, PALI_FIRST_DEKLAROWANY, EN_PL_HH, EN_PL_INNY, NIEUSTALONE. C: NIEUDOKUMENTOWANA, CZĘŚCIOWA, PEŁNA_AI. D: BRAK, ODSTĄPIONO, CZĘŚCIOWA, PEŁNA. E: WSTRZYMANE, DOPUSZCZONE_JAKO_OPRACOWANIE_AI, DOPUSZCZONE_PO_RECENZJI. Znaczeń nie wolno zmienić przez adapter. A ustala wykonawca po FORMAT; B według źródeł/procesu, C według dowodów, D rzeczywisty recenzent lub właściciel przy odstąpieniu, E wyłącznie właściciel.

### SF-RULE-STA-002 — Warunki B i C

Zakres: SUTTA, VINAYA.

B=PALI_FIRST_UDOKUMENTOWANY wymaga dowodu R0 z SF-RULE-SRC-003. C=CZĘŚCIOWA wymaga jawnego zakresu; C=PEŁNA_AI pełnego pokrycia atomowych jednostek oraz istniejących raportów autora i faktycznego recenzenta, tożsamości modeli/kontekstów, niezależności i dokładnej rewizji. coverage_ready=true bez raportów nie wystarcza. Nowego wymaganego APARAT-GATE nie wywodzić z historycznego C. Niepalijski SOURCE FIRST zapisać w metadanych języka i podstawy; nie wymuszać nieprawdziwego pochodzenia EN lub Pali.

### SF-RULE-STA-003 — D: człowiek i typowane odstąpienie

Zakres: SUTTA, VINAYA.

D=CZĘŚCIOWA/PEŁNA wymaga faktycznie wykonanej recenzji człowieka z osobą/rolą, datą, zakresem i rewizją; AI może ją odnotować z dowodu, nie nadać od siebie. ODSTĄPIONO wymaga HUMAN_REVIEW_WAIVER od upoważnionego właściciela, z subject_id, rzeczywistą rewizją/hashem, zakresem, datą, tekstem dowodu i brakiem odwołania. Taka decyzja nie tworzy recenzji ani nie udziela E. BRAK jest stwierdzeniem braku recenzji; nie wolno nim wypełniać nieustalonej historii.

### SF-RULE-STA-004 — E: typowana i zakresowa zgoda

Zakres: SUTTA, VINAYA.

E dopuszczające wymaga PUBLICATION_CONSENT z autoryzowanym właścicielem, subject_id, konkretną rewizją/hashem, zakresem nagrania/publikacji, datą, dowodem i brakiem odwołania. FONT_ONLY, akceptacja szablonu, Standardu, innego tekstu lub rewizji oraz samo APPROVED są niewystarczające. Odmówić obcego typu, zakresu i niezweryfikowanego dowodu. E po recenzji wymaga rzeczywistej recenzji odpowiedniego zakresu; E jako AI ujawnia brak palisty w metryce i zamówionym audio. Nie przenosić zgody MN 41 na inne sutty.

### SF-RULE-STA-005 — Historia statusów i brak wiedzy

Zakres: SUTTA, VINAYA.

Historyczne wartości zachowuje się bez nadpisywania. Nieustaloną historię C/D/E zapisuje się osobno jako UNKNOWN/UNRESOLVED; nie zamienia się niewiedzy w BRAK lub WSTRZYMANE i nie dodaje nowej wartości do zamkniętych enumów. B ma własną dopuszczalną wartość NIEUSTALONE. Nowy dodatni status bez dowodu jest zatrzymany. Dawne DONE oznacza historyczne ukończenie pliku, a nie nową recenzję lub zgodę. Rzeczywiste wcześniejsze zgody zachowują swój dokładny zakres. ZATWIERDZONY_PRZEZ_AI w historycznej mapie oznacza C=PEŁNA_AI, ale nowe potwierdzenie wymaga pełnych rzeczywistych raportów i aktualnej rewizji. RECENZJA_LUDZKA_POTWIERDZONA oznacza D=PEŁNA lub CZĘŚCIOWA według rzeczywistego zakresu i świadectwa człowieka. ZATWIERDZONY_PRZEZ_WŁAŚCICIELA_BEZ_RECENZJI_PALISTY zachowuje historyczne połączenie odstąpienia D i dopuszczenia E jako opracowania AI; nowe nadanie wymaga osobnych zgodnych typowanych dowodów dla obu osi, bez kopiowania samej etykiety. Historyczny PASS/PASS_WITH_NOTES zachowuje zakres, rewizję i uwagi kontroli; nie oznacza publikacji.

### SF-RULE-PUB-001 — Publiczna lista źródeł

Zakres: SUTTA, VINAYA.

Listę budować z rzeczywistych odczytów i użytego zakresu w kolejności grup: tekst Pali/podstawa, kontrola Pali, przekłady porównawcze według pierwszeństwa, dodatkowa kontrola, słowniki, komentarz i teksty pomocnicze. Każde użyte źródło musi być wymienione; nieodczytane nie może być opisane jako użyte. Przy częściowym odczycie podać zakres i rzeczywisty typ materiału. Linkować oficjalne publiczne strony, sprawdzić linki z datą przed publikacją. Nieoficjalną kopię zastąpić publicznym opisem wydania książkowego, zachowując prywatnie faktyczny nośnik odczytu.

### SF-RULE-PUB-002 — Bibliografia, atrybucja i granica capture

Zakres: SUTTA, VINAYA.

Ta sama kompletna lista użytych źródeł stanowi sekcję Źródła dokumentu i podstawę opisu na kanale. DPD wymaga autora i wskazania CC BY-NC-SA 4.0; słownik nieodczytany lub poza zakresem nie trafia do listy jako kontrola. Listę kończy prawdziwa informacja o udziale AI i recenzji palisty lub jej braku. CAPTURED + NIE_ODCZYTANO nie przechodzi walidacji użycia. Publiczny opis nie może twierdzić pełnej kolacji na podstawie kilku terminów ani przypisywać Sujato wpływu z samej infrastruktury.

### SF-RULE-PUB-003 — Licencje, prywatność i historyczne DEC-04/10

Zakres: SUTTA, VINAYA.

Zachować rzeczywistą decyzję o braku monetyzacji i wymóg ponownej decyzji przy jej zmianie. Sam brak monetyzacji nie jest dowodem spełnienia wszystkich warunków CC BY-NC-SA ani praw do konkretnego użycia. Ustalić prawa i atrybucję w realnym zakresie; nierozstrzygnięte prawa blokują zależną publikację. Pełne cudze teksty pozostają wyłącznie w prywatnym, uprawnionym pakiecie dowodów; publicznie krótkie cytaty z lokalizacją. Kod/repo pozostaje prywatny, wszelkie prawa zastrzeżone. Nie dopisywać nowej licencji ani zgody.

### SF-RULE-PUB-004 — Linia EN→PL HH

Zakres: SUTTA, VINAYA.

EN_PL_HH oznacza przekład z konkretnego angielskiego HH/Anīghi. Metoda/metryka wskazuje autora, tytuł, adres, datę i rzeczywisty pomocniczy zakres Pali. Zachować wszystkie oryginalne przypisy HH, odróżniając je od not projektu; luk i potknięć EN nie uzupełniać po cichu. Sporne miejsce oznaczyć notą i sprawdzić w Pali; terminologia projektu pozostaje wiążąca w swoim zakresie. Przed publikacją ustalić licencję i atrybucję HH; bez tej podstawy brak możliwości dopuszczenia E. Nie dodawać domyślnie komentarza audio do K1.

## 7. Zakresy uruchamiane osobnym zleceniem

Audio i nowa odrębna praca tematyczna wymagają właściwego zlecenia. Obowiązkowe sprawdzenie i uzupełnienie relewantnych istniejących dossier po DONE jest dokumentacją dostawy, nie nowym tłumaczeniem ani dowolną zmianą kolejki.

**Odpowiedzialność:** Wykonawca odrębnego zakresu

**Wejście:** Odrębne zlecenie i właściwe źródła.

**Produkt i zakończenie:** Produkt i kontrole tylko zadeklarowanego zakresu.

**Zatrzymanie:** Brak zamówienia audio lub niezatwierdzony wariant: nie uruchamiać zależnej czynności. Nie pomijać obowiązkowej aktualizacji istniejących dossier po DONE.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-AUDIO-001 — Osobne zamówienie i kontrakt

Zakres: AUDIO.

Audio/komentarz lektorski powstaje wyłącznie na odrębne zamówienie, jako osobny zasób z właściwym kontraktem i SCRIPT QA. Wówczas odczytać kanoniczny Standard Tipitaka; tworzenie RC nie jest zamówieniem audio. Brak komentarza w zwykłym K1 nie jest wadą FORMAT ani blokadą przekładu. Zachować pierwotny tekst, datę i wersję; nowe audio otrzymuje własną metrykę, QA i historię. Nie certyfikować nim historycznego Pali-first.

### SF-RULE-AUDIO-002 — Treść i forma komentarza

Zakres: AUDIO.

Komentarz to odrębna redakcja, nie słowa Buddhy ani część line-by-line CORE. Domyślnie 100–170 słów, zwykle 2–3 naturalne akapity: problem i sens sutty; jedna/dwie istotne sprawdzone różnice paralelne, jeśli istnieją; prawdziwa metoda i kontrolerzy. Nie tworzyć różnic dla schematu. Zachować znaczenie doktrynalne, atrybucję, niepewność i brak palisty; nie redukować nauki do relaksu. Styl mówiony bez list, technicznych oznaczeń, surowych linków, emfaz i obietnic. Źródła/lokatory zachować w aparacie odrębnego materiału.

### SF-RULE-AUDIO-003 — SCRIPT QA w rzeczywistym zakresie

Zakres: AUDIO.

SCRIPT QA oddzielnie sprawdza każde zdanie względem kanonu/ujawnionej analizy, kierunek różnic paralelnych, nazwiska i rzeczywiste źródła, brak nieuzasadnionych tez, próbne głośne czytanie dla rytmu/imion/długości i brak znaczników technicznych w warstwie mówionej. Zapisać faktycznie wykonane czytanie i ograniczenia; nie dopisywać fikcyjnego odczytu człowieka. Niewykonana istotna kontrola blokuje finalność audio. Rewizja audio wymaga aktualnych indeksów, właściwego formatowania, ponownego PDF/QA i nowego wpisu, bez usuwania dawnego DONE.

### SF-RULE-THEME-001 — Tworzenie i aktualizacja dossier

Zakres: THEMES.

Tworzyć osobne żywe dossier na życzenie użytkownika albo dla użytecznego zagadnienia przekrojowego, nie dla każdej uwagi. Nazwa: TEMAT · {hasło Pali/pojęcie} · {tytuł polski}; aktualizować w miejscu. W miarę potrzeby zawiera cel, zakres, terminy/formuły, syntezę z rozróżnieniem źródeł, mapę sutt/Vinayi, wkład każdej, status przekładu i bezpośredni link do finalnego PDF oraz wersji źródłowej (dla historycznego produktu link do Doc), paralele, pytania i źródła. Po DONE sprawdzić wszystkie relewantne istniejące dossier; jedna sutta może należeć do wielu.

### SF-RULE-THEME-002 — Mapa tekstów i ograniczenia wnioskowania

Zakres: THEMES.

Mapa odróżnia bezpośrednie wystąpienia formuły/nauki, rozwinięcia jej elementów i teksty powiązane/paralelne. Nie nazywać roboczej listy kompletnym indeksem bez weryfikacji. Twierdzenie filologiczne/historyczne/doktrynalne wymaga odczytanego wydania i dokładnego locus, a nie tylko linku do własnego przekładu. Nieodczytane źródło oznaczyć NIEZWERYFIKOWANE lub hipotezą; odróżnić własną syntezę. Nieobecność terminu nie dowodzi zakazu praktyki; zgodność interpretacji nie dowodzi wyłączności. Dossier nie jest przekładem i nie wymaga translation line-by-line QA.

### SF-RULE-THEME-003 — Dossier nie zmienia kolejki

Zakres: THEMES.

Wpisanie sutty do dossier, także jako „do przetłumaczenia”, nie tworzy QUEUED i nie zmienia kolejności. Wymaga tego odrębna decyzja użytkownika lub wyraźne polecenie dotyczące kolejności. Aktualizacja linku po potwierdzonym DONE jest obowiązkiem dokumentacyjnym, nie nowym zadaniem przekładu.

## 8. Wydanie i zarządzanie zmianami

Dokładną wersję aktywuje jeden wykonawca po wymaganych dowodach, recenzjach i świadomej akceptacji właściciela; każdy zapis ma odczyt. Historię zachowuje się poza aktywnymi instrukcjami.

**Odpowiedzialność:** Jeden wykonawca; właściciel zatwierdza dokładny zakres

**Wejście:** Manifest kandydata, raporty, pilot, migracja, kopie i uzgodnione okno jednego wykonawcy; automatyczny koordynator poza zakresem.

**Produkt i zakończenie:** Dokładny pakiet do oceny; dopiero potem zatwierdzona aktywacja i readback.

**Zatrzymanie:** Otwarta brama lub brak zgody: zachować CANDIDATE, nigdy RELEASED.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-MIG-001 — Migracja dopiero po dry-run i decyzji

Zakres: SUTTA, VINAYA.

Migracja przygotowuje osobny projekt zmian, zachowuje raw i kopię bezpieczeństwa, wersję schematu, źródło dowodu, poprzednią/nową wartość, hash i klucz idempotencji. Dry-run niczego nie aktywuje. Brak dowodu pozostawia UNRESOLVED w metadanych migracji, bez wymyślania statusu osi. Sprawdzić powtórzenie bez zmian, konflikt częściowego zapisu i rollback. Przed rzeczywistą synchronizacją QUEUE/LOG/promptów/repo wymagany jest konkretny plan i upoważnienie właściciela; żadnej syntetycznej zgody do produkcji.

### SF-RULE-REL-001 — Zamrożenie i dwie rzeczywiste recenzje wydania

Zakres: SUTTA, VINAYA.

Zamrozić dokładny kontrakt, kod, konfigurację, testy i produkty pilota. Wykonać dwie odrębne świeże recenzje: normatywną z mapą zachowania obowiązków i techniczną z wykonaniem narzędzi oraz kontrolą produktów. Właściciel zezwolił na dwie recenzje GPT-6.1 dla kandydata wydania. Raporty powstają bez wzajemnych ustaleń przed zamrożeniem; ekspozycja i faktyczny model mają jawny zapis. Przy braku kontekstu przygotować pakiet i prompt bez pozornego raportu. Każde P0/P1 naprawić z kontrolą lub odrzucić z dowodem.

### SF-RULE-REL-002 — Warunki rzeczywistego wydania

Zakres: SUTTA, VINAYA.

Pierwsze wydanie wymaga spójnego pełnego kontraktu, rozliczonej mapy dawnych norm i przyjętych zmian, braku nierozliczonego P0/P1, testów zmienionego zakresu, rzeczywistego pilota, kontroli źródła i obejrzanego PDF, dwóch raportów wydania, gotowej migracji i rollbacku oraz świadomej akceptacji dokładnego manifestu. Właściciel zlecił wykonanie wszystkich ról pilota MN53 przez tego samego agenta: jest to jawny wyjątek zakresowy tego pilota, bez dowodu niezależności i bez zmiany zwykłych obowiązków redaktora, CORE/APARAT oraz IK/ID/IR. Przyjęto ręczny tryb jednego wykonawcy; ochrona referencji wymagana przez odłożony automatyczny koordynator nie jest bramą tego trybu. Stan RELEASED wymaga rzeczywistych zgodnych zapisów i odczytu całego zatwierdzonego zakresu.

### SF-RULE-REL-003 — Bezpieczna aktywacja i kontrola po zapisie

Zakres: SUTTA, VINAYA.

Pierwszą aktywację prowadzi jeden wskazany wykonawca w uzgodnionym oknie bez równoległych zapisów. Przed każdym zapisem odczytuje bieżący obiekt i porównuje go z zaakceptowanym BEFORE; zachowuje pełne natywne kopie Standardu 1.13, QUEUE i LOG oraz kopie lokalnych wejść. Zapisy Google Docs mają requiredRevisionId; odrzucona rewizja lub zaobserwowana obca zmiana zatrzymuje wykonanie. Git służy wersjonowaniu przez zwykłe commity/push bez force-push, rewindu i kasowania historii. Każdy zapis ma odczyt i rzeczywisty wynik; po niepewnym ACK najpierw uzgodnić stan, bez ślepego ponowienia. Przy częściowym wdrożeniu zachować PARTIAL_DEPLOYMENT i wycofywać tylko własne zmiany na uzgodnionej bieżącej rewizji. Manifest, linki i zgody są trwałym zapisem. Ten tryb nie uruchamia koordynatora, nie deklaruje globalnej dzierżawy, niezmienności zdalnej historii ani bezpiecznej automatycznej współbieżności; nie zastępuje authority_check atrapą. Uruchomienie koordynatora pozostaje osobnym zakresem wymagającym jego rzeczywistych zabezpieczeń. Wydanie Standardu nie nadaje E suttom; tag i inne czynności Git muszą należeć do dokładnie zaakceptowanego zakresu.

### SF-RULE-REL-004 — Jedna baza reguł i kontrolowane zmiany

Zakres: SUTTA, VINAYA.

Aktywną instrukcję generuje się z wersjonowanego RULE_REGISTRY.json i jego danych referencyjnych. Nowa zaakceptowana decyzja zastępuje właściwe brzmienie reguły i aktualizuje zależne kontrole; wcześniejsze brzmienie pozostaje w historii. Nie dopisuje się konkurencyjnej instrukcji z ogólnym zastrzeżeniem pierwszeństwa. Każda zmiana podaje źródło, zakres, wpływ i aktualną wersję. Uruchomione zadanie zachowuje swój kontrakt do jawnie rozliczonego przejścia. Starsze protokoły są materiałem historycznym, nie obowiązkową dodatkową lekturą nowych zadań po aktywacji.

## Dane referencyjne dla właściwego zakresu

### Hierarchia źródeł według zbioru

Stan dostępności z katalogu 1.13 jest historyczny (11.10.2026); przed użyciem sprawdzić rzeczywisty zakres. Lista nie jest deklaracją odczytu książek.

**MN**: HH/Anīgha: właściwy przekład lub bezpośrednio relewantne opracowanie → Ñāṇamoli w redakcji Bhikkhu Bodhiego / Bhikkhu Bodhi → Ṭhānissaro Bhikkhu. Kontrola filologiczna: Według konkretnego problemu: warianty, słowniki i literatura.

**SN / AN**: HH gdy adekwatny → Bhikkhu Bodhi → Ṭhānissaro Bhikkhu. Kontrola filologiczna: Według konkretnego problemu i dostępności; nie przyjmować pełnego przekładu HH/Ṭhānissaro z pamięci.

**DN**: HH: indeks z 2026-10-11 wskazywał DN 2, DN 10 → Bhikkhu Bodhi dla DN 1, 2, 15 (BPS), gdy istnieje jego właściwy przekład; poza tym Maurice Walshe, The Long Discourses of the Buddha (Wisdom) → Ṭhānissaro: indeks wskazywał DN 1, 2, 9, 11, 12, 15, 16, 20, 21, 22, 26, 29, 33, 34. Kontrola filologiczna: Walshe także wtedy, gdy drugim kontrolerem jest Bodhi.

**Sutta Nipāta / StNp / Snp**: HH: indeks wskazywał Snp 4.1–4.4, 4.9, 5.9 → Bhikkhu Bodhi, The Suttanipāta (Wisdom, 2017) → Ṭhānissaro Bhikkhu. Kontrola filologiczna: K. R. Norman, The Group of Discourses (PTS).

**Udāna**: HH: indeks wskazywał Ud 1.8 → Ṭhānissaro Bhikkhu. Kontrola filologiczna: John D. Ireland (BPS).

**Itivuttaka**: HH: indeks wskazywał Iti 80 → Ṭhānissaro Bhikkhu. Kontrola filologiczna: John D. Ireland (BPS).

**Dhammapada**: HH: w źródłowym indeksie nie znaleziono → Ṭhānissaro Bhikkhu. Kontrola filologiczna: K. R. Norman, The Word of the Doctrine (PTS).

**Khuddakapāṭha**: HH: w źródłowym indeksie nie znaleziono → Ṭhānissaro Bhikkhu. Kontrola filologiczna: Bhikkhu Ñāṇamoli, Minor Readings (PTS).

**Theragāthā / Therīgāthā**: HH: wskazane Thag 1.21, 2.34, 2.36; dla właściwego zakresu sprawdzić dostępność → Ṭhānissaro Bhikkhu; zakres wyboru albo całości do sprawdzenia. Kontrola filologiczna: K. R. Norman, Elders’ Verses I–II (PTS).

**Inne KN, np. Jātaka, Peṭavatthu**: . Kontrola filologiczna: Osobna decyzja właściciela, gdy zbiór wejdzie do kolejki.

**VinayaFlow**: HH: przekład albo bezpośrednio relewantne opracowanie problemu → Khematto Bhikkhu dla Mahāvaggi i Cullavaggi tam, gdzie dostępny → Ṭhānissaro Bhikkhu, materiały Vinaya i The Buddhist Monastic Code → I.B. Horner / PTS; T.W. Rhys Davids i Hermann Oldenberg → Komentarze Pali, słowniki, inne wydania i badania przy konkretnych problemach. Kontrola filologiczna: Bodhi wyłącznie jako kontroler relewantnych paralelnych sutt; Sujato najwyżej dodatkowy weryfikator; Brahmali nie jest aktywnym nowym poziomem.


### Słowniki i rzeczywiste granice

**DPD** — Digital Pāḷi Dictionary. Rola: Pierwszy słownik roboczy: fleksja, lemma, morfologia, rdzenie, sandhi, złożenia. Zakres: Zapisać datę/wersję; automatyczna dekompozycja nie dowodzi składni zdania. Dla ważnej decyzji dodatkowy właściwy słownik filologiczny.. Adresy: https://www.dpdict.net/, https://docs.dpdict.net/. Licencja zapisana w źródle: CC BY-NC-SA 4.0; masowe cytowanie/redystrybucja wymagają odrębnej kontroli praw

**CONE** — Margaret Cone, A Dictionary of Pāli (PTS). Rola: Kontrola filologiczna z cytatami i przykładami; podać hasło i odczytany tom. Zakres: Według dostarczonego 1.13 trzy elektroniczne tomy, A–Bh. Poza zakresem brak wyniku nie dowodzi nieistnienia słowa. Aktualnego katalogu nie sprawdzano w tej pracy.. Adresy: https://gandhari.org/dictionary?section=dop, https://palitextsociety.org/a-dictionary-of-pali-online/. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

**PED** — T. W. Rhys Davids i William Stede, Pali–English Dictionary (PTS). Rola: Szersze pole znaczeniowe, rozwój leksyki i źródłowe przykłady. Zakres: Historyczne wydanie 1921–1925 wymaga ostrożności wobec nowszych ustaleń; glosa nie jest automatycznym polskim odpowiednikiem. Adresy: https://dsal.uchicago.edu/dictionaries/pali/. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

**CPD** — A Critical Pāli Dictionary, Uniwersytet w Kolonii / PTS. Rola: Krytyczny słownik filologiczny; sprawdzić dokładne hasło i odsyłacze, ewentualnie wariant zapisu bez diakrytyków. Zakres: W źródle niedokończony zakres A–kāreti. Poza zakresem NIEOBEJMUJE_ZAKRESU zamiast brak terminu. Adresy: https://cpd.uni-koeln.de/search. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

**DPPN** — G. P. Malalasekera, Dictionary of Pāli Proper Names. Rola: Imiona, miejsca, postaci i identyfikacja sutt; nie składnia. Zakres: Elektroniczna redakcja może różnić się od druku. Nieoznaczonych dopisków nie przypisywać samemu Malalasekerze. Adresy: https://www.aimwell.org/DPPN/index.html, https://ancient-buddhist-texts.net/Textual-Studies/DPPN/index.htm. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

### Terminologia i zakresy zatwierdzeń

Wpisy o ograniczonym lub niepotwierdzonym zatwierdzeniu nie ustanawiają uniwersalnej glosy. Dla nowych tekstów aktywne konwencje to samādhi → skomponowanie umysłu i sati → pomność (LEX-002/EDIT-003); historyczne zatwierdzenia zachowują swój rzeczywisty zakres.

- **Ānāpānasati**: pamiętność oddychania; zakres: MN 118 i dossier Ānāpānasati; status: ZASTOSOWANE, NIEPOTWIERDZONE.
- **Yoniso manasikāra**: kierowanie umysłu w świetle źródła; zakres: MN 2 i SN 45.55; formy fleksyjne; status: ZASTOSOWANE, NIEPOTWIERDZONE.
- **Saṅkhārā**: aktywności; zakres: SN 12.11; status: ZASTOSOWANE, NIEPOTWIERDZONE.
- **Phassa**: kontakt; zakres: SN 12.11 i MN 18; status: ZASTOSOWANE, NIEPOTWIERDZONE.
- **Yoga / yogakkhema**: jarzmo / bezpieczeństwo od jarzma; zakres: AN 4.10; powiązane StNp 3.2; status: ZASTOSOWANE, NIEPOTWIERDZONE.
- **Papañca**: rozplenianie; zakres: MN 18; status: ZASTOSOWANE, NIEPOTWIERDZONE.
- **Upapajjati**: pojawić się ponownie; pojawi się ponownie, pojawił się ponownie, pojawiają się ponownie; zakres: MN 41 i nowe przekłady; czasownik i parafrazy aparatu, nie ogólne pojęcie odrodzenia; status: ZATWIERDZONE.
- **Opapātika**: pojawiający się spontanicznie; zakres: Użycie MN 41 RC2, przyjęte 2026-10-11; nie uniwersalna akceptacja dla nowych sutt; status: ZASTOSOWANE, ZATWIERDZONE POŚREDNIO.
- **Dhammarakkhitā**: chronione przez Dhammę; zakres: MN 41 RC2; z przypisem o Vin III 139 i sahadhammikā rakkhanti; status: ZATWIERDZONE POŚREDNIO.
- **Saparidaṇḍā**: chronione groźbą kary; zakres: MN 41 RC2; status: ZATWIERDZONE POŚREDNIO.
- **Byāpāda / byāpannacitta / vera**: zła wola / umysł pełen złej woli / wrogość; zakres: MN 41 RC2; status: ZATWIERDZONE POŚREDNIO.
- **Samādhi / asamādhisaṃvattanika**: skomponowanie umysłu / niesprzyjający skomponowaniu umysłu; zakres: doprecyzowanie „umysłu” z 2026-10-15 dla nowych przekładów i zamówionych rewizji; krótka glosa T-02 od 2026-10-11 i MN41 RC2.1 to historia zachowana bez zmian; status: ZATWIERDZONE.

HH pressure → presja w linii materiałów HH; nie ustanawia nowego lemma pali. Pełna morfologia i niepewności wymagają kontroli zdania.

### Wzorzec K1 i nowe produkty

Opis, Interpretacja i pozostałe główne sekcje: 14 pt bold; Decyzje: nagłówek 14 pt i akapit 11 pt. Opis/Interpretacja kursywą. Metryka: nagłówek 14 pt, body 10 pt, szary panel #f0f0f0, lewa linia 3 pt #8c8c8c i padding 8 pt. Tekst #3c3c3c; stopka 10,5 pt po prawej; separator przypisów 144 pt. Linie tekstu 12 pt około 17,3466 pt odpowiadają zmierzonemu Docs 115%, nie CSS 1.15. Przypisy 9,5 pt z własnym rytmem. Ostateczna kontrola obejmuje rzeczywisty PDF. Metryka to 4–6 krótkich wierszy; pełne dowody w repo. Źródłowy K1 i dawne produkty nie są nadpisywane.

### Wykonanie i ograniczenia pierwszej wersji

Nowy proces może być prowadzony przez operatora z jawnym rejestrem etapów i kontrolami narzędzi. Historyczny sfe.finalizer dla natywnych Google Docs pozostaje niezmieniony i nie certyfikuje Markdown. Kontrola Markdown/PDF jest kontrolą techniczną, nie skrótem omijającym źródła, CORE, APARAT, IK/ID/IR i redakcję. Żaden skrypt nie uruchamia modeli ani nie nadaje publikacji. Delegacja wymaga wyraźnego zlecenia; przy braku wymaganej recenzji zachować stan niewykonane i przygotować czysty pakiet do nowego czatu.

### Manifest źródła i znaczenie odczytu

Dla każdego źródła zapisać: source_id, role, language, title, author_or_editor, edition, actual_carrier_url, accessed_at, read_scope, direct_or_indirect, capture_or_snapshot_ref, capture_sha256_when_real, read_event_ref, availability, query_evidence_if_absent, licence_basis, limitations.

- CAPTURED: bajty zachowane; nie dowód lektury.
- READ: rzeczywisty odczyt konkretnego zakresu, wykonawca i dowód.
- PEŁNY_ODCZYT: pełny zakres przypisany danemu źródłu i zadaniu.
- CZĘŚCIOWY_ODCZYT: jawnie wyliczony zakres.
- BRAK_PRZEKŁADU_Z_KWERENDĄ: wynik udokumentowanej kwerendy, nie pojedynczego indeksu.
- BRAK_DOSTĘPU_Z_KWERENDĄ: źródło istnieje, próba odczytu nieskuteczna.
- NIEZWERYFIKOWANE: brak dostatecznego dowodu.

Kwerenda paralel obejmuje: Pali Vinaya i inne miejsca Tipiṭaki; Chińskie Āgamy; Chińskie Vinaye innych szkół; Zachowany sanskryt i fragmenty; Relewantne gāndhārskie, tybetańskie i inne wczesne świadectwa.

### Sygnały terminologii HH–Sujato

Sygnał jest pytaniem do rozstrzygnięcia po sprawdzeniu pali, nie błędem ani uniwersalnie zatwierdzoną glosą. Istniejące wzorce techniczne i świadectwa w config/terminology_hh_sujato_v1.json zachowują DEC-03; przy wykonaniu trzeba zweryfikować ich captures.

- mettā: HH friendliness; Sujato love.
- viharati: HH abide; Sujato meditate.
- yogo karaṇīyo: HH you should exert yourselves; Sujato you should practice meditation.
- jhāna / jhāyati: HH jhāna; Sujato absorption.
- upapajjati: HH reappear; Sujato be reborn.
- bhikkhu: HH bhikkhu; Sujato mendicant.
- bhagavā: HH the Auspicious One; Sujato the Buddha.
- samādhi: HH composure; Sujato immersion.
- sati / sato: HH recollected; Sujato mindful.
- kusala / akusala: HH (un)beneficial; Sujato (un)skillful.
- pīti: HH joy; Sujato rapture.
- vitakka-vicāra (jhāna formula): HH thinking and pondering; Sujato placing the mind and keeping it connected.
- adhammacariyā visamacariyā: HH conduct not in line with the Dhamma, unsuitable; Sujato unprincipled and immoral.
- byāpāda: HH averse; Sujato malicious / ill will.

- ZATWIERDZONE: Wyraźna akceptacja właściciela, świadectwo i zakres.
- ZATWIERDZONE POŚREDNIO: Akceptacja użycia wraz z określonym wydaniem; tylko udokumentowany zakres tej wersji, nie automatycznie nowe sutty.
- ZASTOSOWANE, NIEPOTWIERDZONE: Zaobserwowane użycie, bez odtworzonego świadectwa; nie oznacza że zgoda nigdy nie istniała.
- PROPOZYCJA: Nieprzyjęte rozwiązanie.
- WYCOFANE: Historia zastąpionej decyzji.

### Reguły QUEUE i LOG

QUEUE: 1OYftSe43oq7a6xGGxuukbN-q6GeNcBu9Ipws-9o5du4. LOG: 1Ur7At14TrljgA1le8RnI3TwOaYtlmJNOo8DmnWsYSAI. Odczytać bieżący stan; nie traktować dawnego snapshotu jako obecnej kolejki.

1. Przed każdym nowym tłumaczeniem odczytać aktywny kontrakt SuttaFlow i ten dokument.

2. Sprawdzić przekłady na Drive i wpisy w Translation Log po identyfikatorze i zakresie. Istniejący historyczny DONE potwierdzony dokumentem i logiem uzgodnić bez tworzenia duplikatu; nie oznacza to nowego QA według obecnego Standardu. Sama nazwa „finalny” nie wystarcza. Gdy dokument istnieje bez weryfikowalnego statusu, zapisać stan do uzgodnienia jako BLOCKED, nie nadpisywać go i nie zgadywać ukończenia.

3. Polecenie „kontynuuj” wznawia ACTIVE. Jeśli istnieje blokująca BLOCKED, dotyczy najpierw jej problemu; brak rozwiązania nie upoważnia do przeskoczenia pozycji. Gdy nie ma ACTIVE ani BLOCKED, rozpocząć NEXT tylko przy otwartej bramie fazy.

4. Inwariant: najwyżej jedna bieżąca pozycja ACTIVE albo BLOCKED i wtedy zero NEXT. Przy braku ACTIVE/BLOCKED, otwartej bramie i oczekujących pozycjach bieżącej fazy istnieje dokładnie jeden NEXT, pierwszy w ustalonej kolejności. Pusta kolejka lub zamknięta brama fazy ma zero NEXT. Sprzeczny stan wymaga uzgodnienia z logiem, nie arbitralnego wyboru tekstu.

5. Start: NEXT → ACTIVE; pozostałe pozycje pozostają QUEUED. Problem uniemożliwiający kontynuację: ACTIVE → BLOCKED, z opisem przyczyny, zachowanych materiałów i warunku wznowienia; po usunięciu problemu BLOCKED → ACTIVE. Zakończenie dopiero po bramach tekstowej i FORMAT oraz akceptacji według reguł QA, APP, FMT i STA tego kontraktu. Najpierw sprawdzić finalny dokument, zapisać i odczytać wpis logu, potem ACTIVE → DONE.

6. Po potwierdzonym DONE pierwsza kolejna QUEUED tej samej fazy staje się NEXT, jeżeli nie pozostała ACTIVE/BLOCKED. Nie rozpoczynać jej automatycznie, gdy polecenie obejmowało jedną suttę. Jeśli ukończono ostatnią pozycję fazy, zastosować regułę 10 zamiast awansu tekstu z następnej fazy.

7. Najnowsza wyraźna decyzja użytkownika może dodać, usunąć, przesunąć lub pominąć pozycję. Zmianę należy od razu odzwierciedlić tutaj; nie wolno polegać wyłącznie na pamięci czatu.

8. Archiwizacja następuje przy każdym ukończeniu: dopiero po odczycie potwierdzającym wpis i działający odsyłacz w Translation Log usunąć szczegółową pozycję DONE z kolejki, zachowując licznik fazy i informację o ostatnio ukończonej sutcie. Historii nie usuwać. Po przerwaniu zapisu uzgodnić dokument, log i kolejkę po identyfikatorze oraz wersji; nie dopisywać ponownie istniejącego wpisu. Rewizja przekładu jest nowym zdarzeniem w logu, nie nową suttą w kolejce, chyba że użytkownik zarządzi ponowne tłumaczenie.

9. Jeżeli dwa wpisy okażą się tym samym zakresem tekstu, nie tworzyć duplikatu; scalić stan i zachować jednoznaczne odwołanie.

10. Po ostatniej pozycji fazy ustawić bramę ZAMKNIĘTA i zero NEXT; następne plany pozostają QUEUED. Poinformować o zakończeniu fazy. Dopiero kolejne polecenie użytkownika albo wcześniejsza wyraźna zgoda na automatyczne przejście otwiera następną fazę i awansuje jej pierwszą QUEUED do NEXT. Świadome pominięcie wymaga decyzji użytkownika: oznaczyć SKIPPED z powodem, zachować ślad decyzji i dopiero wtedy ustalić kolejną pozycję.

11. Jeśli kolejka i wcześniejsza rozmowa są sprzeczne, obowiązuje kolejka, chyba że użytkownik właśnie podał nowszą instrukcję. Nowszą instrukcję trzeba najpierw wpisać do kolejki.

12. Nie zmieniać kolejności na podstawie własnej oceny „naturalnej” sekwencji. Można zaproponować zmianę, ale wymaga ona decyzji użytkownika.

1. Nowy wpis ukończenia powstaje po przejściu bram tekstowej i FORMAT oraz sprawdzeniu finalnego produktu właściwego dla ścieżki (nowy Markdown/PDF lub historyczny Google Doc). Zapis logu z wynikiem DONE należy odczytać kontrolnie, zanim zaktualizuje się i oczyści kolejkę. Wymagania jakościowe i akceptację zastrzeżeń określa wyłącznie reguły QA, APP, FMT i STA tego kontraktu; sam wpis nie jest dowodem wykonania kontroli.

2. Nowy wpis zachowuje identyfikator i zakres tekstu, tytuł Pali i polski, datę ukończenia według Europe/Warsaw, link do finalnego produktu właściwego dla ścieżki (nowy Markdown/PDF lub historyczny Google Doc), wersję Standardu oraz krótki protokół QA. Protokół identyfikuje źródło, sprawdzonego kandydata, wykonawcę i rodzaj review, ważne problemy i ich rozstrzygnięcia, akceptację uwag oraz wersję dokumentu i trwały odsyłacz do rzeczywiście sprawdzonego PDF. Brakujące dawne dowody oznacza się jako nieodtworzone, nie dopisuje z pamięci.

3. Zamknięte fazy lub większe partie są grupowane chronologicznie.

4. Log jest historią audytową: wpisów nie usuwać. Korekty istniejącego przekładu odnotowywać jako rewizję, nie jako zniknięcie wcześniejszego wykonania.

5. 01_SUTTAFLOW_QUEUE pozostaje źródłem prawdy dla tego, co ma być wykonywane teraz; ten dokument odpowiada za to, co już zakończono.

Zakres historycznych wyników: wpisy istniejące przed wdrożeniem Standardu 1.0, do AN 4.161 włącznie, zachowują pierwotne statusy i uwagi. Oznaczają ukończenie według ówczesnych, nienumerowanych zasad, nie nową certyfikację zgodności z 1.0. W tej naprawie dokumentacji nie wykonano ponownego pełnego QA korpusu ani nie odtworzono brakujących protokołów. Nowe audyty i korekty są osobnymi zdarzeniami. Data rewizji nie zastępuje daty pierwotnego ukończenia.

Klucz zdarzenia: subject_id, declared_scope, source_edition, candidate_revision_or_content_hash, event_type. Najpierw odczyt produktu, potem zapis i odczyt LOG, na końcu uzgodnienie QUEUE. Wszystkie daty Europe/Warsaw.
