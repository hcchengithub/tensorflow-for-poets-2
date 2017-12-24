
#
# 主程式
# 用來把訓練好的成果讓 WeChat Chatroom 裡的 mates 來玩。
# 只要用 WeChat 在 Chatroom 裡拍一張照片上去，本程式收到照片就會回答照片裡的內容。
#

import sys
import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義
import peforth
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import time
import random
import scripts.label_image2 as ai

# WeChat chatroom name 
chatroom = "剪刀、石頭、布"

# Anti-Robot delay time , thanks to Rainy's great idea.
nextDelay = 3
nextDelay_msg = 'Next anti-robot delay time: %i seconds\n' % (nextDelay)

# Initialize debugger peforth 
peforth.ok(loc=locals(),cmd='''
    :> [0] value main.locals // ( -- dict ) main locals
    none value locals
    none value msg
    : bye main.locals :> ['itchat'].logout() bye ; 
    exit
    ''')  
    
# Sending message to friend or chatroom depends on the given 'send'
# function. It can be itchat.send or msg.user.send up to the caller.
# WeChat text message has a limit at about 2000 utf-8 characters so
# we need to split a bigger string into chunks.
def send_chunk(text, send, pcs=2000):
    s = text
    while True:
        if len(s)>pcs:
            print(s[:pcs]); send(s[:pcs])
        else:
            print(s); send(s)
            break
        s = s[pcs:]    

# Console is a peforth robot that listens and talks.
# Used in chatting with both friends and chatrooms.
def console(msg,cmd):
    if cmd:
        print(cmd)  # already on the remote side, don't need to echo. 
        if peforth.vm.debug==11: peforth.ok('11> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
        # re-direct the display to peforth screen-buffer
        peforth.vm.dictate("display-off")  
        try:
            peforth.vm.push((locals(),globals(),'console prompt'))
            peforth.vm.dictate(":> [0] to locals " + cmd)
        except Exception as err:
            errmsg = "Failed! : {}".format(err)
            peforth.vm.dictate("display-on")
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk(errmsg + nextDelay_msg, msg.user.send)
        else:
            # Normal cases 
            peforth.vm.dictate("display-on screen-buffer")
            screen = peforth.vm.pop()[0]
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk(screen + nextDelay_msg, msg.user.send)

#        
# 讓 Inception V3 Transfered Learning 看照片，回答 剪刀、石頭、布
#        
def predict(msg):
    if peforth.vm.debug==22: peforth.ok('22> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    results = time.ctime() + '\n'
    results += 'Google MobileNet Transfered Learning thinks it is:\n'
    pathname = 'download\\' + msg.fileName # 照片放在 working directory/download 下
    msg.download(pathname)  
    # TensorFlow 的 tf.image.decode_bmp/jpen/png/pcm 很差，改用 ffmpeg 
    peforth.vm.dictate("dos ffmpeg -i {} -y 1.png".format(pathname)+"\ndrop\n")  
    results += ai.predict("1.png")
    peforth.vm.dictate("dos del {}".format(pathname)+"\ndrop\n")
    time.sleep(nextDelay)  # Anti-Robot delay 
    send_chunk(results + nextDelay_msg, msg.user.send)

@itchat.msg_register((ATTACHMENT,VIDEO,VOICE,RECORDING), isGroupChat=True)
def attachment(msg):
    if peforth.vm.debug==33: peforth.ok('33> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        msg.download('download\\' + msg.fileName)
        time.sleep(nextDelay)  # Anti-Robot delay 
        send_chunk('Attachment: %s \nreceived at %s\n' % (msg.fileName,time.ctime()) + nextDelay_msg, msg.user.send)

@itchat.msg_register(TEXT, isGroupChat=True)
def chat(msg):
    if peforth.vm.debug==44: peforth.ok('44> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        if msg.isAt: 
            cmd = msg.text.split("\n",maxsplit=1)[1] # remove the first line: @nickName ...
            console(msg, cmd)                        # 避免帶有空格的 nickName 惹問題
        else:    
            # Shown on the robot computer
            print(time.ctime(msg.CreateTime), end=" ")
            for i in msg.User['MemberList']:
                if i.UserName == msg.ActualUserName:
                    print(i.NickName)
            print(msg.text)

@itchat.msg_register(PICTURE, isGroupChat=True)
def picture(msg):
    if peforth.vm.debug==55: peforth.ok('55> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        predict(msg)

# peforth.vm.debug = 44
if peforth.vm.debug==66: peforth.ok('66> ',loc=locals(),cmd=":> [0] to locals cr")  # breakpoint    
itchat.auto_login(hotReload=False)
itchat.run(debug=True, blockThread=True)
peforth.ok('Examine> ',loc=locals(),cmd=':> [0] to main.locals')

# Bug list
# [x] 正常對話不需 delay --> FP @ v6
# [x] "Next anti-robot delay time" 往上合併好再發，
#     否則中間時間極短又被認出來是個 Bot。
#     --> FP @ v6
# [ ] 檢查 download/ folder 在不在? 不在要警告。
#
#

'''

# --------------- Playground ---------------------------------------------------
# Setup the playground for testing without itchat (avoid the need to login)

<py>
def msg():
    pass
def _():
    pass
msg.user = _    
msg.user.send = print
msg.user.NickName = 'A believer'    
msg.isAt = True
def _():
    print('msg.user.verify() ... pass')
msg.user.verify = _
msg.fileName = '20171222153010.jpg'
msg.type = 'fil' # also 'img'(image), 'vid'(video)
def _(fileName):
    print('Downloaded %s from WeChat cloud' % fileName)
msg.download = _
msg.text = "Message text from the WeChat cloud"
msg.Text = msg.text
push(msg)
</py> constant msg
 __main__ :> predict(v('msg')) . cr


\ 完整設定過程，讓 UUT 回覆它的畫面經由 itchat bot 傳給 AILAB Chatroom.
\ 讓遠端可以來監看執行狀況。這段程式是由遠端灌過來給 UUT 的。
    @秀。。 This line will be ignored 
    \ get itchat module object
    py> sys.modules['itchat'] constant itchat // ( -- module ) WeChat automation
    \ get PIL graph tool
    import PIL.ImageGrab constant im // ( -- module ) PIL.ImageGrab
    \ get AILAB chatroom object through partial nickName 
    itchat :> search_chatrooms('AILAB')[0] constant ailab // ( -- obj ) AILAB chatroom object
    \ Define check command that checks the UUT desktop screenshot
    import time constant time // ( -- module )
    cr time :> ctime() . cr \ print recent time on UUT when making this setting
    : check ( -- ) // check UUT
        time :: sleep(7) \ anti-robot delay time be always 7 seconds
        cr time :> ctime() . cr \ print the recent time on UUT 
        im :: grab().save("1.jpg") \ capture screenshot 
        ailab :> send("@img@1.jpg") \ send to AILAB chatroom 
        . cr \ shows the responsed message
        ;
    \ Define getfile command in case source code were modified on the UUT
    : getfile ( "pathname" -- ) // Get source code for debugging
        time :: sleep(7) py> str(pop()).strip() \ trim pathname 
        s" @fil@" swap + \ command string 
        cr time :> ctime() . space s" getfile: " . dup . cr
        ailab :> send(pop()) \ send to AILAB chatroom so everybody gets it
        . cr \ shows the responsed message
        ;
'''
