# PSI

## Zadanie 1
Napisz zestaw dwóch programów – klienta wysyłającego i serwera odbierającego datagramy UDP. Wykonaj ćwiczenie w kolejnych inkrementalnych wariantach (rozszerzając kod z poprzedniej wersji).

## Zadanie 1.1
Klient wysyła a serwer odbiera datagramy o stałym, niewielkim rozmiarze (rzędu kilkudziesięciu bajtów). Datagramy mogą zawierać ustalony „na sztywno” lub generowany napis – np. „abcde….”, „bcdef…​”, itd. Powinno być wysyłanych kilka datagramów, po czym klient powinien kończyć pracę. Serwer raz uruchomiony pracuje aż do zabicia procesu. Serwer wyprowadza na stdout adres klienta przysyłającego datagram.

Wykonaj programy w dwóch wariantach: C oraz Python. Sprawdzić i przetestować działanie „między platformowe”, tj. klient w C z serwerem Python i vice versa.

## Zadanie 1.2
Na bazie wersji 1.1 napisać klienta, który wysyła kolejne datagramy o przyrastającej wielkości np. 1, 100, 200, 1000, 2000… bajtów. Sprawdzić jaki był maksymalny rozmiar wysłanego (przyjętego) datagramu. Ustalić z dokładnością do jednego bajta jak duży datagram jest obsługiwany. Wyjaśnić.

To zadanie można wykonać korzystając z kodu klienta i serwera napisanych w C lub w Pythonie.