# -*- coding: utf-8 -*-
"""aml-assig2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DiOWSvml4UiRaYoZFxKDV4_TR_TccIVu

**DAT340/DIT886 Applied Machine Learning: Programming Assignment 2 -- Random forests** <br />
**Due Date: 1 February 2021** <br />

## Task 1: Working with a dataset with categorical features

### Step 1 - Reading the data

#### Mounting Files from Google Drive
"""

from google.colab import drive
drive.mount('/content/drive/')

file_paths = ["/content/drive/My Drive/DAT340/adult_train.csv", "/content/drive/My Drive/DAT340/adult_test.csv"]

"""#### Manually Downloading the Data"""

# Download the data
import requests
files = ['adult_train.csv', 'adult_test.csv']
file_paths = []

for file in files: 
    url = 'http://www.cse.chalmers.se/~richajo/dit866/data/{}'.format(file)
    r = requests.get(url)
    file_name = '/content/{}'.format(file)
    file_paths.append(file_name) 
    
    with open(file_name, 'wb') as f:
        f.write(r.content)

"""#### Prepare the Data"""

import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.dummy import DummyClassifier
# from sklearn.model_selection import cross_val_score
  
# Read the CSV file.
data_train = pd.read_csv(file_paths[0])
data_test = pd.read_csv(file_paths[1])


# Select the relevant numerical columns.
selected_cols = [
    'age', 'workclass', 'fnlwgt', 'education', 'education-num', 
    'marital-status', 'occupation', 'relationship', 'race', 'sex',
    'capital-gain', 'capital-loss', 'hours-per-week', 
    'native-country', 'target'
]

train_data = data_train[selected_cols]#.dropna()
test_data = data_test[selected_cols]#.dropna()


# Shuffle the datasets.
train_data_shuffled = train_data.sample(frac=1.0, random_state=0)
test_data_shuffled = test_data.sample(frac=1.0, random_state=0)


# Split into input part X and output part Y.
Xtrain = train_data_shuffled.drop('target', axis=1)
Ytrain = train_data_shuffled['target']

Xtest = test_data_shuffled.drop('target', axis=1)
Ytest = test_data_shuffled['target']

"""### Step 2 - Encoding the features as numbers"""

from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier

import numpy as np

dicts_training_data = Xtrain.to_dict('records')
dicts_test_data = Xtest.to_dict('records')

dv = DictVectorizer()
X_train_encoded = dv.fit_transform(dicts_training_data)
X_test_encoded = dv.transform(dicts_test_data)

# For now, will revisit later reconsider the classifier
clf = DecisionTreeClassifier(random_state=0)
print('Accuracy: ', np.mean(cross_val_score(clf, X_train_encoded, Ytrain)))

"""### Step 3 - Combining the steps"""

from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

pipeline = make_pipeline(DictVectorizer(), DecisionTreeClassifier(random_state=0))
pipeline.fit(Xtrain.to_dict('records'), Ytrain)
print('Accuracy: ', np.mean(cross_val_score(pipeline, dicts_training_data, Ytrain)))

Yguess = pipeline.predict(Xtest.to_dict('records'))
print("Accuracy Score: {}".format(accuracy_score(Ytest, Yguess)))

"""## Task 2: Overfitting and underfitting

### Training process and function
"""

## shared code

import matplotlib.pyplot as plt
from sklearn.metrics import f1_score, accuracy_score
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier


def get_score_for_model(model="DecisionTreeClassifier", max_depth=13, n_estimators=100, measure="f1"):

  max_depths = np.arange(1,max_depth+1)

  clf_train_acc = []
  clf_test_acc = []

  ## create label encoder
  le = preprocessing.LabelEncoder().fit(Ytest)

  # translate true Y
  Ytest_transformed = le.transform(Ytest)
  Ytrain_transformed = le.transform(Ytrain)

  for max_depth in max_depths:  
      if model == "DecisionTreeClassifier":
        clf = DecisionTreeClassifier(random_state=0, 
                                     max_depth=max_depth)

      elif model == "RandomForestClassifier":
        clf = RandomForestClassifier(random_state=0, 
                                     n_estimators=n_estimators, 
                                     n_jobs=-1, 
                                     max_depth=max_depth,
                                     )

      else:
        raise NameError("Not supported model:", model)

      # build pipeline
      pipeline = make_pipeline(DictVectorizer(), clf)
      pipeline.fit(Xtrain.to_dict('records'), Ytrain)

      # translate predicted Y
      predicted_test_transformed = le.transform(pipeline.predict(Xtest.to_dict('records')))
      predicted_train_transformed = le.transform(pipeline.predict(Xtrain.to_dict('records')))
      
      #get scores
      if measure == "f1":
        test_score = f1_score(Ytest_transformed, predicted_test_transformed)
        train_score = f1_score(Ytrain_transformed, predicted_train_transformed)

      elif measure == "accuracy":
        test_score = accuracy_score(Ytest_transformed, predicted_test_transformed)
        train_score = accuracy_score(Ytrain_transformed, predicted_train_transformed)  
      else:
        raise NameError("Not supported measure-score:", measure)


      # append to list
      clf_train_acc.append(train_score)
      clf_test_acc.append(test_score)

  return (clf_train_acc, clf_test_acc)

