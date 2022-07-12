import smtplib

try:
    server = smtplib.SMTP('127.0.0.1', 25)
    server.ehlo()
    server.sendmail("kyle@writer.htb", "john@writer.htb", """Subject: heyhey\n\noops""")
except Exception as e:
    print(e)
finally:
    server.quit()
