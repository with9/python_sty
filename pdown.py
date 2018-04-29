# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import re
import time
import os
import requests
from bs4 import BeautifulSoup
def judge_user():#获取cookie并判断
    global user_name
    global cookies
    cookies=input("请输入cookie信息，如不输入可以直接跳过，但是无法获取收藏夹及标签查找：")
    url="https://www.pixiv.net/"
    headers={"Cookie":cookies}
    html=requests.get(url,headers=headers).text
    req=r'"href="/member.php.id=(\d*)"style="background-image'
    req2=r'</a><div class="user-name-container"><a class="user-name js-click-trackable-later"href="/member.php.id=\d*"data-click-category="mypage-profile-column-simple"data-click-action="click-profile"data-click-label="">(.*?)</a></div>'
    user_id=re.findall(req,html)
    if user_id:
        user_name=re.findall(req2,html)[0]
        print("欢迎用户--%s--"%user_name)
    else:
        print("cookie有误，将使用默认账号登录")
        user_name="默认账号"
        f=open("cookie.txt","r")
        cookies=f.readline()
        f.close()
    global url_root,judge_number
    url_root="https://www.pixiv.net/bookmark.php?rest=show&p="
    judge_number=0
def book_mark():
    def find_page():#查找收藏夹的作品数
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Connection":"keep-alive",
        "Cookie":cookies}    
        url=url_root+str(1)
        html=requests.get(url,headers=headers).text
        reg=r'<span class="count-badge">(\d*)件</span></div>'
        page=re.findall(reg,html)
        print("--------------------------------------------------共找到%s个作品--------------------------------------------------"%page[0])        
        return page[0]
    def find_rank(page):#查找图片的id，返回一个列表
        url=url_root+str(page)
        req=urllib.request.Request(url)
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        req.add_header("Connection","keep-alive") 
        req.add_header("Cookie",cookies)
        html=urllib.request.urlopen(req).read().decode('utf-8')
        reg = r'<a href="member_illust.php.mode=medium&amp;illust_id=(\d*)"><h1 class="title'#正则表达式查找到id所在的网址
        list_id=re.findall(reg,html)
        return list_id
    def judge_like(img_id,txt_name):#判断图片的点赞数，本来是打算收藏数的，但是没有会员（
        print("正在判断%s"%img_id,end="\t")
        try:
            url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(img_id)
            req=urllib.request.Request(url)
            req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
            req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
            html=urllib.request.urlopen(req).read().decode('utf-8')
            reg2=r'class="views">(\d*)</span></li></ul>'#正则表达式查看赞数
            list_like=re.findall(reg2,html)
            text_name=str(time.strftime('%Y_%m_%d',time.localtime(time.time())))+'.txt'
            print("喜欢程度：%s"%list_like[0])
            with open('picture/'+txt_name+'/rank_list/'+ text_name, 'a')as f:
                f.write('https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+img_id+'\n'+'like:'+list_like[0]+"\n")
            if int(list_like[0])>=judge_number:#进行参数判断    
                with open('picture/'+txt_name+'/rank_list/'+"喜爱"+str(judge_number)+"#"+text_name, 'a')as f:
                    f.write('https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+img_id+'\n'+'like:'+list_like[0]+"\n")
                    return 1
        except:
            return 0
            
    def find_img(rank_id):#通过图片所在页面查找图片具体位置
        try:
            url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(rank_id)
            req=urllib.request.Request(url)
            req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
            req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
            req.add_header("Connection","keep-alive") 
            req.add_header("Cookie",cookies)
            html=urllib.request.urlopen(req).read().decode('utf-8')
            reg2=r'<img src="https://i.pximg.net/c/600x600/(.*?)" alt='#正则表达式查看图片具体位置
            list_img=re.findall(reg2,html)
            if len(list_img)>0:#代码测试发现存在无法找到图片的情况，经过验证应该是因为投稿的是动图,实现每次意外会将自动下载一张⑨！
                img_place=list_img[0]
                return('https://i.pximg.net/'+img_place)
            else:
                print('恭喜你，多了个⑨',end='\t')
                return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
        except:
            print("似乎作者删除了这个图片,恭喜你又多个⑨",end='\t')#作者删除图片的话会404，无权限也会（
            return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
    def down_img(img_place,img_id,count,txt_name):#下载图片
        url=str(img_place)
        req=urllib.request.Request(url)
        req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        req.add_header("Connection","keep-alive") 
        req.add_header("Cookie",cookies)
        img=urllib.request.urlopen(req).read()
        with open('picture/'+txt_name+r'/'+img_id+'.jpg','wb')as f:
            print('正在下载图片%9s' %img_id,end='\t')
            f.write(img)
            print('下载完成')
            count=count+1
        return count
    count=0
    start_time=time.time()
    stt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time))
    txt_name=user_name+"/"+"收藏"
    #新建文件夹用于保存每日的图片
    if int(os.path.exists('picture/'+txt_name))==0:
        print('正在创建目录%s' %txt_name,end='\t')
        os.makedirs('picture/'+txt_name)
        print('创建完成')
    if int(os.path.exists('picture/'+txt_name+'/rank_list'))==0:
        os.makedirs('picture/'+txt_name+'/rank_list')
    global skip_number
    skip_number=1
    pages=int(find_page())//20+2
    if skip_number:
        for page in range(1,pages):
            if skip_number:
                print("------------------正在下载第%d页，共有%d页------------------" %(page,pages-1))
                for i in find_rank(page):
                    if skip_number:
                        file_name='picture/'+txt_name+r'/'+i+'.jpg'#以id保存图片
                        if os.path.exists(file_name):
                            log_path="picture/"+txt_name+"/"+"log.txt"
                            if os.path.exists(log_path):
                                skip_number=0
                                print("已完成对该收藏夹的下载")
                            else:
                                print('id%9s图片已存在，正在跳过' %i) #检查图片是否已存在，防止重复下载
                        else:
                            if skip_number:
                                if judge_like(i,txt_name):
                                    if skip_number:
                                        count=down_img(find_img(i),i,count,txt_name)
    end_time=time.time()
    edt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time))
    print('已完成全部下载，谢谢使用，本次下载%3d图片' %count)
    print('开始下载的时间是%s\n结束下载的时间是%s' %(stt,edt))
    process=(end_time-start_time)/60
    print('本次下载耗时%.2f分钟' %process)
    with open('picture/'+txt_name+'/''log.txt','a')as f:
        f.write('已完成全部下载，谢谢使用，本次下载%3d图片\n开始下载的时间是%s\n结束下载的时间是%s\n下载耗时%.2f分钟\n' %(count,stt,edt,process))#生成日志文件保存下载信息
    os.system('picture/'+txt_name+'/''log.txt')
    #不足：漫画只可以保存第一张，虽然将动图替换保存为了琪露诺，但是无法获取动图，其次对于png格式图片无法获取到真是原图。
