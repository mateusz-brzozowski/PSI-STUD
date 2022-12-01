# Zadanie 2
Napisz zestaw dwóch programów – klienta i serwera wysyłające dane w protokole TCP. Wykonaj ćwiczenie w kolejnych inkrementalnych wariantach (rozszerzając kod z poprzedniej wersji). W wariancie Python należy początkowo w kodzie klienta i serwera użyć funkcji `sendall()`. Serwer wyprowadza na stdout adres dołączonego klienta.

# Zadanie 2.1
Klient wysyła a serwer odbiera porcje danych o stałym, niewielkim rozmiarze (rzędu kilkudziesięciu bajtów). Mogą one zawierać ustalony „na sztywno” lub generowany napis – np. „abcde….”, „bcdef…​”, itd. Po wysłaniu danych klient powinien kończyć pracę. Serwer raz uruchomiony pracuje aż do zabicia procesu.

Wykonać program w dwóch wariantach: C oraz Python. Sprawdzić i przetestować działanie „między platformowe”, tj. klient w C z serwerem Python i vice versa.

# Zadanie 2.2
Zmodyfikować program serwera tak, aby bufor odbiorczy był mniejszy od wysyłanej jednorazowo przez klienta porcji danych. W wariancie Python wykonać eksperymenty z funkcjami `send()` i `sendall()`. Jak powinien zostać zmodyfikowany program klienta i serwera aby poprawnie obsłużyć komunikację? Uwaga – w zależności od wykonanej implementacji programu z punktu 2.1 mogą, ale nie muszą, poprawnie obsługiwać wariant transmisji z punktu 2.2.

# Zadanie 2.5
Na bazie wersji 2.1 – 2.2 zmodyfikować serwer tak, aby miał konstrukcję współbieżną, tj. obsługiwał każdego klienta w osobnym procesie. Przy czym:

- Dla C. Należy posłużyć się funkcjami fork() oraz wait().

- Dla Pythona należy posłużyć się wątkami, do wyboru: wariant podstawowy lub skorzystanie z ThreadPoolExecutor.
