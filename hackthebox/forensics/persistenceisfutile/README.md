> Hackers made it onto one of our production servers :sweat_smile:. We've
> isolated it from the internet until we can clean the machine up. The IR team
> reported eight difference backdoors on the server, but didn't say what they
> were and we can't get in touch with them. We need to get this server back into
> prod ASAP - we're losing money every second it's down. Please find the eight
> backdoors (both remote access and privilege escalation) and remove them. Once
> you're done, run /root/solveme as root to check. You have SSH access and sudo
> rights to the box with the connections details attached below.

> Author: **[0xdf][author-profile]**

## Monitoring the system

The ssh credentials for the box are:

```
username: user
password: hackthebox
```

The initial run of `/root/solveme` returns:

[author-profile]: https://app.hackthebox.eu/users/4935
