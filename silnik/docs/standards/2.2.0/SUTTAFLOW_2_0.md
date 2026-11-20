# SuttaFlow 2.2.0 — proces tłumaczenia

Aktywna wersja Standardu. Zapis zgody: prace/20261025-wydanie-2.2.0/aktywacja/OWNER_APPROVAL.md.

Ten dokument powstaje z RULE_REGISTRY.json. Zmiany wprowadza się w rejestrze; nie utrzymuje się osobnych ręcznie redagowanych instrukcji.

## Przebieg w skrócie

1. Odczytaj stan zadania, właściwą kolejkę i istniejące produkty. Ustal źródło, zakres i wersję kontraktu. Nie powtarzaj ukończonych etapów.
2. Dla nowego Pali-first odczytaj całe Pali i utrwal R0 przed kontrolnymi przekładami. Zamówiona rewizja zachowuje istniejące R0 i ekspozycję, bez udawania nowego ślepego początku. EN→PL HH opiera się na konkretnym angielskim źródle i zachowuje jego przypisy; kontrola Pali ma jawny faktyczny zakres. Dla innej tradycji lub pośrednika ustal język, świadectwo i kontroluj właściwą podstawę zgodnie z SRC-001. Bramy wierności, źródeł i autokontroli pozostają; recenzja innego modelu obowiązuje tylko w odrębnie zleconym zakresie, bez fikcyjnej etykiety Pali-first.
3. Jeden autor sprawdza całe znaczenie względem właściwej podstawy, następnie czyta całą polszczyznę bez źródła i szkiców. Zmiany znaczeniowe wracają do źródła. Miejsca wymagające doprecyzowania przedstawia w karcie z kontekstem, podglądem i automatycznymJSON; wdrożenie wyboru wymaga osobnego polecenia.
4. Autor kontroluje cały aparat w zakresach IK/ID/IR. Odrębna recenzja jest opcjonalna, wymaga zlecenia i nie zastępuje odpowiedzialności autora.
5. Zamknięty tekst zapisuje się wMarkdown; kolejne przekłady zPali mają sprawdzone paryPL–Pali z pełnymi notami, strofami i zatwierdzonymK1. Sprawdzić konwersję i cały rzeczywistyPDF; dowody techniczne pozostają wrepo.
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

Kandydat 2.2.0 konsoliduje zatwierdzony układ polsko-palijski, odstępy strof, karty ocen z autozapisemJSON, kontrolę znaczenia, redakcję i terminologię w ich rzeczywistych zakresach. Do odrębnej zgody na dokładny manifest i potwierdzonej aktywacji obowiązuje wydany Standard 2.1.0 wraz z już przyjętymi decyzjami właściciela. Kandydat nie migruje rozpoczętych zadań ani nie zmienia dawnych Standardów, tagów, produktów i raportów. Nie nadaje zgody publikacji sutt, delegacji lub aktywacji. CzynnościGit wymagają zleconego zakresu. Koordynator pozostaje nieaktywny.

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

Produkty sutt: 01_Sutty i Kanon Palijski/{DN,MN,SN,AN,KN}; KN obejmuje Sutta Nipāta/StNp. Vinaya: folder Vinaya i odpowiednie części Mahāvagga, Suttavibhaṅga, Cullavagga, Mūlasarvāstivāda/Bhaiṣajyavastu; inne tradycje trzymać osobno. Themes: 04_SUTTAFLOW_THEMES · Zestawienia tematyczne. Pakiety recenzji, szkice i audyty umieszczać poza folderami produktów w 00_ARCHIWALNE_TŁUMACZENIA lub wskazanym katalogu. Release 2.0 ma osobną przestrzeń roboczą; nie przenosi istniejących produktów. Docelowo foldery zbiorów zawierają tylko aktualny PDF, Markdown i OPIS; archiwalne rewizje tej samej sutty oraz zaplecze są odrębne. Zastosowanie tej organizacji do istniejących zasobów wymaga inwentaryzacji, mapy, zgody i readback; sama norma niczego nie przenosi.

### SF-RULE-OPS-004 — Nazewnictwo i daty

Zakres: SUTTA, VINAYA.

Nazwa produktu czytelniczego: {NIKĀJA NR} · {Tytuł Pali} · {Tytuł polski}.pdf; analogicznie .md i · OPIS.txt według rzeczywistego formatu. Dla Vinayi używać referencji i tytułu rzeczywistej podstawy, bez wymyślania Pali. Modele, daty audytów, statusy i kody rewizji prowadzić w metryce, LOG i archiwum. Rewizja ma rzeczywistą datę Europe/Warsaw; dla Markdown identyfikatorem są SHA-256 surowych bajtów i istniejący commit/blob, dla Google Docs Doc ID i revisionId. Eksport wiąże źródło z hashem PDF. Nie zmieniać istniejących nazw ani lokalizacji automatycznie: wymagana inwentaryzacja ID, wersji, statusów i zależności, zweryfikowana mapa migracji, kopie i odrębny zakres zgody. Zachować stabilne ID i historię; nie przepisywać rozszerzeń bez konwersji.

### SF-RULE-OPS-005 — QUEUE i bramy faz

Zakres: SUTTA, VINAYA.

Kanoniczny algorytm kolejki pozostaje w 01_SUTTAFLOW_QUEUE, „Zasady zarządzania kolejką”; reguły proceduralne są także w danych referencyjnych tego kontraktu; bieżący stan odczytać w QUEUE. Dopuszczalne statusy: NEXT, ACTIVE, QUEUED, DONE, BLOCKED, SKIPPED. Najwyżej jedna ACTIVE albo blokująca BLOCKED, przy niej zero NEXT. Bez obu, przy otwartej fazie, dokładnie jeden pierwszy NEXT. Po zamknięciu fazy zero NEXT i dalsze plany QUEUED, aż do upoważnionego przejścia. Pominięcie i zmiana kolejności wymagają decyzji użytkownika. Backlog tworzyć dopiero przy trwałym przekroczeniu około 20 oczekujących; QUEUE zachowuje około 10–20 najbliższych.

### SF-RULE-OPS-006 — Zakończenie i idempotentne uzgodnienie

Zakres: SUTTA, VINAYA.

Po wymaganych bramach tekstowych i FORMAT odczytać finalny PDF i jego wersję źródłową (w ścieżce historycznej także Doc), dopisać i odczytać sprawdzony wpis LOG z protokołem oraz trwałym PDF; następnie oznaczyć DONE i usunąć z QUEUE tylko szczegółowy wpis tej ukończonej pozycji, zachowując licznik fazy i link do historii. Rewizja jest nowym zdarzeniem logu, nie automatycznie nową suttą kolejki. Przerwany zapis uzgadniać po subject_id, zakresie, rewizji i istniejącym wpisie. Powtórzenie nie może tworzyć duplikatu ani usuwać historii. Kilka zapisów nie stanowi jednej transakcji. Na końcu przekazać w czacie działający link do produktu oraz krótką informację o rzeczywiście użytych źródłach, kontroli i ograniczeniach.

### SF-RULE-OPS-007 — Aktywna brama D4 / MN 53

Zakres: SUTTA, VINAYA.

Historyczna decyzja OWNER-20261011-STANDARD15-D4 i jej testy pozostają w historii. Aktualną pozycję i status MN53 ustala odczyt QUEUE/LOG, nie dawny snapshot NEXT. Zlecony test kolejnej rewizji zachowuje historię R8 i T1, znaną ekspozycję oraz wykonane kontrole; nie przedstawia się go jako nowego ślepego R0. Nie zmienia kolejki ani zgód publikacyjnych.

### SF-RULE-OPS-008 — Checkpoint i rewind

Zakres: SUTTA, VINAYA.

Każdy etap zapisuje wejściowe rewizje i hashe, stan repo/dokumentów, otwarte problemy, faktyczne wyniki i następny atomowy krok. Po przerwaniu weryfikować piny przed wznowieniem. Rewind oznacza powrót do ostatniego udokumentowanego stanu kopii roboczej i ponowną kontrolę zależności; zachowuje późniejsze artefakty jako historię. Nie cofać cudzych zmian ani właścicielskich decyzji samowolnie. Opisać częściowy zapis i plan odtworzenia; nie obiecywać pracy poza aktywną sesją.

## 2. Pali, R0 i porównania

Dla nowego Pali-first odczytaj całe Pali i utrwal R0 przed kontrolnymi przekładami. Zamówiona rewizja zachowuje istniejące R0 i ekspozycję, bez udawania nowego ślepego początku. EN→PL HH opiera się na konkretnym angielskim źródle i zachowuje jego przypisy; kontrola Pali ma jawny faktyczny zakres. Dla innej tradycji lub pośrednika ustal język, świadectwo i kontroluj właściwą podstawę zgodnie z SRC-001. Bramy wierności, źródeł i autokontroli pozostają; recenzja innego modelu obowiązuje tylko w odrębnie zleconym zakresie, bez fikcyjnej etykiety Pali-first.

**Odpowiedzialność:** Autor

**Wejście:** Pełna właściwa podstawa: Pali, zamówiony EN HH lub jawnie określony zachowany język/krytyczny pośrednik; dla rewizji istniejące wersje i ekspozycja.

**Produkt i zakończenie:** Dla nowego Pali-first pełny R0; dla rewizji zachowane R0 i ekspozycja. Pozostałe ścieżki utrwalają rzeczywistą podstawę, porównania i mapę decyzji, bez fikcyjnego R0 z Pali.

**Zatrzymanie:** Brak źródła/kontrolera: jawna kwerenda i wyjątek; brak dowodu nie daje zgodności.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-SRC-001 — SOURCE FIRST i kategorie pośrednie

Zakres: SUTTA, VINAYA.

Dla sutt i palijskiej Vinayi podstawą przekładu jest Pali. Dla innej tradycji ustalić właściwy język i najlepiej zachowane świadectwo. Gdy brak oryginału albo rzetelnego dostępu, można użyć krytycznego przekładu pośredniego, jawnie podając zachowany język, pośrednika i ograniczenie pewności; kontrolę wykonać wobec niego i dostępnych fragmentów oryginału. Nie nazywać takiego wyniku bezpośrednim przekładem z Pali, sanskrytu, chińskiego lub tybetańskiego. EN→PL HH ma własną kategorię i własną podstawę kontroli. Przed kontrolą utrwalić basis.method, basis.language, basis.source_id i basis.indirect; dla pośrednictwa także pośrednika, uzasadnienie i ograniczenia. Dla innych języków wskazać odczytane słowniki, wydania i odpowiednich kontrolerów w planie źródeł. Nakazy Pali, palijskich słowników i hierarchii HH dotyczą właściwej palijskiej ścieżki lub jawnie sprawdzanego fragmentu Pali. Nie wymagają nieistniejącego zdania Pali ani nie nadają paraleli innej tradycji roli podstawy rozstrzygającej.

### SF-RULE-SRC-002 — Wydanie, autor i faktyczny nośnik

Zakres: SUTTA, VINAYA.

Manifest odróżnia wydanie tekstu, jego język, autora/redaktora/przekładowcę, platformę i faktyczny adres odczytu. SuttaCentral może służyć identyfikacji paralel, wariantów i dostępu do oznaczonego Pali przy nieskutecznym dostępie pierwotnym; podać cel i faktyczny zakres. Jeśli odczytano tam podstawę, tak to nazwać. Infrastruktura SuttaCentral nie czyni Sujato źródłem przekładu. Lustro, w tym A Buddhist View lub kopia książki, nie jest automatycznie oficjalnym wydawcą. We wszystkich zbiorach przekład Sujato może być wyłącznie dodatkowym weryfikatorem; nie używać go jako źródła sformułowań ani interpretacji, także poza 14 wzorcami terminologicznymi. Charakterystyczna terminologia wymaga osobnej decyzji. Zgodność liczyć według DEC-03, bez rozszerzania jego zakresu.

### SF-RULE-SRC-003 — R0 i dowód kolejności

Zakres: SUTTA, VINAYA.

Dla nowego przebiegu Pali-first: Pełny R0 musi istnieć jako utrwalony artefakt o określonym zakresie, z rzeczywiście obliczonym SHA-256 surowych bajtów, datą/czasem i dowodem zapisania przed pierwszym odczytem przekładów kontrolnych. Odczytać i zweryfikować sam artefakt, a nie samą niepustą wartość hasha. Pusty zakres, niepełny R0, hash „x”, niezgodne bajty lub odwrócona kolejność nie uzasadniają B=PALI_FIRST_UDOKUMENTOWANY. Capture EN przed R0 jest dopuszczalnym technicznym zachowaniem bajtów tylko bez udostępnienia ich treści autorowi; faktyczne ekspozycje zapisać.

### SF-RULE-SRC-004 — Wcześniejsza ekspozycja i granice Pali-first

Zakres: SUTTA, VINAYA.

Udokumentowane Pali-first opisuje kolejność pracy, nie niezależność treningu modelu. Zachować znane wcześniejsze lektury i ekspozycję. Brak R0 albo dowodu kolejności oznacza PALI_FIRST_DEKLAROWANY lub NIEUSTALONE według dowodów. Czytelnik otrzymuje prawdziwy opis, np. „Przekład opracowano z pomocą sztucznej inteligencji, a jego aktualną wersję sprawdzono względem tekstu palijskiego”. Nie sugerować bezpośredniego ani ślepego powstania z pali przy nieustalonej pierwotnej metodzie. Pełne dowody i ograniczenia metody przechowywać w QA, istotne ograniczenia wiarygodności ujawniać zwięźle w metodzie/weryfikacji.

### SF-RULE-SRC-005 — Faktyczne odczyty i status źródła

Zakres: SUTTA, VINAYA.

CAPTURED jest zachowaniem bajtów, READ/ODCZYTANE rzeczywistą lekturą wskazanego zakresu. Wpis odczytu zawiera wykonawcę, czas, źródło, locator, zakres i dowód użycia w pracy; sam capture_log ani obecność na dysku nie wystarcza. Rozróżniać PEŁNY_ODCZYT, CZĘŚCIOWY_ODCZYT, BRAK_PRZEKŁADU_Z_KWERENDĄ, BRAK_DOSTĘPU_Z_KWERENDĄ i NIEZWERYFIKOWANE. Oryginalne nazwy statusów zachować wraz z semantyką i słownikiem adaptera. Brak odczytu nie może oznaczać zgodności ani nieistnienia utworu.

