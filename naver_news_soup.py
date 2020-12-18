# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 10:34:17 2020

@author: sungtak
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def get_replys(url, article_date, rank, imp_time=2, delay_time=0.1):
    driver = webdriver.Chrome()
    driver.implicitly_wait(imp_time)
    driver.get(url)
    
    # 댓글 창 들어가기
    driver.find_element_by_css_selector('span.lo_txt').click()
    # 현재 url 가져오기
    url = driver.current_url
    # 기사 제목
    title = driver.find_element_by_css_selector('#articleTitle').text
    
    # 댓글 더보기 클릭
    while True:
        try:
            driver.find_element_by_css_selector('span.u_cbox_page_more').click()
            time.sleep(delay_time)
        except:
            break
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    cboxs = soup.find_all(name='div', attrs={'class' : 'u_cbox_area'})
    
    reply_data = []
    
    for cbox in cboxs:
        nick = cbox.find('span', attrs={'class':'u_cbox_nick'}).text
        date = cbox.find('span', attrs={'class':'u_cbox_date'}).text
        try:
            content = cbox.find('span', attrs={'class':'u_cbox_contents'}).text
            data_param = cbox.find('button')['data-param']
            # 개인 URL 문자열 처리
            objectId = data_param[data_param.index("objectId:'")+len("objectId:'"):data_param.index("',commentNo")]
            commentNo = data_param[data_param.index("',commentNo:")+len("',commentNo:"):data_param.index(",mine")]
            nick_url = "#user_comment_{}_{}".format(commentNo, objectId)
            
            # 개인화된 데이터 가져오기
            
            driver.get(url)
            driver.get(url+nick_url)
            # 닉네임
            meta_nick = driver.find_element_by_class_name('u_cbox_userinfo_meta_nickname').text
            # 가입 날짜
            meta_date = driver.find_element_by_class_name('u_cbox_userinfo_meta_date').text
            
            meta_data = driver.find_elements_by_class_name('u_cbox_userinfo_totalstats_column')
            # 현재 댓글
            meta_comment = meta_data[0].find_element_by_class_name('u_cbox_userinfo_totalstats_value').text
            # 현재 답글
            meta_reply = meta_data[1].find_element_by_class_name('u_cbox_userinfo_totalstats_value').text
            # 받은 공감
            meta_sympathy = meta_data[2].find_element_by_class_name('u_cbox_userinfo_totalstats_value').text
            
            laststats = driver.find_elements_by_class_name('u_cbox_userinfo_laststats_dataitem')
            # 최근 30일 작성
            last_comment = laststats[0].find_element_by_tag_name('em').text
            # 최근 30일 삭제
            last_delete = laststats[1].find_element_by_tag_name('em').text
            # 최근 30일 받은공감
            last_sympathy = laststats[2].find_element_by_tag_name('em').text
        except:
            nick_url = ''
            meta_nick = ''
            meta_date = ''
            meta_comment = ''
            meta_reply = ''
            meta_sympathy = ''
            last_comment = ''
            last_delete = ''
            last_sympathy = ''
            try:
                content = cbox.find('span', attrs={'class':'u_cbox_cleanbot_contents'}).text
            except:
                try:
                    content = cbox.find('span', attrs={'class':'u_cbox_delete_contents'}).text
                except:
                    content = '기타 이유로 삭제된 댓글입니다'
        reply_data.append([article_date, rank, nick, date, content, nick_url, meta_nick, meta_date, meta_comment, meta_reply, meta_sympathy, last_comment, last_delete, last_sympathy])

    driver.quit()
    return reply_data, url, title

def top10(start_url):
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get(start_url)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    article_list = soup.find_all('div', attrs={'class':'ranking_text'})
    urls = []
    for rank, article in enumerate(article_list):
        if rank == 10: break
        urls.append('https://news.naver.com' + article.find('a', attrs={'class':'nclicks(rnk.gov)'})['href'])
    
    driver.quit()
    return urls

def get_all(article_date):
    start_url = 'https://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId=100&date=2020{}'.format(article_date)
    urls = top10(start_url)
    for rank, url in enumerate(urls):
        start = datetime.now()
        rank += 1
        reply_data, url, title = get_replys(url, article_date, rank)
        col = ['기사날짜','순위','작성자','작성 날짜','댓글 내용','개인URL','닉네임','가입 날짜','총 댓글 수','총 답글 수','총 받은공감 수','최근 30일 작성','최근 30일 삭제','최근 30일 받은공감']
        data_frame = pd.DataFrame(reply_data, columns=col)
        title = title.replace('[','').replace(']','').replace(':','').replace('*','').replace('?','').replace('/','').replace('\\','').replace('"','').replace("'",'')
        data_frame.to_excel('naver_news_{}_rank{}.xlsx'.format(article_date,rank),sheet_name=title[:15], startrow=0, header=True)
        end = datetime.now()
        print(rank, "기사 뽑는데 걸린 시간:", end-start)

if __name__ == '__main__':    
    dates = ['0411', '0412', '0413']
    for article_date in dates:
        get_all(article_date)