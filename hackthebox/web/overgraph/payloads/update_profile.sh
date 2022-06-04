#!/bin/bash

curl -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    -b $'auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYyOWE5MzM0NzZlYWM4MDQzOTdjZjcwNiIsImVtYWlsIjoiYXBlaGV4QGdyYXBoLmh0YiIsImlhdCI6MTY1NDI5NzY4MywiZXhwIjoxNjU0Mzg0MDgzfQ.bBRCYXrb9A08CBOzyIWAdZZPZfw7ta0xvF1jyEoScEc' \
    --data-binary $'{\"operationName\":\"update\",\"variables\":{\"firstname\":\"a\",\"lastname\":\"null\",\"id\":\"629a933476eac804397cf706\",\"newusername\":\"apehex\"},\"query\":\"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {\\n  update(\\n    newusername: $newusername\\n    id: $id\\n    firstname: $firstname\\n    lastname: $lastname\\n  ) {\\n    username\\n    email\\n    id\\n    firstname\\n    lastname\\n    __typename\\n  }\\n}\"}' \
    $'http://internal-api.graph.htb/graphql'