### SF-RULE-SRC-006 — Ścisła kolejność kontrolerów

Zakres: SUTTA, VINAYA.

Dla nowego Pali-first po R0 porównywać faktyczny zakres kolejno: HH/Anīgha (przekład lub bezpośrednio relewantne opracowanie), właściwy kontroler danego zbioru, następnie Ṭhānissaro. Dla MN właściwy jest Ñāṇamoli w redakcji Bodhiego/Bodhi; dla DN i KN obowiązuje pełen katalog danych referencyjnych tego kontraktu. Przekład i wykład/esej/glosariusz są różnymi dowodami. Gdy HH skraca lub nie obejmuje fragmentu, użyć kolejnego poziomu. Przy istotnej niejasności porównać wszystkie dodatkowo dostępne i sprawdzalne przekłady, zachowując kolejność; nie uśredniać ich. EN→PL kontroluje zadeklarowaną podstawę EN i jawny pomocniczy zakres Pali, bez fikcyjnego wcześniejszego R0 z Pali. Dla innej tradycji albo krytycznego pośrednika stosować plan odpowiednich kontrolerów według SRC-001/SRC-009; palijskiej hierarchii nie przenosić automatycznie na inny język.

### SF-RULE-SRC-007 — Kwerenda, brak i wyjątek kontrolny

Zakres: SUTTA, VINAYA.

Sprawdzić oficjalny indeks HH oraz relewantne znane studia/publikacje; dla EPUB podać nazwę, wydanie i rozdział. Dla każdego poziomu oddzielić odczytane, zidentyfikowane nieodczytane i nieznalezione po kwerendzie, z datą i zapytaniami. Brak w jednym indeksie nie dowodzi nieistnienia. Dostępne źródło najwyższego priorytetu porównać w zadeklarowanym zakresie. Niedostępność rozlicza tylko udokumentowany wyjątek z uzasadnieniem. Brak wszelkich porównań nie może dać wyniku dodatniego bez osobnej decyzji człowieka o ograniczeniach. Nie zastępować automatycznie brakującego kontrolera Sujato.

### SF-RULE-SRC-008 — Wykaz DN/KN i decyzje dla dalszych zbiorów

Zakres: SUTTA, VINAYA.

Pełny wykaz danych referencyjnych tego kontraktu jest normatywny: obejmuje DN z Bodhim/Walshe’em i listą 14 DN Ṭhānissaro; Sutta Nipāta; Udānę; Itivuttakę; Dhammapadę; Khuddakapāṭhę; Theragāthę i Therīgāthę, z kontrolerami filologicznymi. Zakresy indeksów z 2026-10-11 są zapisami odczytu, nie obietnicą aktualnej dostępności. Potwierdzić źródła przy pierwszej sutcie zbioru. Inne KN, np. Jātaka i Peṭavatthu, wymagają osobnej decyzji przy wejściu do kolejki. Proponowane minimum dwóch przekładów w KN nie zostaje aktywowane.

### SF-RULE-SRC-009 — VinayaFlow: kontrola i struktura

Zakres: SUTTA, VINAYA.

Zachować właściwe identyfikatory, dla palijskiej Vinayi Mv/Cv, i granice vatthu, narracji, historii reguły, reguły/zezwolenia, definicji, wyjątków i procedur wspólnotowych. Dla palijskiej Vinayi kontrolerzy: HH gdy bezpośrednio relewantny → Khematto dla dostępnej Mahāvaggi/Cullavaggi → Ṭhānissaro, Vinaya i BMC → Horner/PTS oraz Rhys Davids–Oldenberg → właściwe komentarze, wydania, słowniki i badania. Dla innej tradycji odnotować jej identyfikatory i ustalić plan kontroli właściwego języka i świadectwa według SRC-001; palijski kontroler jest tylko relewantnym porównaniem, nie obowiązkową podstawą. Bodhi jest kontrolerem relewantnej sutty, nie domyślnym Vinayi. Nie mieszać tradycji ani przesądzać kierunku zależności paralel. Brahmali pozostaje propozycją.

### SF-RULE-SRC-010 — Słowniki i zakresy

Zakres: SUTTA, VINAYA.

Dla odczytywanego Pali stosować pięć słowników z danych referencyjnych: DPD; Cone A Dictionary of Pāli; PED Rhys Davids–Stede; CPD; DPPN Malalasekery. DPD służy najpierw morfologii, podstawom, rdzeniom, sandhi i złożeniom, z datą/wersją. Dla ważnego terminu dodatkowo odczytać właściwy słownik filologiczny. Cone obejmuje podany w źródle zakres A–Bh, CPD A–kāreti; poza nim NIEOBEJMUJE_ZAKRESU, a nie „brak terminu”. DPPN służy nazwom, nie rozstrzyganiu składni; nie przypisywać Malalasekerze nieoznaczonych dopisków redakcji elektronicznej. Dla innego języka użyć odpowiednich słowników zapisanych w planie źródeł; nie deklarować kontroli DPD niepalijskiego terminu. Dla EN→PL słowniki Pali dokumentują wyłącznie rzeczywiście sprawdzony pomocniczy zakres Pali.

### SF-RULE-SRC-011 — Protokół leksykalny

Zakres: SUTTA, VINAYA.

Dla istotnego, wieloznacznego lub niejasnego terminu zapisać całe zdanie właściwej podstawy źródłowej z lokatorem, formę powierzchniową, możliwe analizy, kontekst i porównania, alternatywy PL, wybór i powody odrzucenia, niepewność i przypis. Dla Pali podać lemma/rdzeń, odczytane znaczenia DPD i właściwego Cone/PED/CPD, wystąpienia kanoniczne i rzeczywistą kontrolę HH → właściwy kontroler → Ṭhānissaro. Dla innego języka podać analizy, słowniki i kontrolerów właściwych tej podstawie według SRC-001/SRC-009. Dla EN→PL zachować zdanie EN jako podstawę, a odczyt Pali i jego słowników wykazać tylko w faktycznym zakresie; różnicy nie poprawiać po cichu. Niedostępny słownik: NIEODCZYTANO z datą i powodem. Dwie nieodczytane pozycje nie tworzą podwójnej kontroli. Składnię badać na poziomie zdania, nie przez sumowanie glos.

### SF-RULE-SRC-012 — Obowiązkowa kwerenda paralel

Zakres: SUTTA, VINAYA.

Przy każdej nowej sutcie i Vinayi sprawdzić paralele w Pali/Vinayi, chińskich Āgamach i Vinayach, zachowanym sanskrycie oraz relewantnych gāndhārskich, tybetańskich i innych wczesnych świadectwach. Zapisać wynik, zakres kwerendy i poziom lektury. Identyfikacja katalogowa nie jest analizą różnic. Materialne różnice wydarzeń, osób, liczb, kolejności, relacji przyczynowych lub doktryny ujawnić. Głównego przekładu nie kompilować po cichu z tradycji; ewentualny wpływ wariantu uzasadnić argumentem tekstualnym.

### SF-RULE-LEX-001 — Pełen rejestr terminologii i akceptacja

Zakres: SUTTA, VINAYA.

Rejestr terminologii w danych referencyjnych jest częścią kontraktu, nie nową kolejką. Każdy wpis zachowuje Pali, PL, zakres, wyjątki, uzasadnienie/źródło, status i historię. ZATWIERDZONE wymaga wyraźnej akceptacji w zakresie; ZATWIERDZONE POŚREDNIO obejmuje tylko przyjęte użycie w wskazanym wydaniu. ZASTOSOWANE, NIEPOTWIERDZONE nie tworzy nakazu; PROPOZYCJA nie obowiązuje, WYCOFANE przechowuje zastąpienie. Przed nową suttą odczytać relewantne formuły. Zmianę konwencji uzasadnić i wskazać możliwy wpływ na starsze teksty, bez ich automatycznej korekty. Jedynym zapisywalnym źródłem wpisów jest strukturalny rejestr w reference_data tej wersji RULE_REGISTRY.json; widok terminologii jest generowany. Każdy wpis ma stałe ID, znaczenie/kontekst, język, jawny zakres roboczy i ograniczenia detektora. Nowe hasło zaczyna jako PROPOZYCJA, chyba że odtwarza udokumentowaną istniejącą normę. Zmiana zachowuje poprzedni wpis w historii; wycofanie nie usuwa rekordu. Brak daty lub cytatu zgody pozostaje jawny. Zmiany przechodzą SF-RULE-REL-004 i kontrolę spójności; import nie nadaje nowego zatwierdzenia.

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

Rozstrzyga właściwa podstawa źródłowa ustalona według SRC-001, w kontekście i z odpowiednimi słownikami. Dla Pali rozstrzyga tekst Pali; terminologię rozstrzyga HH po kontroli Pali i DPD w granicach zatwierdzonych decyzji; pierwszeństwo HH nie nadaje mu bezbłędności ani prawa do zmiany Pali. Dla innej tradycji lub pośrednika rozstrzyga zadeklarowane świadectwo i ujawniony zakres kontroli; palijskiej paraleli ani glosy DPD nie podstawiać za niepalijskie źródło. EN→PL zachowuje sens właściwego EN i oryginalne noty, ze spornymi miejscami ujawnionymi według PUB-004. Gdy liczba grup i preferencja terminologiczna wskazują inne rozwiązania, zachować obie podstawy i uzasadnienie. Przy upoważnionym odstąpieniu od palisty AI dokumentuje miejsce, właściwy tekst źródłowy, odczytania, słowniki, grupy za/przeciw, decyzję, pewność i regułę. Rekordy o średniej/niższej pewności mają pierwszeństwo przyszłej właściwej recenzji.

### SF-RULE-LEX-006 — Kalki i zamrożone konwencje redakcyjne

Zakres: SUTTA, VINAYA.

Zgłaszać sformułowania PL bez podstawy we właściwym źródle, przejęte z kontrolera lub pośrednika. Dla Pali dotychczasowy sygnał porównuje odpowiednik EN u HH/Sujato w danym akapicie z glosami DPD jego słów Pali; każdy sygnał ma rozliczenie. Lista z MN 41 („innym”/to others, „naruszenie praw”/by law, „Przeciwnie”/Instead) jest ograniczona; brak sygnału nie dowodzi braku kalk. W EN→PL HH odniesieniem jest HH, a w innej zadeklarowanej ścieżce jej rzeczywista podstawa. Nie przedstawiać palijskiego sygnału technicznego jako kontroli innego języka. DEC-07 zachowuje w MN 41 przyjęty stan nazw: Pali pozostaje Pali, przekład pozostaje przekładem; nie ujednolicać wstecz.

### SF-RULE-LEX-007 — Kontrola stosowania rejestru i rozliczenie odstępstw

Zakres: SUTTA, VINAYA.

Przed zamrożeniem kandydata do CORE oraz przed zamknięciem pliku operator wykonuje kontrolę terminologii dla aktualnych bajtów i pełnego zadeklarowanego zakresu przekładu oraz aparatu; po zmianie odnawia tylko zależny zakres i jego piny. sfe.terminology check sprawdza wersję rejestru, hashe plików, jednostki i jawny kontekst: tekst, konkretny artefakt, rodzaj pracy i język. Wzorce działają w rzeczywistych parach źródło–PL, nie przez globalną zamianę. Zatwierdzony wpis obowiązuje wyłącznie w swoim zakresie; użycia niepotwierdzone, propozycje i wycofane oraz wpisy poza zakresem są odniesieniem, nie nakazem. Każdy sygnał wiążącego wpisu wymaga faktycznego rozliczenia autora/redaktora ze źródłem, uzasadnieniem, wykonawcą i datą, także gdy znaleziono oczekiwane słowo. Uzasadniony wyjątek dotyczy tylko wskazanego użycia; nowa konwencja wymaga decyzji i zmiany rejestru. Nierozliczone sygnały lub stare hashe zatrzymują zamknięcie kontroli. Techniczny zapis rozliczenia nie uwierzytelnia decyzji ani nie nadaje PASS, DONE, D/E. Detektor ma jawnie ograniczoną morfologię; brak sygnału lub próbka nie zastępują kontroli całego znaczenia według SF-RULE-QA-001, SF-RULE-EDIT-001 i SF-RULE-LEX-005. Rejestru rozliczeń konkretnego przekładu, raportów autora i wcześniejszych ocen nie dołącza się do czystego CORE według SF-RULE-CORE-001.

## 3. Pełne pokrycie i dwie autokontrole autora

Jeden autor sprawdza całe znaczenie względem właściwej podstawy, następnie czyta całą polszczyznę bez źródła i szkiców. Zmiany znaczeniowe wracają do źródła. Miejsca wymagające doprecyzowania przedstawia w karcie z kontekstem, podglądem i automatycznymJSON; wdrożenie wyboru wymaga osobnego polecenia.

**Odpowiedzialność:** Jeden autor/model

**Wejście:** Przekład lub zamówiona rewizja, właściwa podstawa i aparat.

**Produkt i zakończenie:** Meaning, Polish, mapa jednostek i rozliczone problemy bieżących bajtów. Karta ocen z pełnym kontekstem, podglądem i zapisemJSON; osobne rozliczenie upoważnionego wdrożenia.

**Zatrzymanie:** Niepełna lektura, brak źródła lub nierozstrzygnięty istotny sens blokują zamknięcie.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-MAP-001 — Pełny zakres, powtórzenia i peyyāla

Zakres: SUTTA, VINAYA.

Pełny przekład obejmuje cały zadeklarowany zakres, zdania, strofy, klauzule, formuły, powtórzenia i kolofony. Pierwsze wystąpienie danej powtarzalnej formuły przedstawia wszystkie elementy; rozwinięcie wymaga rzeczywiście odczytanego palijskiego świadectwa, lokalizacji i jawnej decyzji QA. Nie udawać, że rozwinięte wyrazy występowały w skróconej podstawie. W dalszych powtórzeniach zachować źródłowe …pe…; znaczenie samego skrótu peyyāla objaśnić tylko w przypisie przy jego pierwszym wystąpieniu. Ten i każdy kolejny przypis do …pe… wskazują konkretnie, jaka treść została pominięta, z odesłaniem do wcześniejszego pełnego fragmentu i źródła; kolejne przypisy nie powtarzają definicji skrótu. Brak bezpiecznej podstawy rozwinięcia jest problemem do rozstrzygnięcia, nie zgodą na dopisanie treści. Nie skracać samodzielnie pełnej podstawy ani dodawać nieźródłowych śródtytułów. Każde wystąpienie kontrolować, bez zaliczania całości próbką.

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

