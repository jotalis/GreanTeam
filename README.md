# GreanTeam
## Inspiration
Finding an Airbnb is difficult, especially searching for one that's _just right._  Guests looking to stay in Dublin seem to share the same sentiment! In an effort to improve the guest experience on Airbnb, we analysed Strata's 2 datasets of Airbnb guests' searches in Dublin and their following inquiries to hosts.

## What it does
Our project consists of three main components: **data visualization and analysis**, **machine learning**, and a **chatbot**. In this Datathon, we used data analysis as a __tool__ to the other parts of our project. As soon as we found which pieces of data were significant to whether a AirBnB user would have their booking accepted, we proceeded to create our machine learning model. This model takes input variables from the dataset provided to us by Melissa Data, but we didn't stop there. We continued on to make a chatbot that is capable of providing recommendations to users based on the data we analyzed.

## Exploration and Preprocessing
* We were initially given two separate datasets
    * Each user had multiple entries, making it difficult to merge the datasets
        * Combined into one set by user ID
* Outliers
    * Remove outliers with a modified version of z-scores

## Visualization / Analysis
We used R's built-in statistical functions and p-value tests to run some preliminary analysis on the composite data file. This allowed us to discover which variables influence acceptance rate for Airbnb's. Using this information, we were able to generate informative plots using Seaborn and train our machine learning model.

## Machine Learning
**Random Forest Classifier Model**
* Compiled dataset
    * Converted qualitative data to numerical using a scikit-learn LabelEncoder
    * Output: Will a guest be accepted by a host? (1 for true, 0 for false)
    * Inputs: Guest message time, host message time, check-in time, origin country
    * Origin country had the biggest impact (accuracy jumped 78% - 98%)

**Overall accuracy: 98.18% // Training time: 41.61ms**

![Machine Learning Model](https://media.discordapp.net/attachments/1228756315858538496/1229108882266132610/Untitled_presentation_1.jpg?ex=662e7bd9&is=661c06d9&hm=707f5154f27aefd3b29cf74a736289a1c6a2ac28fc27d94fe85c3ba4a2e2dbf5&=&format=webp&width=1246&height=701)

## Chatbot
Meet Bobby, an advanced AI tool developed with OpenAI's latest technology in assistants, designed to analyze and visualize data trends directly from datasets.
* Deep Data Analysis: Excels in extracting meaningful insights and patterns.
* Actionable Visualizations: Converts raw data into clear, actionable visual reports for strategic 
decision-making.

![Bobby in action!](https://media.discordapp.net/attachments/1228756315858538496/1229047807781113856/bobby.gif?ex=662e42f7&is=661bcdf7&hm=6b64bcaa7e84ea0447d26ecc69af47e6fdfa16b6b2ec6e0e15d21d0e86adbc2f&=&width=750&height=422)
## Challenges
**Preprocessing**
* Finding a way to merge the datasets was difficult
    * Users had multiple entries in both datasets, so rows were merged
        * Numerical entries were averaged
        * Categorical entries were appended to sets
    * Preparing the data for the machine learning model was also a challenge
        * All categorical data had to be converted to numerical representations

![What we built our project with](https://media.discordapp.net/attachments/1228756315858538496/1229056158245851331/languages.png?ex=662e4abe&is=661bd5be&hm=fbfcf9633f047db2b61abd226a11f47d372309804524c94c144cfa1bb5dd5e99&=&format=webp&quality=lossless&width=687&height=386)

## What We Learned
* Throughout the course of this Datathon, we've developed several skills:
    * We now have a deeper understanding of machine learning techniques
    * We understand how data analysis can be used to highlight problems and inspire solutions
    * Most importantly, we learned to delegate work and collaborate effectively in a team setting

## What's next for Dublin Dive
* We plan to use an expanded range of data
    * The data we used was from 2014 (10 years ago!) so more recent data would be more relevant
* We will also further refine the ML model
    * Potentially using a Neural Network
