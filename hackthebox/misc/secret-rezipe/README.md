> We have launched a startup that produces soft drinks.
> We use special ingredients to make them very tasty,
> so we have a lot of protections on our files to prevent our competitors from
> copying our ideas.

> Author: **[7Rocky][author-profile]**

## The webapp

For local deployment, I had to specify a DNS server in `/etc/docker/daemon.json`:

```json
{
    "dns": ["10.83.0.1", "8.8.8.8"]
}
```

The website has 2 routes: one to the frontpage, the other to suggest (POST)
ingredients.

Suggesting ingredients

## Mixing known ingredients in

[author-profile]: https://app.hackthebox.com/users/532274
