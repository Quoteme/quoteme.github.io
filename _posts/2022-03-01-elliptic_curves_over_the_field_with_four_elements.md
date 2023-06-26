---
layout: post
title: Elliptic curves over the field with four elements (not finished)
author: Luca Leon Happel
date: 2022-03-01 Di 20:35:13
category: posts
draft: false
---

## Table of contents

- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
- [The Field $\\mathbb{F}\_4$ with four elements](#the-field-mathbbf_4-with-four-elements)
- [The affine plane](#the-affine-plane)
  - [Example of a reducible hypersurface](#example-of-a-reducible-hypersurface)
  - [Example of an irreducible hypersurface](#example-of-an-irreducible-hypersurface)
  - [Example of an irreducible hypersurface that is an elliptic curve](#example-of-an-irreducible-hypersurface-that-is-an-elliptic-curve)
- [The projective space](#the-projective-space)

## Introduction

<!-- TODO -->

## The Field $\mathbb{F}_4$ with four elements

<!-- TODO -->

## The affine plane

We define the _affine space_ $\mathbb{A}^n_k$ over a ground field $k$
to be the set of all tuples $(x_1, \dots, x_n)$ with elements in $k$.
In the case of $n=2$ we call $\mathbb{A}^n_k$ _affine plane_.
A _variety_ $V(A)$ for a subset $A\subset k[X_1, \dots, X_n]$ of
polynomials is the set points in $\mathbb{A}^n_k$ which are zeros for
each polynomial in $A$.
We call $V(A)$ a _hypersurface_, if $A=\{f\}$ contains only one
element.

We can define a topology on $\mathbb{A}^n_k$ by defining the open sets
to be the sets $V(f)$ for each $f\in k[X_1,\dots, X_n]$. I will not
go into detail as to why this results in a topology. As an example,
we can always construct $V(f_1) \cup\dots\cup V(f_r) = V(f_1\cdot\dots\cdot f_r)$

![](https://i.imgur.com/FoVlqcE.png)

This image shows how solution sets can be united by multiplying the
underlying functions. We use the affine real line $\mathbb{A}^1_\mathbb{R}$
for this illustration. The green function is the product of the blue and
red one and as can be seen, the green graph has exactly the same poles
as the red and blue graph combined.
Furthermore, we define a hypersurface $V(f)$ to be _irreducible_ if the
underlying polynomial $f$ is irreducible. A hypersurface is _reducible_
if it is not irreducible.

### Example of a reducible hypersurface

Consider $f=(x-y)(x+y)$ which is reducible in $\mathbb{R}[x,y]$ as it
can be factored into the non-units: $(x-y)$ and $(x+y)$.

This can be seen in the graph of $V(f)$, because $V(f)$ can be
split into two hypersurfaces $V(x-y)$ and $V(x+y)$.

![](https://i.imgur.com/ABBUUqI.png)

### Example of an irreducible hypersurface

Consider $f=x^2+y^2-1$. This defines the circle $V(f) = S^1$.

![](https://i.imgur.com/sGK3Msf.png)

### Example of an irreducible hypersurface that is an elliptic curve

Another irreducible hypersurface is $V(y^2-x^3+x)$ in
$\mathbb{A}^2_\mathbb{R}$.

![](https://i.imgur.com/p8mcDuu.png)

This also happens to define an elliptic curve. Also, note that an irreducible
hypersurface need not be a connected space in the sense of topology.

## The projective space
