FROM python:alpine
RUN pip3 install pymongo
RUN pip3 install flask flask-restful
COPY AA_Registry.py AA_Registry.py
COPY json_files/addresses.json json_files/addresses.json
COPY secrets secrets
COPY classes.py classes.py
#EXPOSE 1600