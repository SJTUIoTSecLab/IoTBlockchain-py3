
# coding: utf-8
import threading
import numpy
class LSP(object):
    def __init__(self,address,c_id):
        self.lock = threading.Lock()
        self.node_id=c_id
        self.basetable=[address[0],address[1]]#'age'://,'seq'://待加入
        self.neighbourip=[]
        self.neighbourport=[]
        self.neighbourdistance=[]
        self.neighbourid=[]
        self.lsp=[]
        self.flag=0#判断是否发送过lsp信息，0未发送
        self.flagg=0#判断是否还能接受lsp信息，0为还可以
        self.message=[]#[msg_bytes,"sendrequest"]
        self.lspgroup=[]# 保存收到的lsp
        self.rootList=[]


        self.dictlsp={}#lsp字典
        self.num=0 #distriction
        self.grouper=[]#根节点特有的储存组员信息
        self.tree=[]
        self.messagestart=[]#用里面的信息标识该节点是否为发起节点
    


    def check(self,message):#判断是否在messagestart
        if self.messagestart==[]:
            return False
        for k in range(len(self.messagestart)):
            if self.messagestart[k]==message:
               return True
        return False



    def judnei(self,node):#判断node是否在邻居中
        flag=0
        k=len(self.neighbourip)
	#for i in range(k):c3/p
		#ip=self.neighbourip[i]
		#if node.ip==ip:   todo格式会改变
        for j in range(k):
                 port=self.neighbourport[j]
                 if node.port==port:
                     flag=1
        return flag
		

    def generatelsp(self):
        #生成lsp的函数
	#print "mark num of nei"
	
        k=len(self.neighbourip)
	#print k
        mid=[]
        for x in range(k):
            node=(self.neighbourip[x],self.neighbourport[x])
            mid.append(node)
        self.lsp.append(self.basetable)
        self.lsp.append(mid)
        self.lsp.append(self.neighbourdistance)
	


    def dictlspfun(self):
        #将lspgroup字典化{0:'ip,port',1:'ip,port'}
        k=len(self.lspgroup)
        self.dictlsp[0]=(self.basetable[0],self.basetable[1])
        for x in range(k):
            m=self.lspgroup[x][0]#[ip,port]
            node=(m[0],m[1])
            #检查node是否已经在字典中
            if not node==self.dictlsp[0]:
                  self.dictlsp[x+1]=node  #(ip,port)

        
    def solvetree(self):
        ##进入solvetree后不能再接受lsp信息
        self.flagg=1
        self.dictlspfun()#lspgroup字典化
        #生成所有信息得到的矩阵树
        s=list(self.dictlsp)
        k=len(s)-1
	#print "mark len of tree"
	#print k
        c=numpy.zeros([k+1,k+1],dtype=int) 
        #第0行的赋值
        for i in range(k+1): #row
            if i<len(self.neighbourdistance):
		#确定对应的node
                node=(self.neighbourip[i],self.neighbourport[i])
		#确定字典中的对应序号
                num=0
                for num in range(k+1):
                         print ("dict:",self.dictlsp,"num",num)
                         if self.dictlsp[num]==node:
                                break
		
                c[0][num]=self.neighbourdistance[i]
                c[num][0]=self.neighbourdistance[i]
        #其余行的赋值,使用字典进行
        for i in range(k+1):
            if i!=0:
                #行坐标为i，对应lspgroup中的第i-1个
                m=self.lspgroup[i-1]#self.lsp=[self.basetable,[(ip,port),(ip,port)],self.neighbourdistance]
                v=len(m[1])
                for x in range(v) :#[(ip,port),(ip,port)],中找到对应的node
                    edge=m[2][x]
                    node=m[1][x]
                    num=0
                    #将该Node在字典中的序号找到，记为num
                    for num in range(k+1):#假设字典记录了所有节点
                        if self.dictlsp[num]==node:
                            break
                    c[i][num]=edge
                    c[num][i]=edge               #检查
        print ("lspgroup生成的树")
        print (c)
        self.tree=c

        #将不在该区的点排除
        for i in range(k+1):
            node=self.dictlsp[i]
            flag=0
            for subnode in self.grouper: #如果点不在辖区内
                  if subnode==node:#点在辖区内
                      flag=1
                      break

            if flag==0: #如果点不在辖区内,边置换为无穷大
               for num in range(k+1):
                  c[i][num]=10000
                  c[num][i]=10000
            
                     

        #根据k+1*k+1的树c生成最小生成树
        #最小生成矩阵d
        d=numpy.zeros([k+1,k+1],dtype=int)
        involved=[0]
        notin=[]
        for i in range(k):
            notin.append(i+1)
        print("notin",notin)
        while notin: #notin非空
            #一次查找
            flag1=0 #记录involved中最小路径的位置
            flag2=0#记录notin中
            short=10000
            for i in range(len(involved)):#可能计数有问题
                j=involved[i]  #j为行坐标
                for n in range(len(notin)):
                    m=notin[n] #m为列坐标
                    if c[j][m]<short and c[j][m]!=0:
                        short=c[j][m]
                        flag1=i
                        flag2=n
            #notin中删除第n个，invovled中加入notin的第n个
            d[involved[flag1]][notin[flag2]]=short#更新最小生成树
            d[notin[flag2]][involved[flag1]]=short#更新最小生成树
            involved.append(notin[flag2])
            notin.pop(flag2)
            self.tree=d#将树记忆
        return d

    def locate(self,lspdict):#返回自己在字典中的序号
        node=(self.basetable[0],self.basetable[1])
        for i in range(len(lspdict)):
            if node==lspdict[i]:
                break
        return i

    def findkids(self,lspdict,d):#根据收到的路由表整理出自己的kids[(ip,port),(ip,port)]#todo根据发送信息路径在kids中删除父亲节点，父亲节点发送时处理路由表删除表中父亲到孩子的路径
	#print "mark d(最小生成树矩阵)"
	#print  d
        mynum=self.locate(lspdict)#找到该节点在字典中的序号
	#print "mark mynum in findikids"
	#print mynum
        kids=[]
        for i in range(len(lspdict)):  
            #找到自己的子节点编号
            if d[mynum][i]!=0 and d[mynum][i]!=10000:
                #i是子节点
                kids.append(lspdict[i])
	
	#删除父节点在kids中的存在
	
        #print ("kids:")
        #print (kids)
        return kids


    def length(self):
        leng=len(self.neighbourport)
        return leng


    def insert(self,node):#插入新节点
        if self.node_id == node.node_id:
            return
        if self.length()>10:#to change
            return
        with self.lock:
            ip=node.ip
            self.neighbourip.append(ip)
            port=node.port
            self.neighbourport.append(port)
            _id=node.node_id
            self.neighbourid.append(_id)

    def get_all_nodes(self):     
        all_nodes = []
        for port in self.neighbourport:
            all_nodes.append(port)
           
        return all_nodes

    def deletenode(self,tree,lspdict):
        mynum=self.locate(lspdict)#找到该节点在字典中的序号
        k=len(lspdict)
        for i in range(k):
                tree[mynum][i]=0
                tree[i][mynum]=0
        return tree
  
    def addmessage(self,message):
        self.message.append(message)
        