def p_tag():#获取用户指定的tag图片的函数
    global url_root,judge_number
    search_word=input("请输入搜索tag:")
    words=urllib.parse.quote(search_word)
    url_root="https://www.pixiv.net/search.php?word="+words+"&order=date_d&p="
    judge_number=int(input("请输入判断数：(必须为整型，否则会崩溃）"))
    def find_page():#查找页码
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Connection":"keep-alive",
        "Cookie":cookies}    
        url=url_root+str(1)
        html=requests.get(url,headers=headers).text
        reg=r'(\d*)件投稿'
        page=re.findall(reg,html)
        print("--------------------------------------------------共找到%s个作品--------------------------------------------------"%page[0])        
        return page[0]
    def find_rank(page):#获取图片的id
        url=url_root+str(page)
        req=urllib.request.Request(url)
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        req.add_header("Connection","keep-alive") 
        req.add_header("Cookie",cookies)
        html=urllib.request.urlopen(req).read().decode('utf-8')
        reg =r'{&quot;illustId&quot;:&quot;(\d*)&quot;,&quot;illustTitle'#正则表达式查找到id所在的网址
        list_id=re.findall(reg,html)
        time.sleep(0.5)
        return list_id
    def judge_like(img_id,txt_name):#判断赞数
        print("正在判断%s"%img_id,end="\t")
        url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(img_id)
        req=urllib.request.Request(url)
        req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        html=urllib.request.urlopen(req).read().decode('utf-8')
        reg2=r'class="views">(\d*)</span></li></ul>'#正则表达式查看赞数
        list_like=re.findall(reg2,html)
        text_name=str(time.strftime('%Y_%m_%d',time.localtime(time.time())))+'.txt'
        print("喜欢程度：%s"%list_like[0])
        with open('picture/'+txt_name+'/rank_list/'+ text_name, 'a')as f:
            f.write('https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+img_id+'\n'+'like:'+list_like[0]+"\n")
        if int(list_like[0])>=judge_number: 
            return 1
            
    def find_img(rank_id):
        try:
            url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(rank_id)
            req=urllib.request.Request(url)
            req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
            req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
            req.add_header("Connection","keep-alive") 
            req.add_header("Cookie",cookies)
            html=urllib.request.urlopen(req).read().decode('utf-8')
            reg2=r'<img src="https://i.pximg.net/c/600x600/(.*?)" alt='#正则表达式查看图片具体位置
            list_img=re.findall(reg2,html)
            if len(list_img)>0:#代码测试发现存在无法找到图片的情况，经过验证应该是因为投稿的是动图,实现每次意外会将自动下载一张⑨！
                img_place=list_img[0]
                return('https://i.pximg.net/'+img_place)
            else:
                print('恭喜你，多了个⑨',end='\t')
                return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
        except:
            print("似乎作者删除了这个图片,恭喜你又多个⑨",end='\t')#作者删除图片的话会404
            return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
    def down_img(img_place,img_id,count,txt_name):
        url=str(img_place)
        req=urllib.request.Request(url)
        req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        req.add_header("Connection","keep-alive") 
        req.add_header("Cookie",cookies)
        img=urllib.request.urlopen(req).read()
        with open('picture/'+txt_name+r'/'+img_id+'.jpg','wb')as f:
            print('正在下载图片%9s' %img_id,end='\t')
            f.write(img)
            print('下载完成')
            count=count+1
            time.sleep(0.5)
        return count

    count=0
    start_time=time.time()
    stt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time))
    txt_name=input("输入文件名(默认为D盘picture下的目录）")
    txt_name=user_name+"/"+txt_name
    #新建文件夹用于保存每日的图片
    if int(os.path.exists('picture/'+txt_name))==0:
        print('正在创建目录%s' %txt_name,end='\t')
        os.makedirs('picture/'+txt_name)
        print('创建完成')
    if int(os.path.exists('picture/'+txt_name+'/rank_list'))==0:
        os.makedirs('picture/'+txt_name+'/rank_list')
    pages=int(find_page())//40+2
    for page in range(1,pages):
        print("------------------正在下载第%d页，共有%d页------------------" %(page,pages-1))
        for i in find_rank(page):
            file_name='picture/'+txt_name+r'/'+i+'.jpg'#以id保存图片
            if os.path.exists(file_name):
                print('id%9s图片已存在，正在跳过' %i) #检查图片是否已存在，防止重复下载
            else:
                if judge_like(i,txt_name):
                    count=down_img(find_img(i),i,count,txt_name)
    end_time=time.time()
    edt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time))
    print('已完成全部下载，谢谢使用，本次下载%3d图片' %count)
    print('开始下载的时间是%s\n结束下载的时间是%s' %(stt,edt))
    process=(end_time-start_time)/60
    print('本次下载耗时%.2f分钟' %process)
    with open('picture/'+txt_name+'/''log.txt','a')as f:
        f.write('已完成全部下载，谢谢使用，本次下载%3d图片\n开始下载的时间是%s\n结束下载的时间是%s\n下载耗时%.2f分钟\n' %(count,stt,edt,process))#生成日志文件保存下载信息
    os.system('picture/'+txt_name+'/''log.txt')