def draw_plot(train, test, model="Unspecified", measure="f1"):
  max_depth = len(train) + 1
  max_depths = np.arange(1,max_depth)

  plt.plot(max_depths, test, label="test")
  plt.plot(max_depths, train, label="train")
  plt.xticks(max_depths)
  plt.legend()
  plt.title("Different " + str(measure) + "-scores dependent on max_depth for " + model)
  plt.xlabel("max depth")
  plt.ylabel(str(measure)+"-score")
  plt.yticks(np.linspace(0, 1, num=11, dtype=np.float))
  plt.show()

"""### Decision trees f1-score"""

TRAIN_DTC, TEST_DTC = get_score_for_model("DecisionTreeClassifier", max_depth=12, measure="f1")
draw_plot(TRAIN_DTC, TEST_DTC, "DecisionTreeClassifier")

"""Yes, we definitely see a similar effect now.

### Random forests f1-score
"""

n_estimators_dict = {}
best_f1_estimators = {}

for n_estimators in [1,10,25,50,75,100,150,300]:
    n_estimators_dict[n_estimators] = {}
    TRAIN_RF, TEST_RF = get_score_for_model("RandomForestClassifier", n_estimators=n_estimators, measure="f1")
    draw_plot(TRAIN_RF, TEST_RF, "\n RandomForestClassifier with n_estimators:" + str(n_estimators))

    ## store for later
    n_estimators_dict[n_estimators]["train"] = TRAIN_RF
    n_estimators_dict[n_estimators]["test"] = TEST_RF

    best_f1_estimators[n_estimators] = max(TEST_RF)

"""### What's the difference between the curve for a decision tree and for a random - forest with an ensemble size of 1, and why do we see this difference?

"""

DTC_train, DTC_test = get_score_for_model("DecisionTreeClassifier", max_depth=13, measure="f1")
RF_train, RF_test = get_score_for_model("RandomForestClassifier", max_depth=13, n_estimators=1, measure="f1")

draw_plot(DTC_train, DTC_test, "\n DecisionTreeClassifier")
draw_plot(RF_train, RF_test, "\n RandomForestClassifier with n_estimators: 1")

"""The `RandomForestClassifier` gets a random subset of the features to select from for each time we build a tree node (usually $\sqrt{|F|}$, were $F$ is the total set of features) in comparison to the `DecisionTreeClassifier` which selects from every single feature $f \in F$ according to [sklearn]( https://scikit-learn.org/stable/modules/ensemble.html#forest). What this means for the ensemble size of $1$ is that the `DecisionTreeClassifier` will use the overall "best" feature determined by its criterion, whilst the `RandomForestClassifier` will use the "best" feature within its randomized subset of features.

### What happens with the curve for random forests as the ensemble size grows?

As the number size of the ensemble grows (number of trees in the forest) the f1-score plotted becomes less "jittery" and more consistent. This is due to the fact that the f1-score is averaged over more trees, meaning each tree has less of an impact, making the score less erratic.

### What happens with the best observed test set accuracy as the ensemble size grows?
"""

n_estimators_accuracy = {}
best_accuracy_estimators_given_n = {}


for n_estimators in [1,10,25,50,150]:
    n_estimators_accuracy[n_estimators] = {}

    TRAIN_RF, TEST_RF = get_score_for_model("RandomForestClassifier", n_estimators=n_estimators, measure="accuracy")

    draw_plot(TRAIN_RF, TEST_RF, "\n RandomForestClassifier with n_estimators:" + str(n_estimators), measure="accuracy")

    ## store for later
    n_estimators_accuracy[n_estimators]["train"] = TRAIN_RF
    n_estimators_accuracy[n_estimators]["test"] = TEST_RF

    best_accuracy_estimators_given_n[n_estimators] = max(TEST_RF)

