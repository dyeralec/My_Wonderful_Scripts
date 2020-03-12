#!/usr/bin/env python
# coding: utf-8

# # Gradient Boosted Classifier 
# Practice/Example of GBC on a platforms dataset.
# 
# This model will use the Gradient Boosted Classifier estimator model from sklearn to determine age at removal. This model can be used for multiclass and multilabel classification.
# 
# About Multiclass and Multilabel Classification: https://scikit-learn.org/stable/modules/multiclass.html
# 
# The problem at hand is a multiclass classification scenario. There are only certain metrics that can be used to access the accuracy of the model. The Matthews correlation coefficient (also called Pearson coefficient) is used in machine learning as a measure of the quality of binary and multiclass classifications.
# 
# About classification metrics: https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics
# About Matthews correlation coeffficient: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html#sklearn.metrics.matthews_corrcoef

# # 1: Input Data
# 
# The CSV used for this notebook contains records of removed platforms with aggregated incident data, scaled incident severity, age at removal, and other platform characteristics.
# 
# This data set contains 5,194 removed platform records
# 
# Start by reading the CSV
# 
# Platform age are removal category field "Age_at_Rem_Category' is what we want to predict. This field bins the age at removal into 5 categories:
# 
# - 0 to 11
# - 11 to 20
# - 20 to 30
# - 30 to 42
# - 42 to 72
# 
# This classification was created using the Fisher-Jenks method, but then rounded up to whole numbers.

# In[2]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets.base import Bunch
from sklearn import preprocessing
from yellowbrick.target import FeatureCorrelation
from yellowbrick.features import Rank2D
from yellowbrick.target import ClassBalance
from sklearn.model_selection import TimeSeriesSplit
from yellowbrick.datasets import load_occupancy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels
from yellowbrick.classifier import ClassificationReport
from yellowbrick.datasets import load_occupancy
from yellowbrick.classifier import ROCAUC
from yellowbrick.classifier import PrecisionRecallCurve
from yellowbrick.classifier import ClassPredictionError
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import validation_curve
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix


# In[38]:


