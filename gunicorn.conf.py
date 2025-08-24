import os


# configuration file for the Gunicorn web server

bind = f"0.0.0.0:{os.getenv('PORT', '9000')}"

workers = 3

# restart worker after
timeout = 120

# wait for requests
keepalive = 5

loglevel = "info"

# send error logs to stderr
errorlog = "-"

# send access logs to stdout
accesslog = "-"

# funnel application prints into error log
capture_output = True