print(best_accuracy_estimators_given_n)

data = best_accuracy_estimators_given_n.items()

x = [tup[0] for tup in data]
y = [tup[1] for tup in data]

plt.plot(x, y)
plt.xticks(x)
plt.yticks(np.linspace(0.85, 0.87, num=11, dtype=np.float))
plt.title("Best accuracies for each n_estimators")
plt.xlabel("n_estimators")
plt.ylabel("accuracy")
plt.show()

"""The best observed test set f1-score stays the same, it does not improve nor worsen after an ensemble size of 10. This is perhaps due to the characteristics of the dataset and the model being a binary classifier. When viewing the *accuracy*, it does not change either.

### What happens with the training time as the ensemble size grows?

Training the same classifier as the ensemble size grows the group has observed a significant difference in computational resources and time. Simply put, the bigger the ensemble size grows the longer the training time.

## Task 3: Feature importances in random forest classifiers
"""

# Get importances and names
importances = pipeline.steps[1][1].feature_importances_
names = pipeline.steps[0][1].feature_names_

# Create list of tuples, linking importance with names
tuples = list(zip(names, importances))

# Reverse Sorting
tuples.sort(key=lambda t: t[1], reverse=True)

# Get top ten names
top_ten = [name for name, _ in tuples[:10]]
print(*top_ten, sep='\n')

"""The most important feature in discriminating between the classes `<=50K` and ``>50K`` is whether a person is married (to a civilian, non armed forces). This is likely due to the fact that marital status can be an indicator of wealth,    [Source](https://www.researchgate.net/publication/333965646_Marriage_and_Income_Differences_in_marital_status_on_outcomes_of_individual_wealth), and married people are therefore more likely to earn more than 50K. Getting married is also not very common for very young age groups which might not have had the time to rise in the ranks and increase their salary yet. The marriage in and of itself also costs a lot of money, giving more reason for less wealthy couples not being married.

`fnlwgt` represents the amount of people in the population a particular entry is deemed to represent. For example, a white divorced male earning <=50K with a `fnlwgt` of 100 000 means that there are an estimated 100 000 white divorced males earning <=50K in the entire population. We struggle to find an intutive reason for it being a key discriminator between `<=50K` and `>50K`. Perhaps since only about 24 % of the entries in the entire dataset have `>50K`, a high `fnlwgt` might be more likely to be correlated to `<=50K` since that group is bigger.

`capital-gain` is a measure of the increase of an individuals value of capital assets, for example a house increasing in value. If an individual has a high capital gain it is more likely that that individual is already wealthy, since some percentage of increase of a valuable assets result in a higher capital gain than the same percentage increase of a less valuable asset. For example, if your capital gain is 1 million dollars, it's probably more likely that a few of your valuable assets increased slightly as opposed to some small assets increasing their value by a high factor. A high capital gain can therefore be an indicator of wealth, and thus a high salary. The more money you have, the faster it can grow. If one inspects the 20 entries with the highest `capital-gain`, all of them are `>50K`.

`hours-per-week` is in direct correlation with your income, the more you work, the more you earn. Working only a few hours a week is not going to make it very likely to earn `>50K`, whereas working more hours makes it more likely. However, your income is also dependent on your hourly wage. People with a lower wage might need to work more, and basing the decision purely by `hours-per-week` can therefore be misleading. 

`capital-loss` works similarly to `capital-gain`. Simply, the more valuable assets you have the more they are going to be affected by a slight percentage change in price. A high capital loss might indicate more valueable assets and therefore a more wealthy individual.

As for `workclass=Private`, `occupation=Exec-managerial`, and `occupation=Sales`, these are probably attributes connected to `>50K`. For example, an individual with an executive managerial position probably has a higher salary than the average individual.

Regarding the ordering of these attributes, one would expect high age, and high education to contribute directly to a salary, which, considering their high ranking of importance, they do.

### Alternative way

Using our intuition, we sense that if we have many branching nodes with a certain feature, it will be of higher importance compared to a feature that is not used as frequently. Perhaps a simple approach would be $i_t = \frac{f_t}{n}$, where $i_t$ is importance score for feature $t$, $f_t$ is the number of times feature $t$ is used as branch and $n$ is the total amount of branches. 

More simplistic, it is also possible to create a dummy-classifier, which given a feature simply guesses the majority. Measuring the accuracy of such a classifier could be an alternative way to measure importance.
"""