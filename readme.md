Hello TA,

This is my implementation of the DNS server programming assignment.

Running the Scripts:

Server: python3 dnsserver.py
Client: python3 client.py


Querying:

To Query the DNS server send a message with the format: ID, host_name, query_type

For example when prompted: "pc1, google.gov , i" there is no need for spaces in between the parameters.


IMPORTANT:
  - Do not Delete cache.txt or delete it without re-creating it. The program requires this to cache dns queries.


default_local.log:
  This is a log of all queries. Shows the requests to other DNS Servers as well as directly to local default server. This will be generated each time there is a request.