Autor może przyjąć PASS_WITH_NOTES do zamknięcia pliku po sprawdzeniu całego zakresu, wykonaniu FORMAT i rozliczeniu każdej uwagi z datą, źródłem i oceną nieblokowania. Kwestia mogąca istotnie zmienić sens blokuje zamknięcie. Sam brak dostępu nie dowodzi nieistotności. To ocena autora, nie niezależny audyt. Gdy odrębne zlecenie wymaga recenzenta lub redaktora, rozliczyć także jego rzeczywisty raport i wymagany zakres; nie zastępować go deklaracją autora.

### SF-RULE-QA-004 — Bezwzględne blokady finalizacji

Zakres: SUTTA, VINAYA.

Nie finalizować przy niezweryfikowanej podstawie, brakującym fragmencie, nierozstrzygniętej różnicy mogącej zmienić sens, podejrzeniu nieuprawnionego dodatku, nieaktualnej rewizji lub niewykonanym wymaganym QA. Nierozliczone CRITICAL/MAJOR blokują APARAT-GATE. Właściciel może świadomie przyjąć materiał roboczy albo ograniczony zakres, ale nie zmienia to niewykonanej kontroli w PASS, fragmentu w pełny przekład ani samokontroli w niezależną recenzję.

### SF-RULE-QA-005 — Granica Evidence QA i adapter zamknięcia

Zakres: SUTTA, VINAYA.

Evidence QA sprawdza strukturę, kompletność i piny; nie nadaje semantycznego PASS, D/E, DONE ani publikacji. A=UKOŃCZONY_PLIK wymaga dwóch rzeczywiście wykonanych pełnych przebiegów autora, sprawdzonego aparatu, rozliczonych problemów, terminologii i FORMAT. Wymagane odrębnym zleceniem recenzje muszą być rzeczywiście wykonane. C=PEŁNA_AUTOKONTROLA odróżnia ten proces od C=PEŁNA_AI, które zachowuje wymagania niezależnej recenzji. Następnie DONE wymaga odczytu produktu, LOG i QUEUE w kolejności SF-RULE-OPS-006. E pozostaje odrębną decyzją właściciela. Historyczny sfe.finalizer zachowuje kontrakt Docs i wymagania publikacyjne; nie jest adapterem nowej ścieżki Markdown. Walidatory nie orzekają rozumienia gramatyki pali ani wykonania lektury człowieka.

### SF-RULE-QA-006 — Błędy wejścia i wymagane negatywne próby

Zakres: SUTTA, VINAYA.

Brak źródła, zakresu, PL, aktualnego hasha, pełnego raportu autora, rozliczenia istotnej uwagi lub FORMAT daje HOLD/BLOCKED. Brak recenzenta blokuje tylko wtedy, gdy wymaga go odrębny kontrakt lub zlecenie. Negatywnie sprawdzić brak jednostki, niezgodne źródło, stary wynik, nierozstrzygnięty problem, niespójne piny i pozorowanie niezależności. SCRIPT QA tylko przy zleconym audio. Po blokadzie sprawdzić zależne dowody i zapisać nowe zdarzenie, bez usuwania historii. Test syntetyczny nie certyfikuje sutty.

### SF-RULE-EDIT-001 — Dwie rzeczywiste autokorekty

Zakres: SUTTA, VINAYA.

Meaning obejmuje cały przekład względem właściwej podstawy źródłowej: znaczenie, negacje, warunki, mówców, obrazy, formuły i powtórzenia. Polish zaczyna się ciągłą lekturą polszczyzny bez podglądania źródeł w tej części; po wskazaniu konkretnych wad autor wraca do właściwej podstawy i sprawdza skutki zmian. Są to autokorekty, nie niezależne recenzje. Wierność sensu zdania i naturalna polszczyzna mają pierwszeństwo przed mechanicznym tłumaczeniem glos. Nie dopisywać nauki, puenty ani techniki medytacji. Dla każdego akapitu lub strofy sprawdzić zrozumiałość i wszystkie formy wskazujące (tutaj, tam, to, ten, w obu miejscach; idha/ettha/tattha). Ustalić referent z pełnej klauzuli i sąsiadów; nie stosować jednej glosy ani automatycznego zakazu „tutaj”. Istotne doprecyzowanie zapisać z kotwicą źródła, podstawą i alternatywą. Chronić także zakres, wyjątki, modalność i rozróżnienia nauki. Osobny wynik odniesień i naturalności obejmuje cały tekst oraz konkretne decyzje i hash kandydata; sama deklaracja Polish PASS nie wystarcza. Dla EN→PL, innej tradycji i pośrednika kontrolować rzeczywistą podstawę według zakresu, nie pozorować kontroli pełnego Pali.

### SF-RULE-EDIT-002 — Odpowiedzialność autora i odrębnie zlecana redakcja

Zakres: SUTTA, VINAYA.

Jeden autor odpowiada za całość tekstu i aparatu. Wykonuje dwa rozdzielone, pełne przebiegi według SF-RULE-EDIT-001: znaczenie względem właściwej podstawy, następnie ciągłą lekturę polszczyzny bez równoczesnego podglądu źródła i szkiców. Każda zmiana znaczeniowa wraca do źródła, sąsiadów i zależnych formuł. Raporty wiążą rzeczywisty zakres i decyzje z aktualnymi bajtami. Osobny redaktor lub recenzent nie jest obowiązkowy przy standardowym nowym przekładzie. Dodatkową osobę lub model uruchamiać po wyraźnym zleceniu właściciela; istotny problem nierozstrzygnięty przez autora blokuje zamknięcie do uzyskania źródeł lub zleconej pomocy. Samokontrola nie jest niezależną recenzją. Recenzent zgłasza problemy i dowody, a autor odpowiada za ich rozliczenie i spójny głos tekstu.

### SF-RULE-EDIT-003 — Aktualne konwencje i objaśnienia

Zakres: SUTTA, VINAYA.

Sati oddawać domyślnie jako pomność, z naturalnymi formami pomny, pamiętając lub mając na uwadze według kontekstu. Samādhi: skomponowanie umysłu; formy czasownikowe dobierać do zdania, bez podwajania umysłu przy citta. Przy pierwszym istotnym użyciu w przekładzie dodać krótkie kontekstowe objaśnienie: opanowanie i stabilność umysłu, z rzetelnym odwołaniem do odczytanego autora HH dla angielskiego composure. Polski zwrot jest konwencją SuttaFlow, nie słowami autora HH. Sprawdzić pełną kotwicę i treść przypisu w PDF. Nie wymuszać rzeczownika w każdym wystąpieniu ani ogólnej definicji niezależnie od sutty. Przy pierwszym objaśnieniu sati podać: „Pomność (sati) — przypominanie sobie i utrzymywanie w pamięci tego, co istotne dla bieżącej praktyki”. Nie dopisywać przedmiotu pamiętania, którego tekst nie ustala. Pamięć nie jest pełnym automatycznym zamiennikiem, pamiętliwość nie jest przyjętą glosą, pamiętność pozostaje niewybranym wariantem. Formy pokrewne, np. paṭissato, sprawdzać osobno w zdaniu; miejscowa korekta nie jest nową uniwersalną glosą.

### SF-RULE-EDIT-004 — Zatwierdzone formy redakcyjne

Zakres: SUTTA, VINAYA.

Aktualny zakres po doprecyzowaniu właściciela tego samego dnia: „jednak ogólnie Czcigodny jeśli pojawia się w tekście powinno być z dużej, nie tylko do Buddhy”. W kolejnych przekładach i zleconych rewizjach zapisuj tytuł „Czcigodny” wielką literą niezależnie od osoby, także w środku zdania i w formach odmiany: np. „Czcigodny Ānanda”, „do Czcigodnego Ānandy”. „Błogosławiony” i jego formy odmiany jako tytuł Buddhy również wielką literą. Decyzja nie ustanawia nowej reguły wielkich liter dla zaimków. Przy autokorekcie polskiej i kontroli konwersji sprawdzić każde wystąpienie obu tytułów, także odmienione. Historia: pierwsza wypowiedź ograniczała oba tytuły do Buddhy; późniejsze doprecyzowanie rozszerza „Czcigodny” na wszystkie osoby i zastępuje to ograniczenie. Nie zastępować automatycznie zwykłego przymiotnika poza funkcją tytułu. W MN 140 przygotowywanej na to zlecenie, kolejnych przekładach i zamówionych rewizjach używać pełnej formy **„Ṭhānissaro Bhikkhu”** przy wskazywaniu autora przekładu, także w przypisach, metodzie, bibliografii, OPIS i nowych wpisach dokumentacji. Nie skracać jej po pierwszym wystąpieniu. Zdanie można przebudować, żeby zachować naturalną polszczyznę i tę pełną formę. Nie zmieniać brzmienia cytowanych źródeł, historycznych produktów lub zamrożonych dowodów. Sprawdzić każde nowe wystąpienie w autokorekcie i konwersji.

### SF-RULE-EDIT-005 — Kontrola znaczenia w pełnym kontekście

Zakres: SUTTA, VINAYA.

Wykonując SF-RULE-QA-001 i SF-RULE-EDIT-001: dla każdego kontrolowanego zdania/formuły czytać cały kontekst. W miejscach niepewnych, metaforycznych i opartych na konwencji zapisać krótko:

1. Co mówi źródło: podmiot, czynność i jej ukończenie, negacja, warunek, modalność (może / musi / chce), zakres osób, obraz i jego funkcja. Forma gramatyczna pomaga ustalić sens, nie przesądza samodzielnie całej interpretacji.
2. Jakie odczytania dopuszczają kontekst i odczytane hasła słowników. Oddzielić dosłowny obraz, znaczenie idiomatyczne, komentarz i konwencję polską. Nie wybierać glosy wyłącznie dlatego, że znalazła się w słowniku.
3. Co polski tekst faktycznie każe czytelnikowi rozumieć, gdy czyta go bez Pali. Zapisać tę myśl prostą parafrazą. To autokontrola autora, nie niezależny test ani badanie na czytelnikach.
4. Porównać oba sensy i rozważyć błędne odczytanie: czy przekład nie zamienia możliwości w konieczność, nie dodaje woli, nie przedstawia zakończonego jako nadal trwającego, nie gubi metafory lub nie wymyśla odniesienia. Dla każdego wykrytego przesunięcia wskazać konkretną podstawę i decyzję.
5. Porównać relewantne kontrolery w istniejącej hierarchii. Zgodność kilku przekładów nie jest głosowaniem ani dowodem niezależności. Odmienną decyzję od HH uzasadnić Pali/kontekstem i słownikiem, nie samą preferencją stylistyczną. Sygnały niepewności odnotować zamiast sztucznego PASS.
6. Wybór sprawdzić ponownie w całym zdaniu i zależnych wystąpieniach. Istotne rozwinięcie lub ograniczenie wyjaśnić czytelnikowi w przypisie. W rejestrze zachować status, zakres, historię i rzeczywisty dowód zgody. Techniczna kontrola obecności zwrotu i poprawne kotwice nie zastępują tej oceny.

### SF-RULE-EDIT-006 — Stała karta ocen, kontekst i autozapisJSON

Zakres: SUTTA, VINAYA.

1. Przy nowym przekładzie albo zleconej rewizji założyć jedną kartę w katalogu zadania: `prace/<zadanie>/karta-ocen/`. Wskazać suttę, rewizję, przyjęty kontrakt i rzeczywisty SHA-256 ocenianego Markdown. Nie dopisywać karty wstecz do zamkniętych wersji. Pierwszy przykład dotyczy MN53 R9.
2. Podczas pracy i kontroli znaczenia dopisywać konkretne niejasności, wieloznaczności, możliwe przesunięcia sensu, wybory redakcyjne oraz trudności w przypisach. Zachować stałe ID miejsca. Karta nie zastępuje pełnej kontroli: brak wpisów oznacza „nie znaleziono miejsc wymagających decyzji”, nie automatyczny PASS.
3. Przedstawić właścicielowi obecne brzmienie, właściwe źródło i kontekst, trudność, uzasadnione warianty oraz ich konsekwencje. Zgodnie z doprecyzowaniem właściciela z 24.10.2026 kontekst jest widoczny od razu przed wariantami: pełny oceniany akapit, a gdy potrzebne — również sąsiednie zdania lub akapity. Wskazać, kto mówi, do kogo i w jakiej części wywodu; oceniany zwrot wyróżnić w cytacie. Przy uwadze do przypisu/metody pokazać pełne objaśnienie autora i związane z nim miejsce w przekładzie. Nie przedstawiać go jako słów mówcy sutty. Nie łączyć oddalonych fragmentów w pozornie ciągły cytat. Nie wymyślać wariantów tylko dla liczby opcji. Oddzielić tekst główny od dokładnego proponowanego przypisu. Nie nazywać każdej niejasności błędem.
4. Pozostawić wszystkie decyzje początkowo niepodjęte. Właściciel może wybrać wariant, zachować dotychczasowy tekst, wpisać własną propozycję albo odłożyć rozstrzygnięcie i zadać pytanie. Rekomendacja autora nie jest wyborem właściciela. Nie stosować zbiorczej oceny punktowej lub pozornego procentu poprawności.
5. Zachować wybory i rzeczywiste polecenie właściciela. Samo kliknięcie, zapis stanu formularza lub utworzenie pliku nie wdraża zmiany i nie uwierzytelnia zgody. Eksport ma status `DRAFT_FOR_OWNER_REVIEW`, `approval_evidence: null` oraz `implemented: false`. Polecenie przekazane w czacie rozlicza się osobno z zakresem i datą; nie nadpisuje się surowego eksportu.

   Zgodnie z poleceniem właściciela z 24.10.2026 JSON przechowywać w folderze danego przekładu, w `karta-ocen/`, a nie w ogólnym katalogu narzędzia ani w Pobranych. Doprecyzowanie tego samego dnia: **lokalna karta aktualizuje go automatycznie po zmianie wyboru lub pola, bez eksportowania i przenoszenia pliku**. Dla MN53 R9 lokalizacja to `prace/20261024-mn53-terminologia/karta-ocen/MN53-R9-wybory.json`. Pierwszy zachowany zapis i bezpośrednio poprzednia wersja mają osobne kopie; bieżący szkic jest plikiem aktualizowanym, nie dziennikiem każdej litery. Zamrożonych zatwierdzeń i rozliczeń wykonania nie zastępować szkicem. Pamięć widoku jest pomocnicza i nie zastępuje JSON.
