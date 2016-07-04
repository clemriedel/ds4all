# Fraud detection case study

Authors: Joel Carlson, Real Limoges, Joe Warren, Clement Riedel.

In this document we detail how we built an entire end to end pipeline to detect fraud from a flow of data related to event postings and dynamically present the results to the user on a dashboard accessible from an internet browser. 

### EDA

We define 'Premium' transactions as *not* fraud and all the other as fraud. In the dataset, approximately 14000 transactions are not fraudulent, while the remaining 2000 are classified as fraud, leading to a proportion of 0.14.

As predictive features we identified the body length of the description, account age, whether the transaction listed a venue, and the email address domain name as useful variables.
 	
### Preprocessing

We drop all the variables that have not been judged to be relevant and dummify the domain names which were present more than 10 times in the database. 


### Modeling

We chose to build a random forest model to predict whether an event posting was fraudulent. The model predictions do not imply a ground truth about whether a transaciton is fraud or not, but rather flags which transactions need further manual review by presenting fraud probability in the dashbord. 

In order to maximize the proportion of frauds that are correctly identified we chose to optimize the recall as our metric.

To gauge the efficacy of the random forest model we first created an 80/20 training/testing split of the data and trained a random forest classifier with the default parameters. This resulted in an initial recall score of 0.34 on the held-out test data.

We then optimized the model by performing a grid search over parameters including the number of estimators, minimum samples per leaf, and the number of features sampled for each tree. The grid search used 5-fold cross validation with each parameter combination, and the parameters with the highest mean recall were selected as the final model parameters.

The optmized random forest model obtained a recall store of: 0.61.
    
    Optimized random forest:
    Recall: 0.61
    
    Confusion matrix:
                                      
                    Actual                        
                     F     T                         
                  -------------                      
               F | 2064 | 158 |                  
    Predicted     -----------         
               T |  401 | 245 |                 
                  -------------                      
                             

Now that our model is ready, we save it as a pickle that will be later loaded to analyze new data.