# Pandas complaining about encoding so "ISO-8859-1" seems to fix
df = pd.read_csv(r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Platforms\Apply VariableBased Ranks\Version2_03262019\Current_removedPlatforms_wAgeAtRemoval_categorized_wMetocean.csv", encoding="ISO-8859-1")

# Fit and Transform really don't like NaN.
df.fillna(0, inplace=True)


# In[39]:


# df


# In[53]:


input_feats = ['PLATI_5','PLONG_4','PBloc_7','WindSp_195','PCran_188','PSlot_166','Severi_158','AvgAg_160',               'WaveHe_194','Number_18','PSlot_165', 'PRigC_16','PSlan_164','Sum_Ranks',               'Sign_Wave_Height_mean',         'Sign_Wave_Height_height_percentile_90','Wave_Period_T02_mean', 'Wave_Period_T02_max',          'Wave_power_p_mean', 'Wave_power_p_max', 'Currents_mean', 'Currents_max', 'wind_mean',         'wind_max', 'wind_percentile_90', 'Tropical', 'Tropical Days', 'C1', 'C1 Days', 'C2', 'C2 Days',         'C3', 'C3 Days', 'C4', 'C4 Days', 'C5', 'C5 Days', 'PStru_12']

categ_feats = ['PStru_12']

features = df[input_feats]


# # 2: Data Exploration

# ## 2.1 Histograms

# In[54]:


# plot from Pandas
# features.hist(figsize=(25,25))


# ## 2.2 Feature Correlation
# 
# We will use statistical methods to determine which independent variables are correlated with eachother, and therefore which variables need to be taken out of the model.

# In[55]:


# pearsoncorr = features.corr()

# fig, ax = plt.subplots(figsize = (25,25))

# sns.heatmap(pearsoncorr, 
#             xticklabels=pearsoncorr.columns,
#             yticklabels=pearsoncorr.columns,
#             cmap='RdBu_r',
#             annot=True,
#             linewidth=0.5,
#            ax=ax)


# Appears that many of the metocean variables are correlated with eachother. This is no suprise but we must be careful with which metocean variables we use for the model. Currents data seem to be highly correlated with some of the wave variables, including wave height max, wave height 90th percentile, wave period max, and wave power, however it is not highly correlated with wave height mean and also wave period mean, so those two can be used together in the model. 
# 
# If we think that wave height 90th percentile is going to be a good model predictor and we put it in the model, the variables that have a low correlation with it and therefore can also be used in the model are wave power mean, wave power max, wave period mean, wave height mean, and wave height max, but NOT all together.
# 
# Not a suprise, but most of the storm data in days are all highly correlated with eachother. 

# ### Having some fun with correlation matrix plots...
# 
# https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
# 
# Just can't figure out how to increase the size of the matrix...???

# In[56]:


# def heatmap(x, y, **kwargs):
#     if 'color' in kwargs:
#         color = kwargs['color']
#     else:
#         color = [1]*len(x)

#     if 'palette' in kwargs:
#         palette = kwargs['palette']
#         n_colors = len(palette)
#     else:
#         n_colors = 256 # Use 256 colors for the diverging color palette
#         palette = sns.color_palette("Blues", n_colors)

#     if 'color_range' in kwargs:
#         color_min, color_max = kwargs['color_range']
#     else:
#         color_min, color_max = min(color), max(color) # Range of values that will be mapped to the palette, i.e. min and max possible correlation

#     def value_to_color(val):
#         if color_min == color_max:
#             return palette[-1]
#         else:
#             val_position = float((val - color_min)) / (color_max - color_min) # position of value in the input range, relative to the length of the input range
#             val_position = min(max(val_position, 0), 1) # bound the position betwen 0 and 1
#             ind = int(val_position * (n_colors - 1)) # target index in the color palette
#             return palette[ind]

#     if 'size' in kwargs:
#         size = kwargs['size']
#     else:
#         size = [1]*len(x)

#     if 'size_range' in kwargs:
#         size_min, size_max = kwargs['size_range'][0], kwargs['size_range'][1]
#     else:
#         size_min, size_max = min(size), max(size)

#     size_scale = kwargs.get('size_scale', 500)

#     def value_to_size(val):
#         if size_min == size_max:
#             return 1 * size_scale
#         else:
#             val_position = (val - size_min) * 0.99 / (size_max - size_min) + 0.01 # position of value in the input range, relative to the length of the input range
#             val_position = min(max(val_position, 0), 1) # bound the position betwen 0 and 1
#             return val_position * size_scale
#     if 'x_order' in kwargs:
#         x_names = [t for t in kwargs['x_order']]
#     else:
#         x_names = [t for t in sorted(set([v for v in x]))]
#     x_to_num = {p[1]:p[0] for p in enumerate(x_names)}

#     if 'y_order' in kwargs:
#         y_names = [t for t in kwargs['y_order']]
#     else:
#         y_names = [t for t in sorted(set([v for v in y]))]
#     y_to_num = {p[1]:p[0] for p in enumerate(y_names)}

#     plot_grid = plt.GridSpec(1, 15, hspace=0.2, wspace=0.1) # Setup a 1x10 grid
#     ax = plt.subplot(plot_grid[:,:-1]) # Use the left 14/15ths of the grid for the main plot

#     marker = kwargs.get('marker', 's')

#     kwargs_pass_on = {k:v for k,v in kwargs.items() if k not in [
#          'color', 'palette', 'color_range', 'size', 'size_range', 'size_scale', 'marker', 'x_order', 'y_order'
#     ]}

#     ax.scatter(
#         x=[x_to_num[v] for v in x],
#         y=[y_to_num[v] for v in y],
#         marker=marker,
#         s=[value_to_size(v) for v in size],
#         c=[value_to_color(v) for v in color],
#         **kwargs_pass_on
#     )
#     ax.set_xticks([v for k,v in x_to_num.items()])
#     ax.set_xticklabels([k for k in x_to_num], rotation=45, horizontalalignment='right')
#     ax.set_yticks([v for k,v in y_to_num.items()])
#     ax.set_yticklabels([k for k in y_to_num])

#     ax.grid(False, 'major')
#     ax.grid(True, 'minor')
#     ax.set_xticks([t + 0.5 for t in ax.get_xticks()], minor=True)
#     ax.set_yticks([t + 0.5 for t in ax.get_yticks()], minor=True)

#     ax.set_xlim([-0.5, max([v for v in x_to_num.values()]) + 0.5])
#     ax.set_ylim([-0.5, max([v for v in y_to_num.values()]) + 0.5])
#     ax.set_facecolor('#F1F1F1')

#     # Add color legend on the right side of the plot
#     if color_min < color_max:
#         ax = plt.subplot(plot_grid[:,-1]) # Use the rightmost column of the plot

#         col_x = [0]*len(palette) # Fixed x coordinate for the bars
#         bar_y=np.linspace(color_min, color_max, n_colors) # y coordinates for each of the n_colors bars

#         bar_height = bar_y[1] - bar_y[0]
#         ax.barh(
#             y=bar_y,
#             width=[5]*len(palette), # Make bars 5 units wide
#             left=col_x, # Make bars start at 0
#             height=bar_height,
#             color=palette,
#             linewidth=0
#         )
#         ax.set_xlim(1, 2) # Bars are going from 0 to 5, so lets crop the plot somewhere in the middle
#         ax.grid(False) # Hide grid
#         ax.set_facecolor('white') # Make background white
#         ax.set_xticks([]) # Remove horizontal ticks
#         ax.set_yticks(np.linspace(min(bar_y), max(bar_y), 3)) # Show vertical ticks for min, middle and max
#         ax.yaxis.tick_right() # Show vertical ticks on the right


# def corrplot(data, size_scale=500, marker='s'):
#     corr = pd.melt(data.reset_index(), id_vars='index')
#     corr.columns = ['x', 'y', 'value']
#     heatmap(
#         corr['x'], corr['y'],
#         color=corr['value'], color_range=[-1, 1],
#         palette=sns.diverging_palette(20, 220, n=256),
#         size=corr['value'].abs()/2.5, size_range=[0,1],
#         marker=marker,
#         x_order=data.columns,
#         y_order=data.columns[::-1],
#         size_scale=size_scale
#     )

# fig, ax = plt.subplots(figsize = (25,25))    

# cm = df_features.corr()
# corrplot(cm,size_scale=2000, marker='s')

# # save the plot as png
# plt.savefig('Corr_Matrix.png')


# # 3: Preprocessing
# 
# ## 3.1 Grab Features from Data Frame Into Arrays

# ## 3.2 Choosing Features & Label Encoding
# 
# Label Encoder for Categorical Dependent Variable
# 
# Now we use sklearns preprocessing to build the labels.
# https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.LabelEncoder.html

# In[57]:


# LabelEncoder for categorical variables
enc = preprocessing.LabelEncoder()
for c in categ_feats:
    features[c] = enc.fit_transform(features[c])

# Set up target
target = df['Age_at_Rem_Category']

# Use LabelEncoder since target is categorical
le = preprocessing.LabelEncoder()
target = le.fit_transform(target)

# create array of target categories
classes = np.array(['(0-11)', '(11-20)', '(20-30)', '(30-42)', '(42-72)'])


# In[58]:


# create a Bunch object
B = Bunch(features = np.array(features), feature_names = input_feats, target = target, target_names = classes)


# ## 3.3 Quick look at feature correlation with dependent variable
# 
# https://www.scikit-yb.org/en/latest/api/target/feature_correlation.html#mutual-information-classification

# In[59]:


# Load the regression dataset
X, y = features, target
X_pd = pd.DataFrame(X, columns=input_feats)

# Instaniate the visualizer
FeatCorr_visualizer = FeatureCorrelation( 
    feature_names=input_feats, 
    sort=True,
    size = (500,600)
)

FeatCorr_visualizer.fit(X_pd, y)        # Fit the data to the visualizer
FeatCorr_visualizer.show()  


# ## 3.4 Co-Occurence Matrix
# 
# Look at the pearson correlation between all features
# 
# https://www.scikit-yb.org/en/latest/api/features/rankd.html#rank-2d

# In[87]:


corr_matrix = features.corr()
plt.figure(figsize = (10,10))
sns.heatmap(corr_matrix)

columns = np.full((corr_matrix.shape[0],), True, dtype=bool)
for i in range(corr_matrix.shape[0]):
    for j in range(i+1, corr_matrix.shape[0]):
        if corr_matrix.iloc[i,j] >= 0.7:
            if columns[j]:
                columns[j] = False
selected_columns = features.columns[columns]
selected_features = features[selected_columns]           # Finalize and render the figure


# We want to drop all but one of two features in the model that have a high correlation with one another.

# In[88]:


print('These are the features that were picked to stay by the Covariance Function.\n')
print(selected_columns)

plt.figure(figsize = (10,10))
sns.heatmap(selected_features.corr())


# In[62]:


selected_feats_list = selected_columns.tolist()


# In[64]:


# Load the regression dataset
X, y = selected_features, target
X_pd = pd.DataFrame(X, columns=selected_feats_list)

# Instaniate the visualizer
FeatCorr_visualizer = FeatureCorrelation(
    feature_names=selected_feats_list, 
    sort=True
)

FeatCorr_visualizer.fit(X_pd, y)        # Fit the data to the visualizer
FeatCorr_visualizer.show()  


# ## 3.5 Quick look at class balance
# 
# https://www.scikit-yb.org/en/latest/api/target/class_balance.html
# 
# If there is an imbalance of classes, the validation scores (e.g. f1 score) may be bias as the classifier is simply guessing the majority class will be correct most of the time.

# In[65]:


# Load the classification dataset
X, y = B['features'], B['target']

# Instantiate the visualizer
visualizer = ClassBalance(labels=B['target_names'])

visualizer.fit(y)        # Fit the data to the visualizer
visualizer.show()        # Finalize and render the figure


# There does appear to be an imbalance in our labels. Fortunately, the '''train_test_split_''' function will stratify the sample, meaning that there will be approximately the same proportion of classese in the training and testing data set. We will look at this later.

# ## 3.6 Scaling
# 
# scaling/standardizing: https://scikit-learn.org/stable/modules/preprocessing.html

# In[66]:


# scale the array
selected_features = preprocessing.scale(selected_features)


# ## 3.7 Create a Train/Test Split
# 
# test_size is a percentage of the features to skip training on and save for testing.
# https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html

# In[67]:


X_train, X_test, y_train, y_test = train_test_split(selected_features, target, test_size=0.2, random_state = 2)


# In[76]:


X_test


# Section below will look at the distributions of the training and testing data in relation to the population. It is important that the train test split keeps the distributions the same.
# Going to focus on only the categorical variables at this point.

# In[69]:


# feature names are stored in the 'feats' variable
# grab the length of feats
for i in range(0,len(selected_columns)):
    plt.hist(selected_features[:,i], color = 'green', label = 'Population')
    plt.hist(X_train[:,i], color = 'blue', label = 'Train')
    plt.hist(X_test[:,i], color = 'red', label = 'Test')
    plt.ylabel('Count')
    plt.title(input_feats[i])
    plt.legend()
    plt.show()


# In[70]:


# from sklearn.preprocessing import StandardScaler
# scaler = StandardScaler()

# # Fit on training set only.
# scaler.fit(X_train)

# # Apply transform to both the training set and the test set.
# X_train = scaler.transform(X_train)
# X_test = scaler.transform(X_test)


# ## 3.8 Check Class Balance
# 
# Now that we have our data split up into training and testing, lets make sure that it is stratifier properly.

# In[78]:


# Instantiate the visualizer
visualizer = ClassBalance(labels=B['target_names'])

visualizer.fit(y_train, y_test)        # Fit the data to the visualizer
visualizer.show()                      # Finalize and render the figure


# Since the rareness of having a platform active for a longer time span is true to the data, it is okay to continue on with the model. We would expect that the number of platforms that are active from 42 to 72 years are going to be low. 
# 
# The training and testing data are stratified properly. 

# ## 3.9 Apply PCA to model
# 
# using code from this article: https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60
# 
# # NOTE: PCA does NOT help this model. Do not use PCA right now

# ### Import and apply PCA
# Notice the code below has .95 for the number of components parameter. It means that scikit-learn choose the minimum number of principal components such that 95% of the variance is retained.

# In[79]:


# from sklearn.decomposition import PCA
# # Make an instance of the Model
# pca = PCA(.95)

# # fit PCA on training set
# pca.fit(X_train)


# Note: You can find out how many components PCA choose after fitting the model using pca.n_components_ . In this case, 95% of the variance amounts to 330 principal components.
# 
# ### Apply the mapping (transform) to both the training set and the test set.

# In[80]:


# X_train = pca.transform(X_train)
# X_test = pca.transform(X_test)


# # 4: Import GradientBoostingClassifier and Train the Model
# 
# https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html
# 
# Train the model with the training data from the previous step.
# Predict the labels of the test dataset
# 
# *__Notice:__ This method takes __significantly__ longer than Naive Bayes*
# 
# Parameters for the GradientBoostingClassifier:
# 
# - n_estimators: The number of boosting stages default is 100. larger numbers result in better prediction but longer training time
# - learning_rate: Shrinks the contribution of each trea by ```learing_rate```. Tradeoff between learning_rate and n_estimators
# - max_depth: Maximum depth of the individual regression estimators. # of nodes in each tree. Tune for best performance, the best value depends on interaction of input values.
# - random_state: Defaults to using ```np.random``` for random number generation.
# - many more

# In[81]:


params = {'n_estimators': 1000, 
          'learning_rate': 0.02, 
          'max_depth': 6, 
          'random_state': 2, 
          'min_samples_leaf': 3,
         'max_features': 0.3
         }

model = GradientBoostingClassifier(**params)
model.fit(X_train, y_train)


# # 5: Evaluate the Results
# 
# ## 5.1 Calculate Accuracy
# Calculate the mean squared error (MSE), root MSE, and matthew's correlation coefficient for the test set predictions.

# In[82]:


mean_squared_error(y_train, model.predict(X_train))


# In[83]:


model_reg = GradientBoostingRegressor(**params)
model_reg.fit(X_train, y_train)
y_pred_reg = model_reg.predict(X_test)


# In[84]:


print('Accuracy Score: ' + format(metrics.r2_score(y_test, y_pred_reg)))


# In[85]:


y_pred = model.predict(X_test)

print('Results on training data')
print("MSE: ", mean_squared_error(y_train, model.predict(X_train)))
print('RMSE: ',np.sqrt(mean_squared_error(y_train, model.predict(X_train))))
print('Matthews Corr. Coef.: ', metrics.matthews_corrcoef(y_train, model.predict(X_train)))
print('------------------------')
print('Results on testing data')
print("MSE: ", mean_squared_error(y_test, y_pred))
print('RMSE: ',np.sqrt(mean_squared_error(y_test, y_pred)))
print('Matthews Corr. Coef.: ', metrics.matthews_corrcoef(y_test, y_pred))
print('------------------------')
print('Classification Report')
print(classification_report(y_test, y_pred))
print('Accuracy Score: ' + format(accuracy_score(y_test, y_pred)))


# ## Just to see how other models compare, lets look at a few...
# 
# ### Decision Tree Classifer

# In[289]:


classifier = DecisionTreeClassifier()
classifier.fit(X_train, y_train)
y_pred_DTC = classifier.predict(X_test)

print(confusion_matrix(y_test, y_pred_DTC))
print(classification_report(y_test, y_pred_DTC))
print('Accuracy Score: ' + format(accuracy_score(y_test, y_pred_DTC)))


# ### Support Vector Machine

# In[130]:


from sklearn.svm import SVC
svclassifier = SVC(kernel='linear')
svclassifier.fit(X_train, y_train)
y_pred_SVM = svclassifier.predict(X_test)
print(confusion_matrix(y_test,y_pred_SVM))
print(classification_report(y_test,y_pred_SVM))
print('Accuracy Score: ' + format(accuracy_score(y_test, y_pred_SVM)))


# ### Random Forests

# In[131]:


from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

rfclassifier = RandomForestClassifier(n_estimators=20, random_state=0)
rfclassifier.fit(X_train, y_train)
y_pred_rf = rfclassifier.predict(X_test)

print(confusion_matrix(y_test,y_pred_rf))
print(classification_report(y_test,y_pred_rf))
print('Accuracy score: ' + format(accuracy_score(y_test, y_pred_rf)))


# The Decision Tree Classifer (DTC) and Support Vector Machine (SVM) models have a lower accuracy score at 0.855 and 0.762, respectively. However, the Random Forets (RF)model has an accuracy score of 0.883, which comes close to the current Gradient Boosted Classifer (GBC) model. The RF could be further looked into by tweaking the parameters to possibly improve the model.

# ## 5.2 Cross Validation Score

# In[132]:


# cvm = GradientBoostingClassifier(**params)
# scores = cross_val_score(cvm, X_train, y_train, cv=5)
# scores
# print("Accuracy (f-score): %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


# ## 5.3 Confusion Matrix
# 
# https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-examples-model-selection-plot-confusion-matrix-py
# 
# #### Quote from page:
# 
# "Example of confusion matrix usage to evaluate the quality of the output of a classifier on the iris data set. The diagonal elements represent the number of points for which the predicted label is equal to the true label, while off-diagonal elements are those that are mislabeled by the classifier. The higher the diagonal values of the confusion matrix the better, indicating many correct predictions.
# 
# The figures show the confusion matrix with and without normalization by class support size (number of elements in each class). This kind of normalization can be interesting in case of class imbalance to have a more visual interpretation of which class is being misclassified."
# 
# #### Citation:
# 
# @article{scikit-learn,
#  title={Scikit-learn: Machine Learning in {P}ython},
#  author={Pedregosa, F. and Varoquaux, G. and Gramfort, A. and Michel, V.
#          and Thirion, B. and Grisel, O. and Blondel, M. and Prettenhofer, P.
#          and Weiss, R. and Dubourg, V. and Vanderplas, J. and Passos, A. and
#          Cournapeau, D. and Brucher, M. and Perrot, M. and Duchesnay, E.},
#  journal={Journal of Machine Learning Research},
#  volume={12},
#  pages={2825--2830},
#  year={2011}
# }

# In[89]:


def plot_confusion_matrix(y_true, y_pred, classes,
                          normalize=False,
                          title=None,
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    return ax


np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plot_confusion_matrix(y_test, y_pred, classes=np.array(classes),
                      title='Confusion matrix, without normalization')

# Plot normalized confusion matrix
plot_confusion_matrix(y_test, y_pred, classes=np.array(classes), normalize=True,
                      title='Normalized confusion matrix')

plt.show()


# ## 5.4 Classification Report
# 
# from: https://www.scikit-yb.org/en/latest/api/classifier/classification_report.html
# 
# "The classification report shows a representation of the main classification metrics on a per-class basis. This gives a deeper intuition of the classifier behavior over global accuracy which can mask functional weaknesses in one class of a multiclass problem. Visual classification reports are used to compare classification models to select models that are “redder”, e.g. have stronger classification metrics or that are more balanced.
# 
# The metrics are defined in terms of true and false positives, and true and false negatives. Positive and negative in this case are generic names for the classes of a binary classification problem. In the example above, we would consider true and false occupied and true and false unoccupied. Therefore a true positive is when the actual class is positive as is the estimated class. A false positive is when the actual class is negative but the estimated class is positive. Using this terminology the meterics are defined as follows:"
# 
# ### Precision: 
# "ability of a classiifer not to label an instance positive that is actually negative. For each class it is defined as as the ratio of true positives to the sum of true and false positives. Said another way, “for all instances classified positive, what percent was correct?”
# "
# 
# ### Recall:
# "ability of a classifier to find all positive instances. For each class it is defined as the ratio of true positives to the sum of true positives and false negatives. Said another way, “for all instances that were actually positive, what percent was classified correctly?”
# "
# 
# ### f1 score:
# "a weighted harmonic mean of precision and recall such that the best score is 1.0 and the worst is 0.0. Generally speaking, F1 scores are lower than accuracy measures as they embed precision and recall into their computation. As a rule of thumb, the weighted average of F1 should be used to compare classifier models, not global accuracy.
# "
# 
# ### Support:
# "the number of actual occurrences of the class in the specified dataset. Imbalanced support in the training data may indicate structural weaknesses in the reported scores of the classifier and could indicate the need for stratified sampling or rebalancing. Support doesn’t change between models but instead diagnoses the evaluation process.
# "
# 
# #### Citation:
# @software{bengfort_yellowbrick_2018,
#     title = {Yellowbrick},
#     rights = {Apache License 2.0},
#     url = {http://www.scikit-yb.org/en/latest/},
#     abstract = {Yellowbrick is an open source, pure Python project that
#         extends the Scikit-Learn {API} with visual analysis and
#         diagnostic tools. The Yellowbrick {API} also wraps Matplotlib to
#         create publication-ready figures and interactive data
#         explorations while still allowing developers fine-grain control
#         of figures. For users, Yellowbrick can help evaluate the
#         performance, stability, and predictive value of machine learning
#         models, and assist in diagnosing problems throughout the machine
#         learning workflow.},
#     version = {0.9.1},
#     author = {Bengfort, Benjamin and Bilbro, Rebecca and Danielsen, Nathan and
#         Gray, Larry and {McIntyre}, Kristen and Roman, Prema and Poh, Zijie and
#         others},
#     date = {2018-11-14},
#     year = {2018},
#     doi = {10.5281/zenodo.1206264}
# }

# In[285]:


# Instantiate the classification model and visualize
visualizer = ClassificationReport(model, classes=classes, support=True)

visualizer.fit(X_train, y_train)        # Fit the visualizer and the model
visualizer.score(X_test, y_test)        # Evaluate the model on the test data
visualizer.show(outpath = "P:\\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\\04_Products\Figures and Graphs\Platforms\Classification_Report.pdf")                       # Finalize and show the figure


# ## 5.5 Multi-class ROCAUC Curve
# 
# https://www.scikit-yb.org/en/latest/api/classifier/rocauc.html
# 
# "A ROCAUC (Receiver Operating Characteristic/Area Under the Curve) plot allows the user to visualize the tradeoff between the classifier’s sensitivity and specificity.
# 
# The Receiver Operating Characteristic (ROC) is a measure of a classifier’s predictive quality that compares and visualizes the tradeoff between the model’s sensitivity and specificity. When plotted, a ROC curve displays the true positive rate on the Y axis and the false positive rate on the X axis on both a global average and per-class basis. The ideal point is therefore the top-left corner of the plot: false positives are zero and true positives are one.
# 
# This leads to another metric, area under the curve (AUC), which is a computation of the relationship between false positives and true positives. The higher the AUC, the better the model generally is. However, it is also important to inspect the “steepness” of the curve, as this describes the maximization of the true positive rate while minimizing the false positive rate."

# In[135]:


# Instantiate the visualizer with the classification model
visualizer = ROCAUC(model, classes=classes)

visualizer.fit(X_train, y_train)        # Fit the training data to the visualizer
visualizer.score(X_test, y_test)        # Evaluate the model on the test data
visualizer.show()                       # Finalize and show the figure


# ## 5.6 Precision- Recall Curve
# 
# https://www.scikit-yb.org/en/latest/api/classifier/prcurve.html
# 
# "Precision-Recall curves are a metric used to evaluate a classifier’s quality, particularly when classes are very imbalanced. The precision-recall curve shows the tradeoff between precision, a measure of result relevancy, and recall, a measure of how many relevant results are returned. A large area under the curve represents both high recall and precision, the best case scenario for a classifier, showing a model that returns accurate results for the majority of classes it selects."

# In[136]:


# Create the visualizer, fit, score, and show it
viz = PrecisionRecallCurve(
    GradientBoostingClassifier(**params), per_class=True, iso_f1_curves=True,
    fill_area=False, micro=False, classes=classes
)
viz.fit(X_train, y_train)
viz.score(X_test, y_test)
viz.show()


# ## 5.7 Class Prediction Error
# 
# https://www.scikit-yb.org/en/latest/api/classifier/class_prediction_error.html
# 
# "The Yellowbrick ClassPredictionError plot is a twist on other and sometimes more familiar classification model diagnostic tools like the Confusion Matrix and Classification Report. Like the Classification Report, this plot shows the support (number of training samples) for each class in the fitted classification model as a stacked bar chart. Each bar is segmented to show the proportion of predictions (including false negatives and false positives, like a Confusion Matrix) for each class. You can use a ClassPredictionError to visualize which classes your classifier is having a particularly difficult time with, and more importantly, what incorrect answers it is giving on a per-class basis. This can often enable you to better understand strengths and weaknesses of different models and particular challenges unique to your dataset.
# 
# The class prediction error chart provides a way to quickly understand how good your classifier is at predicting the right classes."

# In[137]:


# Instantiate the classification model and visualizer
visualizer = ClassPredictionError(
    GradientBoostingClassifier(**params), classes=classes
)

# Fit the training data to the visualizer
visualizer.fit(X_train, y_train)

# Evaluate the model on the test data
visualizer.score(X_test, y_test)

# Draw visualization
visualizer.show()


# ## 5.8 Plot Training Deviance
# 
# https://scikit-learn.org/stable/auto_examples/ensemble/plot_gradient_boosting_regression.html

# In[138]:


# compute test set deviance
test_score = np.zeros((params['n_estimators'],), dtype=np.float64)

for i, y_pred in enumerate(model.staged_decision_function(X_test)):
    test_score[i] = model.loss_(y_test, y_pred)

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
#plt.title('Deviance')
plt.plot(np.arange(params['n_estimators']) + 1, model.train_score_, 'b-',
         label='Training Set Deviance')
plt.plot(np.arange(params['n_estimators']) + 1, test_score, 'r-',
         label='Test Set Deviance')
plt.legend(loc='upper right')
plt.xlabel('Boosting Iterations')
plt.ylabel('Error')


# In[139]:


min(test_score)


# ## 5.9 Plot the learning curve
# 
# https://scikit-learn.org/stable/modules/learning_curve.html
# 
# Info about learning curves: https://www.scikit-yb.org/en/latest/api/model_selection/learning_curve.html

# In[140]:


def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=None, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and training learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross-validation,
          - integer, to specify the number of folds.
          - :term:`CV splitter`,
          - An iterable yielding (train, test) splits as arrays of indices.

        For integer/None inputs, if ``y`` is binary or multiclass,
        :class:`StratifiedKFold` used. If the estimator is not a classifier
        or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validators that can be used here.

    n_jobs : int or None, optional (default=None)
        Number of jobs to run in parallel.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    train_sizes : array-like, shape (n_ticks,), dtype float or int
        Relative or absolute numbers of training examples that will be used to
        generate the learning curve. If the dtype is float, it is regarded as a
        fraction of the maximum size of the training set (that is determined
        by the selected validation method), i.e. it has to be within (0, 1].
        Otherwise it is interpreted as absolute sizes of the training sets.
        Note that for classification the number of samples usually have to
        be big enough to contain at least one sample from each class.
        (default: np.linspace(0.1, 1.0, 5))
    """
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt

title = 'Learning Curve'
# Using cross validation method of ShuffleSplit
cv = ShuffleSplit(n_splits=10, test_size=0.2, random_state=0)
estimator = GradientBoostingClassifier(**params)
output_plot = plot_learning_curve(estimator, title, X_train, y_train, ylim = None, cv=cv, n_jobs=1)

output_plot.show()


# # 6: Feature Importance
# 
# We will go through the feature importance methods described in this article by Eryk Lewinson https://towardsdatascience.com/explaining-feature-importance-by-example-of-a-random-forest-d9166011959e
# 
# ## 6.1 feature_importances_
# 
# This first look at feature importance will be using the basic 'feature_importances' attribute for the model.
# 
# https://scikit-learn.org/stable/auto_examples/ensemble/plot_gradient_boosting_regression.html
# (same as plot deviance link)

# In[272]:


feature_importance = model.feature_importances_
# make importances relative to max importance
feature_importance = 100.0 * (feature_importance / feature_importance.max())
sorted_idx = np.argsort(feature_importance)
pos = np.arange(sorted_idx.shape[0]) + .5
plt.subplot(1, 2, 2)
plt.barh(pos, feature_importance[sorted_idx], align='center')
plt.yticks(pos, selected_feats_list[sorted_idx])
plt.xlabel('Relative Importance')
plt.title('Feature Importance')
plt.show()


# The sklearn feature_importances_ attribute of the model is based on which feature decreases the variance in the model the most. According to Eryk Lewinson's article in  Towards Data Science, this method of explaining feature importance is fast, but may give more importance to continuous variables or high-cardinality categorical variables (2019). 
# 
# This current model is using only continuous variables, so this approach should still be valid. 
# 
# ### Explanation:
# 
# ...
# 
# Lets look at other ways of calculating feature importance.
# 
# ## 6.2 Permutation feature importance
# 
# Directly from article by Lewinson:
# 
# "
# 
# This approach directly measures feature importance by observing how random re-shuffling (thus preserving the distribution of the variable) of each predictor influences model performance.
# 
# The approach can be described in the following steps:
#     1. Train the baseline model and record the score (accuracy/R²/any metric of importance) by passing the validation set (or OOB set in case of Random Forest). This can also be done on the training set, at the cost of sacrificing information about generalization.
#     2. Re-shuffle values from one feature in the selected dataset, pass the dataset to the model again to obtain predictions and calculate the metric for this modified dataset. The feature importance is the difference between the benchmark score and the one from the modified (permuted) dataset.
#     3. Repeat 2. for all features in the dataset.
#     
# Pros:
#     - applicable to any model
#     - reasonably efficient
#     - reliable technique
#     - no need to retrain the model at each modification of the dataset
#     
# Cons:
#     - more computationally expensive than the default feature_importances
#     - permutation importance overestimates the importance of correlated predictors — Strobl et al (2008)
# 
# As for the second problem with this method, I have already plotted the correlation matrix above. However, I will use a function from one of the libraries I use to visualize Spearman’s correlations. The difference between standard Pearson’s correlation is that this one first transforms variables into ranks and only then runs Pearson’s correlation on the ranks.
# 
# Spearman’s correlation:
#     - is nonparametric
#     - does not assume a linear relationship between variables
#     - it looks for monotonic relationships.
#     
# "
# 
# ### 6.2.1 permuation with eli5

# In[190]:


# import eli5
# from eli5.sklearn import PermutationImportance

# # function for creating a feature importance dataframe
# def imp_df(column_names, importances):
#     df = pd.DataFrame({'feature': column_names,
#                        'feature_importance': importances}) \
#            .sort_values('feature_importance', ascending = False) \
#            .reset_index(drop = True)
#     return df

# # plotting a feature importance dataframe (horizontal barchart)
# def var_imp_plot(imp_df, title):
#     a4_dims = (11.7, 8.27)
#     fig, ax = plt.subplots(figsize=a4_dims)
    
#     imp_df.columns = ['feature', 'feature_importance']
#     sns.barplot(x = 'feature_importance', y = 'feature', data = imp_df, orient = 'h', color = 'royalblue') \
#        .set_title(title, fontsize = 20)

# perm = PermutationImportance(model, cv = None, refit = False, n_iter = 50).fit(X_train, y_train)
# perm_imp_eli5 = imp_df(X_train.columns, perm.feature_importances_)
# var_imp_plot(perm_imp_eli5, 'Permutation feature importance (eli5)')


# ### 6.2.2 permutation with rfpimp

# In[189]:


# from sklearn.metrics import r2_score
# from rfpimp import permutation_importances

# def r2(model, X_train, y_train):
#     return r2_score(y_train, model.predict(X_train))

# perm_imp_rfpimp = permutation_importances(model, X_train, y_train, r2)
# perm_imp_rfpimp.reset_index(drop = False, inplace = True)
# var_imp_plot(perm_imp_rfpimp, 'Permutation feature importance (rfpimp)')


# Explanation:
# 
# ....

# ## 6.3 Drop Column Feature Approach
# 
# from webpage:
# 
# "
# 
# This approach is quite an intuitive one, as we investigate the importance of a feature by comparing a model with all features versus a model with this feature dropped for training.
# 
# I created a function (based on rfpimp's implementation) for this approach below, which shows the underlying logic.
# 
# Pros:
#     - most accurate feature importance
# Cons:
#     - potentially high computation cost due to retraining the model for each variant of the dataset (after dropping a single feature column)
# 
# "

# In[188]:


from sklearn.base import clone 

def drop_col_feat_imp(model, X_train, y_train, random_state = 2):
    
    # clone the model to have the exact same specification as the one initially trained
    model_clone = clone(model)
    # set random_state for comparability
    model_clone.random_state = random_state
    # training and scoring the benchmark model
    model_clone.fit(X_train, y_train)
    benchmark_score = model_clone.score(X_train, y_train)
    # list for storing feature importances
    importances = []
    
    # iterating over all columns and storing feature importance (difference between benchmark and new model)
    for col in X_train.columns:
        model_clone = clone(model)
        model_clone.random_state = random_state
        model_clone.fit(X_train.drop(col, axis = 1), y_train)
        drop_col_score = model_clone.score(X_train.drop(col, axis = 1), y_train)
        importances.append(benchmark_score - drop_col_score)
    
    importances_df = imp_df(X_train.columns, importances)
    return importances_df

drop_col_feat_imp(model,X_train, y_train, random_state = 2)

drop_imp = drop_col_feat_imp(model, X_train, y_train)
var_imp_plot(drop_imp, 'Drop Column Feature Importance')


# In this graph, negative importance means that when a feature is removed the model improves.

# ## 7: Model Complexity Influence
# 
# https://scikit-learn.org/stable/auto_examples/applications/plot_model_complexity_influence.html#sphx-glr-auto-examples-applications-plot-model-complexity-influence-py
# 
# Lets demonstrate how model complexity influences both prediction accuracy and computational performance.
# 
# For the model we make the model complexity vary through the choice of relevant model parameters and measure the influence on both computational performance (latency) and predictive power (MSE in the case of using GradientBoostingRegressor).

# In[192]:


# Author: Eustache Diemert <eustache@diemert.fr>
# License: BSD 3 clause

import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.parasite_axes import host_subplot
from mpl_toolkits.axisartist.axislines import Axes
from scipy.sparse.csr import csr_matrix

from sklearn.utils import shuffle
import sklearn.metrics

# #############################################################################
# Routines

def benchmark_influence(conf):
    """
    Benchmark influence of :changing_param: on both MSE and latency.
    """
    prediction_times = []
    prediction_powers = []
    complexities = []
    for param_value in conf['changing_param_values']:
        conf['tuned_params'][conf['changing_param']] = param_value
        estimator = conf['estimator'](**conf['tuned_params'])
        print("Benchmarking %s" % estimator)
        estimator.fit(conf['data']['X_train'], conf['data']['y_train'])
        conf['postfit_hook'](estimator)
        complexity = conf['complexity_computer'](estimator)
        complexities.append(complexity)
        start_time = time.time()
        for _ in range(conf['n_samples']):
            y_pred = estimator.predict(conf['data']['X_test'])
        elapsed_time = (time.time() - start_time) / float(conf['n_samples'])
        prediction_times.append(elapsed_time)
        pred_score = conf['prediction_performance_computer'](
            conf['data']['y_test'], y_pred)
        prediction_powers.append(pred_score)
        print("Complexity: %d | %s: %.4f | Pred. Time: %fs\n" % (
            complexity, conf['prediction_performance_label'], pred_score,
            elapsed_time))
    return prediction_powers, prediction_times, complexities


def plot_influence(conf, mse_values, prediction_times, complexities):
    """
    Plot influence of model complexity on both accuracy and latency.
    """
    plt.figure(figsize=(12, 6))
    host = host_subplot(111, axes_class=Axes)
    plt.subplots_adjust(right=0.75)
    par1 = host.twinx()
    host.set_xlabel('Model Complexity (%s)' % conf['complexity_label'])
    y1_label = conf['prediction_performance_label']
    y2_label = "Time (s)"
    host.set_ylabel(y1_label)
    par1.set_ylabel(y2_label)
    p1, = host.plot(complexities, mse_values, 'b-', label="prediction error")
    p2, = par1.plot(complexities, prediction_times, 'r-',
                    label="latency")
    host.legend(loc='upper right')
    host.axis["left"].label.set_color(p1.get_color())
    par1.axis["right"].label.set_color(p2.get_color())
    plt.title('Influence of Model Complexity - %s' % conf['estimator'].__name__)
    plt.show()


def _count_nonzero_coefficients(estimator):
    a = estimator.coef_.toarray()
    return np.count_nonzero(a)

# #############################################################################
# Main code
data = {'X_train': X_train, 'X_test': X_test, 'y_train': y_train,
            'y_test': y_test}
configuration = {'estimator': GradientBoostingClassifier,
     'tuned_params': {},
     'changing_param': 'n_estimators',
     'changing_param_values': [10, 50, 75, 100, 200],
     'complexity_label': 'n_estimators',
     'complexity_computer': lambda x: x.n_estimators,
     'data': data,
     'postfit_hook': lambda x: x,
     'prediction_performance_computer': metrics.f1_score,
     'prediction_performance_label': 'f1_weighted',
     'n_samples': 30}
    
prediction_performances, prediction_times, complexities = benchmark_influence(configuration)
plot_influence(configuration, prediction_performances, prediction_times,
               complexities)


# The graph above shows how the number of estimators influences the mean squared error (MSE) for the prediction error and latency (computational performance). The MSE plataues at approximately 1% at 50 estimators or greater, which is good. However the latency increases linearly as the number of estimators increases. From this graph we can interpret that the current model should have 50 estimators to mave the lowest MSE and latency.

# The learning curve above shows the validation and training score of the Gradient Boosting Classifier estimator for a varying number of training samples. 
# 
# Explanation...

# # 8: Validation Curve
# 
# https://scikit-learn.org/stable/modules/learning_curve.html#validation-curve
# 
# This method can be used to find the best hyper-parameter value to make the model as accurate as it can be. This method will calcualte the accuracy score of a model with varying a hyper-parameter and displaying the results in a graph, with confidence intervals. This can only be done with one hyper-parameter at a time.

# In[141]:


tuned_parameters = [['n_estimators', [100,500,1000,2000]], ['learning_rate', [0.01, 0.05, 0.1, 0.2]],
                     ['max_depth', [1,2,3,4]]]

for param_name, param_range in tuned_parameters:
    
    train_scores, test_scores = validation_curve(
        GradientBoostingClassifier(),X_train, y_train, param_name="n_estimators", param_range=param_range,
        cv=5, scoring="f1_weighted", n_jobs=1)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.title("Validation Curve with GBC")
    plt.xlabel(param_name)
    plt.ylabel("Score")
    plt.ylim(0.0, 1.1)
    lw = 2
    plt.semilogx(param_range, train_scores_mean, label="Training score",
                 color="darkorange", lw=lw)
    plt.fill_between(param_range, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.2,
                     color="darkorange", lw=lw)
    plt.semilogx(param_range, test_scores_mean, label="Cross-validation score",
                 color="navy", lw=lw)
    plt.fill_between(param_range, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.2,
                     color="navy", lw=lw)
    plt.legend(loc="best")
    plt.show()


# Explanation...
# 
# We can use these same ranges in the Exhaustive Grid Search cross validation method to confirm that these are the best parameter values for the model.

# # 9: Exhaustive Grid Search (EGS)
# 
# The exhaustive grid search is a method is like using the validation curve method above, but is used to determine the best candidates for specified hyper-parameters and their values of an estimator all in one swoop. 

# In[195]:


# Set the parameters by cross-validation
tuned_parameters = [{'learning_rate': [0.1,0.08,0.05,0.02],
                     'min_samples_leaf': [3,5,9,17],
                     'max_depth': [3,4,6], 
                     'max_features': [1.0,0.3,0.1]}]

print()

clf = GridSearchCV(GradientBoostingClassifier(n_estimators = 2000), tuned_parameters)
clf.fit(X_train, y_train)

print("Best parameters set found on development set:")
print()
print(clf.best_params_)
print()
print("Grid scores on development set:")
print()
means = clf.cv_results_['mean_test_score']
stds = clf.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, clf.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r"% (mean, std * 2, params))
# print()

# print("Detailed classification report:")
# print()
# print("The model is trained on the full development set.")
# print("The scores are computed on the full evaluation set.")
# print()
# y_true, y_pred = y_test, clf.predict(X_test)
# print(classification_report(y_true, y_pred))
# print()

# Note the problem is too easy: the hyperparameter plateau is too flat and the
# output model is the same for precision and recall with ties in quality.


# The EGS method of cross validation shows that in order for this model to have the highest accuracy at predicting, it should have a learning rate of 0.1, max depth of 10, 50 estimators, and a random state of 2. This 

# # Predict age at removal for non-removed platforms
# 
# This CSV contians the same fields as the input, but contians only platform records that do not have a removal date. There are 2,090 platform records.
# 
# https://machinelearningmastery.com/make-predictions-scikit-learn/

# In[78]:


# Pandas complaining about encoding so "ISO-8859-1" seems to fix
df_predict = pd.read_csv(r"P:\05_AnalysisProjects_Working\Offshore Infrastructure and Incidents REORG\03_Analysis\Platforms\Apply VariableBased Ranks\Version2_03262019\Current_activePlatforms_wInc_wRankValues_wAgeAtRemoval.csv", encoding="ISO-8859-1")

# Fit and Transform really don't like NaN.
df_predict.fillna(0, inplace=True)

# Features:
age_p = np.array(df.get('PAge_10'))
lat_p = np.array(df.get('PLATI_5'))
long_p = np.array(df.get('PLONG_4'))
block_p = np.array(df.get('PBloc_7'))
water_depth_p = np.array(df.get('PWate_15'))
water_depth_scaled_p = np.array(df.get('Depth_Scaled'))
num_incs_scaled_p = np.array(df.get('IncCount_Scaled'))
drills_scaled_p = np.array(df.get('SlotDrill_Scaled'))
slots_scaled_p = np.array(df.get('Slot_Scaled'))
cranes_scaled_p = np.array(df.get('Crane_Scaled'))
severity_p = np.array(df.get('Severi_158'))
severity_scaled_p = np.array(df.get('Severity_Scaled'))
wave_scaled_p = np.array(df.get('WaveHe_194'))
wind_scaled_p = np.array(df.get('WindSp_195'))
avg_age_scaled_p = np.array(df.get('Avg_Plat_Age'))
sum_ranks_p = np.array(df.get('Sum_Ranks'))
explosion_p = np.array(df.get('ITExp_20'))
fire_p = np.array(df.get('ITFir_21'))
maj_col_p = np.array(df.get('ITMaj_25'))
min_col_p = np.array(df.get('ITMin_26'))
h2s_release_p = np.array(df.get('ITRep_27'))
muster_p = np.array(df.get('ITReq_28'))
gas_release_p = np.array(df.get('ITShu_29'))
abandonment_p = np.array(df.get('POAba_32'))

input_features = [lat_p, long_p, block_p, water_depth_p, severity_p, wave_scaled_p, wind_scaled_p, num_incs_scaled_p,                 cranes_scaled_p, sum_ranks_p, explosion_p, fire_p, maj_col_p, min_col_p,h2s_release_p, muster_p,                 gas_release_p, abandonment_p]

# Convert to strings because theres some mixture of strings and ints caused by us filling NaN values with 0
# This is ok (I think) because we are going to convert all of them to categorical one-hot encoded lists anyway
for feat in input_features:
    for i in range(len(feat)):
        feat[i] = str(feat[i])
        
age_at_removal_cat = np.array(df.get('Age_at_Rem_Category'))
    
for i in range(len(age_at_removal_cat)):
    age_at_removal_cat[i] = str(age_at_removal_cat[i])

# Expand the zip() generator into an actual list so we can fit/transform it
reshaped_predict = np.array(list(zip(block, water_depth, wave_scaled, wind_scaled,                            cranes, drills, num_incs, severity, age_last, slots, rig_count, slant_slot)))


# In[79]:


# make a prediction
ynew = model.predict(reshaped_predict)
# show the inputs and predicted outputs
for i in range(len(reshaped_predict)):
    print("X=%s, Predicted=%s" % (reshaped_predict[i], ynew[i]))


# The output above shows that when the model is trying to predict with a record that has many fields that are zero, it does not predict the age at removal well. You can see this for the records that have a predicted value that continues to be at about 0.15 years of age

# # Put predicted values in dataframe and export as csv

# In[80]:


# create list of predicted values from 'ynew' array
predicted = ynew.tolist()
# 
# put nump array inot a pandas data frame
df_out = pd.DataFrame(data=reshaped_predict, columns=feat_list)
df_out['Predicted_Age_at_Rem_Category'] = ynew
# for index, row in df_out.iterrows():
#     row['Predicted_Age_at_Removal'] = predicted[index]
df_out


# # Export to CSV

# In[ ]:


df_out.to_csv('Predict_output.csv')