6. Przed zastosowaniem wyboru porównać hash i kontekst z bieżącym tekstem. Własne brzmienie wymaga kontroli względem źródła. Jeżeli preferencja zmienia sens albo jest sprzeczna z wiążącą regułą, opisać problem i wrócić do wyjaśnienia; zaznaczenie opcji nie rozstrzyga filologii.
7. Po upoważnionej rewizji zapisać osobne rozliczenie: ID, dokładną decyzję, dowód polecenia, zakres, plik/hash przed i po, zastosowane brzmienie i przypis, zależne wystąpienia, rzeczywiste ponowne kontrole oraz wynik. Sprawdzać zmienione miejsca i ich zależności; nie ponawiać niezmienionych ukończonych kontroli. Otwarte istotne zagadnienie pozostaje otwarte także po wyborze „zachowaj”, jeśli autor nie rozliczył ryzyka.
8. Nowa rewizja zachowuje wcześniejszą kartę i decyzje. Dla zmienionego źródła, brzmienia, opcji lub kontekstu wpływającego na sens decyzji nadać nowy identyfikator/rewizję karty i ponownie rozliczyć dotknięte miejsca. Samo dodanie widocznego, wiernego cytatu z niezmienionej bazy, bez zmiany pytań i wariantów, nie usuwa zapisanych wyborów roboczych; właściciel może je ponownie ocenić w szerszym kontekście. Nie przenosić starej zgody wyłącznie na podstawie podobnego słowa. Nietknięte ustalenia można zachować przez jawne wskazanie nadal aktualnej podstawy i zakresu.

Karta robocza pozostaje w dokumentacji zadania. Czytelnik otrzymuje dopracowany przekład i potrzebne przypisy. Czysty CORE dla odrębnego recenzenta nie zawiera karty, rekomendacji ani wcześniejszych ocen autora. Wybór dla jednej sutty nie jest globalną decyzją terminologiczną, aktywacją Standardu, zgodą na publikację ani zgodą na nagranie.
 Wybory, rejestry rozliczeń i raporty autora pozostają poza czystymCORE według SF-RULE-CORE-001.

## 4. Kontrola aparatu i opcjonalna recenzja

Autor kontroluje cały aparat w zakresach IK/ID/IR. Odrębna recenzja jest opcjonalna, wymaga zlecenia i nie zastępuje odpowiedzialności autora.

**Odpowiedzialność:** Autor; dodatkowy recenzent tylko w osobno upoważnionym zakresie

**Wejście:** Aktualny CORE, aparat i źródła; dla zleconej recenzji odrębny czysty pakiet.

**Produkt i zakończenie:** Źródłowe rozliczenie wszystkich twierdzeń aparatu; ewentualny odrębny raport zleconego recenzenta.

**Zatrzymanie:** Nierozstrzygnięty istotny problem lub niewykonana kontrola wymagana konkretnym zleceniem; niezlecona recenzja nie jest brakiem.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-CORE-001 — Czyste wejście CORE

Zakres: SUTTA, VINAYA.

Po przygotowaniu tekstu autor kontroluje cały CORE w pierwszym przebiegu Meaning i czyta całą polszczyznę w drugim Polish według SF-RULE-EDIT-001. Źródła i PL są przypięte do ID, wydania, dokładnych bajtów, zakresu i rewizji. Autor ma jeden spójny głos i odpowiada za wszystkie rozstrzygnięcia. Opcjonalny recenzent, uruchomiony po wyraźnym zleceniu, otrzymuje odrębny czysty pakiet CORE: pełne źródło i PL bez aparatu, uwag, ocen i propozycji autora. Jest odrębny od autora, dokumentuje ekspozycję i faktyczny zakres; zgłasza konkretne problemy z dowodami, bez przejmowania stylu.

### SF-RULE-CORE-002 — Wykonanie i zamrożenie przed APARAT

Zakres: SUTTA, VINAYA.

W standardowym procesie obowiązkowa jest pełna autokontrola CORE, nie fresh review innego modelu. Gdy zlecono niezależną recenzję CORE→APARAT, recenzent wykonuje krytyczną lekturę całego znaczenia i ciągłą polską lekturę, zapisuje raport i zamraża go przed otwarciem APARAT. Pierwszy raport zachować; późniejsze uwagi i poprawki mają zakresowe dodatki. Oświadczenie lub manifest FROZEN nie dowodzą wykonania kontroli. Nierozstrzygnięty istotny problem blokuje zamknięcie niezależnie od modelu pracy.

### SF-RULE-CORE-003 — Niezależność i brak narzędzia

Zakres: SUTTA, VINAYA.

Zapisać model lub unknown, dostawcę gdy potwierdzony, wykonawcę, kontekst, ekspozycję i ograniczenia. Autor w drugim przebiegu wykonuje autokontrolę, nie niezależną recenzję. Osobny kontekst dokumentuje izolację, nie niezależność treningu i nie kompetencję palisty. Brak opcjonalnej niezleconej recenzji nie blokuje zwykłego procesu. Brak recenzji wyraźnie wymaganej odrębnym zleceniem pozostaje NIEWYKONANE; przygotowanie pakietu nie daje wyniku dodatniego. Nie fabrykować podpisów.

### SF-RULE-CORE-004 — Długie teksty i pełna kontrola globalna

Zakres: SUTTA, VINAYA.

Dzielić deterministycznie po pełnych logicznych jednostkach; nie w środku zdania ani powiązania źródło–PL. Każda część ma source_ids, candidate_ids, kolejność, SHA i powiązania. Sąsiedni KONTEKST nie wchodzi ponownie do mianownika pokrycia. Jednostkę przekraczającą limit podzielić jawnie z nowym mapowaniem. Rozliczyć wszystkie części, przejścia, powtarzane formuły, ciągłość argumentu i pełną polską lekturę; brak realnej kontroli globalnej zaznaczyć. Automat odrzuca osierocone, zdublowane, przestawione jednostki i niezgodny manifest części.

### SF-RULE-APP-001 — Ogólny APARAT pozostaje obowiązkowy

Zakres: SUTTA, VINAYA.

Po kontroli CORE autor merytorycznie kontroluje cały aparat: przypisy i kotwice, Opis, Interpretację, paralele, faktyczne źródła i zakresy odczytów, metodę publiczną, decyzje tłumaczeniowe i metrykę. Sprawdza glosy, warianty, atrybucje, niepewności i pełność bibliografii, a następnie język. Kontrole IK/ID/IR są trzema zakresami tej samokontroli, nie trzema obowiązkowymi wykonawcami. Jeśli osobno zlecono CORE→APARAT, ten sam recenzent po zamrożeniu CORE otrzymuje oddzielny aparat i zamraża oddzielny raport. Recenzja nie zastępuje odpowiedzialności autora.

### SF-RULE-APP-002 — Przypisy i jawna niepewność

Zakres: SUTTA, VINAYA.

Przypis czytelniczy wyjaśnia konkretną trudność: pojęcie, kontekst, składnię, wieloznaczność, wariant źródłowy lub różnicę interpretacji. Pisać naturalną polszczyzną bez sztywnego limitu długości; długość odpowiada wartości objaśnienia. Techniczne uzasadnienia, odrzucone szkice, wykazy kontroli i deklaracje czego nie dopisano przechowywać w QA. Zachować istotną dla czytelnika niepewność, źródła, alternatywy i zakres świadectwa. Własny wniosek oznaczyć; w Vinayi zachować sens prawno-monastyczny. Przy pierwszym użyciu objaśnić BJT, CST i nieoczywiste nazwy wydań po sprawdzeniu ich rzeczywistego charakteru. Zamiast niejasnego „w tym nośniku” używać jednoznacznej nazwy wydania. Nie przedstawiać adaptacji cyfrowej jako lektury druku.

### SF-RULE-APP-003 — Paralele i konflikt prezentacji

Zakres: SUTTA, VINAYA.

Sekcja Paralele kanoniczne opisuje wspólną treść, różnice kontekstu, mówców, sposób przywołania i znaczenie porównania, z dokładnymi odczytanymi miejscami i źródłami. Porównania strofy nie przedstawiać jako pełnej paraleli sutt. W odpowiednim fragmencie dać krótki przypis lub odsyłacz. Ujawnić pośrednictwo i istotne ograniczenie świadectwa, bez historii technicznych kontroli. Nie włączać treści paraleli do przekładu po cichu. Decyzje tłumaczeniowe wyjaśniają wybór, istotne alternatywy, powód i wpływ na znaczenie; nie są samym wykazem glos.

### SF-RULE-INT-001 — Trzy osobne kontrole interpretacyjne

Zakres: SUTTA, VINAYA.

Każdy nowy dokument i zlecona rewizja Opisu/Interpretacji podlegają kontroli autora w trzech jawnie rozdzielonych zakresach: IK zgodność z kanonem, ID doktryna i pochodzenie twierdzeń, IR redakcja. Obejmują wszystkie zdania tych sekcji oraz twierdzenia przypisów i paralel. Pokrycie i wyniki zakresów są odrębne, ale mogą być zapisane w jednym raporcie autora. To samokontrola; osobne konteksty nie są domyślnym wymogiem. Zachować pełność, źródła i blokadę istotnych nierozstrzygniętych problemów.

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

W trybie autokontroli autor zapisuje pełne pokrycie zdań/podtez i rzeczywiste rozstrzygnięcia IK/ID/IR, ze źródłami i powrotem zmian znaczenia do Pali. Nie wymaga się pozorowanej ślepoty wobec własnego tekstu ani trzech niezależnie zamrożonych raportów. Gdy właściciel osobno zleci niezależne kontrole, każda otrzymuje czysty zamrożony pakiet bez cudzych ocen i zamraża własny raport przed wspólnym rozliczeniem. Dokładny zlecony zakres niezależności nadal obowiązuje. Samokontrola nie uzyskuje tej etykiety.

### SF-RULE-INT-007 — Raporty, rozliczenie i APARAT-GATE

Zakres: SUTTA, VINAYA.

Ustalenie wskazuje ID, zdanie/podtezę, brzmienie, źródło/locus, typ, wagę CRITICAL/MAJOR/MINOR/NOTE, pewność, autora/model lub unknown, kontekst, datę, status i uzasadnioną decyzję PRZYJĘTO/ODRZUCONO/ODROCZONO. Rozstrzyga podstawa źródłowa, nie głosowanie. Zmiany i zależności wracają do właściwych zakresów IK/ID/IR; zmiana sensu wymaga ponownego IK i ID. Nierozliczona istotna poprawka lub niewykonana wyraźnie zlecona kontrola blokuje APARAT-GATE. Niezlecona recenzja innego modelu nie jest brakiem zwykłego procesu. Zachować wcześniejsze raporty i wykonane niezmienione zakresy.

## 5. K1, metryka i PDF

Zamknięty tekst zapisuje się wMarkdown; kolejne przekłady zPali mają sprawdzone paryPL–Pali z pełnymi notami, strofami i zatwierdzonymK1. Sprawdzić konwersję i cały rzeczywistyPDF; dowody techniczne pozostają wrepo.

**Odpowiedzialność:** Operator składu i wykonawca FORMAT

**Wejście:** Zamknięty tekst, wspólny CSS/fonty, noty i indeks występujących form Pali, gdy są obecne. Dla nowego Pali: przypięta mapaPL–Pali, nowy polski-pali-v2.css i pełny łańcuch importów; stare style tylko do historii.

**Produkt i zakończenie:** Źródło, PDF, kontrola tekstu/fontów/kotwic i oględziny wszystkich stron.

**Zatrzymanie:** Utrata tekstu, noty, kotwicy lub nieobejrzany PDF: bez FORMAT PASS.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-FMT-001 — Jedyny zatwierdzony K1

Zakres: SUTTA, VINAYA.

Zachować bazowy K1 i historyczny wzorzec ID 1as-k0wrf_sXdXSTPPnoEmmx_fMfdn0C9H0HKO8JcmfY bez zmiany. Nowe produkty powstają z wersjonowanego Markdown przez wspólny K1/Vivliostyle i przypięte fonty. Zatwierdzone zmiany: dyskretna metryka 22.10.2026; odstępy całych strof 23.10.2026 według SF-RULE-FMT-004; domyślny układ PL–Pali 24.10.2026 według SF-RULE-FMT-010. Pozostałe role i parametry K1 zachować. Kolejna zmiana wyglądu wymaga konkretnej akceptacji. Historycznych produktów i Google Docs nie przebudowywać automatycznie.

### SF-RULE-FMT-002 — Pełna struktura nagłówków i dwa podziały

Zakres: SUTTA, VINAYA.

Dokument ma tytuł polski, podtytuł z tytułem właściwej podstawy (Pali dla palijskiego tekstu), zbiorem i numerem/referencją, sześć głównych sekcji: Opis, Interpretacja, Przekład, Jak powstało to tłumaczenie, Paralele kanoniczne i Źródła; podsekcję Decyzje tłumaczeniowe i końcową Metrykę przekładu. Metoda i metryka zaczynają nowe strony przez regułę podziału, nie puste akapity. Historyczne nagłówki „Dokumentacja pracy” i „Historia rewizji” nie są wymagane w nowych dokumentach czytelniczych: pełna dokumentacja trafia do repozytorium. Zachować pozostałe role typograficzne K1. Mapa semantyczna: polski tytuł = TITLE/HTML h1; podtytuł = SUBTITLE/p.subtitle; sześć wymienionych sekcji = HEADING_2/HTML h2; Decyzje tłumaczeniowe i Metryka przekładu = HEADING_3/HTML h3. Podgrupy źródeł także h3. Dwa historyczne H4 metryki nie są wymagane w nowych krótkich metrykach. Sprawdzić poziomy w skonwertowanym HTML, nie tylko rozmiary fontów.

### SF-RULE-FMT-003 — Tagi, dialog, gāthā i metryka

Zakres: SUTTA, VINAYA.

