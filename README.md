# yatzy

Sovellus on noppapeli Yatzy, jota voi pelata yhdestä neljään henkilöä. Kun peliä pelataan yksin, tarkoituksena on aiemman henkilökohtaisen ennätyksen rikkominen. Pelissä tavoitteena on saada viittä noppaa heittämällä erilaisia lukujen yhdistelmiä kolmella heitolla. Voittaja on se pelaaja, jolla on korkeimmat loppupisteet.


Sovelluksen ominaisuuksia ovat:
     
- Pelissä voi valita pelaajien määrän.
     
- Moninpelin yhteydessä pelaajat luovat nimimerkin, jonka perusteella tulokset tallennetaan.
     
- Nopanheiton jälkeen pelaaja voi valita, mitkä silmäluvut jätetään pöydälle.
     
- Pelaaja valitsee, minkä yhdistelmän alle heittojen lopputulos merkitään.
     

### Tulevia mahdollisia ominaisuuksia

- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
     
- Käyttäjä näkee aiemmat huippupisteet taulukossa.

- Säännöt ovat luettavissa pelissä.


## Lopullinen palautus

Pelin alussa sovellus kysyy pelaajien määrää ja pyytää syöttämään pelaajien nimet. Pelaajat heittävät vuorotellen noppia. Yhdellä vuorolla pelaajalla on käytössään maksimissaan kolme heittoa. Jokaisen heiton jälkeen pelaaja voi valita nopista ne, jotka haluaa säilyttää. Viimeistään kolmen heiton jälkeen pelaajan pitää valita alasvetovalikosta, mihin kategoriaan haluaa noppansa sijoittaa. Jokainen kategoria on käytössä vain kerran pelaajaa kohti pelin aikana. Tulokset tallentuvat tietokantaan. Pelin voi myös lopettaa kesken ja jatkaa samaa peliä myöhemmin syöttämällä saadun koodin. Kun molemmat pelaajat ovat käyttäneet kaikki kategoriat, peli päättyy ja ruudulla näkyvät pelaajien saamat pistemäärät.

Sovellus ei ole testattavissa Fly.iossa.

### Käynnistysohjeet paikallisesti

Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:
```
DATABASE_URL=<tietokannan-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```
Sovellusta voi testata luomalla tiedostossa schema.sql osoitetut tietokantataulut ja asentamalla sovelluksen riippuvuudet.

Navigoi pelin kansioon

Sovellus käynnistyy komennolla python sovellus.py

Peli löytyy osoitteesta http://127.0.0.1:5000/setup

Jos pelaaja painaa Continue later -nappia, peliä pääsee jatkamaan uudestaan yllä mainitussa osoitteessa syöttämällä saadun koodin.

### Ohjeet testaamiseen

Valitse pelaajien määräksi esimerkiksi 2 ja syötä pelaajien nimet. Paina Start New Game -nappia. Ruudun yläosassa näkyy, kenen vuoro on kyseessä. Heittoja on käytettävissä maksimissaan kolme per heittovuoro. Valitse nopat, jotka haluat säilyttää raksimalla ruutu nopan oikealla puolella ja paina Roll-nappia heittääksesi uudestaan. Valitse alasvetovalikosta kategoria, johon haluat sijoittaa saamasi nopat ja paina Submit-nappia, jotta peli rekisteröi saamasi pisteet. Jokainen kategoria on käytettävissä vain kerran per pelaaja pelin aikana, ja jo käytetty kategoria ei ole valittavissa uudestaan listasta. Näet kaikkien pelaajien sen hetkiset kokonaispistemäärät ruudulla ja pelin tavoitteena on kerätä mahdollisimman korkea pistemäärä. Paina sivun alalaidasta Continue later -nappia, peli antaa sinulle Game ID -numeron sivun ylälaidassa, mikä kannattaa muistaa tai kirjoittaa ylös. Kokeile syöttää kenttään Enter Game ID (number) to Continue esimerkiksi kirjain. Mitään ei tapahdu, sillä kenttä hyväksyy vain numeroita. Syötä saamasi numero kenttään ja paina Continue Game -nappia ja palaat takaisin kesken jääneeseen peliisi. Painamalla sivun ylälaidan navigointipaneelin Jatka toista peliä -nappia, pystyy jatkamaan kesken jättettyä peliä syöttämällä aiemmin saamasi numero Game ID kenttään ja painamalla Continue-nappia. Ylänavigoinnin Uusi peli -nappi aloittaa uuden pelin. Pelisivun End Game -nappi lopettaa kyseisen pelin tallentamatta sitä. Kun kaikki pelaajat ovat käyttäneet kaikki kategoriat, peli päättyy ja ruudulla näkyvät pelaajien pistemäärät. Sivun ylänavigoinnista on mahdollista aloittaa uusi peli tai jatkaa aiemmin kesken jätettyä peliä.




