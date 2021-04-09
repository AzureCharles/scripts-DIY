import numpy as np
import pandas as pd
"""
# Azurelane simple tools
# updated on 2021年4月9日22:25:07
# This is a Georgia-Formidable coordinator based on the file:
    "可畏佐治亚调速计算器1.03.xlsx" from @玄虚小圣

# Developer's instructions(by @玄虚小圣):
    这个是用于给可畏-佐治亚这个组合调速用的（当然，其他战列也可以用，原理一样）
    调速原理介绍：
    ·可畏的时停有1.5秒，我们需要佐治亚的超重弹在这1.5秒内击中目标。
    ·考虑到一般战斗有3~4轮主炮，所以可畏不能比佐治亚快（可畏先起飞会导致佐治亚吃不到时停）也不能慢太多
    （碰上大凤这种高移动力boss的话，时停结束后的减速效果比时停差很多）
    ·另外注意，战列炮还有0.3秒的抬手前摇。

# 用法(by @玄虚小圣)：
    (1)首先，默认可畏第三格是+10的紫青花鱼，如果没这个鱼雷机的话，可畏废掉了自身输出，而且调速也麻烦
    (2)表格里输入佐治亚的面板CD（去舰船装备替换界面自己看）和可畏的面板装填（比如200好感是124）以及可畏受到的科技装填，和猫的装填（填入这两个的总和）
    (3)然后看下面的表格（分为带信标和不带信标两种），从里面找到符合调速区间的战/轰+鱼雷机组合

    #以上内容引自 哔哩哔哩Wiki-碧蓝海事局：http://wiki.biligame.com/blhx，
    
#原文链接：
    https://wiki.biligame.com/blhx/%E5%8F%AF%E7%95%8F%E4%BD%90%E6%B2%BB%E4%BA%9A%E8%B0%83%E9%80%9F%E8%AE%A1%E7%AE%97%E5%99%A8
    
#Dictionary:
    
    @CD: shorted as 'cool down time' ,即武器冷却时间；
    @beacon: Homing beacon T0,归航信标T0；
    
    @GeorgiaGun/Twi457mmMKAT0:   双联装457mmMKAT0主炮，即二期科研六星彩炮、佐治亚炮；
    @FriedrichGun/Twi406mmSKCT0: 双联装406mmSKCT0主炮，即二期科研速射高爆、大帝炮；
    @MK6_SR/Tri406mmMK6T3:       三联装406mmMK6T3主炮，即四星高爆白鹰炮、MK6；
    @MonarchGun/Tri381mmT0:      三联装381mmT0主炮，即一期科研高爆、君主炮；
    @IzumoGun/Tri410mmT0:        三联装410mmT0主炮，即一期科研穿甲、出云炮；
    @ChampagneGun/Tri406mm/50T0: 试作型三联装406mm/50主炮T0,即三期科研穿甲、香槟炮；
    @Tri406mmMkD:                试作型三联装406mm主炮MkD == WE_AP_SSR；
    @OdinGun/Tri305mmSKC39:      试作型三联装305mmSKC39主炮,即奥丁炮；

"""


BATTLESHIP_GUN = {'GeorgiaGun':20.65, 'FriedrichGun':19.42, 'MK6_SR':20.02,'MonarchGun':23.14, 'IzumoGun':24.14,
    'ChampagneGun':24.02,'WE_AP_SSR':24.21,'OdinGun':18.20,}  
    #主炮数据,以+10单面板为准
FIGHTER = {'天箭':8.98, '萨奇队':9.44, '零战52':9.52, 'VF-17海盗':10.20, '烈风':10.44, '海毒牙':10.60, '地狱猫':10.90,
        '海大黄蜂':10.61, '熊猫':9.64, '虎猫':10.81, }
BOOMBER = {'麦克拉斯基队':11.71, 'SB2C':11.88, 'XSB3C':11.90, '831中队':10.38}
TORPEDO = {'青花鱼':9.98, '梭鱼':10.31, '818中队':10.97, '流星':11.37, '火把':11.64, 'TBD(VT-8)':12.04, 
        'TBM(VT-18)':12.04, 'Ju-87':11.17, '飞龙':11.64}
    #舰载机数据,以+10单面板为准


