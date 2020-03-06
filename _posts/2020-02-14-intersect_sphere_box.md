---
layout: post
title: intersect.mjs und der Sphären/Boxen-Schnitt
category: posts
---

### Problem

Momentan arbeite ich an meiner [intersect.mjs](https://github.com/Quoteme/intersect)
Bibliothek, welche dafür da ist Kollisionen und Schnitte von verschiedenen
geometrischen Strukturen in $$n$$ dimensionen zu erkennen.
Dabei ist gerade diese folgende Zeile zu einer Herausvorderung geworden:

{% highlight javascript %}
// plane2circle :: Real a => [(a,a)] -> a -> [a] -> ([a] -> Real) -> Boolean
const plane2circle = (p,r,c,d=Math.hypot) =>
	//TODO
{% endhighlight %}

| Abkürzung | Name | Eigenschaft | Beschreibung |
|:---------:| ---- | ----------- | ------------ |
| `p` | Hyperwürfel			| `[(a,a)]`	| Zwei Punkte im $$\mathbb{R}^n$$ |
| `r` | Radius				| `a`			| Radius der Sphäre |
| `c` | Position der Sphäre	| `[a]`		| Position des Zentrums der Sphäre |
| `d` | Maß					| `[a] -> a`	| Ein verwendetes [Maß](https://de.wikipedia.org/wiki/Ma%C3%9F_(Mathematik)#Definition) aus der Maßtheorie|

hierbei verwende ich [Haskell](haskell.org) Schreibkonventionen für die
Eigenschaften. Also, `a` bedeuted, ein beliebiger Datentyp oder
`[a,a]` deuted auf zwei beliebige Daten (die nicht gleich sein müssen,
des selben Types hin. Da ich `Real a =>...` am Anfang geschrieben habe,
bedeuted dass: `[(a,a)]` ist eine Liste von Tupeln verschiedener reeller
Zahlen: $$((a_{0_0},a_{0_1}),(a_{1_0},a_{1_1}),\dots), \quad a_{i_j} \in \mathbb{R}$$

### Lösung

Damit ich diese Funktion dazu bringen konnte, zu funktionieren ist mir
eine Lösung gekommen. Gegeben hatte ich bereits eine Funktion, welche
prüft ob eine Hypersphäre und ein Punkt sich schneiden. Daher habe ich
eine weitere Funktion geschrieben, welche prüft, ob sich ein Kreis und
ein Intervall schneiden:

{% highlight javascript %}
// point2circle :: Num a => [a] -> Real -> [a] -> ([a] -> Real) -> Boolean
export const point2circle = (p,r,q=p.map(_=>0),d=Math.hypot) =>
	d(...p.map((x,i) => x-q[i])) <= r;

// interval2circle :: Num a => a -> Real -> [a,a] -> Boolean
export const interval2circle = (c,r,i,d=Math.hypot) =>
	point2circle([c], r+Math.abs(i[0]-i[1])/2, [(i[0]+i[1])/2], d)
{% endhighlight %}

Nun ist es ein Leiches, zu prüfen ob ein Hyperwürfel und eine Hypersphäre
sich schneiden;
Man muss prüfen ob die Projektionen der Sphäre und des Hyperwürfels sich
auf jeder Achse schneiden.

<blockquote class="imgur-embed-pub" lang="en" data-id="a/rZpCzkF" data-context="false" ><a href="//imgur.com/a/rZpCzkF"></a></blockquote><script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>

{% highlight javascript %}
// plane2circle :: Num a => [(a,a)] -> Real -> [a] -> ([a] -> Real) -> Boolean
export const plane2circle = (p,r,c,d=Math.hypot) => p
	.map((i,j) => interval2circle(c[j],r,i,d) )
	.every(e => e==true)
{% endhighlight %}

und diese Funktion können wir nun testen:

{% highlight javascript %}
import * as int from './intersect.mjs'

let p = [[0,1],[0,1],[0,1]]
let r = 1
let c = [0,0,0]
console.log(int.plane2circle(p,r,c)) // true ✅

let p = [[0,1],[0,1],[0,1]]
let r = 1
let c = [0,0,2]
console.log(int.plane2circle(p,r,c)) // false ✅

let p = [[0,1],[0,1]]
let r = 1
let c = [2,2]
console.log(int.plane2circle(p,r,c)) // false ✅
{% endhighlight %}

besonders das letzte Ergebnis kann man leicht überprüfen:

![geometrischer Beweis](https://i.imgur.com/aqI995m.png)

### Fazit

Das Problem _Schnitte zwischen höherdimensinalen Sphären und Würfeln_
zu lösen war nicht all zu einfach auf den ersten Blick; doch verwendet
man (wortwörtlich) verschiedene Perspektiven und ist bereit bereits
bekannte Resultate (wie `point2circle`) zu verwenden und neue zu
finden (wie `interval2circle`), so ist es doch ein Leichtes gewesen
eine allgemeine Lösung zu finden.
