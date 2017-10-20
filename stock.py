#!/usr/bin/python
#coding:utf-8
import urllib
import urllib2
import json
from urllib import urlencode

'''
codes = ['rt_hk00392', 'rt_hk03383', 'rt_hk02607', 'sz002008']
all_in = {
		'rt_hk00392': [500, 41.6],
		'rt_hk03383': [4000, 9.1],
		'rt_hk02607': [500, 20.577],
		'sz002008'  : [400,45.42]
	 }
'''
stock_debets = {'hk': 22714.71}
	
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
	if code.find('sh') >= 0:
		select = 'sh'
	if code.find('sz') >= 0:
		select = 'sz'
	s_name = values[map[select][0]]
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
		'current': s_current
	      } 
	return ret

def calculate_change(code):
	val = get_stock(code)
	change = float(val['current']) - float(val['old'])
	return (change * all_in[code][0], change/float(val['old'])*100)

def day_change(code):
	cur = 1
	if code.find('hk') >= 0:
		cur = get_currency('HKD', 'CNY')
	return calculate_change(code)[0] * float(cur)

def orgin_money(code):
	cur = 1
	if code.find('hk') >= 0:
		cur = get_currency('HKD', 'CNY')
	val = get_stock(code)
	change = all_in[code][1]
        return change *all_in[code][0]*float(cur)

def current_money(code):
	cur = 1
	if code.find('hk') >= 0:
		cur = get_currency('HKD', 'CNY')
	val = get_stock(code)
	change = float(val['current']) - all_in[code][1]
  	return change *all_in[code][0]*float(cur)

def parse_txt():
	global codes, all_in
	codes = []
	all_in = {}
	f = open(os.path.join(os.path.abspath('.', 'stocks.txt'), 'r')
	data = json.loads(f.read())
	for stock in data['stocks']:
		item = []
		codes.append(stock['code'])
		item.append(int(stock['count']))
		item.append(float(stock['price']))
		all_in[stock['code']] = item

def calculate_debet():
        debets=0
        for key in stock_debets:
            cur=1
            if key.find('hk') >= 0:
		cur = get_currency('HKD', 'CNY')

            debets += stock_debets[key]*float(cur)
            return debets

def print_stock(code):
	val = get_stock(code)
	print '%s\t %s\t %s\t %s\t %s\t\t %s\t\t %d \t\t %f' %  (val['name'], val['open'], val['old'], val['top'], val['bottom'], val['current'], calculate_change(code)[0], calculate_change(code)[1])

if __name__ == '__main__':
	parse_txt()
	print 'name \t\t open \t old \t top \t bottom \t current \t change \t percent'
	for i in codes:
		print_stock(i)

	sum = 0
	for i in codes:
		sum += day_change(i)
	print "today_gain CNY %f" % (sum)
	
	sum = 0
	for i in codes:
		sum += current_money(i)
	print "total_gain CNY %f" % (sum)


	for i in codes:
		sum += orgin_money(i)
	print "net_mony CNY %f" % (sum - calculate_debet())
