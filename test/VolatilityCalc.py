from pylab import *
import data.ReadCSV as rc
import pandas as pd
import seaborn as sns
from scipy.stats import normaltest
from scipy.stats import anderson

df = rc.get_data('002415.SZ')

res = pd.concat([rc.get_ma(df['close'], 15), rc.get_ma(df['close'], 2)], join='inner', axis=1)

v = (res['ma2'] - res['ma15'])*100 / res['ma15']


p = normaltest(v, axis=None)

print(p)
print(v.mean(), v.std())

sns.distplot(v,hist=True,kde=True,rug=True) # 前两个默认就是True,rug是在最下方显示出频率情况，默认为False
# bins=20 表示等分为20份的效果，同样有label等等参数
sns.kdeplot(v,shade=True,color='r') # shade表示线下颜色为阴影,color表示颜色是红色
sns.rugplot(v) # 在下方画出频率情况

plt.show()