def getWeaponCD(initial_spd, total_load):
    '''#武器实际冷却时间计算
    #initial_spd: 原始CD面板，取决于武器本身
    #total_load: 总装填面板，由以下部分构成：
        tchc_ld: 科研系统提供的装填
        cat_ld: 指挥猫提供的装填
        bship_ld: 舰船装填数值，默认值是120级佐治亚200好感的装填173
        bsld_buff: 装填buff
        total_load = (bship_ld+tchc_ld+cat_ld)*(1+bsld_buff)
    
    #影响武器攻击速度的不只是装填时间。
    以普通舰炮为例，攻击流程如下：
    武器装填时间→攻击前摇→开炮，并有炮击开火持续时间→攻击后摇→重新装填等下一轮攻击……

　　舰船装填面板值只影响装填时间，攻击动作为强制动画，无法缩短。

　　攻击前摇驱逐0.16s、轻巡0.18s、重巡0.2s

　　目前攻击后摇约为0.1s（20191211更新缩短了后摇时间，目前测试结果较多具体待定。修正后出现了新的卡炮问题，但这是正收益，即没有抬手动作也会强制开火的虚空开火状态，不同船在不同装填下，虚空开火的情况不同，每一艘船都要单独测定。）

    引自 哔哩哔哩Wiki-碧蓝海事局：http://wiki.biligame.com/blhx
    转载请保留原文链接：https://wiki.biligame.com/blhx/%E5%85%AC%E5%BC%8F%E5%90%88%E9%9B%86#.E6.88.98.E6.96.97.E7.9B.B8.E5.85.B3
    '''
    ld_effcy = pow(200/(total_load+100),0.5)
    weaponCD = ld_effcy * initial_spd
    
    return weaponCD



class CarrierVessel:
    '''
        航母类型，内置属性为装填属性值，舰载机携带数。
        默认围绕战列主炮进行调速，故舰载机作为外部属性输入
    '''
    def __init__(self,load,plane1_num,plane2_num,plane3_num):
        self.load = load
        self.plane1_num = int(plane1_num)
        self.plane2_num = int(plane2_num)
        self.plane3_num = int(plane3_num)
        
    def getAircraftInfo(self,plane1,plane2,plane3):
        aircraftCarried = {'Plane1':plane1, 'Plane2':plane2, 'Plane3':plane3}
        return aircraftCarried
        
    def getAverageAircraftCD(self,tchc_ld,cat_ld,cvld_buff,plane1_cd,plane2_cd,plane3_cd,beaconFlag=False):
        '''
            根据选取的飞机计算加权平均舰载机CD
        '''
        total_load = (self.load+tchc_ld+cat_ld)*(1+cvld_buff)
        ld_effcy = pow(200/(total_load+100),0.5)
        attack_roll = 0.1   #释放前摇
        
        if beaconFlag:
            beacon = 0.96
            
        else:
            beacon = 1.0
            

        averageAircraftCD = 2.2*beacon*(self.plane1_num*plane1_cd + self.plane2_num*plane2_cd + self.plane3_num*plane3_cd)/(self.plane1_num+self.plane2_num+self.plane3_num)*ld_effcy + attack_roll
        
        return averageAircraftCD
        

class Battleship:
    '''
        战列/战巡类型，内置属性为装填值和指定主炮的初始CD。
        默认围绕战列主炮进行调速，故主炮初始CD直接作为内置属性初始化
    '''
    def __init__(self,load,main_gun_cd):
        self.load = load
        self.main_gun_cd = main_gun_cd
        
    def getBattleshipInfo(self,main_gun):
        pass    #暂无相关需求
        
    def getMainGunCD(self,tchc_ld,cat_ld,bsld_buff):
        '''
           计算主炮装备面板
        '''
        total_load = (self.load+tchc_ld+cat_ld)*(1+bsld_buff)
        mainGunCD = getWeaponCD(self.main_gun_cd, total_load)
        
        return mainGunCD
        
        

