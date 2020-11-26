---
layout: post
title: Voxels Rings and Modules
author: Luca Leon Happel
date: 2020-11-26 Do 20:25 50
category: posts
draft: false
---

### Introduction

Last semester I studied [abstract algebra](https://en.wikipedia.org/wiki/Abstract_algebra)
in my fourth year of university. It way pretty tough and sadly I did
not understand all the topics which is probably why I failed it in my
first two attempts.

Now I wish to change this and succeed in my next attempt.
And what better way is there to learn for it, than by writing a video
game? 😂

I got to work on my game ["Story"](https://github.com/Quoteme/story)
and expanded on it's worldbuilding. This made me want to actually code
this world into my game, which then lead me to revisit my voxel-mesher.
A voxel mesher is a program which takes in a set of 3-tuples
$(x,y,z) \in \mathbb{Z}^3$ and creates a mesh out of it. Kinda like
this:

![Example of a Voxel Mesh](https://upload.wikimedia.org/wikipedia/commons/b/bc/Voxels.svg)

If you extend this definition and use 4-tuples $(x,y,z,type)\in\mathbb{Z}^4$
you can even create meshes consisting of different materials with
different textures and so on:

![Example of different types from my game story](https://camo.githubusercontent.com/aaf2980eb37da3e0ed4b1f5c351642c788cd90316b018259a0f17f248fb2fca1/68747470733a2f2f692e696d6775722e636f6d2f496d65416c75332e676966)

### Rings and Modules

So, what does this have to do with
[rings](https://en.wikipedia.org/wiki/Ring_(mathematics)) and
[modules](https://en.wikipedia.org/wiki/Module_(mathematics))?

Well, first of a _Ring_ like the integers $\mathbb{Z}=\{\dots,-2,-1,0,1,2,\dots\}$
together with an [abelian group](https://en.wikipedia.org/wiki/Abelian_group)
called addition $+$, a [monoid](https://en.wikipedia.org/wiki/Monoid)
called multiplication $\cdot$ and a $1$-Element is simply speaking
just a set of numbers on which one can multiply, add and subtract
every number from the other (but not necessarily divide).

$(\mathbb{Z}, +, \cdot)$ forms a Ring, because we can add every element
with another and the result will be in $\mathbb{Z}$. We can also
multiply elements with each other, but when we divide for example $1$
by $2$, the result one half is not an integer $\frac{1}{2} \notin \mathbb{Z}$.

We can see this structure in our voxels, because they are indexed
using integers (i.e. there is no voxel between the first and second one).

Now on to the _Modules_. This is simply speaking just a Group under
Addition together with the attribute that we can multiply each element
with an element of our Ring. This group is basically just provides us
with vector addition and the ring extends this to scalar multiplication.

### How is this related to our voxels then?

Well, our Voxelspace (the set of all 3-tuples $(x,y,z)\in\mathbb{Z}^3$)
is just a _module_! On first glance it might look like a
[vector space](https://en.wikipedia.org/wiki/Vector_space), but because
our voxels are arranged on a grid / indexed by integers and because they
cannot leave this grid but we can move them around by whole numbers,
they are in fact an addative group! (This means, we can move one voxel
one voxel down, or 3 voxels right).
Also, we can multiply the voxels with integers. This would correlate
with multiplying the tuple component wise with our factor.


### Cool, but how is this useful?

Basically this gives intuition into what the length of a module is.
The [length of a module](https://en.wikipedia.org/wiki/Length_of_a_module)
is just the longest chain of submodules a module has, where a submodule
is a proper subset of our module which is invariant under multiplication.

In terms of voxels this means:

<blockquote class="imgur-embed-pub" lang="en" data-id="5P7as95"><a href="https://imgur.com/5P7as95">View post on imgur.com</a></blockquote><script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>

The blue arrow is a submodule, as is the red module. In fact, the entire
floor is a submodule (the floor includes the red arrow as a submodule,
and the floor also includes the blue arrow as a submodule). And all these
submodules are submodules of my entire level which is a subset of a
"voxelspace".

Now the length of a submodule also makes sense intuitively! If we consider
the entire level as a module, then we could pick the floor as a submodule
and then we could pick the red arrow as a submodule of the floor submodule,
and finally pick the empty-set as a submodule. But now we are stuck and
have no more submodules of this _submodule_ of the red arrow _submodule_ of the
floor _submodule_. (Actually, this is the longest chain of proper
submodules one could take here). How many submodules are we deep now?
The answer is _3_! Therefor this module is of length three, which
correlates to a vectorspace of dimension _3_!

### Final words of wisdom

Sometimes it is best to relax a bit and just be creative. Maybe imagine
a weird video-game-universe where you would like to live in. And on closer
inspection of these thoughts, you may just be surprised what gems lie
uncovered hidden in your own imagination.
