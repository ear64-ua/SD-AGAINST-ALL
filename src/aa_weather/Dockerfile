FROM python:alpine
RUN pip3 install pymongo
COPY AA_Weather.py AA_Weather.py
COPY classes.py classes.py
COPY json_files/addresses.json json_files/addresses.json
COPY json_files/data.json json_files/data.json
EXPOSE 1700
#CMD ["python","AA_Weather.py"]