Zachować prozę, osobne akapity dialogu i jawne wersy bez tagów demonstracyjnych i nieźródłowych śródtytułów przekładu. Krótka, dyskretna metryka czytelnicza podaje rzeczywistą wersję i datę, podstawę oraz udział sztucznej inteligencji ze wskazaniem potwierdzonego dostawcy. Nie używać skrótu AI ani przypisywać niepotwierdzonej wersji modelu. Nie wymagać stałych wierszy Ograniczenia i Status. Informacje o braku recenzji palisty i technicznych statusach kontroli przechowywać w dokumentacji QA, nie w czytelniczej metryce ani metodzie. Nie usuwać z przypisów ważnych wariantów źródłowych lub nierozstrzygniętych wątpliwości dotyczących samego tekstu. Opis Jak powstało to tłumaczenie podaje rzeczywistą podstawę językową, wykorzystane porównania, słowniki i faktycznie wykonane kontrole. Nie sugerować udokumentowanego Pali-first przy braku dowodu R0. Hashe, checkpointy, historia procedury i osie A–E pozostają w QA; brak wiersza statusu nie nadaje zgody publikacyjnej.

### SF-RULE-FMT-004 — Natywne elementy i zwarty skład

Zakres: SUTTA, VINAYA.

PDF ma A4, marginesy 56,7 pt, rzeczywistą numerację stron i automatycznie numerowane przypisy u dołu strony. Zachować Merriweather: tytuł 24 pt, podtytuł 14 pt, tekst 12 pt, odstęp bazowych wierszy około 17,3466 pt, 0 pt przed i 4 pt po akapicie; strofy z wcięciem 18 pt bez dodatkowych odstępów między wersami; bibliografia i metryka 10 pt; przypisy 9,5 pt. Listy i linki pozostają semantycznymi elementami. Nie wpisywać numerów przypisów ręcznie. Długiej noty nie wolno ucinać: wymagane jest czytelne przeniesienie albo jawne zatrzymanie eksportu do korekty. Między całymi strofami oraz na granicy strofy i prozy stosować 17,3466 pt przed/po bez sumowania sąsiednich marginesów; wewnątrz strofy bez dodatkowych odstępów. Odstęp jest cechą bloku, nie pustym akapitem; na granicy strony nie wymuszać pustego wiersza. Nowe źródła używają .gatha i domyślnego odstepy-r4.css bez ręcznych marginesów; -LegacyLayout służy świadomemu odtworzeniu historii. Miejscowy podział przed Dhp19–20 nie jest powszechną regułą. Osobny font Pali określa SF-RULE-FMT-010.

### SF-RULE-FMT-005 — Normalizacja po rzeczywistych zmianach

Zakres: SUTTA, VINAYA.

Po każdej zmianie tekstu lub noty ponownie zbudować dokument z aktualnego źródła i odtworzyć kotwice oraz mapę tekstu. Nie formatować według indeksów innej rewizji. W ścieżce historycznego Google Doc ponownie odczytać rzeczywistą strukturę i indeksy UTF-16; nie zastępować mechanizmu natywnego imitacją. W ścieżce Markdown sprawdzić wynik konwersji i zgodność bieżącego źródła, stylu, fontów oraz PDF. Puste akapity usuwać selektywnie, bez utraty granic strof i sekcji.

### SF-RULE-FMT-006 — Kursywa Pali w każdym przypisie

Zakres: SUTTA, VINAYA.

Wszystkie omawiane formy i cytaty palijskie w tekście oraz przypisach, także kolejne wystąpienia, warianty, fleksja i złożenia, oznaczać kursywą na podstawie rozpoznanego zakresu słów, a nie samych znaków diakrytycznych. Nie pochylać polskich objaśnień, numerów ani skrótów słowników; nazwę omawianą jako formę pali wyróżniać, nazwę osoby używaną po polsku pozostawiać zgodnie z funkcją. W Markdown używać właściwych znaczników, w definicjach not składni obsługiwanej przez VFM. W PDF sprawdzić faktyczny font Italic i kompletność. Indeks form właściwy danej sutcie nie jest uniwersalnym detektorem pali. Wyjątkiem jest wyłącznie rzeczywisty oryginał w odrębnym bloku .pali-source według SF-RULE-FMT-010: ChivoMono prosto. Nie rozszerzać wyjątku na formy i cytaty Pali w polskich przypisach, komentarzu lub bibliografii.

### SF-RULE-FMT-007 — Dwie osobne bramy Docs i PDF

Zakres: SUTTA, VINAYA.

Dwie osobne kontrole: najpierw struktura aktualnego źródła i wynik konwersji (role, listy, oba podziały, strofy, odwołania, kotwice, kursywa i linki), następnie końcowy PDF. W PDF sprawdzić pełny tekst i wszystkie noty oraz obejrzeć każdą stronę, anomalie w pełnej skali. Brak eksportu lub oględzin oznacza niewykonane/zablokowane, nigdy wynik dodatni. Dawny tryb Docs nadal wymaga rzeczywistego odczytu native i eksportu tej samej rewizji; nie przedstawiać Markdown jako natywnego Google Doc. UkładPL–Pali wymaga sprawdzenia pełnej rzeczywistej liczby par z mapy, zgodności obu stron z podstawą, kolejności, braku osieroconych bloków, diakrytyki i fontów. Oględziny dotyczą każdej strony bieżącego PDF. Wynik poprzedniej wersji wolno wykorzystać wyłącznie w niezmienionym zakresie i przy zgodnych pinach zależności.

### SF-RULE-FMT-008 — Dowód FORMAT i DONE

Zakres: SUTTA, VINAYA.

FORMAT PASS wymaga wykonanych kontroli struktury, treści i wyglądu bez istotnych usterek. Zapis wskazuje ID sutty, rewizję i hash źródła, styl/fonty, końcowy PDF, liczbę stron, zakres oględzin, wykonawcę i poprawione wady. Lokalny test kandydata może wskazywać zachowany plik i manifest w przestrzeni zadania; nie jest dostawą. Przed zamknięciem dostawy wymagany jest trwały link na Dysku oraz odczyt tego samego produktu. Dla historycznego eksportu Google zapisać ponadto Doc ID i revisionId. Po wymaganych bramach merytorycznych i FORMAT można zamknąć plik; zgoda publikacyjna pozostaje odrębna. Zmiana treści lub składu wymaga aktualizacji zależnych kontroli.

### SF-RULE-FMT-009 — Wariant VinayaFlow

Zakres: SUTTA, VINAYA.

Jeśli układ Vinayi mieści się w K1 bez utraty wymaganej struktury, zachować zatwierdzony wzorzec i udowodnić pełny zakres. Gdy potrzebuje innych ról, układu lub sekcji, przygotować odrębny wariant z dokładną mapą do K1, a jego aktywacja wymaga jawnej zgody właściciela. Nie rozszerzać szablonu przez domniemanie ani wciskać wyjątków, definicji i procedur w wariant usuwający granice tekstu. Kontrola numeracji i terminologii prawno-monastycznej pozostaje obowiązkowa.

### SF-RULE-FMT-010 — Domyślny układ polsko-palijski

Zakres: SUTTA, VINAYA.

W kolejnych przekładach z Pali polski tekst zachowuje Merriweather 12 pt. Pod każdym zdaniem lub uzasadnionym spójnym fragmentem umieszczać odpowiadający mu **rzeczywisty tekst użytej podstawy**, Chivo Mono 10,5 pt, prosto, interlinia 1,4, kolor #595959. Słowa palijskie przytaczane w polskich przypisach i komentarzu nadal zapisywać kursywą. Rozróżnienie typografii dotyczy oryginału w osobnym bloku, nie wszystkich obcojęzycznych słów dokumentu. Pary wynikają ze sprawdzonej mapy jednostek, nigdy z samego dzielenia tekstu po kropkach. Dopuszczalne są pary obejmujące kilka klauzul lub całą strofę, gdy tego wymaga rzeczywista relacja języków; nie dopisywać oryginału dla polskiego dodatku. Przypisy czytelnicze pozostają przy polskim tekście. Podpisów Pali/PL nie powtarzać pod każdym zdaniem; język i źródłowy identyfikator zapisuje semantyczna struktura bloku. Nie zostawiać polskiego zdania na końcu strony bez odpowiadającego mu Pali. Długą parę wolno podzielić tylko czytelnie i z kontrolą rzeczywistego PDF. Strofę parować jako spójny blok, zachowując odstępy opisane poniżej; nie utożsamiać wersu z akapitem prozy. Pipeline `ZBUDUJ_PDF.ps1 -PaliMap ...` sprawdza piny i kotwice źródła oraz przekładu, tworzy nowy dwujęzyczny Markdown i składa go przez VFM/K1. Domyślny `polski-pali-v2.css` importuje zachowane `polski-pali.css`, `odstepy-r4.css` i `suttaflow.css`, usuwając wyłącznie tło, lewy pasek i wcięcie metryki; dawne style pozostają bez zmian. Mapa zawiera wyłącznie zadeklarowany CORE, pełną kolejność i niepuste pary. Niesparowane fragmenty, niewłaściwa kolejność, niezgodne bajty lub kotwice zatrzymują skład. Dla każdego nowego przekładu z Pali wymagany jest ten tryb; dla świadomego odtworzenia historii lub tekstu o innej zadeklarowanej podstawie bez Pali zachować rzeczywistą ścieżkę, bez wymyślania oryginału. Kontrola FORMAT obejmuje pełny polski tekst, wszystkie bloki Pali w kolejności i ich zgodność z przypiętą podstawą, relację każdej pary, kompletność przypisów i odsyłaczy, osadzenie fontu i wszystkie znaki diakrytyczne oraz oględziny każdej strony. Mechanika nie zastępuje oceny znaczenia. Samo dodanie oryginału nie ponawia zakończonych recenzji niezmienionego przekładu ani nie nadaje zgody publikacyjnej.

## 6. Statusy, dostawa i dokumentacja

Dostawa nie jest zgodą publikacyjną. Zweryfikuj aktualne produkty na Dysku, zapisz LOG i uzgodnij QUEUE. Pełne dowody przechowuj poza dokumentem czytelniczym.

**Odpowiedzialność:** Operator; D/E tylko uprawnione osoby

**Wejście:** Aktualne produkty i dowody bram.

**Produkt i zakończenie:** Odczytane PDF/OPIS, wpis LOG i uzgodnione QUEUE; oddzielne osie.

**Zatrzymanie:** Niepewny zapis: najpierw readback po ID i wersji, bez ślepego ponowienia.

**Wznowienie:** Sprawdź piny checkpointu i zachowane produkty; wznów pierwszy niewykonany krok. Zmiana wejścia unieważnia wyłącznie zależny zakres, z zachowaniem historii.

### SF-RULE-STA-001 — Dokładne osie i zamknięte wartości

Zakres: SUTTA, VINAYA.

Pięć osi ustala się oddzielnie. A: ROBOCZY, UKOŃCZONY_PLIK. B: PALI_FIRST_UDOKUMENTOWANY, PALI_FIRST_DEKLAROWANY, EN_PL_HH, EN_PL_INNY, NIEUSTALONE. C: NIEUDOKUMENTOWANA, CZĘŚCIOWA, PEŁNA_AI, PEŁNA_AUTOKONTROLA. D: BRAK, ODSTĄPIONO, CZĘŚCIOWA, PEŁNA. E: WSTRZYMANE, DOPUSZCZONE_JAKO_OPRACOWANIE_AI, DOPUSZCZONE_PO_RECENZJI. Znaczeń nie wolno zmienić przez adapter. A ustala wykonawca po FORMAT; B według źródeł/procesu, C według dowodów, D rzeczywisty recenzent lub właściciel przy odstąpieniu, E wyłącznie właściciel. Dla znanej podstawy niepalijskiej poza katalogiem B stosować jawne mapowanie i metadane SF-RULE-STA-002; nie dodaje to nowej wartości enum ani nie zmienia historycznych rekordów.

### SF-RULE-STA-002 — Warunki B i C

Zakres: SUTTA, VINAYA.

B=PALI_FIRST_UDOKUMENTOWANY wymaga dowodu R0 z SF-RULE-SRC-003; PALI_FIRST_DEKLAROWANY zachowuje warunki SRC-004. EN_PL_HH odpowiada rzeczywistej metodzie basis.method=EN_PL_HH, a EN_PL_INNY metodzie EN_PL_OTHER. Dla udokumentowanego SOURCE_FIRST_OTHER albo INDIRECT_SOURCE_FIRST zapisać B=NIEUSTALONE wraz z opisem przyczyny „znana podstawa poza katalogiem osi B” oraz obowiązkowymi metadanymi basis.method, basis.language, basis.source_id, basis.indirect i dowodem rzeczywistego odczytu; pośrednictwo wymaga także identyfikatora pośrednika, powodu i ograniczeń. W tym przypadku NIEUSTALONE dotyczy klasyfikacji w zachowanym enumie, nie nieznajomości źródła. Gdy dowodu metody rzeczywiście brakuje, B=NIEUSTALONE ma osobny opis „metoda nieustalona” i ujawniony brak dowodu; nie wolno pozorować znanej podstawy. Nie wymuszać nieprawdziwego pochodzenia EN/Pali i nie rozszerzać enumu. Publiczna metoda nazywa faktyczny język i pośrednictwo, a nie samą techniczną etykietę B. C=CZĘŚCIOWA wymaga jawnego zakresu; C=PEŁNA_AI pełnego pokrycia atomowych jednostek oraz istniejących raportów autora i faktycznego recenzenta, tożsamości modeli/kontekstów, niezależności i dokładnej rewizji. coverage_ready=true bez raportów nie wystarcza. Nowego wymaganego APARAT-GATE nie wywodzić z historycznego C. C=PEŁNA_AUTOKONTROLA jest nową odrębną wartością od 2.1.0: pełna aktualna kontrola autora obejmująca Meaning, Polish i aparat, jawny brak niezależności oraz źródła, jednostki, problemy i kontrole zależnych zmian. Weryfikuje ją full_author, bez zastępowania faktycznej lektury deklaracją. C=PEŁNA_AI zachowuje poprzednie wymagania odrębnego recenzenta; historycznych wartości i znaczeń nie zmieniać.

### SF-RULE-STA-003 — D: człowiek i typowane odstąpienie

