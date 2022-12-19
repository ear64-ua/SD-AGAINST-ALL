FROM python:alpine
RUN pip3 install kafka-python
RUN pip3 install pymongo
RUN pip3 install requests
RUN pip3 install cryptography
COPY AA_Engine.py AA_Engine.py
COPY json_files/addresses.json json_files/addresses.json
COPY json_files/cities.json json_files/cities.json
COPY json_files/config.json json_files/config.json
EXPOSE 1500
#CMD ["python","AA_Engine.py"]