# Bypass

> **The Client is in full control. Bypass the authentication and read the key to
> get the Flag.**

## Interpretation

Good old `strings -n8`:

```
HTBChallange
.NETFramework,Version=v4.5.2
FrameworkDisplayName
.NET Framework 4.5.2
```

The exe keeps asking for a username / password as long as we don't satisfy it.

## Bypass :O

Judging from the name of the challenge, the idea must be to debug the exe and
short circuit the tests.

Since `Bypass.exe` has been compiled with .Net, `dnSpy` looks perfect for the
job!

Once decompiled, 2 tests stand out:

```
// Token: 0x06000002 RID: 2 RVA: 0x00002058 File Offset: 0x00000258
public static void 0()
{
	bool flag = global::0.1();
	bool flag2 = flag;
	if (flag2)
	{
		global::0.2();
	}
	else
	{
		Console.WriteLine(5.0);
		global::0.0();
	}
}
```

and the subsequent `0.2` function:

```
// Token: 0x06000004 RID: 4 RVA: 0x000020C8 File Offset: 0x000002C8
	public static void 2()
{
	string <<EMPTY_NAME>> = 5.3;
	Console.Write(5.4);
	string b = Console.ReadLine();
	bool flag = <<EMPTY_NAME>> == b;
	if (flag)
	{
		Console.Write(5.5 + global::0.2 + 5.6);
	}
	else
	{
		Console.WriteLine(5.7);
		global::0.2();
	}
}
```

We can simply run the binary in debug mode with breakpoints right before the
tests, and change the value of the flags variables to true.

This will run `Console.Write(5.5 + global::0.2 + 5.6)` and output the result to
the console... and exit before we see it!

A last breakpoint at the end of function `2` freezes the console while we copy
the flag.
