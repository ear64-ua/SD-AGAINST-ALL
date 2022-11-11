FROM python:alpine
RUN pip3 install kafka-python
COPY AA_NPC.py AA_NPC.py
COPY classes.py classes.py
COPY json_files/addresses.json json_files/addresses.json
EXPOSE 4881
#CMD ["python","AA_NPC.py"]