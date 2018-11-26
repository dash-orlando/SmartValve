@echo off
title MQTT Subscribe
echo Subscribing to all available MQTT topics. Press CTRL-C to terminate.
cd C:\Users\pd3dlab\Desktop\mos1.14
mosquitto_sub -h localhost -t "#"
