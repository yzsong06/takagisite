import aiohttp
import asyncio
import argparse
import random
import json
import time
import os

header={'Range': 'bytes=0-0','user-agent': "okhttp/3.10.0"}
email="sxceshi1" 
swdid="b4:cd:27:30:3e:f2"
lock = asyncio.Lock()

async def main(begin:int,end:int,threads:int):
    async with aiohttp.ClientSession() as session:
        print("begin:"+str(begin))
        print("end:"+str(end))
        print("threads:"+str(threads))
        temp=-1
        tasks= []
        for i in range(begin,end+1):
            temp+=1
            if temp==threads:
                temp=0
                task1=tasks
                tasks= []
                print("执行"+str(temp))
                await asyncio.wait(task1)
            task=asyncio.ensure_future(GetInfoExistsAndRun(session,i))
            tasks.append(task)
            print("部署："+str(temp))
        if len(tasks)!=0:
            print("收尾:"+str(temp))
            await asyncio.wait(tasks)

async def GetInfoExistsAndRun(session:aiohttp.ClientSession,id:int):
    url = "https://cloud.linspirer.com:883/download.php?email="+email+"&appid="+str(id)+"&swdid="+"4a"+"&version="+str(random.randint(1,9000000))
    realurl="Null"
    async with session.head(url,headers=header) as res:
        url1= res.headers.get('Location')
        if url1!=None:
            realurl=str(url1)
            await GetDetailInfo(session,id,realurl)
        else:
            await Inf2File(str(id),"Null","Null","Null","Null","Null","Null","Null","Null")    
            print(str(id)+":null")

async def GetDetailInfo(session:aiohttp.ClientSession,id:int,Realurl:str):
    print(f'GetDetailInfo{id} {Realurl}')
    async with session.post("https://cloud.linspirer.com:883/public-interface.php",headers=header,data=json.dumps(
        {"is_encrypt":False,"method":"com.linspirer.app.getappbyids","id":"1","!version":"1","jsonrpc":"2.0","params":{"swdid":swdid,"username":email,"token":"null","ids":[str(id)]},"client_version":"5.1.0","_elapsed":1}
        )) as res:
        data=json.loads(await res.text())
        if(data.get('code')!=0):
            print("account and swdid invaild!")
            await Inf2File(str(id),Realurl,"not support","not support","not support","not support","not support","not support","not support")
        else:
            datab=data.get('data')
            if(len(datab)==0):
                await Inf2File(str(id),Realurl,"not support","not support","not support","not support","not support","not support","not support")    
            else:
                for item in datab:
                    packagename=item.get('packagename')
                    targetapi=str(item.get('target_sdk_version'))
                    name=str(item.get('name'))
                    versionname=item.get('versionname')
                    versioncode=str(item.get('versioncode'))
                    md5sum=item.get('md5sum')
                    if item.get('sha1')==None:
                        sha1="no sha1"
                    else :
                        sha1=str(item.get('sha1'))
                    await Inf2File(str(id),Realurl,packagename,name,targetapi,versionname,versioncode,md5sum,sha1)


async def Download_and_parse(session:aiohttp.ClientSession,id:int,Realurl:str):
    print("Download_and_parse()")
    await Inf2File(str(id),Realurl,"not support","not support","not support","not support","not support","not support","not support")
    '''
    path=mkdir(f'temp')
    async with session.post(Realurl) as resp:
        with open(path+"/"+str(id)+".apk", 'wb') as fd:
            async for chunk in resp.content.iter_chunked(8192):
                fd.write(chunk)
        await PARSE(id,path+"/"+str(id)+".apk",Realurl)
    '''
    pass
'''
async def PARSE(id:int,path:str,Realurl:str):
    cmd_=os.system("aapt dump badging "+path)
    if cmd_==1:
        return -1
    
    _=subprocess.Popen("aapt dump badging "+path,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cmd=_.stdout.readlines()
    print("waiting")
    _.wait()
    _.stdout.close()
    print("closed")
    if "ERROR" in str(cmd[0]) or  "Error opening" in str(cmd[0]):
        return -1
    
    str_cmd=str(cmd[0]).split(' ')
    pkgname=str_cmd[1][6:-1]
    vercode=str_cmd[2][13:-1]
    vername=str_cmd[3][13:-1]
    print("write")
    await Inf2File(id,Realurl,pkgname,"",cmd[2][18:-2],vername,vercode,"","")
    os.remove(path)
'''


async def Inf2File(id:str,realurl:str,packageName:str,LabelName:str,targetApi:str,VersionName:str,VersionCode:str,md5sum:str,sha1:str):
    await lock.acquire()
    f = open("./result.csv", "a",encoding="utf-8") 
    f.write(id+","+realurl+","+packageName+","+LabelName+","+targetApi+","+VersionName+","+VersionCode+","+md5sum+","+sha1+"\n")           
    f.close()
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}] {id} {packageName} {VersionName}')
    lock.release()


def mkdir(path):
    is_exist = os.path.exists(path)
    if not is_exist:
        os.makedirs(path)
        return path
    return path


if __name__=="__main__":
    print("Laser 2.Powered by ljlVink")
    parser = argparse.ArgumentParser(description='Please run with at least 3 arguments.')
    parser.add_argument('begin_id', type=int, help='Start_id')
    parser.add_argument('end_id', type=int, help='End_id')
    parser.add_argument('threads', type=int, help='Threads Count')
    args = parser.parse_args()
    beg = args.begin_id
    end = args.end_id
    threads = args.threads

    loop = asyncio.get_event_loop()
    task = loop.create_task(main(beg,end,threads))
    loop.run_until_complete(task)
    print("exit.")