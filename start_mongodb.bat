@echo off
title Farm-to-Market AI - MongoDB Server
echo ======================================================================
echo   STARTING MONGODB SERVER (Farm-to-Market AI)
echo ======================================================================
echo   Port: 27017
echo   Binding: 127.0.0.1
echo   Data Path: D:\mongodb_data (95 GB Free)
echo   Log Path:  D:\mongodb_log\mongod.log
echo ======================================================================
"C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe" --dbpath "D:\mongodb_data" --logpath "D:\mongodb_log\mongod.log" --port 27017 --bind_ip 127.0.0.1