def get_rank():#获取排行榜的函数1
    def find_rank(page):#通过每日排行榜获取最新没张图的链接，保存为一个列表
        url="https://www.pixiv.net/ranking_area.php?type=detail&no="+str(page)
        req=urllib.request.Request(url)
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        html=urllib.request.urlopen(req).read().decode('utf-8')
        reg = r'<h2><a href="(.*?)">'#正则表达式查找到id所在的网址
        list_img=re.findall(reg,html)
        rank_place=['北海道_东北','关东','中部','近畿','中国_四国','九州_冲绳','国际']
        text_name=str(rank_place[page])+'.txt'
        #新建一个文本文档用于存储id信息，文件名是程序运行的时间,加上对应排行榜的标题
        if os.path.exists('picture/'+txt_name+'/rank_list/'+text_name):
            os.remove('picture/'+txt_name+'/rank_list/'+text_name)#先移除旧文档，再新建，防止信息重复
        for i in list_img: 
                with open('picture/'+txt_name+'/rank_list/'+text_name, 'a')as f:
                    f.write('https://www.pixiv.net/'+i+'\n')
        rank_id=[]#创建一个空列表用于储存id
        for i in list_img:
            rank_id.append(i.split('=')[-1])
        return rank_id
    def find_img(rank_id):
        try:
            url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(rank_id)
            req=urllib.request.Request(url)
            req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
            req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
            #添加头文件信息
            html=urllib.request.urlopen(req).read().decode('utf-8')
            reg2=r'<img src="https://i.pximg.net/c/600x600/(.*?)" alt='#正则表达式查看图片具体位置
            list_img=re.findall(reg2,html)
            if len(list_img)>0:#代码测试发现存在无法找到图片的情况，经过验证应该是因为投稿的是动图,实现每次意外会将自动下载一张⑨！
                img_place=list_img[0]
                return('https://i.pximg.net/'+img_place)
            else:
                print('恭喜你，多了个⑨',end='\t')
                return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
        except:
            print("似乎作者删除了这个图片,恭喜你又多个⑨",end='\t')#作者删除图片的话会404
            return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
    def down_img(img_place,img_id,count,txt_name):
        url=str(img_place)
        req=urllib.request.Request(url)
        req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        img=urllib.request.urlopen(req).read()
        with open('picture/'+txt_name+r'/'+img_id+'.jpg','wb')as f:
            print('正在下载图片%9s' %img_id,end='\t')
            f.write(img)
            print('下载完成')
            count=count+1
        return count

    count=0
    start_time=time.time()
    stt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time))
    global txt_name
    txt_name=str(time.strftime('%Y_%m_%d',time.localtime(time.time())))
    txt_name="rank/" +txt_name
    #新建文件夹用于保存每日的图片
    if int(os.path.exists('picture/'+txt_name))==0:
        print('正在创建目录%s' %txt_name,end='\t')
        os.makedirs('picture/'+txt_name)
        print('创建完成') 
    if int(os.path.exists('picture/'+txt_name+'/rank_list'))==0:
        os.makedirs('picture/'+txt_name+'/rank_list')
    for page in range(7):
        for i in find_rank(page):
            file_name='picture/'+txt_name+r'/'+i+'.jpg'#以id保存图片
            if os.path.exists(file_name):
                print('id%9s图片已存在，正在跳过' %i)
            else:
                count=down_img(find_img(i),i,count,txt_name)
    end_time=time.time()
    edt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time))
    print('已完成全部下载，谢谢使用，本次下载%3d图片' %count)
    print('开始下载的时间是%s\n结束下载的时间是%s' %(stt,edt))
    process=(end_time-start_time)/60
    print('本次下载耗时%.2f分钟' %process)
    with open('picture/'+txt_name+'/''log.txt','a')as f:
        f.write('已完成全部下载，谢谢使用，本次下载%3d图片\n开始下载的时间是%s\n结束下载的时间是%s\n下载耗时%.2f分钟\n' %(count,stt,edt,process))#生成日志文件保存下载信息
    os.system('picture/'+txt_name+'/''log.txt')
    #不足：漫画只可以保存第一张，虽然将动图替换保存为了琪露诺，但是无法获取动图，其次对于png格式图片无法获取到真是原图。
