import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

if 'expenses' not in st.session_state:
    st.session_state['expenses'] = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])

if 'history' not in st.session_state:
    st.session_state['history'] = []

def add_expense(date, category, amount, description):
    if amount <= 0:
        st.error("Amount must be greater than zero!")
        return
    new_expense = pd.DataFrame([[date, category, amount, description]], 
                               columns=st.session_state['expenses'].columns)
    
    if not st.session_state['expenses'][(st.session_state['expenses']['Date'] == date) & 
                                        (st.session_state['expenses']['Category'] == category) & 
                                        (st.session_state['expenses']['Amount'] == amount) & 
                                        (st.session_state['expenses']['Description'] == description)].empty:
        st.error("Duplicate expense detected! Not added.")
    else:
        st.session_state['expenses'] = pd.concat([st.session_state['expenses'], new_expense], ignore_index=True)
        st.session_state['history'].append(f"Added expense: {date}, {category}, {amount}, {description}")

def delete_expense(index):
    if 1 <= index <= len(st.session_state['expenses']):
        deleted_expense = st.session_state['expenses'].iloc[index - 1]
        st.session_state['expenses'].drop(index - 1, inplace=True)
        st.session_state['expenses'].reset_index(drop=True, inplace=True)
        st.session_state['history'].append(f"Deleted expense: {deleted_expense['Date']}, {deleted_expense['Category']}, {deleted_expense['Amount']}, {deleted_expense['Description']}")
        st.success("Expense deleted successfully!")
    else:
        st.error("Invalid index for deletion.")

def load_expenses():
    uploaded_file = st.file_uploader("Choose a file", type=['csv'])
    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
            if all(col in data.columns for col in ['Date', 'Category', 'Amount', 'Description']):
                st.session_state['expenses'] = pd.concat([st.session_state['expenses'], data], ignore_index=True)
                st.session_state['history'].append("Loaded expenses from file.")
                st.success("Expenses loaded successfully!")
            else:
                st.error("Uploaded file does not have the required columns.")
        except Exception as e:
            st.error(f"Error loading file: {e}")

def save_expenses():
    file_name = st.text_input("Enter file name (with .csv extension):", value="expenses.csv")
    if st.button("Save File"):
        st.session_state['expenses'].to_csv(file_name, index=False)
        st.session_state['history'].append(f"Saved expenses to file: {file_name}")
        st.success(f"Expenses saved successfully as {file_name}!")

def visualize_expenses():
    if st.session_state['expenses'].empty:
        st.warning("No expenses to visualize!")
        return
    
    aggregated_data = st.session_state['expenses'].groupby('Category', as_index=False)['Amount'].sum()
    fig, ax = plt.subplots()
    sns.barplot(data=aggregated_data, x='Category', y='Amount', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    st.session_state['history'].append("Visualized expenses.")

def calculate_daily_totals():
    if st.session_state['expenses'].empty:
        st.warning("No expenses to calculate daily totals!")
        return
    daily_totals = st.session_state['expenses'].groupby('Date', as_index=False)['Amount'].sum()
    st.write("### Daily Totals")
    st.dataframe(daily_totals)
    st.session_state['history'].append("Calculated daily totals.")

st.title("Daily Expenses Tracker")
with st.sidebar:
    st.header("Add Expenses")
    date = st.date_input("Date")
    category = st.selectbox("Category", ['Food', 'Transport', 'Entertainment', 'Utilities', 'Other'])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    description = st.text_input("Description")
    if st.button("Add"):
        add_expense(date, category, amount, description)

    st.header("File Operations")
    load_expenses()
    save_expenses()

st.header("Expenses")
if not st.session_state['expenses'].empty:
    st.dataframe(st.session_state['expenses'])
    delete_index = st.number_input("Enter the index of the expense to delete", min_value=1, max_value=len(st.session_state['expenses']), step=1, format="%d")
    if st.button("Delete Expense"):
        delete_expense(delete_index)
else:
    st.write("No expenses added yet.")

st.header("Visualization")
if st.button("Visualize Expenses"):
    visualize_expenses()

st.header("Daily Totals")
if st.button("Calculate Daily Totals"):
    calculate_daily_totals()

st.header("Action History")
if st.button("View History"):
    st.write("### Action History")
    st.write("\n".join(st.session_state['history']))
