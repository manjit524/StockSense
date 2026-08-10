# The Trading Desk (An investment Website)

An AI-powered financial analytics and advisory web application built with Python, Flask, and TensorFlow/Keras. 
This project features real-time/intraday stock tracking, market data analysis, and deep learning prediction models.

---

## 📁 Repository Structure


```text
.
├── static/                         # Frontend static assets (CSS, JavaScript)
│   ├── app.js
│   └── style.css
├── templates/                      # HTML templates (Flask views)
│   ├── about.html
│   ├── base.html
│   ├── contact.html
│   ├── input.html
│   ├── landing.html
│   ├── loading.html
│   ├── login.html
│   ├── markets.html
│   ├── output.html
│   └── reports.html
├── .gitignore                      # Configured to ignore virtualenvs, cache & datasets
├── advisor_engine.py               # Core financial advisory engine logic
├── app.py                          # Main Flask application entrypoint
├── etf_tickers.py                  # ETF data configurations
├── intraday_advisor.py             # Short-term market signals and recommendations
├── intraday_engine.py              # Intraday market data processing engine
├── markets_data.py                 # Market data extraction scripts
├── reports_data.py                 # Report generation utilities
├── sp500_tickers_cache.json        # Cached tickers list
├── stock_advisor_multi_exchange.py # Multi-exchange stock data handling
├── train_model.py                  # Keras model training pipeline
├── us_tickers.py                   # US stock tickers dataset/utility
├── requirements.txt                # Required Python dependencies
└── README.md                       # Project documentation
```
##Do this steps only one time in your computer.

#Step 1: Clone the Repository & Navigate into Folder

Opens VS Code, opens the integrated Terminal (Ctrl + ~), and runs:
git clone https://github.com/manjit524/The_Trading_Desk.git
cd The_Trading_Desk

#Step 2: Create & Activate Virtual Environment

python -m venv myenv
myenv\Scripts\activate

#Step 3: Install Required Packages

pip install -r requirements.txt

#Step 4 Add Dataset

Dataset add by yourself as i already shared it with everyone.
In advisor_engine.py find this:
NSE_FOLDER = "C:/Users/Manjit/Downloads/Market_Data/NSE"
BSE_FOLDER = "C:/Users/Manjit/Downloads/Market_Data/BSE"
US_FOLDER = "C:/Users/Manjit/Downloads/Market_Data/US"
And change this with your folder path.

#Step 5: Run model as usual(run this steps every time you have to run code):

python stock_advisor_multi_exchange.py 
python train_model.py (when you run this 2 command then in your project folder it will automatic create 2 file's advisor_model.keras and master_df_cache.pkl) (If you want updated data then only you run this two steps otherwise run only app.py)
python app.py   

##How to Make Changes and Push Code (Never make changes directly on the main branch. Follow this workflow:)

#Create a new branch for your feature:
git checkout -b feature-your-task-name (gave task name as per your changes eg. if you wan to change login page then run git checkout -b feature-login-page)

#After making code edits, stage and commit your changes:
git add .
git commit -m "Add description of what you changed"

#Push your branch to GitHub:
git push origin feature-your-task-name

#At Last:
Go to https://github.com/manjit524/The_Trading_Desk and click Compare & pull request to submit your work for review.

Once reviewed and merged into main, all other team members can click the Sync Changes / Refresh button in the bottom-left corner of VS Code to pull the latest code.


##Dont do this all for new code with changes just run this in VSCode Terminal:

git pull origin main



