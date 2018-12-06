#fang_test herokuapp
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from firebase import firebase
from linebot.models import (
    SourceUser,SourceGroup,SourceRoom,LeaveEvent,JoinEvent,
    TemplateSendMessage,PostbackEvent,AudioMessage,LocationMessage,
    ButtonsTemplate,LocationSendMessage,AudioSendMessage,ButtonsTemplate,
    ImageMessage,URITemplateAction,MessageTemplateAction,ConfirmTemplate,
    PostbackTemplateAction,ImageSendMessage,MessageEvent, TextMessage, 
    TextSendMessage,StickerMessage, StickerSendMessage,DatetimePickerTemplateAction,
    CarouselColumn,CarouselTemplate
)
from imgurpython import ImgurClient
from config import *
import re
from bs4 import BeautifulSoup as bf
import requests
import random
import os,tempfile

app = Flask(__name__)
#imgur上傳照片
client_id = os.getenv('client_id',None)
client_secret = os.getenv('client_secret',None)
album_id = os.getenv('album_id',None)
access_token = os.getenv('access_token',None)
refresh_token = os.getenv('refresh_token',None)
client = ImgurClient(client_id, client_secret, access_token, refresh_token)
url = os.getenv('firebase_bot',None)
fb = firebase.FirebaseApplication(url,None)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN',None))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET', None))

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body,signature)
    except LineBotApiError as e:
        print("Catch exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("ERROR is %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)
    return 'OK'


import json
from selenium import webdriver
def get_shop_rank(shop_name):
    temp = shop_name
    print(temp)
    url = 'https://www.google.com.tw/search?q='+temp+'&rlz=1C1EJFA_enTW773TW779&oq='+temp+'&aqs=chrome..69i57j0j69i60l2j69i59l2.894j0j7&sourceid=chrome&ie=UTF-8'
    res = requests.get(url)
    soup = bf(res.text,'html.parser')
    n = soup.find_all('div',{'class':"IvtMPc"})
    name = []
    rank = []
    for t in n:
        name.append(t.find_all('span')[0].text)
        rank.append(t.find_all('span')[1].text)
    return name,rank

def img_describe(text,img_id):#紀錄describe 把firebase裡面describe修改
    t = fb.get('/pic',None)
    tex = text[1:]
    patterns = str(img_id)+'.*'
    if re.search(patterns,text.lower()):
        count = 1
        for key,value in t.items():
            if count == len(t):#取得最後一個dict項目
                data2 = {'describe': str(tex), 'id': value['id'], 'user': value['user']}
                fb.put(url+'/pic/',data=data2,name=key)
            count+=1
        return 'Image紀錄程功'
def get_image(text):
    if len(text) <4:
        return None
    else:
        tex = text[3:]
        t = fb.get('/pic',None)
        for key,value in t.items():
            if value['describe'] == tex:
                
                client = ImgurClient(client_id, client_secret)
                images = client.get_album_images(album_id)
                img_id = int(value['id'])-1  #從firebase取出來是字串
                url = images[img_id].link
                image_message = ImageSendMessage(
                        original_content_url=url,
                        preview_image_url=url
                )
                return image_message
def job_seek():
    target_url = 'https://www.104.com.tw/jobbank/custjob/index.php?r=cust&j=503a4224565c3e2430683b1d1d1d1d5f2443a363189j48&jobsource=joblist_b_relevance#info06'
    print('Start parsing appleNews....')
    rs = requests.session()
    res = rs.get(target_url)
    res.encoding = 'utf-8'
    soup = bf(res.text, 'html.parser')
    content = ""
    temp = []
    reback = []
    for date in soup.select('.joblist_cont .date'):
        if date.text == '':
            temp.append('緊急!!重點職務')
        else:
            temp.append(date.text)
    for v,data in enumerate(soup.select('.joblist_cont .jobname a'),0):
        link = data['href']
        title = data['title']
        content += '發布時間->{}\n工作名稱->{}\n連結網址->{}\n'.format(temp[v],title,'https://www.104.com.tw'+link)
        if v%5==0 :
            if v == 0:
                continue
            reback.append(TextSendMessage(text=content))
            content = ''
    return reback
def movie_template():
            buttons_template = TemplateSendMessage(
            alt_text='電影 template',
            template=ButtonsTemplate(
                title='服務類型',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/zzv2aSR.jpg',
                actions=[
                    MessageTemplateAction(
                        label='近期上映電影',
                        text='近期上映電影'
                    ),
                    MessageTemplateAction(
                        label='依莉下載電影',
                        text='eyny'
                    ),
                    MessageTemplateAction(
                        label='觸電網-youtube',
                        text='觸電網-youtube'
                    ),
                    MessageTemplateAction(
                        label='Marco體驗師-youtube',
                        text='Marco體驗師'
                    )
                ]
            )
        )
            return buttons_template
