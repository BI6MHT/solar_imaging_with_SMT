#!/usr/bin/env python
# coding: utf-8



# -*- coding: utf-8 -*-


######### S形扫描 #############

# 例如5X4个像素的扫描顺序，也是文件的命名
# 1  2  3  4  5
# 10 9  8  7  6
# 11 12 13 14 15
# 20 19 18 17 16



###########常数###############

# 积分上下限，flag = 0时默认为整个频带上积分
# flag不为0时（例如flag=1），积分上下限为 fre_lower和fre_upper
# 单位为MHz

flag = 0
freq_lower =  1417.5
freq_upper = 1424.5


# x轴的像素数
x_num = 5
# y轴的像素数
y_num = 5
# 插值次数
inter_num = 3


# txt频谱文件在哪个目录，基本目录，默认为这个py文件所在目录
# 目录参考格式 base_dir = 'C:\\Users\\BI6MHT\\Desktop\\新建文件夹 (3)\\'
base_dir = '.\\Data'

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# 生成x_num*y_num规格的矩阵，用来记录氢谱线频谱的数据
power_integral_HI = np.zeros(x_num*y_num)

for i in np.arange(1,x_num*y_num+1): # i从1到x_num*y_nym进行循环，即依次对x_num*y_num个文件进行读取
    
    file_data = np.loadtxt(base_dir+'%d.txt' % i,skiprows=1) 
    # i会取代%d，即为文件的名字为1.txt,2.txt。。。。。
    # loadtxt方法将取读txt文件的内容，生成多维数组，也可视为矩阵，如下所示；skiprows=1为跳过txt第一行，即不取读。
    # 下面左边是频率，右边是信号强度，即取读到的txt文本中的内容
    # [[1.41800000e+03 1.75199500e-02]
    # [1.41800977e+03 1.96757570e-02]
    # [1.41801953e+03 2.03458950e-02]
    # ...
    # [1.42797070e+03 1.79514570e-02]
    # [1.42798047e+03 1.85912490e-02]
    # [1.42799023e+03 1.88292690e-02]]
    
    freq_HI = file_data[:,0]
    # file_data是一个矩阵，这种写法即读取第0列所有行的内容
    # 读取矩阵的第0列的全部内容，即把所有采样频率取读为一个数组
    
    power_HI = file_data[:,1]
    # 读取矩阵的第1列的全部内容，即把所有信号强度取读为一个数组

    
    dx = freq_HI[1]-freq_HI[0]
    
    
    # 如果flag不为零，则在指定的频段进行积分
    if flag != 0:
        freq_HI[freq_HI<=freq_lower] = 0
        freq_HI[freq_HI>=freq_upper] = 0
        
        freq_HI_logical = (freq_HI!=0) 
        power_HI = power_HI*freq_HI_logical
        
    power_integral_HI[i-1]=sum(power_HI*dx)
    # 取tp的第i-1个元素来储存一个文件信号的功率


power_integral_HI=power_integral_HI.reshape((y_num,x_num))
# 把tp这个含有x_num*y_num个元素的数组转为x_num*y_num的矩阵
# 该矩阵每一个元素记录了一个文件(一次观测)对应的信号功率


# 像素顺序改为S形走位
for i in np.arange(1,len(power_integral_HI)+1):
    # 如果是偶数行，则翻转该行
    if (i % 2) == 0: 
        power_integral_HI[i-1,:] = np.flip(power_integral_HI[i-1,:])  


# 对像素进行线性插值
if inter_num != 0:
    for j in np.arange(0,inter_num):
        
        
        # 沿着矩阵的行方向进行线性插值
        y_num = y_num*2-1
        x_num = x_num
        Pow_new1 =  np.zeros((y_num,x_num))
        for i in np.arange(1,len(power_integral_HI)):
            Pow_new1[(2*i-1)-1,:] = power_integral_HI[i-1,:] 
            Pow_new1[(2*i)-1,:] = (power_integral_HI[i-1,:] + power_integral_HI[i,:])/2
            Pow_new1[(2*i+1)-1,:] = power_integral_HI[i,:]
        
        # 沿着矩阵的列方向进行线性插值
        y_num = y_num
        x_num = x_num*2-1
        Pow_new2 =  np.zeros((y_num,x_num))
        for i in np.arange(1,len(Pow_new1[1,:])):
            Pow_new2[:,(2*i-1)-1] = Pow_new1[:,i-1] 
            Pow_new2[:,(2*i)-1] = (Pow_new1[:,i-1] + Pow_new1[:,i])/2
            Pow_new2[:,(2*i+1)-1] = Pow_new1[:,i]
        
        power_integral_HI = Pow_new2

# 对像素强度进行归一化
power_integral_HI_norm = power_integral_HI/power_integral_HI.max()


# 下面就是seaborn，matplotlib库的内容了，可以百度一下，就是用这个库画热图
# 如果不够明显的话，可以用10logP，P为功率，即把功率转为dB的形式再成像
fig = plt.figure()

sns_plot = sns.heatmap(power_integral_HI_norm,cmap='RdBu_r')
plt.rcParams['font.sans-serif']=['SimHei']
plt.title('热力图')
plt.xticks ( []) 
plt.yticks ( [])
plt.show()
fig.savefig(base_dir+'Heatmap.png')