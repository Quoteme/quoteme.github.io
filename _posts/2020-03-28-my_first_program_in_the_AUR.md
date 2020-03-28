---
layout: post
title: Custom login-prompt in linux
category: posts
draft: false
---

Recently I discovered some more of the incredibly useful features of
my favorite text-editor [Neovim](https://github.com/neovim/neovim):

---

Entering `:read !somefunction` in Neovim causes the editor to execute
the command `somefunction` and then insert the echoed response into the
file you are currently editing at your cursor position.

---

This got me thinking... Maybe I could use this to make my programming
more concise. And after installing `figlet` I was proven right:

{% highlight bash %}
# Use `:read figlet "Example"`
#     and then select the output and comment it out: `:'<,'>norm ^i# `
#
#  _____                           _
# | ____|_  ____ _ _ __ ___  _ __ | | ___
# |  _| \ \/ / _` | '_ ` _ \| '_ \| |/ _ \
# | |___ >  < (_| | | | | | | |_) | |  __/
# |_____/_/\_\__,_|_| |_| |_| .__/|_|\___|
#                           |_|
echo "It works!"
{% endhighlight %}

And after all this thinking I was stuck with an idea, which I had for
quite some time already, but never really knew how to implement in vim:

I can use this, to show complex math formulas in programs, as actual math formulas
{: text-align: center}

The problem however was, that no package I searched for seemed to
provide the ability to render math formulas as ASCII / ANSI / Unicode.
And therefor I just set out to create my own program:

### [prettymath](http://github.com/quoteme/prettymath)

The programming was the easy part. Just write a python script that
internally parses expressions using [SymPy](https://www.sympy.org/en/index.html)
and then pretty prints them. But publishing this program with none more
than ~50 lines of code was a real pain.

1. Publish to GitHub
2. Create an account on [https://aur.archlinux.org ](https://aur.archlinux.org/)
3. Use my [.ssh/config](#ssh_config)
4. Generate an ssh key: `$ ssh-keygen -f ~/.ssh/aur`
5. Clone your future repository: `git clone ssh://aur@aur.archlinux.org/your_package_name.git`
6. Put your `PKGBUILD` in there
7. Add, Commit, Push

```bash
$ cat .ssh/config
Host aur.archlinux.org
User aur
PreferredAuthentications publickey
IdentityFile ~/.ssh/aur
```
{#ssh_config}

---

And after all this struggle, which honestly drove me to reddit because I
had no more clue what to do, I was able to install my package using the AUR:

```bash
yay -S prettymath-git
```
