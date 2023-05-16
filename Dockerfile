FROM python:3.8
COPY requirements.txt /temp/requirements.txt
COPY tenant_project /tenant_project
 
WORKDIR /tenant_project
 
EXPOSE 8000
EXPOSE 8889
 
RUN pip install --upgrade pip
RUN pip3 install -r /temp/requirements.txt
