# SuttaFlow

SuttaFlow to eksperymentalny projekt tłumaczenia kanonu palijskiego na język polski z pomocą sztucznej inteligencji. W [czytelni](https://suttaflow.pl/) można otworzyć suttę, włączyć tekst pāḷi przy przekładzie dwujęzycznym i przeczytać przypisy. Osobny [opis metody](https://suttaflow.pl/jak-powstaja-tlumaczenia.html) pokazuje, jak powstaje szkic, jak rozstrzyga się trudne miejsca i co można sprawdzić samodzielnie.

## Czytelnia na własnym komputerze

Z katalogu głównego repozytorium uruchom serwer Pythona 3.

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory czytelnia
```

Otwórz [Bibliotekę na swoim komputerze](http://127.0.0.1:8000/). Katalog, teksty, skrypty i krój pisma są w folderze [czytelnia](czytelnia/). Zakładki są zapisywane w przeglądarce dla adresu, pod którym czytasz.

Biblioteka pokazuje początkowo dziesięć ostatnio dodanych tekstów. Pole `addedOn` w katalogu oznacza dzień pierwszego dodania do czytelni. Przy tej samej dacie decyduje kolejność kanoniczna. Po wybraniu zbioru teksty są uporządkowane według numerów.

### Wyszukiwanie

Wpisanie numeru lub tytułu pokazuje pasujące sutty z katalogu. Przycisk „Szukaj też w treści” pozwala znaleźć tę samą frazę we fragmentach mów. Przy wyszukiwaniu w treści przeglądarka pobiera indeksy zaznaczonego zbioru. Osobne pliki zawierają pāḷi i przypisy. Nowa wersja indeksu dostaje nazwę zależną od zawartości.

Po aktualizacji katalogu lub przekładów przebuduj indeksy, a potem sprawdź wyniki względem pełnych tekstów. Oba polecenia uruchom z katalogu głównego.

```sh
python narzedzia/indeks_szukania.py czytelnia/assets
node narzedzia/test_wyszukiwania.cjs czytelnia/assets
```

Przy publikacji najpierw udostępnij pliki indeksów, a następnie katalog, który się do nich odwołuje.

## Silnik tłumaczeniowy

Folder [silnik](silnik/) zawiera kod Pythona z wydania SuttaFlow 2.2.0, reguły redakcyjne, schematy danych, kartę ocen i narzędzia składu. [Standard 2.2.0](silnik/docs/standards/2.2.0/SUTTAFLOW_2_0.md) opisuje pracę nad przekładem. [Rejestr reguł](silnik/docs/standards/2.2.0/RULE_REGISTRY.json) i [słownik decyzji terminologicznych](silnik/docs/standards/2.2.0/TERMINOLOGY.md) dokumentują kryteria używane przy sprawdzaniu tekstu.

Pierwszy fragment MN 10 pokazuje, jak narzędzie łączy zatwierdzony polski tekst z właściwym zdaniem pāḷi. Przykład działa lokalnie w Pythonie 3.12. Z katalogu głównego wykonaj następujące polecenia.

```sh
cd silnik
python -m sfe.parallel_text przyklad/przeklad.md przyklad/mapa.json mn10-przyklad.md
python -m unittest discover -s tests
```

W pliku `mn10-przyklad.md` znajdziesz oba teksty i oznaczenie fragmentu. Narzędzie najpierw porównuje sumy kontrolne wejść i sprawdza zakres tekstu przypisany do każdego zdania. Przy ponownym uruchomieniu wybierz nową nazwę pliku wynikowego.

Szkic i ocenę sensu przygotowuje model językowy według standardu. W powyższym przykładzie przekład jest już gotowy. Python sprawdza jego powiązanie ze źródłem. Moduły przeznaczone do kontroli konkretnych wydań wymagają plików źródłowych i zapisów decyzji dla danej pracy. Zestaw testów zawiera także wcześniejszy rejestr 2.0.0 potrzebny do sprawdzenia zgodności między wydaniami.

## Pochodzenie materiałów

Kod silnika pochodzi z oznaczonego wydania `suttaflow-2.2.0`. Opis na stronie uwzględnia też praktykę redakcyjną późniejszych rewizji. Źródła poszczególnych przekładów podano przy suttach. Dołączone kroje pisma, ikony i biblioteka dzielenia wyrazów mają własne informacje o autorstwie i licencjach w katalogach zasobów.
