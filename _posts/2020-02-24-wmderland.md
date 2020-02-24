---
layout: post
title: wmderland - mein erster Windowmanager bei dem ich geholfen habe
category: posts
---

### Intro

[Wmderland](https://github.com/aesophor/wmderland) ist ein
[Window-manager](https://wiki.archlinux.org/index.php/Window_manager)
für Linux. Also, ein gewisses Programm, welches mit einem Display-server
kommuniziert und dafür sorgt, dass Fenster auf einem PC angezeigt werden.
In diesem Fall ist Wmderland eine Software, welche von [i3](http://i3wm.org/)
inspiriert ist und zu den so genannten tiling-window-managern gehört;
Also window manager, welche dadurch ausgezeichnet sind, dass diese Fenster
platzsparend auf dem Computerbildschirm aufteilen (in sogenannten tiles).

Wmderland soll dabei einfacher, schneller und kürzer geschrieben sein als
i3, doch dafür steht wmderland noch in den Kinderschuhen.
Ein Problem, welches daraus resultiert ist, dass Wmderland noch nicht
als Binary, also als fertiges Programm verfügbar ist und bisher immer
neu compiliert werden muss. Das alleine wäre noch kein Problem, doch
Wmderland ist auch in keinem Repository verfügbar, also in keiner Sammlung
von Programmen welche auf Linux installiert werden können.

Diese Probleme wollte ich lösen und habe den Inhaber [aesophor](https://github.com/aesophor)
darauf angesprochen, welcher darauf hin ein [PKGBUILD](https://wiki.archlinux.org/index.php/PKGBUILD)
bereitgestellt hat, doch es war meine Aufgabe dieses zu testen.
Da ich jedoch nicht alle meine Daten auf meinem Laptop zu verlieren
riskieren wollte, kam mir eine Idee: Ich emuliere einen PC und lasse darauf
alle tests laufen.

Hier ist das Abenteuer, welches ich dadurch innerhalb einer Nacht durchlaufen
habe:

### Vorbereitung

Als erstes musste ich einen virtuellen PC einrichten. Dafür habe ich
[QEMU](https://www.qemu.org/) verwendet.

1. `pacman -S qemu` (installiert QEMU)

2. `wget http://artfiles.org/archlinux.org/iso/2020.02.01/archlinux-2020.02.01-x86_64.iso`
	(downloaded Archlinux)

3. `qemu-img create -f raw arch 8G` (kreiert einen virtuellen Computer
	mit 8G Speicher. Zuerst hatte ich 4G, was wie es sich später
	herausstellte viel zu wenig war)

4. `qemu-system-x86_64 -cdrom ../archlinux-2020.02.01-x86_64.iso -m 512M  -boot order=d -drive file=arch,format=raw`
	(startetet den virtuellen Computer mit 512MB RAM und läd die Archlinux
	ISO als CD)

5. Von hier aus habe ich den [Archlinux installationsguide](https://wiki.archlinux.org/index.php/Installation_guide)
	befolgt

### Installation von Wmderland

Mit einem fertig eingerichteten virtuellen Computer war ich nun in der
Lage, Software zu installieren wie ich es wollte, ohne dabei Angst haben
zu müssen mein System zu verlieren. Also ging es weiter damit, [aesophor](https://github.com/aesophor)'s
Auftrag weiter auszuführen und zu prüfen, ob sein Wmderland PKGBUILD
funktionieren würde oder nicht.

1. `sudo pacman -S fakeroot bintools` (installiert Programme, welche für
	`makepkg` notwendig sind)

2. `mkdir wmderland && cd wmderland` (erstelle einen neuen Ordner im
	virtuellen computer für Wmderland und gehe dort hinen)

3. kopiere die [PKGBUILD und wmderland.install](https://github.com/aesophor/wmderland/issues/31)
	Dateien von aesophor in den wmderland Ordner
	- dafür habe ich zuerst die Dateien auf meinem Laptop erstellt
	- dann einen http server im selben Ordner gestartet
	- `sudo pacman -S wget` (um im nächsten `wget` verwenden zu können)
	- und zuletzt die dateien mit `wget 10.0.2.2:8080/PKGBUILD` und `wget 10.0.2.2:8080/wmderland.install`
		auf meinen virtuellen Computer gezogen

4. `pacman -S gcc cmake make git` (installiert Compiler die für Wmderland
	benötigt sind und Anderes)

5. `makepkg -si` (compiliert und installiert Wmderland, mit den von
	aesophor spezifizierten Dependencies)
	- hier hängt sich der Compiler bisher bei 14% auf. Deswegen muss ich
		noch etwa testen, bis es ganz klapt
