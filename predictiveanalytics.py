# -*- coding: utf-8 -*-
"""PredictiveAnalytics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CdiV2Ks4fxOalYcKaWCR-SVjNkGg5OzO
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# %matplotlib inline
import seaborn as sns

# load to dataset
url = 'https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv'
diamonds = pd.read_csv(url)
diamonds

diamonds.info()

diamonds.describe()

x = (diamonds.x == 0).sum()
y = (diamonds.y == 0).sum()
z = (diamonds.z == 0).sum()

print('Nilai 0 dikolom x ada: ', x)
print('Nilai 0 dikolom y ada: ', y)
print('Nilai 0 dikolom z ada: ', z)

diamonds.loc[(diamonds['z']==0)]

diamonds = diamonds.loc[(diamonds[['x','y','z']]!=0).all(axis=1)] # drop baris dengan nilai 0 pada x,y, dan z
diamonds.shape # cek ukuran data untuk memastikan baris sudah di drop

diamonds.describe()

sns.boxplot(x=diamonds['carat'])

sns.boxplot(x=diamonds['table'])

sns.boxplot(x=diamonds['x'])

Q1 = diamonds.quantile(0.25)
Q3 = diamonds.quantile(0.75)
IQR = Q3-Q1
diamonds = diamonds[~((diamonds<(Q1-1.5*IQR))|(diamonds>(Q3+1.5*IQR))).any(axis=1)]
diamonds.shape # cek ukuran dataset setelah drop outliers

# membagi fitur dataset menjadi dua bagian yaitu numerical dan categorical
numerical_features = ['price','carat','depth','table','x','y','z']
categorical_features = ['cut','color','clarity']

# ANALISIS UNIVARIATE FITUR CATEGORY TERLEBIH DAHULU
# Fitur Cut
feature = categorical_features[0]
count = diamonds[feature].value_counts()
percent = 100*diamonds[feature].value_counts(normalize=True)
df = pd.DataFrame({'jumlah sampel':count, 'persentase':percent.round(1)})
print(df)
count.plot(kind='bar', title=feature);

# Fitur Color
feature = categorical_features[1]
count = diamonds[feature].value_counts()
percent = 100*diamonds[feature].value_counts(normalize=True)
df = pd.DataFrame({'jumlah sampel':count, 'persentase':percent.round(1)})
print(df)
count.plot(kind='bar', title=feature);

# Fitur Clarify
feature = categorical_features[2]
count = diamonds[feature].value_counts()
percent = 100*diamonds[feature].value_counts(normalize=True)
df = pd.DataFrame({'jumlah sampel':count, 'persentase':percent.round(1)})
print(df)
count.plot(kind='bar', title=feature);

# NUMERICAL FEATURES
diamonds.hist(bins=50, figsize=(20,15))
plt.show()

# ANALISIS MULTIVARIATE
# Categorical Features

cat_features = diamonds.select_dtypes(include='object').columns.to_list()
for col in cat_features:
  sns.catplot(x=col,y='price',kind='bar',dodge=False,height=4,aspect=3,data=diamonds,palette='Set3')
  plt.title("Rata-rata 'price' relatif terhadap - {}".format(col))

# Numerical Features
# menagamati hubungan antar fitur numerik dengan fungsi pairplot()
sns.pairplot(diamonds, diag_kind='kde')

plt.figure(figsize=(10,8))
correlation_matrix = diamonds.corr().round(2)
# annot = True untuk print values inside the square
sns.heatmap(data=correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, )
plt.title("Correlation Matrix untuk Fitur numerik: ", size=20)

# Fitur yang memiliki korelasi yang rendah(sangat), dapat di-drop
diamonds.drop(['depth'], inplace=True, axis=1)
diamonds.head()

from sklearn.preprocessing import  OneHotEncoder
diamonds = pd.concat([diamonds, pd.get_dummies(diamonds['cut'], prefix='cut', drop_first=True)],axis=1)
diamonds = pd.concat([diamonds, pd.get_dummies(diamonds['color'], prefix='color', drop_first=True)],axis=1)
diamonds = pd.concat([diamonds, pd.get_dummies(diamonds['clarity'], prefix='clarity', drop_first=True)],axis=1)
diamonds.drop(['cut','color','clarity'], axis=1, inplace=True)
diamonds.head()

sns.pairplot(diamonds[['x','y','z']], plot_kws={"s": 3});

from sklearn.decomposition import PCA
pca = PCA(n_components=3, random_state=123)
pca.fit(diamonds[['x','y','z']])
princ_comp = pca.transform(diamonds[['x','y','z']])

pca.explained_variance_ratio_.round(3)

from sklearn.decomposition import PCA
pca = PCA(n_components=1, random_state=123)
pca.fit(diamonds[['x','y','z']])
diamonds['dimension'] = pca.transform(diamonds.loc[:, ('x','y','z')]).flatten()
diamonds.drop(['x','y','z'], axis=1, inplace=True)

diamonds.head()

from sklearn.model_selection import train_test_split
X = diamonds.drop(['price'], axis=1)
y = diamonds['price']
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1, random_state = 123)

print(f'Total # of sample in whole dataset: {len(X)}')
print(f'Total # of sample in train dataset: {len(X_train)}')
print(f'Total # of sample in test dataset: {len(X_test)}')

from sklearn.preprocessing import StandardScaler
numerical_features = ['carat', 'table', 'dimension']
scaler = StandardScaler()
scaler.fit(X_train[numerical_features])
X_train[numerical_features] = scaler.transform(X_train.loc[:, numerical_features])
X_train[numerical_features].head()

X_train[numerical_features].describe().round(4)

# siapkan dataframe untuk analisis model
models = pd.DataFrame(index=['train_mse', 'test_mse'],
                      columns=['KNN', 'RandomForest', 'Boosting'])

from sklearn.neighbors import KNeighborsRegressor
knn = KNeighborsRegressor(n_neighbors=10)
knn.fit(X_train, y_train)
y_pred_knn = knn.predict(X_train)

# import library yg dibutuhkan
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
# membuat model prediksi
RF = RandomForestRegressor(n_estimators=50, max_depth=16, random_state=55, n_jobs=-1)
RF.fit(X_train, y_train)
models.loc['train_mse','RandomForest'] = mean_squared_error(y_pred=RF.predict(X_train), y_true=y_train)

from sklearn.ensemble import AdaBoostRegressor
boosting = AdaBoostRegressor(n_estimators=50, learning_rate=0.05, random_state=55)
boosting.fit(X_train, y_train)
models.loc['train_mse','Boosting'] = mean_squared_error(y_pred=boosting.predict(X_train), y_true=y_train)

X_test.loc[:, numerical_features] = scaler.transform(X_test[numerical_features])

mse = pd.DataFrame(columns=['train', 'test'], index=['KNN', 'RF', 'Boosting'])
model_dict = {'KNN': knn, 'RF': RF, 'Boosting':boosting}
for name, model in model_dict.items():
  mse.loc[name, 'train'] = mean_squared_error(y_true=y_train, y_pred=model.predict(X_train))/1e3
  mse.loc[name, 'test'] = mean_squared_error(y_true=y_test, y_pred=model.predict(X_test))/1e3

mse

fig, ax = plt.subplots()
mse.sort_values(by='test', ascending=False).plot(kind='barh', ax=ax, zorder=3)
ax.grid(zorder=0)

prediksi = X_test.iloc[:1].copy()
pred_dict = {'y_true':y_test[:1]}
for name, model in model_dict.items():
  pred_dict['prediksi_'+name] = model.predict(prediksi).round(1)

pd.DataFrame(pred_dict) # juga bisa menguji prediksi data lain dengan mengubah indeks pada X_test.