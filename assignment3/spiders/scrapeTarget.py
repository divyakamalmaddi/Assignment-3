import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from targetItems import *
from pipelines import *
import json
from scrapy import signals


class ScrapeTarget(CrawlSpider):
	name = "scrapeTarget"
	start_urls = [
		'http://target.com'
	]
	injection_points = {}

	rules = [
		Rule(
		    LinkExtractor(
		        canonicalize=False,
		        unique=True
		    ),
		    follow=True,
		    callback="parse"
		)
    	]
	
	def parse(self, response):
		#extract forms on the page
		forms = response.css('form')
		self.injection_points[response.url] = []
		for form in forms:
		    formJson = {}
		    method = form.xpath('@method').extract()
		    formJson['type'] = method[0] if len(method)>0 else 'GET' 
		    #print(form.xpath('@method').extract()[0])
		    formJson['params'] = []
		    inputs = form.css('input')
		    for inp in inputs:
			name = inp.xpath('@name').extract()
			typ = inp.xpath('@type').extract()
			inpJson = {'name': name[0] if len(name)>0 else '', 'type': typ[0] if len(typ)>0 else 'text'}
			formJson['params'].append(inpJson)
		    self.injection_points[response.url].append(formJson)
		
		items = []
		links = LinkExtractor(canonicalize=False, unique=True).extract_links(response)
		for link in links:
		    item = URLItem()
		    item['from_url'] = response.url
		    item['to_url'] = link.url
		    items.append(item)
		    yield scrapy.http.Request(url=link.url, callback=self.parse)

	@classmethod
	def from_crawler(cls, crawler, *args, **kwargs):
		spider = super(ScrapeTarget, cls).from_crawler(crawler, *args, **kwargs)
		crawler.signals.connect(spider.spider_opened, signals.spider_opened)
		crawler.signals.connect(spider.spider_closed, signals.spider_closed)
		return spider

	def spider_opened(self, spider):
        	print('Opening {} spider'.format(spider.name))

	def spider_closed(self, spider):
        	with open(self.name + '_phase1.json', 'a') as fp:
            		json.dump(self.injection_points, fp, sort_keys=True, indent=4)
