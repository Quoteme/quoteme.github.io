---
layout: post
title: Math meme finished
author: Luca Leon Happel
date: 2021-10-21 Di 23:58:35
category: posts
draft: false
---

## The exercise

Around one year ago I tried to solve
[the following riddle](/posts/math_meme_proof) involving
abstract algebra, but I failed and did not finish the question at that

![Prove that Rx/(x^2+bx+c) is isomorphic to R^2 or C](https://i.imgur.com/5gUWnRL.png)

## The proof

Let $$f=x^2+bx+c\in\mathbb{R}[x]$$.
$$f$$ can either have one double root, iff the discriminant
$$\Delta f=b^2-4c$$ is
zero, or it can have two real roots iff $$\Delta f>0$$, or it can have
two complex roots iff $$\Delta f<0$$.

### Negative discriminant

If $$\Delta f>0$$ we have $$f(x)\in\mathbb{R}$$ with $$x\not\in\mathbb{R}$$.
We can rewrite $$f(x)=x^2+bx+c=0$$ to be $$x^2+bx=-c$$, and therefor
$$x^2+bx\in\mathbb{R}$$.
Also, because $$\Delta f>0$$, we know that that we can split $$f(x)$$
into its linear factors $$f(x)=(x-w)(x-v)$$ with $$w,v\in\mathbb{R}$$.
This means that our number $$x$$ will be equal to $$0$$ if we subtract
a real number from it, meaning it must be real, thereofr concluding
that $$\mathbb{R}/(x^2+bx+c)\cong \mathbb{R}\times \mathbb{R}$$

### Positive discriminant

In case our discriminant $$\Delta f$$ is positive we know that
$$f(x)$$ cannot be split into real linear monomial factors, which
means that $$x$$ cannot be a real number.
Also, because $$f$$ only has purely complex roots, $$x$$ must be a
purely complex number as well.
Because $$\mathbb{R}[x]/(f)$$ is a vectorspace over $$\mathbb{R}$$
we know that $$\alpha x+\beta=i$$ for $$\alpha, \beta\in \mathbb{R}$$,
concluding that $$\mathbb{R}[x]/(x^2+bx+c) \cong \mathbb{R}[i]=\mathbb{C}$$

## Conclusion

Reading Bosch Algebra really helped me grasp some of the concepts like
field extensions some more. I assume that this knowledge also took
some time to ripen inside my brain, but after some time algebra
finally makes more sense to me. Also I finished my exam about abstract
algebra a few months ago! (While also studying for commutative algebra
and already having finished my introductory course in algebraic geometry).