Zakres: SUTTA, VINAYA.

D=CZĘŚCIOWA/PEŁNA wymaga faktycznie wykonanej recenzji człowieka z osobą/rolą, datą, zakresem i rewizją; AI może ją odnotować z dowodu, nie nadać od siebie. ODSTĄPIONO wymaga HUMAN_REVIEW_WAIVER od upoważnionego właściciela, z subject_id, rzeczywistą rewizją/hashem, zakresem, datą, tekstem dowodu i brakiem odwołania. Taka decyzja nie tworzy recenzji ani nie udziela E. BRAK jest stwierdzeniem braku recenzji; nie wolno nim wypełniać nieustalonej historii.

### SF-RULE-STA-004 — E: typowana i zakresowa zgoda

Zakres: SUTTA, VINAYA.

E dopuszczające wymaga PUBLICATION_CONSENT z autoryzowanym właścicielem, subject_id, konkretną rewizją/hashem, zakresem nagrania/publikacji, datą, dowodem i brakiem odwołania. FONT_ONLY, akceptacja szablonu, Standardu, innego tekstu lub rewizji oraz samo APPROVED są niewystarczające. Odmówić obcego typu, zakresu i niezweryfikowanego dowodu. E po recenzji wymaga rzeczywistej recenzji odpowiedniego zakresu; E jako AI zachowuje informację o braku recenzji palisty w dokumentacji QA; nie wymaga jej ujawniania w czytelniczej metryce ani metodzie dokumentu. Zamówione audio zachowuje swój odrębny kontrakt SF-RULE-AUDIO-002. Nie przenosić zgody MN 41 na inne sutty.

### SF-RULE-STA-005 — Historia statusów i brak wiedzy

Zakres: SUTTA, VINAYA.

Historyczne wartości zachowuje się bez nadpisywania. Nieustaloną historię C/D/E zapisuje się osobno jako UNKNOWN/UNRESOLVED; nie zamienia się niewiedzy w BRAK lub WSTRZYMANE i nie dodaje nowej wartości do zamkniętych enumów. B ma własną dopuszczalną wartość NIEUSTALONE. Nowy dodatni status bez dowodu jest zatrzymany. Dawne DONE oznacza historyczne ukończenie pliku, a nie nową recenzję lub zgodę. Rzeczywiste wcześniejsze zgody zachowują swój dokładny zakres. ZATWIERDZONY_PRZEZ_AI w historycznej mapie oznacza C=PEŁNA_AI, ale nowe potwierdzenie wymaga pełnych rzeczywistych raportów i aktualnej rewizji. RECENZJA_LUDZKA_POTWIERDZONA oznacza D=PEŁNA lub CZĘŚCIOWA według rzeczywistego zakresu i świadectwa człowieka. ZATWIERDZONY_PRZEZ_WŁAŚCICIELA_BEZ_RECENZJI_PALISTY zachowuje historyczne połączenie odstąpienia D i dopuszczenia E jako opracowania AI; nowe nadanie wymaga osobnych zgodnych typowanych dowodów dla obu osi, bez kopiowania samej etykiety. Historyczny PASS/PASS_WITH_NOTES zachowuje zakres, rewizję i uwagi kontroli; nie oznacza publikacji. B=NIEUSTALONE dla udokumentowanej podstawy poza katalogiem B ma osobny opis i metadane według SF-RULE-STA-002; nie jest UNKNOWN historii C/D/E ani twierdzeniem, że język lub źródło są nieznane.

### SF-RULE-PUB-001 — Publiczna lista źródeł

Zakres: SUTTA, VINAYA.

Listę budować z rzeczywistych odczytów i użytego zakresu w kolejności grup: tekst Pali/podstawa, kontrola Pali, przekłady porównawcze według pierwszeństwa, dodatkowa kontrola, słowniki, komentarz i teksty pomocnicze. Każde użyte źródło musi być wymienione; nieodczytane nie może być opisane jako użyte. Przy częściowym odczycie podać zakres i rzeczywisty typ materiału. Linkować oficjalne publiczne strony, sprawdzić linki z datą przed publikacją. Nieoficjalną kopię zastąpić publicznym opisem wydania książkowego, zachowując prywatnie faktyczny nośnik odczytu.

### SF-RULE-PUB-002 — Bibliografia, atrybucja i granica capture

Zakres: SUTTA, VINAYA.

Ta sama kompletna lista faktycznie użytych źródeł stanowi sekcję Źródła dokumentu i podstawę opisu na kanale. DPD wymaga autora i wskazania CC BY-NC-SA 4.0; słownik nieodczytany lub poza zakresem nie trafia do listy jako kontrola. Prawdziwą informację o wykorzystaniu sztucznej inteligencji ujawnia metoda lub metryka. Recenzję palisty lub jej brak oraz techniczne statusy kontroli dokumentuje QA; nie umieszczać ich w wersji czytelniczej dokumentu ani powtarzać na końcu bibliografii. CAPTURED + NIE_ODCZYTANO nie przechodzi walidacji użycia. Publiczny opis nie może twierdzić pełnej kolacji na podstawie kilku terminów ani przypisywać Sujato wpływu z samej infrastruktury.

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

Nowe osobne żywe dossier tworzyć po wyraźnym zleceniu lub upoważnieniu użytkownika obejmującym jego utworzenie. Użyteczne zagadnienie przekrojowe uzasadnia propozycję, ale samo nie uruchamia nowej pracy tematycznej. Nazwa: TEMAT · {hasło Pali/pojęcie} · {tytuł polski}; aktualizować w miejscu z zachowaniem historii. W miarę potrzeby zawiera cel, zakres, terminy/formuły, syntezę z rozróżnieniem źródeł, mapę sutt/Vinayi, wkład każdej, status przekładu i bezpośredni link do finalnego PDF oraz wersji źródłowej (dla historycznego produktu link do Doc), paralele, pytania i źródła. Po DONE obowiązkowo sprawdzić i uzupełnić wszystkie relewantne istniejące dossier; nie wymaga to nowego zlecenia ich utworzenia. Jedna sutta może należeć do wielu dossier. Taka aktualizacja nie zmienia kolejki.

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

Przed aktywacją wydania zamrozić kontrakt, kod, testy i pilot oraz uzyskać dwie świeże odrębne recenzje wydania: normatywną i techniczną. Nie jest to obowiązek recenzji każdego przekładu. Delegacja wymaga wyraźnego zlecenia właściciela dotyczącego tego wydania; wcześniejsze zgody nie są przenoszone. Przygotowanie kandydata i własny przegląd spójności nie zastępują tych recenzji. Gdy nie zlecono recenzentów, zachować gotowy pakiet CANDIDATE do ich oceny bez aktywacji i bez pozornego raportu. P0/P1 muszą być rozliczone przed wydaniem.

### SF-RULE-REL-002 — Warunki rzeczywistego wydania

Zakres: SUTTA, VINAYA.

Wydanie wymaga spójnego kontraktu, rozliczonej mapy zmian, braku otwartych P0/P1, odpowiednich testów, rzeczywistego pilota, sprawdzonego i obejrzanego PDF, dwóch recenzji wydania według SF-RULE-REL-001, planu migracji/rollbacku i świadomej zgody na dokładny manifest. Pilot 2.1.0 stosuje normalny model autora z dwiema autokontrolami; dawnego wyjątku pilota 2.0 nie rozszerza się i nie przerabia dawnych raportów. Ręczna aktywacja nie uruchamia automatycznego koordynatora. RELEASED wymaga rzeczywistych zgodnych zapisów i ich odczytów; samo przygotowanie kandydata pozostaje CANDIDATE.

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

**Palijska VinayaFlow**: HH: przekład albo bezpośrednio relewantne opracowanie problemu → Khematto Bhikkhu dla Mahāvaggi i Cullavaggi tam, gdzie dostępny → Ṭhānissaro Bhikkhu, materiały Vinaya i The Buddhist Monastic Code → I.B. Horner / PTS; T.W. Rhys Davids i Hermann Oldenberg → Komentarze Pali, słowniki, inne wydania i badania przy konkretnych problemach. Kontrola filologiczna: Bodhi wyłącznie jako kontroler relewantnych paralelnych sutt; Sujato najwyżej dodatkowy weryfikator; Brahmali nie jest aktywnym nowym poziomem.


Dla innych tradycji i krytycznego pośrednictwa plan odpowiednich językowo kontrolerów ustala się według SF-RULE-SRC-001 i SF-RULE-SRC-009; powyższych palijskich hierarchii nie przenosić automatycznie.

### Słowniki i rzeczywiste granice

**DPD** — Digital Pāḷi Dictionary. Rola: Pierwszy słownik roboczy: fleksja, lemma, morfologia, rdzenie, sandhi, złożenia. Zakres: Zapisać datę/wersję; automatyczna dekompozycja nie dowodzi składni zdania. Dla ważnej decyzji dodatkowy właściwy słownik filologiczny.. Adresy: https://www.dpdict.net/, https://docs.dpdict.net/. Licencja zapisana w źródle: CC BY-NC-SA 4.0; masowe cytowanie/redystrybucja wymagają odrębnej kontroli praw

**CONE** — Margaret Cone, A Dictionary of Pāli (PTS). Rola: Kontrola filologiczna z cytatami i przykładami; podać hasło i odczytany tom. Zakres: Według dostarczonego 1.13 trzy elektroniczne tomy, A–Bh. Poza zakresem brak wyniku nie dowodzi nieistnienia słowa. Aktualnego katalogu nie sprawdzano w tej pracy.. Adresy: https://gandhari.org/dictionary?section=dop, https://palitextsociety.org/a-dictionary-of-pali-online/. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

**PED** — T. W. Rhys Davids i William Stede, Pali–English Dictionary (PTS). Rola: Szersze pole znaczeniowe, rozwój leksyki i źródłowe przykłady. Zakres: Historyczne wydanie 1921–1925 wymaga ostrożności wobec nowszych ustaleń; glosa nie jest automatycznym polskim odpowiednikiem. Adresy: https://dsal.uchicago.edu/dictionaries/pali/. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

**CPD** — A Critical Pāli Dictionary, Uniwersytet w Kolonii / PTS. Rola: Krytyczny słownik filologiczny; sprawdzić dokładne hasło i odsyłacze, ewentualnie wariant zapisu bez diakrytyków. Zakres: W źródle niedokończony zakres A–kāreti. Poza zakresem NIEOBEJMUJE_ZAKRESU zamiast brak terminu. Adresy: https://cpd.uni-koeln.de/search. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

**DPPN** — G. P. Malalasekera, Dictionary of Pāli Proper Names. Rola: Imiona, miejsca, postaci i identyfikacja sutt; nie składnia. Zakres: Elektroniczna redakcja może różnić się od druku. Nieoznaczonych dopisków nie przypisywać samemu Malalasekerze. Adresy: https://www.aimwell.org/DPPN/index.html, https://ancient-buddhist-texts.net/Textual-Studies/DPPN/index.htm. Licencja zapisana w źródle: Nie ustalono w tym rekordzie; sprawdzić prawa do konkretnego użycia.

Ten katalog dotyczy Pali. Inne języki wymagają właściwych słowników według SF-RULE-SRC-010; brak palijskiego terminu nie unieważnia dozwolonej podstawy innego języka.

### Terminologia i zakresy zatwierdzeń

Widok generowany z rejestru Standardu. Status i zakres ograniczają każde użycie.

| ID / hasło | Polski odpowiednik | Status | Zakres |
| --- | --- | --- | --- |
| SF-TERM-ANAPANASATI · Ānāpānasati | pamiętność oddychania | ZASTOSOWANE, NIEPOTWIERDZONE | MN 118 i dossier Ānāpānasati |
| SF-TERM-YONISO_MANASIKARA · Yoniso manasikāra | kierowanie umysłu w świetle źródła | ZASTOSOWANE, NIEPOTWIERDZONE | MN 2 i SN 45.55; formy fleksyjne |
| SF-TERM-SANKHARA · Saṅkhārā | aktywności | ZASTOSOWANE, NIEPOTWIERDZONE | SN 12.11 |
| SF-TERM-PHASSA · Phassa | kontakt | ZASTOSOWANE, NIEPOTWIERDZONE | SN 12.11 i MN 18 |
| SF-TERM-YOGA · Yoga / yogakkhema | jarzmo / bezpieczeństwo od jarzma | ZASTOSOWANE, NIEPOTWIERDZONE | AN 4.10; powiązane StNp 3.2 |
| SF-TERM-PAPANCA · Papañca | rozplenianie | ZASTOSOWANE, NIEPOTWIERDZONE | MN 18 |
| SF-TERM-UPAPAJJATI · Upapajjati | pojawić się ponownie; pojawi się ponownie, pojawił się ponownie, pojawiają się ponownie | ZATWIERDZONE | MN 41 i nowe przekłady; czasownik i parafrazy aparatu, nie ogólne pojęcie odrodzenia |
| SF-TERM-OPAPATIKA · Opapātika | pojawiający się spontanicznie | ZASTOSOWANE, ZATWIERDZONE POŚREDNIO | Użycie MN 41 RC2, przyjęte 2026-10-11; nie uniwersalna akceptacja dla nowych sutt |
| SF-TERM-DHAMMARAKKHITA · Dhammarakkhitā | chronione przez Dhammę | ZATWIERDZONE POŚREDNIO | MN 41 RC2; z przypisem o Vin III 139 i sahadhammikā rakkhanti |
| SF-TERM-SAPARIDANDA · Saparidaṇḍā | chronione groźbą kary | ZATWIERDZONE POŚREDNIO | MN 41 RC2 |
| SF-TERM-BYAPADA_BYAPANNACITTA_VERA · Byāpāda / byāpannacitta / vera | zła wola / umysł pełen złej woli / wrogość | ZATWIERDZONE POŚREDNIO | MN 41 RC2 |
| SF-TERM-SAMADHI · Samādhi / asamādhisaṃvattanika | skomponowanie umysłu / niesprzyjający skomponowaniu umysłu | ZATWIERDZONE | Nowe przekłady i zamówione rewizje; doprecyzowanie z 2026-10-15. T-02 z 2026-10-11 i MN41 RC2.1 zachowane historycznie. |
| SF-TERM-SATI · sati | pomność | ZATWIERDZONE | Nowe przekłady i zamówione rewizje w zakresie konwencji sati |
| SF-TERM-HH-PRESSURE · pressure | presja | ZATWIERDZONE | Nowe przekłady i zamówione rewizje w zakresie EN→PL HH |
| SF-TERM-PUBBENIVASA · pubbenivāsa | poprzednie życia | ZATWIERDZONE | Formuły wspominania wcześniejszych egzystencji w nowych przekładach i zamówionych rewizjach; bez automatycznej zmiany historii. |
| SF-TERM-PUBBENIVASANUSSATI · pubbenivāsānussati | przypominanie sobie poprzednich żyć | ZATWIERDZONE | Formuły wspominania wcześniejszych egzystencji w nowych przekładach i zamówionych rewizjach; bez automatycznej zmiany historii. |
| SF-TERM-MN53-SEKHO-PATIPADO · sekho pāṭipado | uczeń, który wkroczył na drogę treningu | ZATWIERDZONE | MN53, zwrot sekho pāṭipado i jego biernik w ramie narracji oraz dwóch podsumowaniach |
| SF-TERM-MN53-SUGATA · sugata | ten, który dobrze przebył drogę | ZATWIERDZONE | MN53:11.3, tytuły Buddhy; nowe przekłady i zamówione rewizje MN53. Wcześniejsze produkty bez zmian. |
| SF-TERM-MN53-PURISADAMMASARATHI · anuttaro purisadammasārathi | niezrównany przewodnik ludzi zdolnych do treningu | ZATWIERDZONE | MN53:11.3, tytuły Buddhy; nowe przekłady i zamówione rewizje MN53. Wcześniejsze produkty bez zmian. |
| TERM-PALI-RUPA-VISIBLE-OBJECTS · rūpā cakkhuviññeyyā | widoki poznawane okiem | ZATWIERDZONE | Kolejne nowe przekłady; widzialne przedmioty wzroku, m.in. pięć pasm zmysłowości; naturalna odmiana. |

