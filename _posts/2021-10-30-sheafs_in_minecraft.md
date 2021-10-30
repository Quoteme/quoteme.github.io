---
layout: post
title: sheaves in Minecraft
author: Luca Leon Happel
date: 2021-10-29 Di 10:12:35
category: posts
draft: false
---

## Introduction

A few days ago after my introductory class in topology and right before
my class about algebraic geometry, me and my friend Anastasia were asked
by our fellow students from topology about our current topics in
algebraic geometry. This then lead to the discussion
about [sheaves](https://en.wikipedia.org/wiki/Sheaf_(mathematics)), as
they saw my sketch of them in my lecture notes (because I mentioned that
I typically only draw geometric sketches of ideas and proofs instead of
writing actual sentences like most people).

After some explaining they seemed to understand the concept somewhat,
but I was unable to really give them a deeper understanding. I assume
this was caused by my inability to relate the importance of this
structure to them in a practical way. So after some days, I started to
imagine fictional conversations in my spare time where I would try to
explain this topic to them again. I especially tried to focus on
giving real world examples of sheaves, which are not exactly linked to
algebraic geometry, but instead convey the idea of tracking data which
is connected to open sets. And as I thought about this, I started to
imagine video games, which typically provide very natural applications
of impressively deep mathematical structures, leading me to relate the
game [Minecraft](https://en.wikipedia.org/wiki/Minecraft)
to algebraic geometry, or sheaves more exactly.

## Minecraft as a game

Minecraft is the most popular game in existence currently. Therefor it
is very likely that you, the reader, have heard about it at some point
in your life. But here is a quick recap of what Minecraft is and how
it works (abstractly).

### What is minecraft?

![Example view of minecraft](https://i.imgur.com/gJAxAuO.png)

In Minecraft you start a game as digital character in a blocky world.
There you start to collect resources by mining different materials (in
the form of breaking blocks mainly) or slaying enemies which roam your
digital world.

### How does it technically work?

Now the interesting part for us at least would be, how the game stores
this world and its inhabitants. We know that the blocks are arranged in
a lattice pattern which happens to be $$\mathbb{Z}^3$$ and because each
block can be identified by its type (_air_, _grass_, _dirt_, _wood_, ...)
and there are just a finite number of unique blocks, we can store
the blocky part of a Minecraft world as a subset
$$M\subset \mathbb{Z}^3\times\mathbb{N}$$ by using a bijective mapping
from the types of blocks to $$\mathbb{N}=\{0,1,2,\dots\}$$.

Now how can Minecraft be able to process infinitely many blocks and
render them to a screen? The answer is that this would be impossible,
because traversing every block in an infinite Minecraft world (which
most Minecraft worlds basically are) would take a very long time, let
alone rendering them. This would be impossible to render at a stable
30FPS and therefor the developers at Mojang decided to split the
Minecraft world into chunks of $$16\times 16\times 256$$ (here we can
neglect the last coordinate of our tuples in $$M$$, because the number
of different blocks is small small enough that a computer can traverse
them easily).

![Examples of chunks - chunkbounds shader](https://i.imgur.com/6sKQkg8.jpg)
![Examples of chunks - chunk edge indicator](https://i.imgur.com/I3ZECeE.png)

These subsets of the world $$$C_{x,y,z}\subset M\subset \mathbb{Z}^3\times\mathbb{N}$$
are called chunk and each exist for each $$x,y \in 16\mathbb{Z}, \> z\in 256\mathbb{Z}$$
(technically the $$z$$ is fixed to $$0$$ because Minecraft has a finite
height of $$256$$ blocks, but we will abstract/future proof a bit for now).

<!--
TODO: Link basis of topology
-->

So why are these chunks important for us? How do they relate to sheaves?
Well, these $$C_{x,y,z}$$ form a
[basis of a topology](https://en.wikipedia.org/wiki/Base_(topology))
on $$M$$ if we name the "chunks" not "chunks"
but "open sets" instead! This is quite
natural because Minecraft creates a union of these chunks (the number
of which is free for the user to decide, therefor possibly infinite)
and then renders this union of chunks to the screen. This union of chunks
would not be considered a chunk in Minecrafts' code, but we will refer to
the union of chunks as "open set" nonetheless, because this gives us our
topological structure on $$M$$. (Bonus: to really proof that the
$$C_{x,y,z}$$ form a topological basis, one must show that the finite
intersection of open sets must also be an open set. The proof is quite
trivial but left as an exercise to the reader.)

### So we have a topological space on our Minecraft world $$M$$, what now?

After having done all of this for the sake of rendering parts of our
world on a computer in a finite time, we get some fundamentally needed
game mechanics (which are not obviously related to the rendering pipeline)
for free!

Like for example when the player wants to go to sleep in the game.
Minecraft first checks if the player does not have any hostile entities
in the current chunk. Therefor the game must calculate the set of
all entities in currently in the game world, which are also in the
currently inhabited chunk.

For this, Minecraft stores all entities as tuples $$e\in\mathbb{R}^3\times\mathbb{N}$$,
where $$\mathbb{N}$$ again denotes the type of enemy. But now, minecraft
also has a functor $$\mathcal{F}: (\frac{\text{open}}{M})\to \mathcal{E}$$, where
$$\mathcal{E}$$ is the category of entities, which has as objects just
sets of entities and as morphisms the surjective maps
$$\phi: V \twoheadrightarrow V'\subset V$$ for $$V, V'\in \mathcal{E}$$
and $$\frac{\text{open}}{M}$$ denotes the category of open sets over $$M$$
created by set inclusion as well.

In tradition to the notation used by my professor Schröer, I will
denote the application of this functor as $$\Gamma(U, \mathcal{F})=V$$.

### A quick recap in simple terms

What we did now, was define a mapping from the open sets in our Minecraft
world to the sets of entities. This just allows us to ask the
following question using the mathematical/computer language:

> Which entities (like zombies, skeleton, player, ...) are inside
> the collection of the following chunks:
> $$C_{x_1, y_1, z_1}, C_{x_2, y_2, z_2}, \dots$$ ?

And the formulation in mathematical lingo would be:

$$\begin{equation}
\Gamma(\bigcup_{i\in I} C_{x_i, y_i, z_i}, \mathcal{F})=V
\end{equation}$$

where $$V$$ is the set of entities we are looking for. We can say as a
rule, that for our purposes $$\mathcal{F}$$ must suffice the following
condition:

- For each open set $$U$$ of $$M$$, we have the set $$\Gamma(U, \mathcal{F})$$.

### But who needs the structure of a sheaf for that? Doesn't a function suffice?

![Well yes, but actually no](https://i.imgur.com/4RXyf44.jpg)

The problem with just mapping open sets of our
Minecraft world to sets of entities raises the problem of
_restricting our open set_ but _increasing our number of entities therein_.
Imagine the following. You have your Minecraft map and play the game inside.
Now you wish to poll the number of entities which are located in your
current chunk (the one your player resides in) and the ones adjacent to
this one. This would give you in total $9$ chunks in which you poll
for entities, because you wish to sleep in the game and the game does 
not let you sleep, if there are any monster (subset of entities) near
your bed. So the game says everything is fine, your player is the only
entity in these chunks and you can go to bed. But when you wake up
in Minecraft to your dismay you are getting attacked by a zombie, because
actually there was one more entity nearby. This problem/bug occurred,
because the mapping which shows entities residing in a open set of our
topology did not respect _restriction mappings_. This means, even if
one takes the subset of an open set, the correlating entities in this
subset need not be a subset of the entities correlating to the supset.

We can solve this issue by requesting our function $$\mathcal{F}$$ must
fulfill the following criteria:

- For each inclusion $$V'\subset V$$ there must be a function
  $$\text{res}^{V}_{V'}:\Gamma(V,\mathcal{F})\to\Gamma(V',\mathcal{F})$$ <!--__-->
- $$\text{res}^{V'}_{V''} \circ \text{res}^{V}_{V'} = \text{res}^{V}_{V''}$$ <!--__ -->
- $$\text{res}^{V}_{V} = id$$ <!--__-->

This so far just means, that given some $$\Gamma(V,\mathcal{F})$$ which
is the set of entities inside some open set, we can look at smaller
open sets' entities if these open sets are included in the prior open set.

### The last problem to solve

So now we have done all of this to formalize our notion of entities
inside some set of chunks. But there is still some problem in the example
we wrote one paragraph before. We still have not solved the problem
that given our knowledge of $$\Gamma(V,\mathcal{F})$$ where $$U$$ is some
open set (with the player inside) we want to infer that open subsets
$$V'\subset V$$ cannot have more entities or ones, that cannot be found
inside $$V$$.

The problem which we are facing is that we are missing the **sheaf axiom**,
which completes our requirements from before:

- For each open set $$U$$ of $$M$$, we have the set $$\Gamma(U, \mathcal{F})$$.
- For each inclusion $$V'\subset V$$ there must be a function
  $$\text{res}^{V}_{V'}:\Gamma(V,\mathcal{F})\to\Gamma(V',\mathcal{F})$$ <!--__-->
- $$\text{res}^{V'}_{V''} \circ \text{res}^{V}_{V'} = \text{res}^{V}_{V''}$$ <!--__ -->
- $$\text{res}^{V}_{V} = id$$ <!--__-->

which define a sheaf. The sheaf axiom now states the following:

- (_Locality_) If $$\mathcal{U}=\bigcup_{i\in I} U_i$$ is an open
  covering of an open set $$U$$ and if $$s,t\in\Gamma(U,\mathcal{F})$$
  with $$\text{res}^U_{U_i}(s)=\text{res}^U_{U_i}(t)$$, then $$s=t$$
- (_Gluing_) If $$\mathcal{U}=\bigcup_{i\in I} U_i$$ is an open covering
  of an open set $$U$$ and $$s_i\in U_i$$$ for $$i\in I$$ holds
  $$\text{res}^{U_i}_{U_i\cup U_j}(s_i) = \text{res}^{U_j}_{U_i\cup U_j}(s_j)$$
  then there must be exactly one $$s\in\Gamma(U,\mathcal{F})$$ with
  $$\text{res}^U_{U_i}(s) = s_j$$

And these basically state, that if there is some entity $$e'$$ in
$$V'\subset V$$, ergo $$e'\in\Gamma(V', \mathcal{F})$$, then there
must also be exactly one $$e\in\Gamma(V,\mathcal{F})$$ which
is then equal to $$e'$$ is we restrict our focus back to $$V'$$.

In our situation with the zombie before, we had looked at an open set
$$V$$ which was defined as the chunk with the player $$p$$ inside glued together
with the chunks adjacent to that one. We said $$\Gamma(V,\mathcal{F})$$
only included the player, because this was the only entity which was
mapped from $$V$$ by $$\mathcal{F}$$, but then we said there
was actually one zombie $$z'$$ (another entity) inside $$V'$$, which
we defined as the chunk the player was inside.

This clearly violates our sheaf axiom! Because by the _gluing_ property,
we must have $$z\in\Gamma(V,\mathcal{F})$$ as it follows from
$$z'\in\Gamma(V',\mathcal{F})$$ that there needs to be this $$z$$ with
$$\text{res}^V_{V'}(z)=z'$$. So we know that because there is an open set
with a zombie $$z'$$ inside, an entity $$z$$ that looks like this zombie if
we restrict our focus to the open set where we found $$z'$$ must also
exist in any open set $$V$$ that includes $$V'$$.

## Conclusion

This concept might look daunting at first and maybe even useless
because of its' apparent abstractness. But in fact we are very far away
from some abstract useless construct as I tried to visualize in this
blog post. In fact the construct of a sheaf is quite natural as it
canonically allows us to track data attached to open sets (or as is the
case in Minecraft: track entities in unions of chunks).

This concept can be much further observed though, providing a rich
theory not just applicable in algebraic geometry. In fact, I will try to
publish another post soon where I analyze some art I found
particularity interesting using the structures defined in this post while
also extending the notions of a sheaf to the ideas of stalks (which in
our Minecraft example would allocate the entities in the smallest open
set around some some point to said point; Or more concretely all the
entities in a chunk are returned, if we enter some point inside said
chunk) and possibly also the idea of germs.

Until then I wish all of you good luck and fun applying abstract math
with seemingly no application 😉.
