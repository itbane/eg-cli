# eg-cli

CLI-Tool für Berechnung/Auswertungen zu [evergore](https://evergore.de). Ich stehe in keiner Verbindung zu evergore oder dem evergore e.V.

## Verwendung

**Die Verwendung findet auf eigene Gefahr statt!**

Die Hilfe des Tools zeigt die detaillierten Möglichkeiten an.

Ganz allgemein:

- `--login` Parameter fragt Benutzername/Passwort ab. Das wird benötigt, um mit dem Spiel zu interagieren. Die Daten werden nirgends zwischengespeichert oder geloggt.

Die Logindaten können in der Datei `.config` im aktuellen Ordner abgelegt werden. Es wird das JSON-Format erwartet.

Beispiel:
~~~json
{
"user":"mein-user",
"password":"mein-passwort"
}
~~~

### Routenplaner

- Berechnet die kürzeste Route
- Optionales Eintragen der Aufträge in der aktuellen Gruppe (`-a`-Parameter)

~~~bash
$ ./eg-cli.py RoutePlaner
~~~

Initial müssen die Städte einmal gesynct werden, um mit dem Städtenamen arbeiten zu können:

~~~bash
$ ./eg-cli.py --login PullCities
~~~

Anschließend können die Wege berechnet werden:

~~~bash
$ ./eg-cli.py --login RoutePlaner -s "Draga Sol" -t "Dur Celusse" -l
User: <user>
Password: 
53:72
43:58
42:56
44:51
42:48
40:45
30:40
~~~

## Danksagung

Vielen Dank an das Evergore-Team für das großartige Spiel.

Vielen Dank an DonPaulus, von dessen [EG Routenplaner](egroutenplaner.bplaced.net) dieses Tool inspiriert wurde und dessen Implentierung des Dijkstra-Algorithmus verwendet wird.
