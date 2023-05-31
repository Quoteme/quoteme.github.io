---
layout: post
title: Cohomology of various spaces
author: Luca Leon Happel
date: 2023-05-29 Mo 14:37
category: posts
draft: true
---

## Goals

Let us consider the following topological spaces:

- $K$ which is the Klein-bottle
- $\mathbb{P}^n(\mathbb{R})$ which is the real projective space of dimension $n$
- $T^n$ which is the product of $n$ circles.

We want to calculate their cohomology and analyze the differences we encounter regarding regular homology.

## Introduction

### Cell/Simplicial complexes

(Co-)Homology is a method to work with holes of some topological space $X$. Not all spaces are
"good", for calculating (co-)homology though. So for the rest of this article, we will
restrict ourselves only to those spaces, which are "good enough" in the sense that
calculating their (co-)homology will be easy for us.
These "good" spaces are given as [cell complexes](https://en.wikipedia.org/wiki/CW_complex).
But before we look at them, we will take a quick detour and look at their smaller cousins,
the [simplicial complexes](https://en.wikipedia.org/wiki/Simplicial_complex)[^1].

A simplicial complex is a space, which can be constructed by taking points,
lines between points, faces between lines, and so on. Think of polytopes, like those you
would generally run into if you play 3D-videogames. In the case of 3D-videogames, the
simplicial complexes would be the "polygons" (technically polytopes) for the player, the environment
and so on. Someone just slapped some textures onto the faces of these simplicial complexes. Also,
generally, in 3D-videogames you do not run into simplicial complexes, which have a dimension greater than 3.

<figure>
<a href="https://en.wikipedia.org/wiki/Simplicial_complex#/media/File:Simplicial_complex_example.svg"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Simplicial_complex_example.svg/1280px-Simplicial_complex_example.svg.png" alt="Example of a simplicial complex"/></a>
<figcaption>__Figure 1__: Example of a simplicial complex. 
    Note that we may call any space which is homeomorphic to a simplicial complex, a simplicial complex.
</figcaption>
</figure>

We construct cell complexes analogously, but instead of using $n$-simplices ("$n$-triangles"),
we use $n$-disks ($n$-cells) which we glue together along their boundaries.

### Homology

Now, we can construct the homology of a cell complex by looking at its _chain complex_.
Let's consider the Klein-bottle $K$ for example. First, we can look at its fundamental polygon.
We can see, that there is only one vertex $v$, two sides $s,t$ and one face $f$. To construct the
homology of our space, we construct modules out of each of these sets:

- $C_0 = \mathbb{Z}v$
- $C_1 = \mathbb{Z}s \oplus \mathbb{Z}t$
- $C_2 = \mathbb{Z}f$

Note here, that we made a choice. Namely, we _chose_ to use $\mathbb{Z}$
as a $\mathbb{Z}$-Module and not some other $R$-Module $M$![^2]
This forms a **chain complex** by providing maps $\partial_n : C_{n} \to C_{n-1}$
between each of these modules:

\begin{equation}
\dots \to 0 \to C_2 \to C_1 \to C_0 \to 0
\end{equation}

We call elements $v\in C_i$ which have a boundary $\partial v$ of $0$ a **cycle**
and all those elements $w\in C_{i-1}$ a **boundary**, which are the boundary $\partial v = w$ 
for some other element $v\in C_i$
Now, holes are just those cycles, which are not the boundary of some other element, leading to the
definition of homology:

\begin{equation}
H_i(X) = \frac{\text{ker d_i}}{\text{im} d_{i+1}}
\end{equation}

### Cohomology

Similarly, we would now like to look at the dual of the above definition. Consider the following
**cochain-complex**:

- $C^0 = \text{Hom}(\mathbb{Z}v, \mathbb{Z})$
- $C^1 = \text{Hom}(\mathbb{Z}s \oplus \mathbb{Z}t, \mathbb{Z})$
- $C^2 = \text{Hom}(\mathbb{Z}f, \mathbb{Z})$

---

[^1]: Further information about simplicial complexes can be found in "Glen E. Bredon: Topology and Geometry" in Definition 21.1
[^2]: In general, we will denote the _chain complex with coefficients in $M$_ as $C_*(X; M)$, where $M$ ist a $R$-Module for some ring $R$.