def apple_news():
    target_url = 'https://tw.appledaily.com/new/realtime'
    print('Start parsing appleNews....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = bf(res.text, 'html.parser')
    content = ""

    for index, data in enumerate(soup.select('.rtddt a'), 0):
        if index == 5:
            return content
        title = data.select('font')[0].text
        link = data['href']
        content += '{}\n{}\n'.format(title,link)
    return content

def get_image_link(search_query):
    img_urls = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.getenv('GOOGLE_CHROME_BIN',None)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=os.getenv('CHROMEDRIVER_PATH',None))
#    driver = webdriver.Chrome(executable_path='/app/.chromedriver/bin/chromedriver')
    if search_query[-4:] == 'menu':
        t = search_query[:-4]+'餐點價格'
        url = 'https://www.google.com.tw/search?q='+t+'&rlz=1C1EJFA_enTW773TW779&source=lnms&tbm=isch&sa=X&ved=0ahUKEwjX47mP-IjfAhWC7GEKHcZCD4YQ_AUIDigB&biw=1920&bih=969'
    elif search_query[-3:] == 'pic':
        t = search_query[:-3]
        url = 'https://www.google.com.tw/search?rlz=1C1EJFA_enTW773TW779&biw=1920&bih=920&tbs=isz%3Alt%2Cislt%3Asvga&tbm=isch&sa=1&ei=1UwFXLa8FsT48QWsvpOQDQ&q='+t+'&oq='+t+'&gs_l=img.3..0l10.10955.19019..20688...0.0..0.65.395.10......3....1..gws-wiz-img.....0..0i24.sGlMLu_Pdf0'
    driver.get(url)
    imges = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta notranslate")]')
    count = 0
    for img in imges:
        img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
        print(str(count)+'--->'+str(img_url))
        if img_url.startswith('https') == False or (img_url in img_urls) == True or img_url.endswith('jpg') == False:
            continue
        else:
            img_urls.append(img_url)
            count = count + 1
            if count > 3:
                break
    driver.quit()
    return img_urls

#更改
def drink_menu(text):
    pattern = r'.*menu$'
    web = []
    if re.search(pattern,text.lower()):
        
        temp = get_image_link(text)
        print('fun'+str(temp))
        for t in temp:
            web.append(ImageSendMessage(original_content_url=t,preview_image_url=t))
        return web
    
def google_picture(text):
    pattern = r'.*pic$'
    web = []
    if re.search(pattern,text.lower()):
        temp = get_image_link(text)
        for t in temp:
            web.append(ImageSendMessage(original_content_url=t,preview_image_url=t))
        return web
def sister_picture(text):
    pattern = r'.*sister$'
    web = []
    r = random.randint(0,122)
    url = 'https://forum.gamer.com.tw/Co.php?bsn=60076&sn=26514065'
    res = requests.get(url)
    soup = bf(res.text,'html.parser')
    if re.search(pattern,text.lower()):
       temp = []
       temp.append('https://img.pornpics.com/2014-07-14/281181_13.jpg')
       for item in soup.select('.photoswipe-image'):
           temp.append(item.get('href'))
       for t in temp[r:r+5]:
            web.append(ImageSendMessage(original_content_url=t,preview_image_url=t))
       return web
def movie():
    target_url = 'http://www.atmovies.com.tw/movie/next/0/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = bf(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('ul.filmNextListAll a')):
        if index == 20:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "http://www.atmovies.com.tw" + data['href']
        content += '{}\n{}\n'.format(title, link)
    return content
