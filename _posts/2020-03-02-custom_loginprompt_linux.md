---
layout: post
title: Custom login-prompt in linux
category: posts
draft: false
---

I was asked on [reddit](https://www.reddit.com/r/archlinux/comments/fc4vqs/removing_lightdm/) how to change this:

| how to change this | to this: | or this: |
|--------------------|----------|----------|
| [![default login-prompt for Arch Linux](https://i.imgur.com/lmKNzQn.png)](https://i.imgur.com/lmKNzQn.png) | [![login-prompt for Arch Linux with screenfetch](https://i.imgur.com/3BCKr8A.png)](https://i.imgur.com/3BCKr8A.png) | [![login-prompt for Arch Linux with screenfetch](https://i.imgur.com/bXuArnx.png)](https://i.imgur.com/bXuArnx.png) |
| default login screen | a loginscreen that runs neofetch every boot (has bugs tho) | a loginscreen that runs neofetch every shutdown (information is one shutdown old, but it works better)

##### TL;DR:

How do I display Screenfetch/Neofetch before login in a TTY?

---

### Instructions

1. install [neofetch](https://github.com/dylanaraps/neofetch) or [screenfetch](https://github.com/KittyKatt/screenFetch) (`sudo pacman -S neofetch`) (I will use neofetch here, but it is the same process for screenfetch)

2. download my [neofetch_login_prompt.service](#update_login_prompt) system.d service file

3. place this file in `/etc/systemd/system/`

4. enable the script to run at boot: `sudo systemctl enable neofetch_login_prompt --now`

5. reboot! it should work now

---

### Files

#### neofetch_login_prompt {#update_login_prompt}

##### Version that updates on shutdown

{% highlight bash %}
# /etc/systemd/system/neofetch_login_prompt.service
[Util]
Description=Display Neofetch before login in a TTY

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStop=/usr/bin/env bash -ec 'neofetch > /etc/issue'

[Install]
WantedBy=multi-user.target
{% endhighlight %}

##### Version that updates at boot

{% highlight bash %}
# /etc/systemd/system/neofetch_login_prompt.service
[Util]
Description=Display Neofetch before login in a TTY

[Service]
ExecStart=/usr/bin/env bash -ec 'neofetch > /etc/issue'

[Install]
WantedBy=multi-user.target
{% endhighlight %}