class PlayerLoadData:
    '''
    	玩家外部装填数据
    '''
    def __init__(self,bstch_ld,bscat_ld,bsld_buff,cvtch_ld,cvcat_ld,cvld_buff):
        self.bstch_ld = bstch_ld
        self.bscat_ld = bscat_ld
        self.bsld_buff = bsld_buff
        self.cvtch_ld = cvtch_ld
        self.cvcat_ld = cvcat_ld
        self.cvld_buff = cvld_buff
        
    def getPlayerInfo(self,ship_type=0):
        if not ship_type:
            #cv_data:ship_type == 0
            return [self.cvtch_ld, self.cvcat_ld, self.cvld_buff]
        else:
            #bs_data:ship_type != 0
            return [self.bstch_ld, self.bscat_ld, self.bsld_buff]

      
class Coordinator:
	'''
		调速器类型,封装调速相关方法。
		*由于可畏调速必然绑定 plane3 = '青花鱼'，较为特殊，故暂时单列为独立方法。
	'''
	def getFormidableAircraft(PlayerLoadData,Battleship,CarrierVessel,times,beaconFlag=False):
	    '''
		    提供调速推荐配装结果
		    1.计算调速区间
		    2.遍历舰载机数据，计算舰载机平均CD,判定是否落在调速区间
		    3.记录落入调速区间的组合，加入DataFrame
		        
		    times: 调速轮数，即希望对几轮主炮进行调速
	    '''
	    #Default:Formidable skill_time = 1.5
	    global FIGHTER, BOOMBER, TORPEDO
	    skill_time = 1.5
	    attack_roll = 0.3
	    #attack_roll: Before the attack roll, 即攻击前摇
	    bsInfo = PlayerLoadData.getPlayerInfo(1)
	    lowerCD = Battleship.getMainGunCD(bsInfo[0],bsInfo[1],bsInfo[2])
	    upperCD = lowerCD + attack_roll + float(skill_time)/float(times)
	    plane1Dict = dict(FIGHTER,**BOOMBER) 
	    cvInfo = PlayerLoadData.getPlayerInfo(0)

	    resultDF = pd.DataFrame()

	    for torpedo_name,torpedo_cd in TORPEDO.items():
	        for plane1_name,plane1_cd in plane1Dict.items():
	            average = CarrierVessel.getAverageAircraftCD(cvInfo[0],cvInfo[1],cvInfo[2],plane1_cd,torpedo_cd,TORPEDO['青花鱼'],beaconFlag) 
	            #固定plane3 = '青花鱼'
	            if average > lowerCD and average < upperCD:
	                resultDF = resultDF.append(CarrierVessel.getAircraftInfo(plane1_name,torpedo_name,'青花鱼'),ignore_index=True)

	    return resultDF


class QueryCombination:
    '''
        查询器类型，封装查询相关方法
    '''
    def queryWithTorpedo(resultDF,target,beaconFlag=False):
        '''检索指定鱼雷机（2号位）的组合'''
        #condition_col = resultDF.loc[[:]]['Plane2']
        
        queryResult = resultDF[(resultDF['Plane2'] == target)]
        
        #queryResult.loc[0,'beacon'] = beaconFlag	
        return queryResult


if __name__=="__main__":
    
    #用户定义区
    
    PlayerTest = PlayerLoadData(4,15,0,19,0,0.08)  #在此定义用户外部装填加成，顺序为bstch_ld,bscat_ld,bsld_buff,cvtch_ld,cvcat_ld,cvld_buff
    
    mainGunName = 'WE_AP_SSR'    #在此定义目标主炮,以香槟炮为例
    
    times = 4   #在此定义调速轮数
    
    Formidable = CarrierVessel(124,2,3,3)   #初始化可畏,
    #beaconFlag = False	#是否携带信标
    Georgia = Battleship(173,BATTLESHIP_GUN[mainGunName])   #初始化携带指定主炮的佐治亚
    
    targetTorpedo = '流星'	#在此定义目标鱼雷机
    """
    print(Formidable.getAverageAircraftCD(19,0,0.08,FIGHTER['VF-17海盗'],TORPEDO[targetTorpedo],TORPEDO['青花鱼'],True)) 
    >> 19.866322876940465
    """
    #以下为测试函数     
    for flag in [True,False]:
        recommend = Coordinator.getFormidableAircraft(PlayerTest,Georgia,Formidable,times,flag)
        #print(recommend)
        query = QueryCombination.queryWithTorpedo(recommend,targetTorpedo,flag)
        print(query)
        print('beacon:',flag)	#暂时将信标信息外置输出