def pattern_mega(text):
    patterns = [
        'mega', 'mg', 'mu', 'ＭＥＧＡ', 'ＭＥ', 'ＭＵ',
        'ｍｅ', 'ｍｕ', 'ｍｅｇａ', 'GD', 'MG', 'google',
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
def eyny_movie():
    target_url = 'http://www.eyny.com/forum-205-1.html'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = bf(res.text, 'html.parser')
    content = ''
    for titleURL in soup.select('.bm_c tbody .xst'):
        if pattern_mega(titleURL.text):
            title = titleURL.text
            if '11379780-1-3' in titleURL['href']:
                continue
            link = 'http://www.eyny.com/' + titleURL['href']
            data = '{}\n{}\n\n'.format(title, link)
            content += data
    return content

def panx():
    target_url = 'https://panx.asia/'
    print('Start parsing ptt hot....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = bf(res.text, 'html.parser')
    content = ""
    for data in soup.select('div.container div.row div.desc_wrap h2 a'):
        title = data.text
        link = data['href']
        content += '{}\n{}\n\n'.format(title, link)
    return content
def magazine():
    target_url = 'https://www.cw.com.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = bf(res.text, 'html.parser')
    temp = ""
    for v ,date in enumerate(soup.select('.caption h3 a'),0):
        url = date['href']
        title = date.text.strip()
        temp += '{}\n{}\n'.format(title,url)
        if(v>4):
            break
    return temp
def check_pic(img_id):
    Confirm_template = TemplateSendMessage(
    alt_text='要給你照片標籤描述嗎?',
    template=ConfirmTemplate(
    title='注意',
    text= '要給你照片標籤描述嗎?\n要就選Yes,並且回覆\n-->id+描述訊息(這張照片id是'+ str(img_id) +')',
    actions=[                              
            PostbackTemplateAction(
                label='Yes',
                text='I choose YES',
                data='action=buy&itemid=1'
            ),
            MessageTemplateAction(
                label='No',
                text='I choose NO'
            )
        ]
    )
    )
    return Confirm_template

def button_template(name,shop_name,title,text,image_url):
    message = TemplateSendMessage(
            alt_text = 'Button Template',
            template = ButtonsTemplate(
                    title = title,
                    text = name+text,
                    thumbnail_image_url = image_url,
                    actions = [
                            URITemplateAction(
                                    label = '搜尋一下附近其他美食',
                                    uri = 'line://nv/location'
                                    ),
                            PostbackTemplateAction(
                                    label = shop_name+'的google評價',
                                    data = 'rank&'+shop_name,
                                    ),
                            MessageTemplateAction(
                                    label = '納入口袋名單',
                                    text = '納入口袋名單'
                                    )
                            ]
                    )
            
            )
    return message
def mrt_stop(text):
    url = 'http://tcgmetro.blob.core.windows.net/stationnames/stations.json'
    res = requests.get(url)
    doc=json.loads(res.text)
    t = doc['resource']
    print('doc'+str(doc))
    temp = ''
    for i in t:
        if text == i['Destination']:
             temp += '現在捷運在->'+i['Station']+'\n'
    print('mrt_fun'+temp)
    return temp
    
@handler.add(PostbackEvent)
def handle_postback(event):
    temp = event.postback.data
    s = ''
    if event.postback.data[0:1] == 'T':
        temp = event.postback.data[1:]
        print('postback'+temp)
        s = mrt_stop(temp)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=s))
    elif temp[:4] == 'rank':
        name,rank = get_shop_rank(temp[5:])
        print(name)
        print(rank)
        for i in range(len(name)):
            s = s + '{}的評價是{}顆星-僅為參考\n'.format(name[i],rank[i])
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=s))
@handler.add(JoinEvent)
def handle_join(event):
    newcoming_text = "謝謝邀請我這個ccu linebot來至此群組！！我會當做個位小幫手～"
#    謝謝邀請我這個ccu linebot來至此群組！！我會當做個位小幫手～<class 'linebot.models.events.JoinEvent'>
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=newcoming_text + str(JoinEvent))
        )
