#!/usr/bin/python

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import shutil
import requests
import xlsxwriter
import getpass

class App():

	def __init__(self, username, password, target_username, path ):
		self.username = username
		self.password = password
		self.target_username = target_username
		self.path = path
		self.error_flag = False
		self.driver = webdriver.Chrome(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'), 'chromedriver'))
		self.driver.get('https://www.instagram.com')
		self.path = os.path.join(self.path, target_username)
		time.sleep(3)
		if(self.error_flag == False):
			self.log_in()
		
		if(self.error_flag == False):
			self.open_target_profile()
		
		if(self.error_flag == False):
			self.scroll_target_profil()
		
		if(self.error_flag == False):
			if not os.path.exists(self.path):
				os.makedirs(self.path)
			self.download_target_image()
							
		self.driver.close()

	def caption_in_excel_file(self, images, caption_path):
		workbook = xlsxwriter.Workbook(caption_path + '/captions.xlsx')
		worksheet = workbook.add_worksheet()
		row = 0
		worksheet.write(row, 0, 'Image Name')
		worksheet.write(row, 1, 'Caption')
		row += 1
		for image in images:
			caption = image.get('alt')
			file_name = image.get('src')
			file_name = file_name.split('/')
			file_name = file_name[-1]
			worksheet.write(row, 0, file_name)
			worksheet.write(row, 1, caption)
			row += 1
		workbook.close()

	def download_captions(self, images):
		if not os.path.exists(os.path.join(self.path, 'captions')):
			os.makedirs(os.path.join(self.path, 'captions'))
		caption_path = os.path.join(self.path, 'captions')
		self.caption_in_excel_file(images, caption_path)

	def download_target_image(self):
		soup = BeautifulSoup(self.driver.page_source, 'lxml')
		images = soup.findAll('img', src=True)
		print('Images found : ', len(images))
		self.download_captions(images)
		count = 1
		image_links = [image.get('src') for image in images]
		for link in image_links:
			file_name = link.split('/')
			file_name = file_name[-1]
			path = os.path.join(self.path, file_name)
			try:
				response = requests.get(link, stream=True)
			except Exception:
				print("image link not found")
			print("Downloading image :", str(count))
			count += 1
			try:
				with open(path, 'wb') as fimage:
					for data in response:
						fimage.write(data)

			except Exception:
				print("Something went wrong while downloading", file_name)
			time.sleep(1)

	def scroll_target_profil(self):
		try:
			post = self.driver.find_element_by_xpath("//span[@class='_bkw5z']").text
			post = str(post).replace(',' , '')
			self.total_post = 0
			self.total_post = int(post)
			if(self.total_post > 12):
				self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(1)
				try:
					load_button = self.driver.find_element_by_link_text('Load more')
					load_button.click()
					time.sleep(3)
					no_of_scroll = (self.total_post - 12)
					no_of_scroll = (no_of_scroll)/12 + 2
					try:
						for value in xrange(no_of_scroll):
							self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
							time.sleep(2)
					except Exception :
						print("Something went wrong while scrolling the target profile")
						self.error_flag = True
				except Exception :
					print("Couldn't find Load more button")
					self.error_flag = True
		except Exception:
			print("Couldn't find the post")
			self.error_flag = True
	
	def open_target_profile(self):
		try:
			self.driver.find_element_by_xpath("//input[@placeholder='Search']").send_keys(self.target_username)
			time.sleep(1)
			self.driver.get(self.driver.current_url + self.target_username + '/')
			time.sleep(5)
		except Exception :
			print("Couldn't find the target profile")
			self.error_flag = True

	def log_in(self):
		try:
			log_in_button = self.driver.find_element_by_link_text('Log in')
			log_in_button.click()
			
			try:
				username_field = self.driver.find_element_by_xpath("//input[@placeholder='Username']")
				username_field.send_keys(self.username)
				password_field = self.driver.find_element_by_xpath("//input[@placeholder='Password']")
				password_field.send_keys(self.password)
				password_field.submit()
				time.sleep(5)
			except Exception:
				print("Something went wrong login credentials, Please Try again with correct credentials")
				self.error_flag == True

		except Exception:
			print('Login button not found')
			self.error_flag = True

if __name__ == '__main__':
	username = raw_input('Enter Your Insta username: ')
	password = getpass.getpass('Enter Password: ')
	target_username = raw_input('Enter target username: ')
	path = os.path.join(os.path.expanduser('~'), 'Downloads')
	print "Enter the path by default is your Download Directory Do you want to enter y/n"
	y = raw_input()
	if y.upper() == 'Y':
		path = raw_input('Enter the path')
	app = App(username, password, target_username, path)
	