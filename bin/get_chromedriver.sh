# platform options: linux32, linux64, mac64, win32
PLATFORM=linux64
curl https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > package/chromedriver.zip
unzip package/chromedriver.zip -d package/bin
rm package/chromedriver.zip