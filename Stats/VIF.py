import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
import csv

input_csv = r"C:\Users\dyera\Documents\Offshore Task 3\GradientBoostingRegressor\RFE with Hyperparameter Tuning\Removed_Platforms_Ver4_Reformatted_wDataStats_edits_wWellProd.csv"
# Pandas complaining about encoding so "ISO-8859-1" seems to fix
df = pd.read_csv(input_csv, encoding="ISO-8859-1")

# get rid of all records that have a blank or nan age at removal category
# df = df[pd.notnull(df['Age_at_Removal'])]

# split up the target from the data frame. Change type to integer
target = df['Age_at_Removal'].astype('int8')
df.drop(['Age_at_Removal'], axis=1)

no_list = ['LstPrdDate_lastDate', 'LstPrdDate_firstDate',\
           'CompDate_lastDate', 'CompDate_firstDate',\
           'SpudDate_lastDate', 'SpudDate_firstDate',\
           'API14', 'APIs', 'installDate', 'removalDate', 'installDate_Julian', 'removalDate_Julian',\
           'authorityNumber', 'leaseNumber',\
           'fieldNameCode', 'structureName',\
           'Age_at_Removal', 'Age_at_Rem_Category', 'Sum_Ages_at_Inc', 'Avg_Age_at_Inc', 'Age_at_Last_Inc',\
            'Total Storms',\
           'Tropical Sum', 'C1 Sum', 'C2 Sum', 'C3 Sum', 'C4 Sum', 'C5 Sum',\
           'Tropical Days Sum', 'C1 Days Sum', 'C2 Days Sum', 'C3 Days Sum', 'C4 Days Sum', 'C5 Days Sum',\
           'Wave Height Count', 'Wave Height None Count', 'Wave Height Sum',\
           'MSWS Count', 'MSWS None Count', 'MSWS Sum',\
           'MRWG Count', 'MRWG None Count', 'MRWG Sum',\

          'MRWG None Count', 'MSWS Count', 'Wave Height None Count', 'MSWS Sum',\
           'districtCode', 'structureNumber', 'complexIDNumber',\
           'P_ID'
           ]

# script below will look for any columnds in the df that have all null\n",
# values and add that column name to the no_list\n",
header = df.columns.values
empty_train_columns = []
for col in df.columns.values:
    # all the values for this feature are null
    if sum(df[col].isnull()) == df.shape[0]:
        empty_train_columns.append(col)
        no_list.append(col)
if empty_train_columns:
        print('These fields have all null values in the df and are being removed from the model: {}'.format(empty_train_columns))

# for each array in the data frame, determine if it is continous and categorical\n",
# and separate into contin and categ data frames\n",
contin_fields = []
categ_fields = []

with open('GBR_Ver5_VIF_PreFeatureList.csv', 'w', newline='') as outputCSV:
    writer = csv.writer(outputCSV)
    writer.writerow(['Variable', 'Type'])
    # loop through all features in the data frame
    for feat in df:
        if feat not in no_list:
            t = df[feat].dtype
            if (t == 'int64') or (t == 'float64'):
                contin_fields.append(feat)
                writer.writerow([feat, 'Continous'])
            if t == 'object':
                categ_fields.append(feat)
                writer.writerow([feat, 'Categorical'])
        else:
            print('Removed: {}'.format(feat))

# LabelEncoder for categorical variables\n",
# only want one so they coding is the same for the training and testing sets\n",
enc = preprocessing.OneHotEncoder(handle_unknown = 'ignore')

def CategTransformer(categ):

    # Function to process categorical features. It will fill NaN (empty)
    # values with the string that is the most frequent for that feature,
    # and will also one hot encode the feature.\n",

    categ_fill = mis_imp.fit_transform(categ)

    categ_features_enc = enc.fit_transform(categ_fill).toarray()

    return categ_features_enc

##########################################

def AutobotTransformer(contin_feats, categ_feats):

    # Function to pre-process continous and categorical features and
    # then combine the two data frames together.

    # if not categ_feats.empty:
    #     categ_feats_processed = CategTransformer(categ_feats)
    # if (contin_feats_processed.any()) and (categ_feats_processed is None):
    #     transformed_features = contin_feats
    # elif (contin_feats_processed is None) and (categ_feats_processed.any()):
    #     transformed_features = categ_feats
    # else:
    #     transformed_features = np.concatenate([contin_feats, categ_feats_processed], axis = 1)

    categ_feats_processed = CategTransformer(categ_feats)
    transformed_features = np.concatenate([contin_feats, categ_feats_processed], axis=1)

    return transformed_features

# plt.hist(target, bins=20)

df_contin_features = df[contin_fields]
df_categ_features = df[categ_fields].astype(str) # need to treat all categorical variable values as strings

# now combine processed continous and categorical features into one
processed_features = AutobotTransformer(df_contin_features, df_categ_features)

# create list of all the feature names in order
df_feature_list = contin_fields + enc.get_feature_names(categ_fields).tolist()

X_train = pd.DataFrame(processed_features, columns=df_feature_list)

# Use Variance Inflation Factor (VIF) to determine features to drop that have a high correlation
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif_data = pd.DataFrame()
vif_data["feature"] = X_train.columns

vif_data['VIF'] = [variance_inflation_factor(X_train.values, i) for i in range(len(X_train.columns))]

vif_data.to_csv('GBR_Ver5_VIF_VIFResults.csv', index=True)

print('VIF Complete.')