#### SF-TERM-ANAPANASATI

**Znaczenie/kontekst:** Ānāpānasati → „pamiętność oddychania”. Zakres zaobserwowany: MN 118 i dossier Ānāpānasati. Status: ZASTOSOWANE, NIEPOTWIERDZONE. Źródło użycia: Translation Log, wpis MN 118; nie przesądza o przekładzie sati w każdym kontekście.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-ANAPANASATI

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: pamiętność oddychania; ZASTOSOWANE, NIEPOTWIERDZONE; MN 118 i dossier Ānāpānasati. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-ANAPANASATI
- Data nieodtworzona: pamiętność oddychania; ZASTOSOWANE, NIEPOTWIERDZONE; MN 118 i dossier Ānāpānasati. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-YONISO_MANASIKARA

**Znaczenie/kontekst:** Yoniso manasikāra → „kierowanie umysłu w świetle źródła”. Zakres zaobserwowany: MN 2 i SN 45.55, z formami fleksyjnymi. Status: ZASTOSOWANE, NIEPOTWIERDZONE. Źródło użycia: Translation Log, wpisy MN 2 i SN 45.55. Rozwiązanie interpretacyjnie istotne, nie neutralny zamiennik w każdym zdaniu.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-YONISO_MANASIKARA

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: kierowanie umysłu w świetle źródła; ZASTOSOWANE, NIEPOTWIERDZONE; MN 2 i SN 45.55; formy fleksyjne. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-YONISO_MANASIKARA
- Data nieodtworzona: kierowanie umysłu w świetle źródła; ZASTOSOWANE, NIEPOTWIERDZONE; MN 2 i SN 45.55; formy fleksyjne. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-SANKHARA

**Znaczenie/kontekst:** Saṅkhārā → „aktywności”. Zakres zaobserwowany: SN 12.11. Status: ZASTOSOWANE, NIEPOTWIERDZONE. Źródło użycia i zastrzeżenie co do szerokiego zakresu: Translation Log, wpis SN 12.11. Nie przenosić automatycznie na wszystkie zastosowania terminu.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-SANKHARA

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: aktywności; ZASTOSOWANE, NIEPOTWIERDZONE; SN 12.11. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-SANKHARA
- Data nieodtworzona: aktywności; ZASTOSOWANE, NIEPOTWIERDZONE; SN 12.11. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-PHASSA

**Znaczenie/kontekst:** Phassa → „kontakt”. Zakres zaobserwowany: SN 12.11 i MN 18. Status: ZASTOSOWANE, NIEPOTWIERDZONE. Źródło użycia: Translation Log, wpis SN 12.11 oraz tekst MN 18. Wcześniejsza deklaracja modelu o spójności projektu nie zastępuje świadectwa zatwierdzenia.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-PHASSA

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: kontakt; ZASTOSOWANE, NIEPOTWIERDZONE; SN 12.11 i MN 18. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-PHASSA
- Data nieodtworzona: kontakt; ZASTOSOWANE, NIEPOTWIERDZONE; SN 12.11 i MN 18. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-YOGA

**Znaczenie/kontekst:** Yoga → „jarzmo”. Zakres zaobserwowany: AN 4.10; powiązane yogakkhema → „bezpieczeństwo od jarzma”. Status: ZASTOSOWANE, NIEPOTWIERDZONE. Źródło użycia: Translation Log, wpis AN 4.10 odsyłający także do StNp 3.2. Rejestr zachowuje użycie, nie wprowadza nowej decyzji filologicznej.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-YOGA

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: jarzmo / bezpieczeństwo od jarzma; ZASTOSOWANE, NIEPOTWIERDZONE; AN 4.10; powiązane StNp 3.2. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-YOGA
- Data nieodtworzona: jarzmo / bezpieczeństwo od jarzma; ZASTOSOWANE, NIEPOTWIERDZONE; AN 4.10; powiązane StNp 3.2. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-PAPANCA

**Znaczenie/kontekst:** Papañca → „rozplenianie”. Zakres zaobserwowany: MN 18. Status: ZASTOSOWANE, NIEPOTWIERDZONE. Źródło użycia i uzasadnienia: MN 18, „Uwaga interpretacyjna”, oraz Translation Log, wpis MN 18. Złożenia z papañca wymagają osobnej analizy.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-PAPANCA

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: rozplenianie; ZASTOSOWANE, NIEPOTWIERDZONE; MN 18. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-PAPANCA
- Data nieodtworzona: rozplenianie; ZASTOSOWANE, NIEPOTWIERDZONE; MN 18. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-UPAPAJJATI

**Znaczenie/kontekst:** Upapajjati → „pojawić się ponownie” (formy: „pojawi się ponownie”, „pojawił się ponownie”, „pojawiają się ponownie”). Zakres: MN 41 i nowe przekłady. Status: ZATWIERDZONE — decyzja właściciela T-01 z 2026-10-11 („upapajjati - pojawić się ponownie”), rekord data/owner_decisions_v1.json w repozytorium SuttaFlow. Podstawa: HH/Anīgha, Ñāṇamoli/Bodhi i Ṭhānissaro „reappear”; Sujato „be reborn”; DPD upapajjati 1 „is reborn; re-arises”, upapajjati 2 „appears; arises”, dosł. „goes towards”. Decyzja dotyczy przekładu czasownika i jego parafraz w aparacie sutty; ogólna nazwa pojęcia „odrodzenie” w innych materiałach (np. tytuły wykładów) nie jest nią objęta — potwierdzone przez właściciela 2026-10-11.

**Wyjątki:** Czasownik i parafrazy w aparacie; nie ogólna nazwa pojęcia odrodzenia w innych materiałach. Naturalna fleksja.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-UPAPAJJATI; data/owner_decisions_v1.json#T-01; data/owner_decisions_v1.json#T-01-SCOPE

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: pojawić się ponownie; pojawi się ponownie, pojawił się ponownie, pojawiają się ponownie; ZATWIERDZONE; MN 41 i nowe przekłady; czasownik i parafrazy aparatu, nie ogólne pojęcie odrodzenia. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-UPAPAJJATI
- Data nieodtworzona: pojawić się ponownie; pojawi się ponownie, pojawił się ponownie, pojawiają się ponownie; ZATWIERDZONE; MN 41 i nowe przekłady; czasownik i parafrazy aparatu, nie ogólne pojęcie odrodzenia. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji
- 2026-10-21T17:35:26.226288+00:00: pojawić się ponownie; pojawi się ponownie, pojawił się ponownie, pojawiają się ponownie; ZATWIERDZONE; MN 41 i nowe przekłady; czasownik i parafrazy aparatu, nie ogólne pojęcie odrodzenia. Źródło: prace/20261021-wydanie-2.0.2/recenzje/r1/normatywna/REPORT.md#SF202-N-001; correction of overly broad machine projection, not a new owner decision

#### SF-TERM-OPAPATIKA

**Znaczenie/kontekst:** Opapātika → „pojawiający się spontanicznie” (np. „istoty pojawiające się spontanicznie”). Zakres: MN 41. Status: ZASTOSOWANE, ZATWIERDZONE POŚREDNIO — przyjęte wraz z całym MN 41 RC2 (2026-10-11); samo rozstrzygnięcie podjęła AI według DEC-03 pkt 2 i spójności z T-01. Przeciwne świadectwa: Ñāṇamoli/Bodhi, Ṭhānissaro, Sujato i DPD („spontaneously reborn”).

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania. Akceptacja dotyczy wyłącznie MN41 RC2, nie nowych sutt ani późniejszych rewizji.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-OPAPATIKA; data/owner_decisions_v1.json#RC2-APPROVAL

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: pojawiający się spontanicznie; ZASTOSOWANE, ZATWIERDZONE POŚREDNIO; Użycie MN 41 RC2, przyjęte 2026-10-11; nie uniwersalna akceptacja dla nowych sutt. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-OPAPATIKA
- Data nieodtworzona: pojawiający się spontanicznie; ZASTOSOWANE, ZATWIERDZONE POŚREDNIO; Użycie MN 41 RC2, przyjęte 2026-10-11; nie uniwersalna akceptacja dla nowych sutt. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-DHAMMARAKKHITA

**Znaczenie/kontekst:** Dhammarakkhitā → „chronione przez Dhammę” z przypisem o glosie Vin III 139 (sahadhammikā rakkhanti — pod opieką współwyznawców). Zakres: MN 41. Status: ZATWIERDZONE POŚREDNIO (MN 41 RC2). Podstawa: HH, Ṭhānissaro; DPD „protected by a religion”.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania. Akceptacja dotyczy wyłącznie MN41 RC2, nie nowych sutt ani późniejszych rewizji.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-DHAMMARAKKHITA; data/owner_decisions_v1.json#RC2-APPROVAL

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: chronione przez Dhammę; ZATWIERDZONE POŚREDNIO; MN 41 RC2; z przypisem o Vin III 139 i sahadhammikā rakkhanti. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-DHAMMARAKKHITA
- Data nieodtworzona: chronione przez Dhammę; ZATWIERDZONE POŚREDNIO; MN 41 RC2; z przypisem o Vin III 139 i sahadhammikā rakkhanti. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-SAPARIDANDA

**Znaczenie/kontekst:** Saparidaṇḍā → „chronione groźbą kary”. Zakres: MN 41. Status: ZATWIERDZONE POŚREDNIO (MN 41 RC2). Podstawa: DPD „protected by threat of punishment”; „prawo” występuje tylko w przekładach angielskich (kalka, sekcja 24.3).

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania. Akceptacja dotyczy wyłącznie MN41 RC2, nie nowych sutt ani późniejszych rewizji.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-SAPARIDANDA; data/owner_decisions_v1.json#RC2-APPROVAL

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: chronione groźbą kary; ZATWIERDZONE POŚREDNIO; MN 41 RC2. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-SAPARIDANDA
- Data nieodtworzona: chronione groźbą kary; ZATWIERDZONE POŚREDNIO; MN 41 RC2. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-BYAPADA_BYAPANNACITTA_VERA

**Znaczenie/kontekst:** Byāpāda / byāpannacitta → „zła wola” / „umysł pełen złej woli”; vera → „wrogość”. Zakres: MN 41. Status: ZATWIERDZONE POŚREDNIO (MN 41 RC2). Podstawa: HH, Ñāṇamoli/Bodhi, Ṭhānissaro „ill will”; DPD.

**Wyjątki:** Wyłącznie opisany zakres; nowe znaczenie lub złożenie wymaga odrębnej analizy zdania. Akceptacja dotyczy wyłącznie MN41 RC2, nie nowych sutt ani późniejszych rewizji.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-BYAPADA_BYAPANNACITTA_VERA; data/owner_decisions_v1.json#RC2-APPROVAL

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: zła wola / umysł pełen złej woli / wrogość; ZATWIERDZONE POŚREDNIO; MN 41 RC2. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-BYAPADA_BYAPANNACITTA_VERA
- Data nieodtworzona: zła wola / umysł pełen złej woli / wrogość; ZATWIERDZONE POŚREDNIO; MN 41 RC2. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-SAMADHI

**Znaczenie/kontekst:** Konwencja SuttaFlow według LEX-002/EDIT-003; krótkie kontekstowe objaśnienie opanowania i stabilności umysłu. Polski odpowiednik nie jest cytatem HH.

**Wyjątki:** Formy czasownikowe według zdania; nie podwajać umysłu przy citta. Dawne krótkie brzmienie bez automatycznej korekty. Wzorzec nie obejmuje całej morfologii.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#Terminologia i zakresy zatwierdzeń; docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-SAMADHI; data/owner_decisions_v1.json#T-02; data/owner_decisions_v1.json#RC2.1

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: skomponowanie / niesprzyjający skomponowaniu; ZATWIERDZONE; Przekłady sutt od 2026-10-11; MN 41 §9 tylko odrębna rewizja RC2.1, starsze pozostałe bez zmian. Źródło: docs/standards/2.0-RC.1/ANN-TERMINOLOGY-v1.json#SF-TERM-SAMADHI
- Data nieodtworzona: skomponowanie umysłu / niesprzyjający skomponowaniu umysłu; ZATWIERDZONE; Nowe przekłady i zamówione rewizje; doprecyzowanie z 2026-10-15. T-02 z 2026-10-11 i MN41 RC2.1 zachowane historycznie.. Źródło: Wydany Standard 2.0.1; import 2026-10-21, bez odtwarzania daty nieznanej decyzji

#### SF-TERM-SATI

