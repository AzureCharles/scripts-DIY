# scripts-DIY
## Azurelane Georgia-Formidable coordinator

This is a Georgia-Formidable coordinator based on the file:"可畏佐治亚调速计算器1.03.xlsx" from @玄虚小圣

原文链接与原理：
    https://wiki.biligame.com/blhx/%E5%8F%AF%E7%95%8F%E4%BD%90%E6%B2%BB%E4%BA%9A%E8%B0%83%E9%80%9F%E8%AE%A1%E7%AE%97%E5%99%A8
    
独立使用的话可以直接在最下方的用户定义区修改相关参数：

    #用户定义区
    
    PlayerTest = PlayerLoadData(4,15,0,19,0,0.08)  #在此定义用户外部装填加成，顺序为bstch_ld,bscat_ld,bsld_buff,cvtch_ld,cvcat_ld,cvld_buff
    
    mainGunName = 'WE_AP_SSR'    #在此定义目标主炮
    
    times = 4   #在此定义最大调速轮数
    
    Formidable = CarrierVessel(124,2,3,3)   #初始化可畏,
    #beaconFlag = False	#是否携带信标 #单独使用的话把这句解注释，再注释掉下面的for循环即可
    Georgia = Battleship(173,BATTLESHIP_GUN[mainGunName])   #初始化携带指定主炮的佐治亚
    
    targetTorpedo = '流星'	#在此定义目标鱼雷机  #这句是对应固定鱼雷机查询的参数指定，不需要的话可注释掉这句
    
4月9日的版本支持目前大多数主流战列主炮和舰载机（主要是金装），比1.03的xlsx表支持更多。如果有自己感兴趣的装备，直接在文件开头的3个字典里依照格式添加数据即可，需要注意的是主炮计算的时候是手动指定的。
    
后续可能有其他功能比如伤害计算或者更傻瓜化的一键式分析什么的，姑且先集成起来了。目前可能会有点过耦合，调用的时候层次太多什么的（自己写的时候已经发现了，笑）
    
enjoy the game~
