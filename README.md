# sitemonitor
This will monitor a URL for changes and then text an alert via Twilio when a change is detected.

A simple python script that will grab a URL and hash it every 90 seconds. If that hash changes it will send an sms via Twilio to a specified user.

The script will provide periodic updates and an alert when an SMS is sent.