def art_collect(art_id):#保存收藏夹函数
    global url_root,judge_number
    url_root="https://www.pixiv.net/member_illust.php?id="+art_id+"&type=all&p="
    judge_number=0
    def find_page():#查找收藏夹的作品数
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Connection":"keep-alive",
        "Cookie":cookies}    
        url=url_root+str(1)
        html=requests.get(url,headers=headers).text
        reg=r'</a></h1><span class="count-badge">(\d*)件</span>'
        page=re.findall(reg,html)
        print("--------------------------------------------------共找到%s个作品--------------------------------------------------"%page[0])        
        return page[0]
    def find_rank(page):#查找图片的id，返回一个列表
        url=url_root+str(page)
        req=urllib.request.Request(url)
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        req.add_header("Connection","keep-alive") 
        req.add_header("Cookie",cookies)
        html=urllib.request.urlopen(req).read().decode('utf-8')
        reg = r'<li class="image-item"><a href="/member_illust.php.mode=medium&amp;illust_id=(\d*)"class'#正则表达式查找到id所在的网址
        list_id=re.findall(reg,html)
        return list_id
    def judge_like(img_id,txt_name):#判断图片的点赞数，本来是打算收藏数的，但是没有会员（
        print("正在判断%s"%img_id,end="\t")
        try:
            url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(img_id)
            req=urllib.request.Request(url)
            req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
            req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
            html=urllib.request.urlopen(req).read().decode('utf-8')
            reg2=r'class="views">(\d*)</span></li></ul>'#正则表达式查看赞数
            list_like=re.findall(reg2,html)
            text_name=str(time.strftime('%Y_%m_%d',time.localtime(time.time())))+'.txt'
            print("喜欢程度：%s"%list_like[0])
            with open('picture/'+txt_name+'/rank_list/'+ text_name, 'a')as f:
                f.write('https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+img_id+'\n'+'like:'+list_like[0]+"\n")
            if int(list_like[0])>=judge_number:#进行参数判断    
                return 1
        except:
            return 0
            
    def find_img(rank_id):#通过图片所在页面查找图片具体位置
        try:
            url='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(rank_id)
            req=urllib.request.Request(url)
            req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
            req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
            req.add_header("Connection","keep-alive") 
            req.add_header("Cookie",cookies)
            html=urllib.request.urlopen(req).read().decode('utf-8')
            reg2=r'<img src="https://i.pximg.net/c/600x600/(.*?)" alt='#正则表达式查看图片具体位置
            list_img=re.findall(reg2,html)
            if len(list_img)>0:#代码测试发现存在无法找到图片的情况，经过验证应该是因为投稿的是动图,实现每次意外会将自动下载一张⑨！
                img_place=list_img[0]
                return('https://i.pximg.net/'+img_place)
            else:
                print('恭喜你，多了个⑨',end='\t')
                return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
        except:
            print("似乎作者删除了这个图片,恭喜你又多个⑨",end='\t')#作者删除图片的话会404，无权限也会（
            return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
    def down_img(img_place,img_id,count,txt_name):#下载图片
        url=str(img_place)
        req=urllib.request.Request(url)
        req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        req.add_header("Connection","keep-alive") 
        req.add_header("Cookie",cookies)
        img=urllib.request.urlopen(req).read()
        with open('picture/'+txt_name+r'/'+img_id+'.jpg','wb')as f:
            print('正在下载图片%9s' %img_id,end='\t')
            f.write(img)
            print('下载完成')
            count=count+1
        return count
    def find_art_name():
        html=requests.get(url_root+str(1))
        soup=BeautifulSoup(html.text)
        art_name= soup.title.string.split("」")[0].split("「")[1]#获取画师名称
        return art_name
    count=0
    start_time=time.time()
    stt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time))
    txt_name="画师投稿/"+find_art_name()+"("+art_id+")"
    try:
        if int(os.path.exists('picture/'+txt_name))==0:
            print('正在创建目录%s' %txt_name,end='\t')
            os.makedirs('picture/'+txt_name)
            print('创建完成')
    except:
        txt_name="画师投稿/"+"id_"+"("+art_id+")"
        if int(os.path.exists('picture/'+txt_name))==0:
            print('正在创建目录%s' %txt_name,end='\t')
            os.makedirs('picture/'+txt_name)
            print('创建完成')
    if int(os.path.exists('picture/'+txt_name+'/rank_list'))==0:
        os.makedirs('picture/'+txt_name+'/rank_list')
    global skip_number#判断是否已经下载过该画师图集的标记
    skip_number=1
    pages=int(find_page())//20+2
    if skip_number:
        for page in range(1,pages):
            if skip_number:
                print("------------------正在下载第%d页，共有%d页------------------" %(page,pages-1))
                for i in find_rank(page):
                    file_name='picture/'+txt_name+r'/'+i+'.jpg'#以id保存图片
                    if os.path.exists(file_name):
                        log_path="picture/"+txt_name+"/"+"log.txt"
                        if os.path.exists(log_path):
                            print("已完成对该画师图片的下载")
                            skip_number=0
                            break
                        else:
                            print('id%9s图片已存在，正在跳过' %i) #检查图片是否已存在，防止重复下载
                    else:
                        if skip_number:
                            if judge_like(i,txt_name):
                                if skip_number:
                                    count=down_img(find_img(i),i,count,txt_name)
    end_time=time.time()
    edt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time))
    print('已完成全部下载，谢谢使用，本次下载%3d图片' %count)
    print('开始下载的时间是%s\n结束下载的时间是%s' %(stt,edt))
    process=(end_time-start_time)/60
    print('本次下载耗时%.2f分钟' %process)
    with open('picture/'+txt_name+'/''log.txt','a')as f:
        f.write('已完成全部下载，谢谢使用，本次下载%3d图片\n开始下载的时间是%s\n结束下载的时间是%s\n下载耗时%.2f分钟\n' %(count,stt,edt,process))#生成日志文件保存下载信息
    os.system('picture/'+txt_name+'/''log.txt')
