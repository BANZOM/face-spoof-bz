workers = 4 

# bind = "unix:/tmp/gunicorn.sock" 
bind = "0.0.0.0:5001"  # Direct access

timeout = 120

accesslog = "-"  # STDOUT
errorlog = "-"   # STDERR
capture_output = True

limit_request_line = 4094
limit_request_fields = 100