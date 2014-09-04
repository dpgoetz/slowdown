Slow stuff down:

If you want to slow down a swift object-server you can add this to
your object-server configs:

[pipeline:main]
pipeline = slowdown object-server


[filter:slowdown]
use = egg:slowdown#slowdown
data_file = /tmp/oslowdown1

and then create a file  /tmp/oslowdown1 containing:

{"slowdown_percentage": 90, "account": "all",
 "time_to_sleep": 5, "bytes_to_read": 45}

With that config 90% of requests to the obj server will feed out 45 bytes
and then sleep for 5 seconds before feeding out the rest of the file.

You can restrict the account to a specific account by changing "all" to
the account hash.

You can update the file and the changes will be updated without a
service reload within 10 seconds.

You can put this middleware in the obj, container, or account servers.
