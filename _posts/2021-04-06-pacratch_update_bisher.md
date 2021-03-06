---
layout: post
title: Pacratch Update bisher
author: Luca Leon Happel
date: 2021-04-06 Di 21:06 44
category: posts
---

<blockquote class="imgur-embed-pub" lang="en" data-id="a/a9oSq6x"  ><a href="//imgur.com/a/a9oSq6x">Pacrach update 2020/04/06</a></blockquote><script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>

Ich arbeite jetzt seit fünf Tagen (plus/minus ein Tag oder so) an einem
neuen Spiel, welches ich "Pacratch" nenne, nach dem Kartenspiel,
welches ich in meiner Grundschule mal entworfen habe. Mehr dazu kann
man auf [https://github.com/Quoteme/pacratch](https://github.com/Quoteme/pacratch)
nachlesen 👍🏻.

Hier ist ein kleiner Statusreport von dem, wie weit ich momentan bin.
Zuerst würde ich aber gerne Robert Smykala und Dominik Du für Ihre
Hilfe beim Zeichnen der entsprechenden neuen Figuren Zitronenmann
und Oni Warrior danken 🙏🏻.

## Kartenupdate

Updates zum Spielsystem sind, dass Karten nun folgende Daten angeben:

![momentanes Kartenlayout und abgespeicherte Daten](https://i.imgur.com/eNGu2rf.png)

Mehr zu dem Thema, welche Daten in einer Karte abgespeichert werden,
wie man selber Karten entwerfen kann und wie man eine Preview einer
Karte bekommen kann, kann man im [Pacrach Wiki](https://github.com/Quoteme/pacratch/wiki/How-to-create-a-new-Pacratch)
nachlesen.

## Spielsystem

Das Spielsystem, beziehungsweise die Spiellogik wurde auch gestern
Nacht etwas mehr von mir überdacht. Wie es jetzt aussieht, ist dass
jeder Spieler ein Kartendeck hat, welches (sagen wir) 60 Karten je hat.
Der Spieler zieht nun in jedem Zug eine gewisse Anzahl von Karten und
darf diese, je nachdem wie schnell die Karte ist, um sein Deck legen.
Es gibt Karten, welche Krieger sind, oder welche Stützpunkte sind, oder
Ausrüstung, oder Infrastruktur, oder ..., jedoch kommen diese alle
vom Deck des Spielers.

Ziel ist es, das Deck der anderen Spieler mit seinen Kriegern zu
übernehmen. Dabei muss man bedenken, dass Krieger nicht all zu weit weg
vom Kartendeck, beziehungsweise der Infrastruktur des Spielers gehen
sollten, da sie dann keine Energie mehr erhalten (und Schaden durch
Verschleiß erleiden).

Man muss also abwägen, wie man am besten sein eigenes Imperium ausbaut
und durch Monster, Krieger und gut geplante Infrastruktur zum Sieg
gelangt.

Hier ist noch ein Bild von dem momentanen Spielideeenplan:

![Spielideeenplan](https://i.imgur.com/91asZx9.png)

---

Zu guter Letzt ist hier noch eine Work-In-Progress preview für eine
neue Art von Karte: Eine Infrastrukturkarte, welche es erlaubt Kriegern
weiter vom Deck weg zu gehen und trotzdem Energie zu bekommen.
Somit gibt sie Schutz und weil sie ein fliegendes Schloss ist, ist sie
sogar etwas mobil, obwohl das mehr Energie zum Erhalt dieser Karte
bedeutet.

![Preview der neuen Karte](https://i.imgur.com/1Kew2c0.png)
