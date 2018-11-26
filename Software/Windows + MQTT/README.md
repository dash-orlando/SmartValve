# Mosquitto MQTT Broker for Windows
1) Extract and CD into directory from the command line.

2) Run mosquitto service by executing: mosquitto.

3) You can monitor **ALL** incoming traffic by opening another command
prompt and executing: mosquitto_sub -h localhost -t "#"

### IMPORTANT NOTE:
Two batch files are provided: mqtt_autorun.bat and mqtt_subscribe.bat

1) mqtt_autorun.bat is to be used to run the MQTT server on system boot. Simply modify
the script to point to where mos1.14 was extracted and then place a shortcut of the bat
file in the startup directory by typing *shell:startup* in a *Run* window.

2) mqtt_subscribe.bat is currently used to subscribe to **ALL** the topics that are available on
the server. Again, modify the script to point to where mos1.14 was extracted.