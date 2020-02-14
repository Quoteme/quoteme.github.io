---
layout: post
title: intersect.mjs und der Sphären/Boxen-Schnitt
category: posts
draft: true
---

Momentan arbeite ich an meiner [intersect.mjs](https://github.com/Quoteme/intersect)
Bibliothek, welche dafür da ist Kollisionen und Schnitte von verschiedenen
geometrischen Strukturen in $n$ dimensionen zu erkennen.

Dabei ist gerade diese folgende Zeile zu einer Herausvorderung geworden:

~~~ javascript
// plane2circle :: Real a => [(a,a)] -> a -> [a] -> ([a] -> Real) -> Boolean
const plane2circle = (p,r,c,d=Math.hypot) =>
~~~

Hierbei definiere ich eine Funktion `plane2circle`,
mit folgenden Eigenschaften:
| Name | Abkürzung | Eigenschaft | Beschreibung |
|:---|:---:|:---:|---:|
| Name | Abkürzung | Eigenschaft | Beschreibung |
<!---
|Hyperwürfel | `p` |`[(a,a)]` | Zwei Punkte im $\mathbb{R}^n$|
|Radius | `r` |`a` | Radius der Sphäre|
|Position der Sphäre | `c` |`[a]` | .|
|Maß | `d` | `[a] -> a` | Ein verwendetes [Maß](https://de.wikipedia.org/wiki/Ma%C3%9F_(Mathematik)#Definition) aus der Maßtheorie|
-->

wichtig ist, dass hierbei [Haskell](haskell.org) Schreibkonventionen
verwendet werden. Also, `a` bedeuted, ein beliebiger Datentyp oder
`[a,a]` deuted auf zwei beliebige Daten (die nicht gleich sein müssen,
des selben Types hin. Da ich `Real a =>...` am Anfang geschrieben habe,
bedeuted dass: `[(a,a)]` $\Rightarrow ((a_{0_0},a_{0_1}),(a_{1_0},a_{1_1}),\dots)$
