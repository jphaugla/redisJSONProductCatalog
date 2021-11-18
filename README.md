# redisPythonProductCatalog
A simple product catalog solution based on icecat files
## Initial project setup
Get this github code
```bash 
get clone https://github.com/jphaugla/redisPythonProductCatalog.git
```
Two options for setting the environment are given:  
  * run with docker-compose using a flask and redis container
  * installing for mac os
docker-compose is much easier and is main method documented here
## docker compose startup
```bash
docker-compose up -d --build
```
## Code and File discussion
This is an implementation of a product Catalog using data download from
 [icecat](https://iceclog.com/open-catalog-interface-oci-open-icecat-xml-and-full-icecat-xml-repositories/)

### Download the datafiles to the data subdirectory
To download the datafiles, a free login id from icecat is required
Once effectively logged in to icecat need to retrieve these two files
  * https://data.Icecat.biz/export/freexml/refs/CategoriesList.xml.gz
  * https://data.icecat.biz/export/freexml/nl/files.index.xml.gz

### unzip data files
The data file directory is mapped 
using docker-compose volume to /data in flask container
```bash
cd data
unzip files.index.csv.zip
gunzip CategoriesList.xml.gz
```
### load categories
The redis node and port can be changed. The python code uses 2 environment variable REDIS_SERVER and REDIS_PORT.  The default is REDIS_SERVER=redis and REDIS_PORT=6379
```bash
docker exec -it flask bash -c "python categoryImport.py"
```
### load Products
This can take quite a long time (maybe 35 minutes)
The redis node and port can be changed. The python code uses 2 environment variable REDIS_SERVER and REDIS_PORT.  The default is REDIS_SERVER=redis and REDIS_PORT=6379
```bash
docker exec -it flask bash -c "python productImport.py"
```
  * THIS IS HOW to start flask app server
  * However, it is already running as part of the flask container
 ```bash
#  docker exec -it flask bash -c "python appy.py"
 ```
  * run API tests
Make sure to use *bash* as *zsh* has issues with the curl command 
Note:  there are multiple API tests in the file but only one should be run at a time
So, the tests not to be run should be commented out.
 ```bash
./scripts/sampleput.sh
```
##  installing on mac
1. install xcode
2. install homebrew
```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
3. verify homebrew
```bash
brew doctor
```
4. install python
```bash
brew install python
```
5. install redis-py
```bash
pip install redis
```
6.  install flask
```bash
pip install flask
```
6. clone repository
```bash
git clone https://github.com/jphaugla/redisPythonProductCatalog.git
```
7. install redis
```bash
brew install redis
```
8. start redis 
	redis-server /usr/local/etc/redis.conf

