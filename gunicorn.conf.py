# configuration file for the Gunicorn web server

bind = "0.0.0.0:9000"

workers = 3

# restart worker after
timeout = 120

# wait for requests
keepalive = 5

loglevel = "debug"

# send error logs to stderr
errorlog = "-"
