# PSI Laboratorium 2
Zespół Z43:
```
Mateusz Brzozowski
Bartłomiej Krawczyk
Jakub Marcowski
Aleksandra Sypuła
```

# Zadanie 2
Napisz zestaw dwóch programów – klienta i serwera wysyłające dane w protokole TCP. Wykonaj ćwiczenie w kolejnych inkrementalnych wariantach (rozszerzając kod z poprzedniej wersji). W wariancie Python należy początkowo w kodzie klienta i serwera użyć funkcji `sendall()`. Serwer wyprowadza na stdout adres dołączonego klienta.

# Zadanie 2.1
> Klient wysyła a serwer odbiera porcje danych o stałym, niewielkim rozmiarze (rzędu kilkudziesięciu bajtów). Mogą one zawierać ustalony „na sztywno” lub generowany napis – np. „abcde….”, „bcdef…​”, itd. Po wysłaniu danych klient powinien kończyć pracę. Serwer raz uruchomiony pracuje aż do zabicia procesu.

> Wykonać program w dwóch wariantach: C oraz Python. Sprawdzić i przetestować działanie „między platformowe”, tj. klient w C z serwerem Python i vice versa.

Napisane po dwa programy w języku C oraz Python - client.c, server.c oraz client.py, server.py działające w protokole UDP. Klient wysyła do serwera określoną liczbę porcji danych o stałym rozmiarze. Istnieje możliwość zdefiniowania własnego hosta oraz portu dla klienta przez podanie przy wywołaniu client.c oraz client.py jako pierwszy argument numer hosta a drugi numer portu. Jeśli wartości te nie zostaną podane, klient będzie korzystał z `localhosta` oraz portu `8000`. Serwer można skonfigurować w analogiczny sposób.

Klient wysyła porcje danych o wielkości zadeklarowanej w stałej `DATA_GRAM_LENGTH` w ilości `DATA_GRAM_NUMBER`. Przed wysłaniem danych, przesyłane dane są wyświetlane na ekranie. Serwer po odbiorze danej porcji danych, dodaje je do już odebranego napisu i dopiero kiedy przestanie otrzymywać dane od klienta (wszystkie informacje zostały przesłane), wyświetla całość na ekranie (zdekodowane na kod `ASCII`) wraz z informacją o adresie, z którego zostały wysłane.

Rozwiązanie zostało przetestowane w każdej konfiguracji klient-serwer również w przypadku działania między platformowego. 

Wszystkie konfiguracje klient-serwer można uruchomić korzystając z docker-compose.yaml. Po wywołaniu `docker compose build`, można wybrać konkretną konfigurację klienta i serwera w wybranych językach np. `z43_client_python_2` z klientem w Pythonie oraz serwerem w C.

Możliwe jest również jedną komendą uruchomienie wszystkich konfiguracji: 
```s
docker-compose up --build
```

# Zadanie 2.2
> Zmodyfikować program serwera tak, aby bufor odbiorczy był mniejszy od wysyłanej jednorazowo przez klienta porcji danych. W wariancie Python wykonać eksperymenty z funkcjami `send()` i `sendall()`. Jak powinien zostać zmodyfikowany program klienta i serwera aby poprawnie obsłużyć komunikację? Uwaga – w zależności od wykonanej implementacji programu z punktu 2.1 mogą, ale nie muszą, poprawnie obsługiwać wariant transmisji z punktu 2.2.

> Demonstrujemy działanie 2 programów: serwer i klient w dowolnym języku.

W funkcji send_text wykorzystywanej do przesyłu danych przez klienta zostały przetestowane obie funkcje: send() oraz sendall() z buforem po stronie serwera mniejszym od przesyłanych przez klienta porcji danych. Po przetestowaniu konfiguracji z wielkością przesyłanych przez klienta danych w ilości 60 a następnie 10 000 z wielkością bufora 10, w obu przypadkach serwer zdołał odebrać wszystkie dane przesłane przez klienta.

# Zadanie 2.5
> Na bazie wersji 2.1 – 2.2 zmodyfikować serwer tak, aby miał konstrukcję współbieżną, tj. obsługiwał każdego klienta w osobnym procesie. Przy czym:

> - Dla C. Należy posłużyć się funkcjami fork() oraz wait().

> - Dla Pythona należy posłużyć się wątkami, do wyboru: wariant podstawowy lub skorzystanie z ThreadPoolExecutor.

> Demonstrujemy działanie 2 programów: serwer w C i klient w Pythonie, albo serwer w Pythonie i klient w C.

Zadanie wykonane w konfiguracji z serwerem współbieżnym w Pythonie oraz klientami w C.