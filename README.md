Simple USD -> RUB converter 


**Installation**
-
`docker pull tashunya/converter:v0.2`

`docker run tashunya/converter:v0.2`


**API documentation**
-

Service API works on HTTP protocol and accepts POST method only.

All responses are JSON structures.

To receive response with converted value send POST request with query parameters to

`http://localhost:8009`

**Query parameters**:

**usd**  value (int/float)

**Query parameters example**:

`{"usd": 300.00}`

**Query example**:

` curl --data '{"usd": 300.00}' --header 'Content-Type: application/json'
                                                        http://localhost:8009`

**Response parameters**:

- success 

- data 

    - requested currency
    - result currency
    - exchange rate
    - requested value
    - result value
    

     
**Response code**:

`200` 
                                                 
**Response body example**:

`{
    "success": true,
    "data": {
        "requested currency": "usd",
        "result currency": "rub",
        "exchange rate": 66.4437,
        "requested value": 300.00,
        "result value": 19933.11
    }
}`

**Error body example**:

`{
    "success": false,
    "error": {
        "code": 0,
        "status": 405,
        "name": "Method Not Allowed",
        "message": "GET method is not allowed"
    }
}`

**Error codes and description**:

0 Method Not Allowed

1 Incorrect Content-Type

2 Request parameters not in JSON format

3 Incorrect key in request parameters

4 Incorrect value in request parameters

5 Service is not available
    