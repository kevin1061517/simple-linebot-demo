Linebot處理音檔及相關爬蟲
====
問題:
-------  
當user傳來音檔(.aac)可以透過google提供的python套件speech_recognition來解析音檔內容，並且可以轉成文字，這中間必須透過pydub這個套件來幫魔，因為line傳來的音檔格式是(.aac)，跟speech_recognition所支援的格式不一樣，所以首先要先把音檔轉成.wav格式，這樣才有辦法做解析，但遇到了很大問題就是pydub套件非常麻煩，搞了我好幾個禮拜才了解，原來是pydub好像沒有很完整，他需要一個叫做ffmpeg的東西來幫忙解碼(decode)，所以首先要把ffmpeg加入heroku的buildpack裡面，然後要去找ffmpeg在heroku的位置，像是我找到的位置是在'/app/vendor/ffmpeg/ffmpeg'這裡面，所以必須做一些處理，下面來一步一步做，以提醒之後遇到相同問題!

下圖是跑了幾百次一直都出現例外(exception)，包括了上面講的ffmpeg問題，還有一部分是我路徑沒設好
步驟:

#一.
先在heroku的buildpack中加入 https://github.com/alevfalse/heroku-buildpack-ffmpeg
##二.再把程式push到heroku上面(git push heroku master -f)後，可以用指令看ffmpeg有沒有建立在heroku上面，指令是heroku run "ffmpeg -version"，接著進入bash看ffmpeg的位置在heroku的哪裡，因為要給AudioSegment.converter來指定ffmpeg位置，用指令heroku run bash就可以進入bash殼了，在輸入指令which ffmpeg，這時ㄧ般正常的話就會回應給你ffmpeg的位置，如下圖這樣子，他給我的ffmpeg的位置在(/app/vendor/ffmpeg/ffmpeg)裡面
###三.知道了位置我們就可以在python裡面做手腳了，
參考:

https://stackoverflow.com/questions/26477786/reading-in-pydub-audiosegment-from-url-bytesio-returning-oserror-errno-2-no

https://github.com/integricho/heroku-buildpack-python-ffmpeg.git

https://hk.saowen.com/a/4e1f6599b0c03d19d8945f9cc23a7bc313b638d9d134d8bd335db9B
