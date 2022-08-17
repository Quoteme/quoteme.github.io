---
layout: post
title: What are "differential forms"
author: Luca Leon Happel
date: 2022-05-27 Fr 02:05:32
category: posts
draft: false
---

<!-- FIX: change date +1 day -->

## Introduction

Currently while visiting the "[KoMa](http://die-koma.org/)"
(Konferenz der deutschsprachigen Mathematikfachschaften / conference of
German-speaking mathematics students) I got into a lot of interesting
conversations about geometry, topology and category theory. This set
the stage for me to think about differential forms, because I wanted to
understand how exactly these things look and feel like.

## My sketches

<blockquote class="imgur-embed-pub" lang="en" data-id="a/2bqRwJy">
<a href="//imgur.com/a/2bqRwJy">My notes about differential forms</a>
</blockquote>
<script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>

The proof mentioned on page 1 is viewable on [https://web.archive.org/web/20211224033113/https://planetmath.org/tensorproductofdualspacesisadualspaceoftensorproduct](https://web.archive.org/web/20211224033113/https://planetmath.org/tensorproductofdualspacesisadualspaceoftensorproduct)

## Notation

Throughout this article we will choose the following symbols and notation:

- $$M$$ a smooth manifold over a field $$K\subset \mathbb{R}$$
- $$p\in M$$ a point in $$M$$
- $$T_p M$$ the tangent space of $$M$$ at $$p$$
- $$T_p^\ast M$$ the cotangent space of $$M$$ at $$p$$, which
  consists of the linear functions $$\phi: T_p M \to K$$.
  For finite tangent spaces $$T_p M$$, we can canonically
  identify $$T_p^\ast M$$ with $$T_p M$$.
- $$T M = \bigcup_{p\in M} \{p\}\times T_p M$$ and
  $$T^\ast M = \bigcup_{p\in M} \{p\}\times T_p^\ast M$$
  are the tangent/cotangent bundles of $$M$$
- $$\Lambda^k(T^\ast M)$$ is the
  [k-th exterior product](https://en.wikipedia.org/wiki/Exterior_algebra)
  of the cotangent bundle of $$M$$.
  Its elements $$\mu_p\in\Lambda^k(T^\ast M)$$ are called
  [k-coblades](https://en.wikipedia.org/wiki/Blade_(geometry)) and
  allow to measure volumes on some tangentspace $$T_pM$$ in $$k$$-dimensions.
- $$\Gamma(M, \Lambda^k(T^\ast M)) = \Gamma(\Lambda^k(T^\ast M))$$
  is the space of
  [global sections](https://en.wikipedia.org/wiki/Section_(fiber_bundle))
  from the basespace $$M$$ to the total space $$\Lambda^k(T^\ast M)$$.
  We use this, because for an element
  $$\omega:M \to \Lambda^k(T^\ast M)$$ 
  in it, we can smoothly associate for each point $$p$$ on $$M$$
  a k-coblade.

## Formal definition

A differential form $\omega$ is defined as an element
in the space of global sections over the kth exterior algebra
of the cotangent bundle over a smooth manifold $M$. We denote this
as:

$$\omega \in \Gamma(M, \Lambda^k(T^\ast M))$$

## My interpretation

Basically a differential 1-form can be visualized as appending
a vector on to each point of our manifold. Because we work with a smooth
section, these vectors need to vary "smoothly" from one point to
another. This means, if we wiggle the point we look at on our manifold
just a tiny bit, the vector we have related to this point will also
wiggle just a tiny bit. Also out corresponding vector cannot take any
sharp turns if we do not move our point in sharp turns.