**Znaczenie/kontekst:** Domyślna konwencja i objaśnienie: przypominanie sobie i utrzymywanie w pamięci tego, co istotne dla bieżącej praktyki.

**Wyjątki:** Nie dopisywać nieustalonego przedmiotu pamiętania; paṭissato wymaga osobnej analizy. Pamiętność jest niewybranym wariantem; pamiętliwość nie jest przyjęta. Nie zmienia to historycznego ānāpānasati.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#SF-RULE-EDIT-003

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: pomność; ZATWIERDZONE; Nowe przekłady i zamówione rewizje w zakresie konwencji sati. Źródło: Normatywna konwencja wydanego Standardu 2.0.1; brak nowego świadectwa właściciela; import 2026-10-21

#### SF-TERM-HH-PRESSURE

**Znaczenie/kontekst:** Celowy termin w linii materiałów HH.

**Wyjątki:** Nie ustanawia nowego lemma pali; poza EN→PL HH brak automatycznego zastosowania.

**Podstawa:** docs/standards/2.0.1/RULE_REGISTRY.json#SF-RULE-LEX-002

**Historia (zachowane brzmienia, nie nowe zgody):**

- Data nieodtworzona: presja; ZATWIERDZONE; Nowe przekłady i zamówione rewizje w zakresie EN→PL HH. Źródło: Normatywna konwencja wydanego Standardu 2.0.1; brak nowego świadectwa właściciela; import 2026-10-21

#### SF-TERM-PUBBENIVASA

**Znaczenie/kontekst:** Decyzja właściciela 22.10.2026: pubbenivāsa → poprzednie życia.

**Wyjątki:** Nie dotyczy każdego nivāsa. Odmienny kontekst i złożenie wymagają analizy źródła.

**Podstawa:** wejscia/ZLECENIE.md#4; wejscia/decisions.txt#1

**Historia (zachowane brzmienia, nie nowe zgody):**

- 2026-10-22: poprzednie życia; ZATWIERDZONE; Formuły wspominania wcześniejszych egzystencji w nowych przekładach i zamówionych rewizjach; bez automatycznej zmiany historii.. Źródło: Bezpośrednie zlecenie właściciela i dokument decyzji
- 2026-10-22: poprzednie życia; ZATWIERDZONE; Formuły wspominania wcześniejszych egzystencji w nowych przekładach i zamówionych rewizjach; bez automatycznej zmiany historii.. Źródło: Korekta detektora w kandydacie: fleksja uczeń/ucznia i łącznik w pubbe-nivāsa; bez zmiany zatwierdzonej glosy lub zakresu.

#### SF-TERM-PUBBENIVASANUSSATI

**Znaczenie/kontekst:** Decyzja właściciela 22.10.2026: pubbenivāsānussati → przypominanie sobie poprzednich żyć.

**Wyjątki:** Nie dotyczy każdego nivāsa. Odmienny kontekst i złożenie wymagają analizy źródła.

**Podstawa:** wejscia/ZLECENIE.md#4; wejscia/decisions.txt#1

**Historia (zachowane brzmienia, nie nowe zgody):**

- 2026-10-22: przypominanie sobie poprzednich żyć; ZATWIERDZONE; Formuły wspominania wcześniejszych egzystencji w nowych przekładach i zamówionych rewizjach; bez automatycznej zmiany historii.. Źródło: Bezpośrednie zlecenie właściciela i dokument decyzji
- 2026-10-22: przypominanie sobie poprzednich żyć; ZATWIERDZONE; Formuły wspominania wcześniejszych egzystencji w nowych przekładach i zamówionych rewizjach; bez automatycznej zmiany historii.. Źródło: Korekta detektora w kandydacie: fleksja uczeń/ucznia i łącznik w pubbe-nivāsa; bez zmiany zatwierdzonej glosy lub zakresu.

#### SF-TERM-MN53-SEKHO-PATIPADO

**Znaczenie/kontekst:** Uczeń pozostający na drodze praktyki, nie ukończony trening; wkroczenie nie oznacza samo w sobie arahantostwa.

**Wyjątki:** Nie globalna glosa wszystkich sekha ani paṭipadā. Gramatykę i kontekst każdorazowo sprawdzić.

**Podstawa:** wejscia/ZLECENIE.md#4; wejscia/decisions.txt#10

**Historia (zachowane brzmienia, nie nowe zgody):**

- 2026-10-22: uczeń, który wkroczył na drogę treningu; ZATWIERDZONE; MN53, zwrot sekho pāṭipado i jego biernik w ramie narracji oraz dwóch podsumowaniach. Źródło: Wyraźna decyzja właściciela, sekho pāṭipado; nie dotyczy zdania o plecach
- 2026-10-22: uczeń, który wkroczył na drogę treningu; ZATWIERDZONE; MN53, zwrot sekho pāṭipado i jego biernik w ramie narracji oraz dwóch podsumowaniach. Źródło: Korekta detektora w kandydacie: fleksja uczeń/ucznia i łącznik w pubbe-nivāsa; bez zmiany zatwierdzonej glosy lub zakresu.

#### SF-TERM-MN53-SUGATA

**Znaczenie/kontekst:** Tytuł Buddhy od su + gata; czytelnicza parafraza z dodanym obrazem drogi. Nie teraźniejsze podążanie. Nie stosować do innych znaczeń sugata, w tym pomyślnego losu istot.

**Wyjątki:** Poza MN53 tylko odniesienie, nie wiążąca glosa. Przypis wyjaśnia parafrazę i obraz źródłowy; nie stosować globalnej zamiany. Detektor obejmuje wyłącznie zapisane formy, bez pełnej fleksji i analizy składni.

**Podstawa:** prace\20261024-mn53-terminologia\ZLECENIE.md; MN53:11.3; CST/VRI cst.p7; DPD sugata/purisadamma/damma/sārathi/anuttara; https://www.dhammatalks.org/suttas/MN/MN53.html

**Historia (zachowane brzmienia, nie nowe zgody):**

- 2026-10-24: ten, który dobrze przebył drogę; PROPOZYCJA; MN53:11.3, tytuły Buddhy; nowe przekłady i zamówione rewizje MN53. Wcześniejsze produkty bez zmian.. Źródło: Poprzednia odpowiedź asystenta: propozycja do oceny, nie zgoda właściciela
- 2026-10-24: ten, który dobrze przebył drogę; ZATWIERDZONE; MN53:11.3, tytuły Buddhy; nowe przekłady i zamówione rewizje MN53. Wcześniejsze produkty bez zmian.. Źródło: prace\20261024-mn53-terminologia\ZLECENIE.md; bezpośrednie przyjęcie dwóch propozycji dla MN53

#### SF-TERM-MN53-PURISADAMMASARATHI

**Znaczenie/kontekst:** Niezrównany przewodnik/szkolący; metafora woźnicy. Możliwość wyćwiczenia nie jest koniecznością poskromienia ani udokumentowaną gotowością/wolą osoby.

**Wyjątki:** Poza MN53 tylko odniesienie, nie wiążąca glosa. Przypis wyjaśnia parafrazę i obraz źródłowy; nie stosować globalnej zamiany. Detektor obejmuje wyłącznie zapisane formy, bez pełnej fleksji i analizy składni.

**Podstawa:** prace\20261024-mn53-terminologia\ZLECENIE.md; MN53:11.3; CST/VRI cst.p7; DPD sugata/purisadamma/damma/sārathi/anuttara; https://www.dhammatalks.org/suttas/MN/MN53.html

**Historia (zachowane brzmienia, nie nowe zgody):**

- 2026-10-24: niezrównany przewodnik ludzi zdolnych do treningu; PROPOZYCJA; MN53:11.3, tytuły Buddhy; nowe przekłady i zamówione rewizje MN53. Wcześniejsze produkty bez zmian.. Źródło: Poprzednia odpowiedź asystenta: propozycja do oceny, nie zgoda właściciela
- 2026-10-24: niezrównany przewodnik ludzi zdolnych do treningu; ZATWIERDZONE; MN53:11.3, tytuły Buddhy; nowe przekłady i zamówione rewizje MN53. Wcześniejsze produkty bez zmian.. Źródło: prace\20261024-mn53-terminologia\ZLECENIE.md; bezpośrednie przyjęcie dwóch propozycji dla MN53

#### TERM-PALI-RUPA-VISIBLE-OBJECTS

**Znaczenie/kontekst:** Widzialne przedmioty poznawane okiem; nie ogólna glosa każdego rūpa.

**Wyjątki:** Nie przenosić na skupisko formy/materialność ani cakkhunā rūpaṁ disvā. Nie poprawiać automatycznie historii. Detektor obejmuje zapisane formy bez pełnej analizy składni.

**Podstawa:** docs/DECYZJE_REDAKCYJNE.md#OWNER-20261024-VISIBLE-OBJECTS

**Historia (zachowane brzmienia, nie nowe zgody):**

- 2026-10-24: widoki poznawane okiem; ZATWIERDZONE; Kolejne nowe przekłady; widzialne przedmioty wzroku, m.in. pięć pasm zmysłowości; naturalna odmiana.. Źródło: docs/DECYZJE_REDAKCYJNE.md#OWNER-20261024-VISIBLE-OBJECTS

Pełne surowe rekordy historyczne i źródła importu: legacy_history w tym samym rejestrze.
Wzorce są ograniczonym detektorem. Brak sygnału nie dowodzi zgodności znaczeniowej.


### Wzorzec K1 i nowe produkty

Opis, Interpretacja i pozostałe główne sekcje: 14 pt bold; Decyzje: nagłówek 14 pt i akapit 11 pt. Opis/Interpretacja kursywą. Metryka: nagłówek 14 pt, body 10 pt, dyskretna postać bez szarego panelu, lewego obramowania i dodatkowego wcięcia (decyzja 22.10.2026). Tekst #3c3c3c; stopka 10,5 pt po prawej; separator przypisów 144 pt. Linie tekstu 12 pt około 17,3466 pt odpowiadają zmierzonemu Docs 115%, nie CSS 1.15. Przypisy 9,5 pt z własnym rytmem. Ostateczna kontrola obejmuje rzeczywisty PDF. Metryka to krótkie wiersze wersji/daty, podstawy i dostawcy sztucznej inteligencji; metoda nazywa rzeczywistą podstawę i źródła; techniczne statusy i brak recenzji palisty pozostają wQA według SF-RULE-FMT-003. Pełne dowody w repo. Źródłowy K1 i dawne produkty nie są nadpisywane. Zatwierdzone odstępy strof określa SF-RULE-FMT-004; osobne proste blokiPali SF-RULE-FMT-010. Kursywa omawianych form w polskim aparacie pozostaje obowiązkowa. Domyślny arkusz nowych dokumentów polski-pali-v2.css importuje zachowane polski-pali.css, odstepy-r4.css i suttaflow.css. Wspólna korekta metryki może być stosowana również w dokumentach o innej podstawie; sam wybór arkusza nie wymaga dodania tekstu palijskiego. Obowiązek par PL–Pali dotyczy kolejnych przekładów z Pali według SF-RULE-FMT-010; EN→PL i inne podstawy zachowują własny zakres według SF-RULE-SRC-001. WersjaV2 usuwa tło, lewy pasek i wcięcie metryki; stare style oraz gotowePDF pozostają niezmienione.

### Wykonanie i ograniczenia pierwszej wersji

Nowe zadania 2.1.0 prowadzi jeden autor z dwiema pełnymi autokontrolami i kontrolą aparatu IK/ID/IR. Samokontrola nie jest niezależną recenzją. Kod full_author w sfe.release_evidence oraz nowa wartość C=PEŁNA_AUTOKONTROLA sprawdzają zapis dowodów, nie znaczenie ani prawdziwość deklaracji wykonania. C=PEŁNA_AI i historyczny finalizer Docs pozostają przy dawnych wymaganiach, bez automatycznego obniżenia. Zlecona niezależna recenzja nadal musi być wykonana. Żaden skrypt nie uruchamia modeli ani nie nadaje D/E lub publikacji. Wydanie wymaga osobnych dwóch recenzji i zgody według REL-001/002; nie są recenzją każdego przekładu.

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

Mapowanie osi B i znanej podstawy poza jej katalogiem określa SF-RULE-STA-002. W zapleczu zachować rzeczywiste basis.method, language, source_id, indirect oraz dowody i ograniczenia; publicznie nazwać rzeczywisty język i pośrednictwo.

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

2. Nowy wpis zachowuje identyfikator i zakres tekstu, tytuł we właściwym języku podstawy (Pali dla palijskiego tekstu) i polski, datę ukończenia według Europe/Warsaw, link do finalnego produktu właściwego dla ścieżki (nowy Markdown/PDF lub historyczny Google Doc), wersję Standardu oraz krótki protokół QA. Protokół identyfikuje źródło, sprawdzonego kandydata, wykonawcę i rodzaj review, ważne problemy i ich rozstrzygnięcia, akceptację uwag oraz wersję dokumentu i trwały odsyłacz do rzeczywiście sprawdzonego PDF. Brakujące dawne dowody oznacza się jako nieodtworzone, nie dopisuje z pamięci.

3. Zamknięte fazy lub większe partie są grupowane chronologicznie.

4. Log jest historią audytową: wpisów nie usuwać. Korekty istniejącego przekładu odnotowywać jako rewizję, nie jako zniknięcie wcześniejszego wykonania.

5. 01_SUTTAFLOW_QUEUE pozostaje źródłem prawdy dla tego, co ma być wykonywane teraz; ten dokument odpowiada za to, co już zakończono.

Zakres historycznych wyników: wpisy istniejące przed wdrożeniem Standardu 1.0, do AN 4.161 włącznie, zachowują pierwotne statusy i uwagi. Oznaczają ukończenie według ówczesnych, nienumerowanych zasad, nie nową certyfikację zgodności z 1.0. W tej naprawie dokumentacji nie wykonano ponownego pełnego QA korpusu ani nie odtworzono brakujących protokołów. Nowe audyty i korekty są osobnymi zdarzeniami. Data rewizji nie zastępuje daty pierwotnego ukończenia.

Klucz zdarzenia: subject_id, declared_scope, source_edition, candidate_revision_or_content_hash, event_type. Najpierw odczyt produktu, potem zapis i odczyt LOG, na końcu uzgodnienie QUEUE. Wszystkie daty Europe/Warsaw.
