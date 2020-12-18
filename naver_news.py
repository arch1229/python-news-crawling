from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_replys(url, imp_time=2, delay_time=0.1):
    #웹 드라이버
    driver = webdriver.Chrome()
    driver.implicitly_wait(imp_time)
    driver.get(url)
    # 댓글 창 들어가기    
    driver.find_element_by_css_selector('span.lo_txt').click()
    
    url = driver.current_url #현재 url
    title = driver.find_element_by_css_selector('#articleTitle').text # 기사 제목

    # 더보기 계속 클릭하기
    while True:
        try:
            driver.find_element_by_css_selector('span.u_cbox_page_more').click()
            time.sleep(delay_time)
        except:
            break

    
    list_elements = driver.find_elements_by_class_name('u_cbox_area')
    
    reply_data = []
    for element in list_elements:
        nick = element.find_element_by_class_name('u_cbox_nick').text
        date = element.find_element_by_class_name('u_cbox_date').text
        content = element.find_element_by_class_name('u_cbox_contents').text
        try:
            data_param = element.find_element_by_class_name('u_cbox_btn_totalcomment').get_attribute('data-param')
            objectId = data_param[data_param.index("objectId:'")+len("objectId:'"):data_param.index("',commentNo")]
            commentNo = data_param[data_param.index("',commentNo:")+len("',commentNo:"):data_param.index(",mine")]
            nick_url = "#user_comment_{}_{}".format(commentNo, objectId)
        except:
            content = '삭제된 댓글'
            nick_url = ''
        reply_data.append([nick, date, content, nick_url])
    
    driver.quit()
    return reply_data, url, title



if __name__ == '__main__':
    from datetime import datetime
    urls = [
            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=009&aid=0004553461&date=20200408&type=1&rankingSectionId=100&rankingSeq=1',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=025&aid=0002990468&date=20200406&type=1&rankingSectionId=100&rankingSeq=2',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=028&aid=0002492360&date=20200406&type=1&rankingSectionId=100&rankingSeq=3',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=003&aid=0009798864&date=20200406&type=1&rankingSectionId=100&rankingSeq=4',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=023&aid=0003521057&date=20200406&type=1&rankingSectionId=100&rankingSeq=5',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=277&aid=0004656816&date=20200406&type=1&rankingSectionId=100&rankingSeq=6',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=001&aid=0011526223&date=20200406&type=1&rankingSectionId=100&rankingSeq=7',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=028&aid=0002492332&date=20200406&type=1&rankingSectionId=100&rankingSeq=8',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=081&aid=0003079951&date=20200406&type=1&rankingSectionId=100&rankingSeq=9',
#            'https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=469&aid=0000484928&date=20200406&type=1&rankingSectionId=100&rankingSeq=10'
            ]
    for rank, url in enumerate(urls):
        rank += 1
        start = datetime.now()
        reply_data, url, title = get_replys(url)
        col = ['작성자','날짜','댓글','개인URL']
        data_frame = pd.DataFrame(reply_data, columns=col)
        title = title.replace('[','').replace(']','').replace(':','').replace('*','').replace('?','').replace('/','').replace('\\','')
        data_frame.to_excel('naver_news_0407_rank{}.xlsx'.format(rank),sheet_name=title[:15], startrow=0, header=True)
        end = datetime.now()
        print(rank, "기사 뽑는데 걸린 시간:", end-start)