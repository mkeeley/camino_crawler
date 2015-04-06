#!/usr/bin/env python

from sys import stdin
import subprocess
import time
import requests
import zipfile
import json
import os
import re
from bs4 import BeautifulSoup, SoupStrainer
from operator import itemgetter

def get_info():
	with open('../info.txt', 'r') as f:
		line = f.read().replace(' ','').rstrip('\n')
	info = {}
	for pair in line.split('\n'):
		pair = pair.split(':', 1)
		info[pair[0]] = pair[1]
	return info

def choose_assignment(session, course_id):
	course = 'https://camino.instructure.com/courses/' + course_id + '/gradebook'
	assignments = 'https://camino.instructure.com/api/v1/courses/' + course_id + '/assignment_groups'

	r = session.get(course)
	payload = {'include[]' : 'assignments', 'override_assignment_dates' : 'false' , 'page_view_id' : r.headers['x-request-context-id']}
	r = session.get(assignments, params = payload)
	dump = json.loads(r.content.split(';')[1])
	dump = dump[0]['assignments']
	
	spot = 0
	links = []
	for assignment in sorted(dump, key = itemgetter('id')):
		title = assignment['name'].lower().split('(')[0].replace(' ','')
		title = re.sub("[^a-z0-9-.]", "-", title)
		url = assignment['html_url']
		links.append((title, url))
		print '\t%d: %s' %(spot, title)
		spot += 1
	i = int(stdin.readline().strip())
	if i >= 0 and i < spot:
		print 'Assignment: %s' % links[i][0]
		# return the session (for cookies), name id, and url
		return (session, links[i][0], links[i][1])
	else:
		print 'incorrect selector'

def choose_course(session):
	r = session.get('https://camino.instructure.com/courses')
	spot = 0
	links = []
	
	soup = BeautifulSoup(r.text)
	courses = soup.find('table', {'id':'my_courses_table'})
	courses = courses.find_all('tr', {'class' : 'course-list-table-row'})
	print 'Course to download submissions from:'
	for i in courses:
		if 'TA' in str(i.contents[7]):
			title = i.contents[3].find('span')['title']
			url = ''.join(c for c in i.contents[3].find('a')['href'] if c.isdigit())
			links.append((title, url))
			print '\t%d: %s' %(spot, title)
			spot += 1
	i = int(stdin.readline().strip())
	if i >= 0 and i < spot:
		print 'Class: %s' % links[i][0]
		return choose_assignment(session, links[i][1])
	else:
		print 'incorrect selector'
	
# login to camino, response is camino homepage
def login(session):
	info = get_info()
	login = info['login_url']
	auth = info['auth_url']
	login_pay = {'Ecom_User_ID': info['login'], 'Ecom_Password': info['password']}
	auth_pay = {'SAMLResponse' : info['samlresponse']}
	headers = {'User-Agent': 'Firefox'}

	r = session.post(login, data = login_pay, headers = headers, allow_redirects = True)
	r = session.post(auth, data = auth_pay)
	return session

# download zip of all submissions for assignment,
# extract contents, and then remove zip 
def download_submission(session, name, url):
	url += '/submissions?zip=1'
	r = session.get(url)
	zip = name + '.zip'
	print url 

	r = session.get(url + '/submissions?zip=1')
	with open(zip, 'wb') as z:
		z.write(r.content)
	f = 'file ' + zip
	while "archive data" not in subprocess.check_output(f, shell=True):
		print 'Camino still packing zip file...'
		os.remove(zip)
		time.sleep(1)
		r = session.get(url + '/submissions?zip=1')
		with open(zip, 'wb') as z:
			z.write(r.content)

	z = zipfile.ZipFile(zip)
	z.extractall(name)
	rename(name)
	os.remove(zip)
	return session

# rename all unzipped files, remove excess timestamps and spaces
def rename(dir):
	for f in os.listdir(dir):
		tmp = re.split("[(--)|_]", f)
		tmp = '_'.join(filter(lambda a: not (a.isdigit() or not a), tmp))
		tmp = os.path.join(os.getcwd(), dir, tmp)
		f = os.path.join(os.getcwd(), dir, f)
		os.rename(f, tmp)
		
if __name__ == "__main__":
	session = requests.session()
	session = login(session)
	session, name, url = choose_course(session)
	session = download_submission(session, name, url)
