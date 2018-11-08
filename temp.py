from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from firebase import firebase
from linebot.models import (
    TemplateSendMessage,AudioMessage,AudioSendMessage,BaseSize,ImagemapArea,URIImagemapAction,MessageImagemapAction,ImagemapSendMessage,ButtonsTemplate,ImageMessage,URITemplateAction,MessageTemplateAction,ConfirmTemplate,PostbackTemplateAction,ImageSendMessage,MessageEvent, TextMessage, TextSendMessage,StickerMessage, StickerSendMessage
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
client_id = '6255d5f00adb13c'
client_secret = '42e6189ab784cc81f1daff96a09873ea225a2d62'
album_id = '5P2TA2e'
access_token = '11814d667925db5f085baee3f423554963eaeab8'
refresh_token = 'd75aaee1c138c25144b6719f4e7e169f36758c50'
client = ImgurClient(client_id, client_secret, access_token, refresh_token)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
#老師id-->U055f980c2a280233a6342e8132099b1a
line_bot_api = LineBotApi('3xmkcHdxeFREm5d7X0YtBS5sdZS5J/XvwYAUf2XS5hcs0+LS2v+x1DMTorheXcddfL0GKgwb+of87nujHWkfWehHKtH469+UGGMbyFo+0Fzppar85P6gTt+aNsqVSmOjCUIZn8IaxQYdfJVEj+1UhAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('04cc956e1800201b2005c5228958488d')
url = 'https://line-bot-by-python.firebaseio.com'
fb = firebase.FirebaseApplication(url,None)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
@app.route('/cuu_test')#輸入網頁{https://robotyung.herokuapp.com/cuu_test就會發出訊息
def display():
    temp_set = save_line_id('U728ffb2ce052577e6165dfc60d5b0dc0')#取得所有要推播訊息的userid
    for v in temp_set:
        if(app_send()=='投票'):
            push_msg(v)
        else:
            line_bot_api.push_message(v, TextSendMessage(text=app_send()))
            #line_bot_api.push_message(v, TextSendMessage(text='如有看到訊息請回ok或好\n表示你收到有意見就直接回'))
    return 'hello'
def bug(text):
    url = 'http://www.mis.ccu.edu.tw:8088/faculty_chi.aspx#AdjunctProfessor'
    html = requests.get(url)
    sp = bf(html.text,'html.parser')
    name = sp.find("table",{"style":"width: 725px; height: 145px; line-height: 16pt;"})
    name2 = name.find_all('a',{'target':'_blank'})#size=35,資料到27為止
    professor = []
    for v in name2[0:28]:
        professor.append(v.text.strip())
        #len(professor)--->28
    job = sp.find("table",{"style":"width: 725px; height: 145px; line-height: 16pt;"})
    job2 = job.find_all('div',{'align':'center'})#size138  good
    for v in range(5,59,4):
        professor.append(job2[v].text.strip())
    for v in range(0,28,2):
        if re.search(professor[v]+r'.*email',text):
            return professor[v+1]
        elif re.search(professor[v]+r'.*job',text):
            return professor[v+28]
from urllib.parse import quote

def doing(event,text):
    patterns = ['你好','hi','hello','哈囉','嗨','fuck']
    r = ['吳帆教授最近好嗎','哈囉吳教授 最近很忙嗎','你好阿 在做實驗室測試','這邊是中正大學資訊管理研究所','哈囉阿','帥哥 找我嗎?']
    n = random.randint(0,5)
    for pattern in patterns:
        if re.search(pattern,text.lower()):
                push_txt = r[n]
                t =  quote(push_txt)
                stream_url = 'https://google-translate-proxy.herokuapp.com/api/tts?query='+t+'&language=zh-tw'
                test = 'https://google-translate-proxy.herokuapp.com/api/tts?query=%E5%93%88%E5%9B%89&language=zh-tw'
#               with open('stream.mp3', 'wb') as f:
#                    try:
#                        for block in r.iter_content(1024):
#                            f.write(block)
#                        f.close()
#                        subprocess.call('madplay stream.mp3 -o wave:- | aplay -D plughw:1,0',shell=True) 
#                    except KeyboardInterrupt:
#                        pass
                n = len(push_txt)
                message = AudioSendMessage(
                    original_content_url = stream_url,
                    duration=n*400#千分之一秒
                )
                line_bot_api.reply_message(event.reply_token,message)
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
    
def judge(arr,text):#判斷輸入的值是否為keyError Exception
    r = random.randint(0,4)
    try:
        for key,value in arr[text][r].items():
            return str(key+value)
    except KeyError:
        return 'keyError'
def fbchoose(text):
    t = fb.get('/chat',None)
    for key,value in t.items():
        if judge(value,text)!='keyError':
            return judge(value,text)
def get(text,name):
    tex = ''
    temp = ''
    patterns = ['收到','ok']
    for pattern in patterns:
        if re.search(pattern,text.lower()):
            t = fb.get('/app',None)
            count = 1
            for key,value in t.items():
                if count == len(t):#取得最後一個dict項目
                    tex = value['read']
                count+=1
            a = tex.split('\n')
            a.remove('')
            s = set(a)
            for v in s:
                temp=temp+v+'\n'
            return '已收到，目前已讀人數是:'+str(len(s))+'人\n如下人員:\n'+temp
def app_send():#取得APP發的訊息，要推播給Line_user的訊息
    t = fb.get('/app',None)
    count = 1
    for key,value in t.items():
        if count == len(t):#取得最後一個dict項目
            return value['msg']
        count+=1
def save_response(read_name,reply):#儲存對話紀錄
    t = fb.get('/app',None)
    count = 1
    for key,value in t.items():
        if count == len(t):#取得最後一個dict項目
            s = value['read']
            s = s+read_name+'\n'#記錄姓名
            r = value['reply']
            r = r+read_name+': '+reply+'\n'#記錄已讀回話
            data2 = {'msg': value['msg'], 'read': s, 'reply':r, 'time': value['time']}
            fb.put(url+'/app/',data=data2,name=key)
        count+=1
def save_line_id(user_id):#儲存line使用者id，使用在推播訊息
    s = set()      #建立一個set，set裡面的資料不會重覆出現
    t = fb.get('userid',None)
    if t != None:
        for key,value in t.items():#把firebase裡面的value一個個取出
            s.add(value)
    if user_id not in s:#如果set裡面沒有user_id就加入database
        fb.post('/userid',user_id)
        s.add(user_id)
    return s
def push_msg(line_id):
    title=''
    text=''
    item=''
    item2=''
    item3=''
    count = 1
    t = fb.get('/vote',None)
    for key,value in t.items():
        if count == len(t):#取得最後一個dict項目
            title = value['title']
            text = value['text']
            item = value['item1']
            item2 = value['item2']
            item3 = value['item3']
        count+=1
    if item3=='':
        item3 = '--------------'
    buttons_template = TemplateSendMessage(
    alt_text='Buttons Template',
    template=ButtonsTemplate(
    title= title,
    text= text,
    thumbnail_image_url='https://i.imgur.com/M7R0Enu.jpg',
    actions=[
            MessageTemplateAction(
                    label=item,
                    text='ButtonsTemplate'
            ),
            PostbackTemplateAction(   
                    label=item2,
                    text='postback text',
                    data='postback1'
            ),
            MessageTemplateAction(
                    label=item3,
                    text='ButtonsTemplate'
            )
            ]
    )
    )
    line_bot_api.push_message(line_id,buttons_template)
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
#def imagemap(event,text):
#    patterns = ['bye','掰','再見']
#    for pattern in patterns:
#        if re.search(pattern,text.lower()):
#            message = ImagemapSendMessage(
#                    base_url='https://www.youtube.com/watch?v=3QHxNGB7Q0s',
#                    alt_text='this is an imagemap',
#                    base_size=BaseSize(height=1040, width=1040),
#                    actions=[
#                            URIImagemapAction(
#                                    link_uri='https://i.imgur.com/M7R0Enu.jpg',
#                                    area=ImagemapArea(
#                                            x=0, y=0, width=520, height=1040
#                                )
#                                ),
#                                MessageImagemapAction(
#                                        text='hello',
#                                        area=ImagemapArea(
#                                            x=520, y=0, width=520, height=1040
#                                         )
#                               )
#                   ]
#            )
#            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='Hello, world')
#處理音訊
from pydub import AudioSegment
import speech_recognition as sr
@handler.add(MessageEvent,message=AudioMessage)
def handle_aud(event):
    r = sr.Recognizer()
    message_content = line_bot_api.get_message_content(event.message.id)
    ext = 'aac'
    try:
        with tempfile.NamedTemporaryFile(prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        
        test = 'out'
        
        AudioSegment.converter = '/app/.heroku/vendor/ffmpeg/bin/ffmpeg'
        sound = AudioSegment.from_file(dist_path, format="aac")
        dist_path = os.path.splitext(dist_path)[0]+'.mp3'
        sound.export(dist_path, format="mp3")
        test = 'in'
#        
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path,dist_path)
        test = 'in'
        path = os.path.join('/tmp', dist_name)
        with sr.AudioFile(path) as source:
            audio = r.record(source)
    except:
        t = '音訊有問題'+test
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=t))
    os.remove(path)
    text = r.recognize_google(audio,language='zh-TW')
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='你的訊息是=\n'+text))
#處理圖片
@handler.add(MessageEvent,message=ImageMessage)
def handle_msg(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    tem_name = str(profile.display_name)
    temp=''
    ext = 'jpg'
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
        with tempfile.NamedTemporaryFile(prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            fb.post('/pic',{'id':str(img_id),'user':tem_name,'describe':''})
            tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path,dist_path)
        client = ImgurClient(client_id, client_secret, access_token, refresh_token)
        config = {
            'album': album_id,
            'name' : img_id,
            'title': img_id,
            'description': 'Cute kitten being cute on'
        }
        
        path = os.path.join('/tmp', dist_name)
        temp='ok'
        client.upload_from_path(path, config=config, anon=False)
        os.remove(path)
        image_reply = check_pic(img_id)
        line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='上傳成功'),image_reply])
    except :
        t = '上傳失敗dist_name'+temp
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=t))
# 處理訊息:
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global tem_id
    profile = line_bot_api.get_profile(event.source.user_id)
    tem_id = str(profile.user_id)
    tem_name = str(profile.display_name)
    content = event.message.text  
    save_line_id(tem_id)#儲存lineId
    save_response(tem_name,content)#save response
    count = 1
    t = fb.get('/pic',None)
    for key,value in t.items():
        if count == len(t):#取得最後一個dict項目
            img_id = value['id']
        count+=1
    if doing(event,event.message.text)!=None:
        return
    elif img_describe(event.message.text,img_id)!=None:
        content = img_describe(event.message.text,img_id)
    elif get_image(event.message.text)!=None:
        image = get_image(event.message.text)
        line_bot_api.reply_message(event.reply_token, image)
        return
