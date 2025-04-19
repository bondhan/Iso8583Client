.PHONY: run-server run-client

run-server:
	set PYTHONPATH=D:\workspace\python\iso8583client && python server\server.py

run-client:
	set PYTHONPATH=D:\workspace\python\iso8583client && python client\client.py
