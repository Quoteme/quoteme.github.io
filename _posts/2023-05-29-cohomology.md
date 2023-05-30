---
layout: post
title: Cohomology of various spaces
author: Luca Leon Happel
date: 2023-05-29 Mo 14:37
category: posts
draft: false
---

## Goals

Let us consider the following topological spaces:

- $K$ which is the Klein-bottle
- $\mathbb{P}^n(\mathbb{R})$ which is the real projective space of dimension $n$
- $T^n$ which is the product of $n$ circles.

We want to calculate their homology and analyze the differences we encounter in regards to regular homology.

## Introduction

### Homology

Let's first look at Homology. Homology is a method to work with the holes of some space $X$.
In this post, we will only look at "nice" spaces, which are given as **simplicial complexes**.
A simplicial complex is a space, which can be constructed by taking points,
lines between points, faces between lines, and so on. Think of polytopes, like those you
would generally run into, if you play 3D-videogames. In the case of 3D-videogames, the
simplicial complexes would be the "polygons" (technically polytopes) for the player, the environment
and so on. Someone just slapped some textures onto the faces of these simplicial complexes. Also,
generally in 3D-videogames you do not run into simplicial complexes, which have dimension greater than 3.

Now, we can construct the homology of a simplicial complex by looking at its _chain complex_.
Lets consider the Klein-bottle $K$ for example. First, we can look at it's fundamental polygon.
We can see, that there is only one vertex $v$, two sides $s,t$ and one face $f$. To construct the
simplicial homology of our space, we construct modules out of each of these sets:

- $C_0 = \mathbb{Z}v$
- $C_1 = \mathbb{Z}s \oplus \mathbb{Z}t$
- $C_2 = \mathbb{Z}f$

This forms a **chain complex** by providing maps $\partial_n : C_{n} \to C_{n-1}$
between each of these modules:

\[\begin{align*}
\dots \to 0 \to C_2 \to C_1 \to C_0 \to 0
\end{align*}\]

We call elements $v\in C_i$ which have a boundary $\partial v$ of $0$ a **cycle**
and all those elements $w\in C_{i-1}$ a **boundary**, which are the boundary $\partial v = w$ 
for some other element $v\in C_i$
Now, holes are just those cycles, which are not the boundary of some other element, leading to the
definition of homology:

\[\begin{align*}
H_i(X) = \frac{\text{ker d_i}}{\text{im} d_{i+1}}
\end{align*}\]

### Cohomology

Similarly, we would now like to look at the dual of the above definition. Consider the following
**cochain-complex**:

- $C^0 = \text{Hom}(\mathbb{Z}v, \mathbb{Z})$
- $C^1 = \text{Hom}(\mathbb{Z}s \oplus \mathbb{Z}t, \mathbb{Z})$
- $C^2 = \text{Hom}(\mathbb{Z}f, \mathbb{Z})$
