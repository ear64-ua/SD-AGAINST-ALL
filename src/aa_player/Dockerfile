FROM python:alpine
RUN pip3 install kafka-python
RUN pip3 install requests
COPY AA_Player.py AA_Player.py
COPY json_files/addresses.json json_files/addresses.json
EXPOSE 8881
#CMD ["python","AA_Player.py"]