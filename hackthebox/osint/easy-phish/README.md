# Easy Phish

> **Customers of secure-startup.com have been recieving some very convincing
> phishing emails, can you figure out why?**

## Looking around

The website is empty, google returns nothing.

Looking for employes / subdomains with `theharvester`, returns no exact match.
Still `_dmarc.secure-startup.com` is up.

## Email spoofing controls

Hence the idea of checking whether SPF / DMARC are enabled:

```
dig -t TXT secure-startup.com
dig -t TXT _dmarc.secure-startup.com
```

Well, there are no restrictions:
- `v=spf1 a mx ?all`
- `v=DMARC1;p=none;`

Also our flag is there, one chunk in each TXT record.
