# yatzy

Sovellus on noppapeli Yatzy, jota voi pelata yhdestä neljään henkilöä. Kun peliä pelataan yksin, tarkoituksena on aiemman henkilökohtaisen ennätyksen rikkominen. Pelissä tavoitteena on saada viittä noppaa heittämällä erilaisia lukujen yhdistelmiä kolmella heitolla. Voittaja on se pelaaja, jolla on korkeimmat loppupisteet.


Sovelluksen ominaisuuksia ovat:

- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
     
- Käyttäjä näkee aiemmat huippupisteet taulukossa.
     
- Pelissä voi valita pelaajien määrän.
     
- Moninpelin yhteydessä pelaajat luovat nimimerkin, jonka perusteella tulokset tallennetaan.
     
- Nopanheiton jälkeen pelaaja voi valita, mitkä silmäluvut jätetään pöydälle.
     
- Pelaaja valitsee, minkä yhdistelmän alle heittojen lopputulos merkitään.
     
- Säännöt ovat luettavissa pelissä.

  ## Välipalautus 2

Pelin alussa sovellus kysyy pelaajien määrää ja pyytää syöttämään pelaajien nimet. Pelaajat heittävät vuorotellen noppia. Yhdellä vuorolla pelaajalla on käytössään maksimissaan kolme heittoa. Jokaisen heiton jälkeen pelaaja voi valita nopista ne, jotka haluaa säilyttää. Viimeistään kolmen heiton jälkeen pelaajan pitää valita alasvetovalikosta, mihin kategoriaan haluaa noppansa sijoittaa. Jokainen kategoria on käytössä vain kerran pelaajaa kohti pelin aikana ja käytetyt kategoriat ja niiden pistemäärät ovat näkyvissä ruudulla. Tulokset tallentuvat tietokantaan. Pelin voi myös lopettaa kesken ja jatkaa samaa peliä myöhemmin syöttämällä saadun koodin.

Sovellus ei ole testattavissa Fly.iossa.

### Käynnistysohjeet paikallisesti

Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:
```
DATABASE_URL=<tietokannan-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```
Navigoi kansioon peli
Sovellus käynnistyy komennolla python sovellus.py
Peli löytyy osoitteesta http://127.0.0.1:5000/setup




