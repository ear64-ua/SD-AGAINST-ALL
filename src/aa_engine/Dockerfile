FROM python:alpine
RUN pip3 install kafka-python
RUN pip3 install pymongo
COPY AA_Engine.py AA_Engine.py
COPY json_files/addresses.json json_files/addresses.json
COPY json_files/conf.json json_files/conf.json
EXPOSE 1500
#CMD ["python","AA_Engine.py"]