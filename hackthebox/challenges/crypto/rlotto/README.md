> Are you ready to win lottery? Guess the Random Lotto Numbers.
> It's TIME you become a millionaire.

> Author: **[4lpha5ec][author-profile]**

## The lottery

The service picks 5 "random" values from 1 to 90, the first "extraction".
Then it asks for the next five numbers.

The pseudo random number generator is seeded on the server time:

```python
seed = int(time.time())
random.seed(seed)
```

And for each extraction:
- the numbers are distinct
- the seed is unchanged
- the numbers must be given in the same order

## Guessing

The seed is taken right after opening the session.

So we can save the timestamp of the request on our side: the server is bound to
take a seed very close to ours.

```bash
date +%s && ncat 139.59.174.182 30518
```

Validating a seed can be performed by comparing a local extraction to the one
provided by the server.

```python
def pick(count: int=5):
    extracted = []
    while len(extracted) < count:
        r = random.randint(1, 90)
        if (r not in extracted):
            extracted.append(r)
    return extracted
```

## Bruteforcing

The server seed should be close to ours since the ping is very low:

```bash
ncat -v -z 139.59.174.182 30518
# Ncat: Version 7.91 ( https://nmap.org/ncat )
# Ncat: Connected to 139.59.174.182:30518.
# Ncat: 0 bytes sent, 0 bytes received in 0.12 seconds.
```

The ping is 0.12s so 0.06s one-way: there's 94% chance that the server sees our
request in the same second it was sent.

Adding the overhead of the service and other disturbance there's still a high
chance that our time / seed guess is right.

**Yet** trying the neighbooring seeds didn't work for me! 

So I checked my `hwclock` and made sure that timestamps don't depend on
timezones. Somehow my local time and the server time differ.

No problem, we'll just try all the possible seeds starting from our local time:

```python
def potential_seeds(guess: int, days: int=10):
    s = 0
    while s < days * 86400:
        yield guess + s
        yield guess - s
        s += 1 

def bruteforce(target: str, guesses: list):
    for seed in guesses:
        random.seed(seed)
        if serialize(pick(5)) == target:
            return seed
    return -1
```

There was somehow a 64s delay?!

> `HTB{n3v3r_u53_pr3d1c74bl3_533d5_1n_p53ud0-r4nd0m_numb3r_63n3r470r}`

[author-profile]: https://app.hackthebox.com/users/141340
