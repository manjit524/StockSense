# StockSense (An investment Website)

An AI-powered financial analytics and advisory web application built with Python, Flask, and TensorFlow/Keras. 
This project features real-time/intraday stock tracking, market data analysis, and deep learning prediction models.
---

##  Initial Setup Instructions (Do these steps only ONE time on your computer)

### Step 1: Clone the Repository & Navigate into Folder
Open VS Code, open the integrated Terminal (`Ctrl + ~`), and run:
```bash
git clone https://github.com/manjit524/StockSense
cd StockSense
```

### Step 2: Create & Activate Virtual Environment
```bash
python -m venv myenv
myenv\Scripts\activate
```

### Step 3: Install Required Packages
```bash
pip install -r requirements.txt
```

### Step 4: Add Dataset
Dataset add by yourself as I already shared it with everyone.  
In `advisor_engine.py` find this:
```python
NSE_FOLDER = "YOUR_NSE_FOLDER_PATH"
BSE_FOLDER = "YOUR_BSE_FOLDER_PATH"
US_FOLDER = "YOUR_US_FOLDER_PATH"
```
And change this with your folder path.

---

##  Step 5: Run Model & Application

Run this step every time you need to run the code:
```bash
python stock_advisor_multi_exchange.py
python train_model.py
```
*(When you run these 2 commands, it will automatically create 2 files in your project folder: `advisor_model.keras` and `master_df_cache.pkl`.)*  
*(If you want updated data then only run these two steps, otherwise run only `python app.py`)*

```bash
python app.py
```

---

##  How to Make Changes and Push Code

**Never make changes directly on the main branch. Follow this workflow:**

### 1. Create a new branch for your feature:
```bash
git checkout -b feature-your-task-name
```
*(Give task name as per your changes, e.g., if you want to change the login page, run `git checkout -b feature-login-page`)*

### 2. After making code edits, stage and commit your changes:
```bash
pip freeze > requirements.txt
git add .
git commit -m "Add description of what you changed"
```

### 3. Push your branch to GitHub:
```bash
git push origin feature-your-task-name
```

### 4. At Last:
Go to [https://github.com/manjit524/StockSense](https://github.com/manjit524/StockSense) and click **Compare & pull request** to submit your work for review.

Once reviewed and merged into `main`, all other team members can click the **Sync Changes / Refresh** button in the bottom-left corner of VS Code to pull the latest code.

---

##  How to Get Latest Code Changes

Don't repeat all initial setup steps for new code changes. Just run this in VS Code Terminal:

```bash
git pull origin main
