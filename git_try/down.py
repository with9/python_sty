# -*- coding: utf-8 -*-
import urllib.request
import re
import time
import os
from multiprocessing import Pool
import multiprocessing
def get_cookies():
    return open("cookie.txt").readline()
global cookies
cookies=get_cookies()
def find_rank(page):#通过每日排行榜获取最新没张图的链接，保存为一个列表
    url="https://www.pixiv.net/ranking_area.php?type=detail&no="+str(page)
    req=urllib.request.Request(url)
    req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
    html=urllib.request.urlopen(req).read().decode('utf-8')
    reg = r'<h2><a href="(.*?)">'#正则表达式查找到id所在的网址
    list_img=re.findall(reg,html)
    rank_place=['北海道_东北','关东','中部','近畿','中国_四国','九州_冲绳','国际']
    txt_name=str(time.strftime('%Y_%m_%d',time.localtime(time.time())))+str(rank_place[page])+'.txt'
    #新建一个文本文档用于存储id信息，文件名是程序运行的时间,加上对应排行榜的标题
    if os.path.exists('V:/picture/rank_list/'+txt_name):
        os.remove('V:/picture/rank_list/'+txt_name)#先移除旧文档，再新建，防止信息重复
    for i in list_img: 
            with open('V:/picture/rank_list/'+ txt_name, 'a')as f:
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
        req.add_header("Cookie",cookies)
        #添加头文件信息
        html=urllib.request.urlopen(req).read().decode('utf-8')
        reg2=r'<img src="https://i.pximg.net/c/600x600/(.*?)" alt='#正则表达式查看图片具体位置
        list_img=re.findall(reg2,html)
        reg3="一次性投稿多张作品"
        complex_img=re.findall(reg3,html)
        if len(list_img)>0:#代码测试发现存在无法找到图片的情况，经过验证应该是因为投稿的是动图,实现每次意外会将自动下载一张⑨！
            if complex_img:
                print("该作品有多张，仅下载第一张",end="\t")
                return("https://i.pximg.net/"+list_img[0])#漫画地址不同，故进行判断
            else:
                img_place=list_img[0][11:-18]
                return('https://i.pximg.net/img-original/'+img_place+"_p0.jpg")#获取真实原图
        else:
            print('恭喜你，多了个⑨',end='\t')
            return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
    except:
        print("似乎作者删除了这个图片,恭喜你又多个⑨",end='\t')#作者删除图片的话会404
        return('https://i.pximg.net/img-original/img/2012/07/25/05/39/57/28864480_p0.jpg')
def down_img(img_place,img_id,txt_name,count):
    try:
        url=str(img_place)
        req=urllib.request.Request(url)
        req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        img=urllib.request.urlopen(req).read()
    except:
        #对jpg与png进行判断
        url=url[:-3]+"png"
        req=urllib.request.Request(url)
        req.add_header('Referer','https://www.pixiv.net/ranking_area.php?type=detail&no=6')
        req.add_header("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        img=urllib.request.urlopen(req).read()   
    with open('V:/picture/'+txt_name+r'/'+img_id+'.jpg','wb')as f:
        print('正在下载图片%9s' %img_id,end='\t')
        f.write(img)
        print('下载完成')
        count=count+1
    return count
def main(page):
    count=0
    for i in find_rank(page):
        txt_name=str(time.strftime('%Y_%m_%d',time.localtime(time.time())))
        file_name='V:/picture/'+txt_name+r'/'+i+'.jpg'#以id保存图片
        if os.path.exists(file_name):
            print('id%9s图片已存在，正在跳过' %i) #检查图片是否已存在，防止重复下载
        else:
            count=down_img(find_img(i),i,txt_name,count)
    return count
if __name__=="__main__":
    start_time=time.time()
    stt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time))
    txt_name=str(time.strftime('%Y_%m_%d',time.localtime(time.time())))
       #新建文件夹用于保存每日的图片
    if int(os.path.exists('V:/picture/'+txt_name))==0:
        print('正在创建目录%s' %txt_name,end='\t')
        os.makedirs('V:/picture/'+txt_name)
        print('创建完成')
    if int(os.path.exists('V:/picture/rank_list'))==0:
        os.makedirs('V:/picture/rank_list')
    pool=Pool()
    counts=(pool.map(main,range(7)))#每页分别计数，最后返回一个数目列表
    count=0
    print(counts)
    for i in counts:
        count=count+i#对列表进行统计
    end_time=time.time()
    edt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time))
    print('已完成全部下载，谢谢使用，本次下载%3d图片' %count)
    print('开始下载的时间是%s\n结束下载的时间是%s' %(stt,edt))
    process=(end_time-start_time)/60
    print('本次下载耗时%.2f分钟' %process)
    with open('V:/picture/'+txt_name+'/''log.txt','a')as f:
        f.write('已完成全部下载，谢谢使用，本次下载%3d图片\n开始下载的时间是%s\n结束下载的时间是%s\n下载耗时%.2f分钟\n' %(count,stt,edt,process))#生成日志文件保存下载信息
    os.system('V:/picture/'+txt_name+'/''log.txt')
#不足：漫画只可以保存第一张，虽然将动图替换保存为了琪露诺，但是无法获取动图，其次对于png格式图片无法获取到真是原图。
#目前可以获得真实原图了，漫画的情况还要等等看、
