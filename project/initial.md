<!-- Nagłówek – nazwę przedmiotu, nazwę projektu (proszę zaproponować jego nazwę własną), nazwiska autorów, wskazanie lidera, datę sporządzenia. -->

# Programowanie Sieciowe

Zespół Z43:
```s
Mateusz Brzozowski
Bartłomiej Krawczyk
Jakub Marcowski
Aleksandra Sypuła  # lider
```

## Odbiór częściowy

### Działanie

#### Faza nawiązywania połączenia

![](https://i.imgur.com/0FYPE3h.png)

```
z43_sender_1    | Wiadomość wysłana: 1
```
Klient inicjuje połączenie wysyłając kod '1'.

```
z43_receiver    | Otrzymano wiadomość
z43_receiver    | Rozmiar otrzymanych danych: 1
z43_receiver    | Adres klienta: ('172.23.0.4', 39434)
z43_receiver    | Typ pakietu: 1
z43_receiver    | Wiadomość wysłana: 1
```

Serwer odbiera połączenie i jeśli pakiet jest poprawny to odsyła właściwą odpowiedź.

**Uwaga:** Na tym etapie pomijamy fazę uzgadniania kluczy i korzystamy z komunikacji nie szyfrowanej.

#### Faza przedstawiania się

```
z43_sender_1    | Otrzymana wiadomość: 1
z43_sender_1    | Wiadomość wysłana: "3 8 [Miernik CO2     ][Miernik SO2     ][Miernik NO2     ][Miernik CO      ][Miernik C6H6    ][Miernik O3      ][Miernik PM10    ][Miernik PM2.5   ]"
```

Klient oczekuje na pakiet od serwera i jeśli otrzyma go to przedstawia się.

W wiadomości przesyła kod '3', ilość strumieni - w tym wypadku 8 oraz stringi z identyfikatorami stumieni (powiększone o spacje do osiągnięcia 16B).

```
z43_receiver    | Otrzymano wiadomość
z43_receiver    | Rozmiar otrzymanych danych: 130
z43_receiver    | Adres klienta: ('172.23.0.4', 39434)
z43_receiver    | Typ pakietu: 3
z43_receiver    | Wiadomość wysłana: 3
```

Serwer odbiera pakiet z deklaracją od klienta, przesyła potwierdzenie i przechodzi do kolejnej fazy - fazy wymiany danych.


#### Faza wymiany danych

Pierwszy nadawca komunikatów:
![](https://i.imgur.com/A7YTNC2.png)

Drugi nadawca komunikatów:
![](https://i.imgur.com/bg7Uq9n.png)

Na powyższych zdjęciach możemy zauważyć fazę wymiany danych, pierwszy jak i drugi nadawca komunikatów wysyła wiadomość w bajtach zgodnie z założonym protokołem przesyłu danych, następnie odbiorca komunikatów odbiera dostarczone dane.

Wysyłamy datagram o maksymalnym rozmiarze, nie przekraczającym 512 bajów, w tym przypadku 507 bajtów, składa się on z kodu komunikatu (w tym przypadku '4'), numeru przesyłanego datagramu ('0' pierwszy komunikat) oraz danych składających się z id strumienia, znacznika czasu i wartości.

```
z43_sender_1    | Rozmiar pakietu: 507
z43_sender_1    | Wiadomość wysłana: 4 0 [0 1672862250 723][1 1672862250 960][2 1672862250 973][3 1672862250 420][4 1672862250 922][5 1672862250 482][6 1672862250 630][7 1672862250 199][1 1672862251 1000][6 1672862251 586][4 1672862251 972][5 1672862251 471][7 1672862251 249][3 1672862251 460][2 1672862251 1000][0 1672862252 719][6 1672862252 600][5 1672862252 442][1 1672862253 1000][4 1672862253 933][7 1672862253 238][3 1672862253 442][2 1672862253 967][0 1672862253 692][6 1672862253 608][5 1672862254 444][1 1672862254 976][4 1672862254 927][7 1672862254 269][6 1672862255 656][3 1672862255 457][1 1672862255 1000][2 1672862255 1000][0 1672862255 721][5 1672862256 394][7 1672862256 288][4 1672862256 928][3 1672862256 471][1 1672862256 1000][2 1672862256 983][6 1672862257 670][5 1672862257 394][0 1672862257 696][7 1672862257 281][3 1672862257 439][4 1672862257 905][2 1672862258 960][1 1672862258 986][6 1672862258 657][0 1672862258 676][5 1672862259 346][3 1672862259 471][7 1672862259 284][2 1672862259 943][4 1672862259 883][1 1672862260 1000]"
z43_sender_1    | Wiadomość wysłana (raw): b'4\x00\x00\x00c\xb5\xda*\x00\x00\x02\xd3\x01c\xb5\xda*\x00\x00\x03\xc0\x02c\xb5\xda*\x00\x00\x03\xcd\x03c\xb5\xda*\x00\x00\x01\xa4\x04c\xb5\xda*\x00\x00\x03\x9a\x05c\xb5\xda*\x00\x00\x01\xe2\x06c\xb5\xda*\x00\x00\x02v\x07c\xb5\xda*\x00\x00\x00\xc7\x01c\xb5\xda+\x00\x00\x03\xe8\x06c\xb5\xda+\x00\x00\x02J\x04c\xb5\xda+\x00\x00'[...]"
```

Odbiorca komunikatów otrzymuje datagram (w tym przypadku jego dłuość wynosi 507) i decoduje całą wiadomość, możemy zauważyć, że otrzymaliśmy poprawnie zinterpretowane dane: id strumienia, znacznika czasu i wartość dla tego strumienia.

```
z43_receiver    | Otrzymano wiadomość
z43_receiver    | Rozmiar otrzymanych danych: 507
z43_receiver    | Adres klienta: ('172.23.0.4', 39434)
z43_receiver    | Typ pakietu: 4
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik CO2: 723
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik SO2: 960
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik NO2: 973
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik CO: 420
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik C6H6: 922
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik O3: 482
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik PM10: 630
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:30 pochodzące od 172.23.0.4:39434:Miernik PM2.5: 199
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:31 pochodzące od 172.23.0.4:39434:Miernik SO2: 1000
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:31 pochodzące od 172.23.0.4:39434:Miernik PM10: 586
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:31 pochodzące od 172.23.0.4:39434:Miernik C6H6: 972
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:31 pochodzące od 172.23.0.4:39434:Miernik O3: 471
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:31 pochodzące od 172.23.0.4:39434:Miernik PM2.5: 249
z43_receiver    | Nowe dane datowane na 2023-01-04 19:57:31 pochodzące od 172.23.0.4:39434:Miernik CO: 460
```

```
z43_sender_1    | Otrzymana wiadomość: 4 0
```

Możemy zauważyć, że numery przesyłanych datagramów są poprawnie inkrementowane (wcześniej było '0' teraz '1'):

```
z43_sender_1    | Rozmiar pakietu: 507
z43_sender_1    | Wiadomość wysłana: 4 1 [6 1672862260 694][0 1672862260 633][3 ...
z43_sender_1    | Wiadomość wysłana (raw): b'4\x00\x01\x06c\xb5\xda4\x00\x00\x02 ...
```

```
z43_sender_1    | Otrzymana wiadomość: 4 1
```

![](https://i.imgur.com/ea2V2xa.png)

### Wykres

![](https://i.imgur.com/L2hE9sr.png)


Dane zebrane w bazie danych są wyświetlane również na wykresie. Dla każdego klienta tworzony jest osobny wykres z wszystkimi przesyłanymi strumieniami (ośmioma). Pojedynczy klient identyfikowany jest przez adres IP oraz numer portu, z którego przesyła wyniki pomiarów. Na osi x wyświetlana jest data pomiaru a na osi y zmierzona wartość. Wyświetlane dane dla przejrzystości wykresu ograniczone są do dziesięciu najnowszych punktów pomiarów z danego strumienia.