#    elif imagemap(event,event.message.text)!=None:
#        
#        return
    elif bug(event.message.text)!=None:
        content = bug(event.message.text)
    elif content =='lab':
        content = 'successful again'
    elif fbchoose(event.message.text)!=None:
        content = fbchoose(event.message.text)
    elif get(event.message.text,tem_name)!=None:
        content = get(event.message.text,tem_name)
    elif event.message.text 
    elif event.message.text == "吳帆":
        imagemap_message = ImagemapSendMessage(
                        base_url='https://i.imgur.com/PJlGQ2v.jpg',
                        alt_text='this is an imagemap',
                        base_size=BaseSize(height=520, width=420),
                        actions=[
                            URIImagemapAction(
                                link_uri='https://youtu.be/mi4ZEqNWzCE',
                                area=ImagemapArea(
                                    x=0, y=0, width=260, height=220
                                )
                            ),
                            MessageImagemapAction(
                                text='右下',
                                area=ImagemapArea(
                                    x=260, y=220, width=260, height=220
                                )
                            ),
                            MessageImagemapAction(
                                text='右上',
                                area=ImagemapArea(
                                    x=260, y=0, width=260, height=220
                                )
                            )
                        ]
                    )
        line_bot_api.reply_message(event.reply_token,imagemap_message)
    elif event.message.text == "隨便一張":
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
    else:
        reword = ['安靜啦 乾','去找你妹','請問沛最近好嗎?','不要跟我耍嘴砲','在嘴阿','小楊是育成高中','我覺得有道理','你在說泰語','別靠北','在嗆阿','你在恭殺小啦','怎樣?','請注意你說話','高潮你妹啦','在說人話嗎?','管你?','你知道林北是誰嗎','閉嘴']
        r = random.randint(0,17)
        t =  quote(reword[r])
        stream_url = 'https://google-translate-proxy.herokuapp.com/api/tts?query='+t+'&language=zh-tw'
        message = AudioSendMessage(
            original_content_url = stream_url,
            duration=300000
        )
        line_bot_api.reply_message(event.reply_token,message)
        return
#    elif event.message.text == "template":    
#        Confirm_template = TemplateSendMessage(
#        alt_text='目錄 template',
#        template=ConfirmTemplate(
#            title='這是Template',
#            text='這就是ConfirmTemplate,用於兩種按鈕選擇',
#            actions=[                              
#                PostbackTemplateAction(
#                    label='Y',
#                    text='Y',
#                    data='action=buy&itemid=1'
#                ),
#                MessageTemplateAction(
#                    label='N',
#                    text='I choose N'
#                )
#            ]
#        )
#        )
#        line_bot_api.reply_message(event.reply_token,Confirm_template)
    
    message = TextSendMessage(text=content)
    line_bot_api.reply_message(event.reply_token,message)
#image_url = "https://i.imgur.com/k8v9RiM.jpg"
#line_bot_api.push_message(tem_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
