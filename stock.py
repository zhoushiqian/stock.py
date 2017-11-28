#!/usr/bin/python
#coding:utf-8
import urllib
import urllib2
import json
import os
import sys
from urllib import urlencode

map = {
	'sh': [0,1,2,4,5,3],
	'hk': [1,2,3,4,5,6],
	'sz': [0,1,2,4,5,3],
      }
	

def get_currency(scur, tcur):
# http://api.fixer.io/latest?base=CNY
	url = 'http://api.fixer.io/latest'
	params = {
		'base' : tcur
	}
	params = urlencode(params)

	f = urllib.urlopen('http://api.fixer.io/latest?base=HKD')

	fixer_call = f.read()
        f.close()
	#print content
	a_result = json.loads(fixer_call)
	if a_result:
		#print a_result
		return a_result['rates'][tcur]

def get_stock(code):
	url = 'http://hq.sinajs.cn/list=' + code
	req = urllib2.Request(url)
	res = urllib2.urlopen(req).read()
	res = res.decode('gb2312').encode('utf8')
	values = res.split('=')[1].split('"')[1].split(',')
	if code.find('hk') >= 0:
		select = 'hk'
                s_location = 0
	if code.find('sh') >= 0:
		select = 'sh'
                s_location = 1
	if code.find('sz') >= 0:
		select = 'sz'
                s_location = 2
	s_name = values[map[select][0]]
        if len(s_name) < 12:
            s_name += '   ';
	s_open = values[map[select][1]]
	s_old = values[map[select][2]]
	s_top = values[map[select][3]]
	s_bottom = values[map[select][4]]
	s_current = values[map[select][5]]
	ret = {
		'name': s_name,
		'open': s_open,
		'old': s_old,
		'top': s_top,
		'bottom': s_bottom,
		'current': s_current,
                'location':s_location
	      } 
	return ret


class stock:
    def __init__(self, code, count, price):
        self.code = code
        self.price = float(price)
        self.count = int(count)
	self.cur = 1
	self.value = 0
	self.gain = 0
	#self.day_percent = 0
	#self.gain_percent = 0
	if code.find('hk') >= 0:
		#self.cur = float(get_currency('HKD', 'CNY'))
		self.cur = cur
	val = get_stock(code)
        self.name = val['name'][0:18]
	self.open = val['open']
	self.old = float(val['old'])
	self.top = val['top']
	self.bottom = val['bottom']
	self.current = float(val['current'])
	self.day_change = self.get_day_change()
        self.gain = self.get_gain()
        self.value = self.get_value()
        self.location = val['location']

    def get_day_change(self):
	self.day_change  = round((self.current - self.old) * self.count, 2)
        self.day_percent = round((self.current - self.old) / self.old * 100, 2)
	return self.day_change

    def get_value(self):
	self.value  = round((self.current) * self.count*self.cur, 2)
	return self.value 

    def get_gain(self): 
        self.gain = round((self.current - self.price) * self.count, 2)
        self.gain_percent = round((self.current - self.price) /self.price * 100, 2)
        return self.gain

    def update(self):
        val = get_stock(self.code)
	self.top = val['top']
	self.bottom = val['bottom']
	self.current = val['current']

def parse_txt():
	global codes, all_in, debet, cur
	codes = []
	all_in = {}
        dirt = os.path.dirname(os.path.realpath(__file__))
	f = open(os.path.join(dirt, 'stocks.txt'), 'r')
	data = json.loads(f.read())
        f.close()
        cur = float(get_currency('HKD', 'CNY'))
        debet = float(data['debet']) * cur
	for s in data['stocks']:
		item = []
		codes.append(s['code'])
		item.append(int(s['count']))
		item.append(float(s['price']))
		all_in[s['code']] = item



if __name__ == '__main__':
	parse_txt()
        stocks = [] 
	print 'name \t\t open \t old \t top \t bottom \t current \t day_change \t day_percent \t gain \t\t gain_percent \t net_value'
        for code in codes:
            s = stock(code, all_in[code][0], all_in[code][1])
	    print '%s\t %s\t %s\t %s\t %s\t\t %s\t\t %s\t\t %s\t\t %s\t\t %s\t\t %s' % \
                    (s.name, s.open, s.old, s.top, s.bottom, str(s.current),\
                    str(s.day_change), str(s.day_percent), str(s.gain), str(s.gain_percent),\
                    str(s.value))
            stocks.append(s)

        print 
        day_change = 0
        gain = 0
        value = 0
        for s in stocks:
            if s.location != 0:
                day_change += s.day_change
                gain += s.gain
                value += s.value
            else:
                day_change += s.day_change * s.cur
                gain += s.gain * s.cur
                value += s.value *s.cur
        print 'day_change \t\t gain \t\t\t value'
        print '%s\t\t %s\t\t %s\t' % (day_change, gain, value)


