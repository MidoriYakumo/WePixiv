#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:37:35 2015
Project	:Python-Project
Version	:0.0.1
@author	:MidoriYakumo

"""

import os, sys, time
import shutil
# pickle

# WeCase API
API_KEY = "1011524190"
API_SECRET = "83822a8addf08cbcdaca75c76bec558a"
REDIRECT_URI = 'https://api.weibo.com/oauth2/default.html'
TOKEN_FILE = os.getenv('HOME')+'/.weibo_token'
IMG_TMPFILE = '/tmp/weiboImage_%s'
PIXIV_BASEURL = 'http://pixiv.net/member_illust.php?mode=medium&illust_id='
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MiB

import re

from weibo import Client

def initClient(forceRefreshToken = False):
	try:
		if forceRefreshToken: raise BaseException()
		token = eval(open(TOKEN_FILE, 'r').read())
		c = Client(API_KEY, API_SECRET, REDIRECT_URI, token)
	except BaseException:
		c = Client(API_KEY, API_SECRET, REDIRECT_URI)
		#print(c.authorize_url)
		#code = input('Input code:')
		code = os.popen("kdialog --inputbox 'Open the URL and paste back the code' '"+ c.authorize_url +"'").read().rstrip()
		print(code)
		try:
			c.set_code(code)
		except BaseException as e:
			print('Error:', e)
			os.popen('notify-send -i facebook "微博发图:init" "Error:%s"' % (e))
#			c = initClient(True)
			c = None
		else:
			f = open(TOKEN_FILE, 'w')
			f.write(repr(c.token))
			f.close()
	return c

#朝ノよー - 音ノ木坂学院2月14日。 (48784184@630924)[バレンタイン ラブライブ! 西木野真姫 2月14日 ゔぇえ 下駄箱 ツンデレ ]{Photoshop SAI}(_)
def uploadPixivImage(c, ffn):

	try:
		tn = IMG_TMPFILE %  time.time()

		shutil.copy2(ffn, tn)
		print((ffn, tn))

#		cp_exit = os.popen( ("zsh -c \"cp '%s' '%s'\"") % (fn,tn)).read()
#		if cp_exit.split(): print(cp_exit)

		fn = os.path.basename(os.path.splitext(ffn)[0])

		disc = ""
		p_id = re.search('\(\d+@\d+\)', fn).span()
		disc += fn[0:p_id[0]]

		p_tags = re.search('\[.*\]', fn).span()
		if p_tags[1]-p_tags[0]-2:
			disc += '#' + '# #'.join(fn[p_tags[0]: p_tags[1]].split(' '))[1:-2]

		p_tools = re.search('\{.*\}', fn).span()
		if p_tools[1]-p_tools[0]-2:
			disc += 'Tools: #' + '# #'.join(fn[p_tools[0]: p_tools[1]].split(' '))[1:-1] + '#'

		s_page = fn[p_tools[1]:]
		if len(s_page)>3:
			disc += ' P' + fn[p_tools[1]+1:-1].replace('_', '/')

		p_iid = re.search('\(\d+', fn[p_id[0]: p_id[1]]).span()
		disc += ' ' + PIXIV_BASEURL + fn[p_id[0]+1: p_id[0] + p_iid[1]]


		print('Uploading:%s\nAs:%s' % (fn, disc))
		f = open(tn, 'rb')
		c.post('statuses/upload', status=disc, pic=f)
	except BaseException as e:
		print('Error:', e)
		os.popen('notify-send -i facebook "微博发图:err:%s" "%s"' % (e, fn))
		if 'token' in str(e):
		#if 'token' in e.args[0]:
			c = initClient(True)
			uploadPixivImage(c, ffn)
	else:
		print('Done')
		os.popen('notify-send -i facebook "微博发图:done" "%s"' % (fn))
		f.close()
		os.remove(tn)



c = initClient()
for fn in sys.argv[1:]:
	uploadPixivImage(c, fn)
	time.sleep(15)
#uploadPixivImage('/tmp/tmp-macrobull/0.jpg')
