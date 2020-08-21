# Web API

## Configuration

Configuraton is a simple key/value pair dictionary.  Obtaining the dictionary
is one request:

```bash
curl --request GET http://localhost:5000/api/v1/config
```

You can also request a specific configuration:

```bash
curl --request GET http://localhost:5000/api/v1/config/thermostat.delta
```

To make a change to a setting, use PUT:

```bash
curl --header "Content-Type: application/json" \
    --request PUT --data '{"foo": "bar"}' \
    http://localhost:5000/api/v1/config
```


## References

I used the guide below as a reference on how to put the API together.

https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design

Some summaries of the above:

* *GET* retrieves a representation of the resource at the specified URI. The 
body of the response message contains the details of the requested resource.
* *POST* creates a new resource at the specified URI. The body of the request 
message provides the details of the new resource. Note that POST can also be 
used to trigger operations that don't actually create resources.
* *PUT* either creates or replaces the resource at the specified URI. The body 
of the request message specifies the resource to be created or updated.
* *PATCH* performs a partial update of a resource. The request body specifies 
the set of changes to apply to the resource
* *DELETE* removes the resource at the specified URI.

For return codes, I found the following helpful:

https://restfulapi.net/http-status-codes/