# 處理圖片
@handler.add(MessageEvent,message=ImageMessage)
def handle_msg_img(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    tem_name = str(profile.display_name)
    img_id = 1
    t = fb.get('/pic',None)
    if t!=None:
        count = 1
        for key,value in t.items():
            if count == len(t):#取得最後一個dict項目
                img_id = int(value['id'])+1
            count+=1
    try:
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(prefix='jpg-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            fb.post('/pic',{'id':str(img_id),'user':tem_name,'describe':''})
            tempfile_path = tf.name
        path = tempfile_path
        client = ImgurClient(client_id, client_secret, access_token, refresh_token)
        config = {
            'album': album_id,
            'name' : img_id,
            'title': img_id,
            'description': 'Cute kitten being cute on'
        }
        client.upload_from_path(path, config=config, anon=False)
        os.remove(path)
        image_reply = check_pic(img_id)
        line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='上傳成功'),image_reply])
    except  Exception as e:
        t = '上傳失敗'+str(e.args)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=t))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    title = event.message.title
    latitude = event.message.latitude
    longitude = event.message.longitude
    temp = 'hey guy~\ntitle={} latitude={} longitude={}'.format(title,latitude,longitude)
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=temp))
# 處理訊息:
@handler.add(MessageEvent, message=TextMessage)
def handle_msg_text(event):
    content = event.message.text  
    profile = line_bot_api.get_profile(event.source.user_id)
    user_name = profile.display_name
    picture_url = profile.picture_url
    if event.message.text == 'where':
        message = LocationSendMessage(
        title='My CCU Lab',
        address='中正大學',
        latitude=23.563381,
        longitude=120.4706944
        )
        line_bot_api.reply_message(event.reply_token, message)
        return
    elif event.message.text == '國泰金控公司簡介':
        t = '''公司簡介\n隨著金融產業多元化與全球化的發展,以及國內金融機構購併、整合法源之制訂,國泰金融控股股份有限公司於民國九十年十二月三十一日正式成立,登記額定資本額新台幣一千二百億元。結合保險、證券、銀行等多樣化的金融機構,國泰金控架構起一個功能完整的經營平台。藉由遍佈全省之營業據點與銷售人員,發展共同行銷 (cross-selling) 的策略,提供客戶一站購足 (one-stop shopping) 的服務。\n 
*榮登美國富比士排名2000大企業，台灣企業排名第一名 
*榮獲中華信用評等「twAA+」為業界之冠 
*榮獲天下雜誌1000大企業調查，蟬聯金融業榜首*英國金融時報全球500大企業台灣區金融業第一名 
*今周刊公佈「金控經營績效評比」中，以策略、財務、經營品質三項指標，排名金控業第一\n
主要商品／服務項目\n
金融（保險、銀行、證券…..）\n
福利制度\n
年終獎金，端午、中秋代金，婚喪禮金，生日禮物，員工保險，子女教育補助費，登山活動，春秋兩季旅遊，年終聚餐補助，國建購屋優惠。\n
經營理念\n
四大經營理念：\n
1.經營腳踏實地，工作精益求精 \n
2.注重商業道德，講究職業良心 \n
3.重視保戶權益，負起社會責任 \n
4.加強員工福利，兼顧股東利益 \n
六大工作方針： \n
1.經營效率化 \n
2.加強各級幹部權責 \n
3.重視各種教育訓練 \n
4.待遇與工作合理化 \n
5.以行動及成果證明一切 \n
6.年年是自強年'''    
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=t))
        return 0
    elif event.message.text.lower() == "國泰金控工作職缺":
        t = job_seek()
        line_bot_api.reply_message(event.reply_token,t)
        return 0
    elif event.message.text.lower() == "國泰工作":
         buttons_template = TemplateSendMessage(
            alt_text='國泰工作template',
            template=ButtonsTemplate(
                title='國泰金融控股股份有限公司',
                text='請選擇需要選項',
                thumbnail_image_url='https://i.imgur.com/Rlbwhuy.jpg',
                actions=[
                    MessageTemplateAction(
                        label='國泰金控公司簡介',
                        text='國泰金控公司簡介'
                    ),
                    MessageTemplateAction(
                        label='國泰金控工作職缺',
                        text='國泰金控工作職缺'
                    ),
                ]
            )
        )
         line_bot_api.reply_message(event.reply_token, buttons_template)
         return 0
    elif event.message.text.lower() == "eyny":
        content = eyny_movie()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    elif google_picture(event.message.text) != None:
        image = google_picture(event.message.text)
        line_bot_api.reply_message(event.reply_token,image)
        return
    elif sister_picture(event.message.text) != None:
        image = sister_picture(event.message.text)
        line_bot_api.reply_message(event.reply_token,image)
        return
    elif event.message.text == "PanX泛科技":
        content = panx()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    elif drink_menu(event.message.text) != None:
        image = drink_menu(event.message.text)
        image.append(button_template(user_name,event.message.text[:-4],'請問一下~','有想要進一步的資訊嗎?',picture_url))
        line_bot_api.reply_message(event.reply_token,image)
        return
    elif event.message.text == "近期上映電影":
        content = movie()
        template = movie_template()
        line_bot_api.reply_message(
            event.reply_token,[
                    TextSendMessage(text=content),
                    template
            ]
            )
        return 0
    elif event.message.text.lower() == "tool":
        Carousel_template = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/Upw0mY5.jpg',
                title = '功能目錄',
                text = user_name+'我可以幫你做到下列這些喔',
                actions=[
                    MessageTemplateAction(
                        label='國泰工作查詢',
                        text= '國泰工作'
                    ),
                    MessageTemplateAction(
                        label='電影資訊',
                        text= 'movie'
                    ),
                    MessageTemplateAction(
                        label='新聞資訊',
                        text= 'news'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/Upw0mY5.jpg',
                title = '功能目錄',
                text = user_name+'我可以幫你做到下列這些喔',
                actions=[
                    MessageTemplateAction(
                        label='捷運到站資訊',
                        text= 'MRT'
                    ),
                    MessageTemplateAction(
                        label='正妹圖片',
                        text= 'pic sister'
                    ),
                    MessageTemplateAction(
                        label='資料庫裡面隨便一張照片',
                        text= 'ramdom picture'
                    )
                ]
            )
        ]
        )
        )
        line_bot_api.reply_message(event.reply_token,Carousel_template)
        return 0
    elif event.message.text.lower() == "mrt":
        Carousel_template = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/l1UuvZp.jpg',
                title='請選擇你要到的路線終點',
                text='此張是文湖線及板南線',
                actions=[
                    PostbackTemplateAction(
                        label='南港展覽館站',
                        data = 'T南港展覽館站'
                    ),
                    PostbackTemplateAction(
                        label='動物園站',
                        data = 'T動物園站',
                    ),
                    PostbackTemplateAction(
                        label='頂埔站',
                        data = 'T頂埔站'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/l1UuvZp.jpg',
                title='請選擇你要到的路線終點',
                text='此張是新店線及淡水線',
                actions=[
                    PostbackTemplateAction(
                        label='新店站',
                        data = 'T新店站'
                    ),
                    PostbackTemplateAction(
                        label='松山站',
                        data = 'T松山站'
                    ),
                    PostbackTemplateAction(
                        label='象山站',
                        data = 'T象山站'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/l1UuvZp.jpg',
                title='請選擇你要到的路線終點',
                text='此張是淡水線及蘆洲線',
                actions=[
                    PostbackTemplateAction(
                        label='淡水站',
                        data = 'T淡水站'
                    ),
                    PostbackTemplateAction(
                        label='北投站',
                        data = 'T北投站'
                    ),
                    PostbackTemplateAction(
                        label='蘆洲站',
                        data = 'T蘆洲站'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/l1UuvZp.jpg',
                title='請選擇你要到的路線終點',
                text='此張是迴龍蘆洲',
                actions=[
                    PostbackTemplateAction(
                        label='南勢角站',
                        data = 'T南勢角站'
                    ),
                    PostbackTemplateAction(
                        label='迴龍站',
                        data = 'T迴龍站'
                    ),
                    PostbackTemplateAction(
                        label='台電大樓站',
                        data = 'T台電大樓站'
                    )
                ]
            )
        ]
    )
    )
        line_bot_api.reply_message(event.reply_token,Carousel_template)
        return 0
    elif event.message.text == "Marco體驗師":
        target_url = 'https://www.youtube.com/channel/UCQTIdBx41To9Gg42aGEO0gQ/videos'
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        soup = bf(res.text, 'html.parser')
        template = movie_template()
        seqs = ['https://www.youtube.com{}'.format(data.find('a')['href']) for data in soup.select('.yt-lockup-title')]
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                template
            ])
        return 0
    elif event.message.text == "觸電網-youtube":
        target_url = 'https://www.youtube.com/user/truemovie1/videos'
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        soup = bf(res.text, 'html.parser')
        seqs = ['https://www.youtube.com{}'.format(data.find('a')['href']) for data in soup.select('.yt-lockup-title')]
        template = movie_template()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                template
            ])
        return 0
    elif event.message.text.lower() == "ramdom picture":
        client = ImgurClient(client_id, client_secret)
        images = client.get_album_images(album_id)
        index = random.randint(0, len(images) - 1)
        url = images[index].link
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(event.reply_token,image_message)
        return
    elif event.message.text.lower() == "妹妹":
        url = 'https://i.imgur.com/J5m2pm7.jpg'
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(event.reply_token,image_message)
        return
    elif event.message.text.lower() == "movie":
        buttons_template = movie_template()
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    elif event.message.text == "蘋果即時新聞":
        content = apple_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    elif event.message.text.lower() == "news":
        buttons_template = TemplateSendMessage(
            alt_text='news template',
            template=ButtonsTemplate(
                title='新聞類型',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/GoAYFqv.jpg',
                actions=[
                    MessageTemplateAction(
                        label='蘋果即時新聞',
                        text='蘋果即時新聞'
                    ),
                    MessageTemplateAction(
                        label='天下雜誌',
                        text='天下雜誌'
                    ),
                    MessageTemplateAction(
                        label='PanX泛科技',
                        text='PanX泛科技'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    elif event.message.text == "天下雜誌":
        content = magazine()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    elif event.message.text == "test":
        static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
        content = static_tmp_path

    message = TextSendMessage(text=content)
    line_bot_api.reply_message(event.reply_token,message)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