def find_artists():#查找用户关注画师，并下载画师作品
    def find_page():
        url="https://www.pixiv.net/bookmark.php?type=user&rest=show"
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Connection":"keep-alive",
        "Cookie":cookies}    
        html=requests.get(url,headers=headers).text
        reg=r'</a></h1><div class="unit-count">(\d*)</div>'
        page=re.findall(reg,html)
        print("--------------------------------------------------共找到%s个画师--------------------------------------------------"%page[0])        
        return int(page[0])//48+2
    def find_artists_id(page):
        artists_id=[]
        url="https://www.pixiv.net/bookmark.php?type=user&rest=show&p="+str(page)
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Connection":"keep-alive",
        "Cookie":cookies}    
        html=requests.get(url,headers=headers)
        soup=BeautifulSoup(html.text,"lxml")
        for i in soup.find_all("a","_user-icon size-75 cover-texture ui-profile-popup"):
            artists_id.append(i["data-user_id"])
        return artists_id
    pages=find_page()
    for page in range(1,pages):
        for i in find_artists_id(page):
            print("正在下载画师id=%s"%i)
            art_collect(i)
judge_user()


while True:
    cmd=input("请选择模式\n（1：获取排行榜，2：tag搜索，3：个人收藏夹保存，4：画师图片提取，5：个人关注画师作品下载，6：退出）")
    if cmd not in ["1","2","3","4","5","6"]:
        print("错误输入！")
        cmd=input("请重新输入")
    if cmd=="1":
        print("--------------------------------------------------进入排行榜获取模式--------------------------------------------------")
        get_rank()
    if cmd=="2":
        print("--------------------------------------------------进入tag搜索模式--------------------------------------------------")
        p_tag()
    if cmd=="3":
        print("--------------------------------------------------进入个人收藏夹保存模式--------------------------------------------------") 
        book_mark()
    if cmd=="4":
        print("--------------------------------------------------进入画师提取页面--------------------------------------------------")
        art_id=input("请输入画师id信息：")
        art_collect(art_id)
    if cmd=="5":
        print("--------------------------------------------------进入关注画师作品下载--------------------------------------------------")
        find_artists()
    if cmd=="6":
        print("--------------------------------------------------正在退出，谢谢使用--------------------------------------------------")
        break

