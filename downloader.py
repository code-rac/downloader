from PIL import Image
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, argparse, sys, time, threading, time, traceback, base64, io, re, os, requests

keyword = raw_input('enter keyword:')

def save_image(ext, data):
	i = 0
	image = Image.open(io.BytesIO(data))
	path = '%s/%d.%s' % (keyword, i, ext)
	while os.path.exists(path):
		i += 1
		path = '%s/%d.%s' % (keyword, i, ext)
	image.save(path)

def plain_image(src):
	match = re.match(r'^data\:image/(?P<ext>[^;]+);[^,]+,(?P<data>.*)$', src)
	if not match:
		return False
	match = match.groupdict()
	save_image(match['ext'], base64.b64decode(match['data']))
	return True

def encrypted_image(src):
	r = requests.get(src)
	ext = r.headers['Content-Type'].split('/')[1]
	data = r.content
	save_image(ext, data)

def main():

	driver = webdriver.Firefox()
	wait = WebDriverWait(driver, 10)

	driver.get('https://images.google.com/')
	element = wait.until(EC.presence_of_element_located((By.XPATH, '//INPUT[@id=\"lst-ib\"]')))
	element.send_keys(keyword)
	element = wait.until(EC.presence_of_element_located((By.XPATH, '//BUTTON[@aria-label=\"Google Search\"]')))
	element.click()
	time.sleep(5)
	element = wait.until(EC.presence_of_element_located((By.XPATH, '//A[.=\"Tools\"]')))
	element.click()
	element = wait.until(EC.presence_of_element_located((By.XPATH, '//DIV[.=\"Size\"]')))
	element.click()
	element = wait.until(EC.presence_of_element_located((By.XPATH, '//A[.=\"Large\"]/..')))
	element.click()

	for i in range(5):
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(3)

	elements = driver.find_elements_by_xpath('//IMG[@alt="Image result for %s"]' % keyword)

	print 'found:', len(elements), 'images'

	if not os.path.exists(keyword):
		os.mkdir(keyword)

	for element in elements:
		src = element.get_attribute('src')
		if not src:
			continue

		if not plain_image(src):
			encrypted_image(src)

if __name__ == '__main__':
	main()