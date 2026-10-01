import random
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Banking System", page_icon="🏦", layout="centered")

# Session-scoped data: suitable for a demonstration app.
if "accounts" not in st.session_state:
    st.session_state.accounts = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = None

accounts = st.session_state.accounts


def generate_account_number():
    while True:
        account_number = str(random.randint(10000000, 99999999))
        if account_number not in accounts:
            return account_number


def add_transaction(account_number, transaction_type, amount, details=""):
    accounts[account_number]["transactions"].append(
        {
            "type": transaction_type,
            "amount": amount,
            "details": details,
            "time": datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"),
        }
    )


def create_account(name, phone, pin):
    name = name.strip()
    phone = phone.strip()
    pin = pin.strip()

    if not name:
        return False, "Name cannot be empty.", None
    if not phone.isdigit() or len(phone) != 10:
        return False, "Please enter a valid 10-digit phone number.", None
    if not pin.isdigit() or len(pin) != 4:
        return False, "PIN must contain exactly 4 digits.", None

    account_number = generate_account_number()
    accounts[account_number] = {
        "name": name,
        "phone": phone,
        "pin": pin,
        "balance": 0.0,
        "transactions": [],
    }
    return True, "Account created successfully!", account_number


def money_input(label):
    amount = st.number_input(label, min_value=0.0, step=100.0, format="%.2f")
    return float(amount)


st.title("🏦 Banking System")
st.caption("Python + Streamlit Mini Project")

if st.session_state.logged_in is None:
    tab_create, tab_login = st.tabs(["Create Account", "Login"])

    with tab_create:
        st.subheader("Create a New Account")
        with st.form("create_account_form"):
            name = st.text_input("Full Name")
            phone = st.text_input("10-digit Phone Number", max_chars=10)
            pin = st.text_input("Create 4-digit PIN", type="password", max_chars=4)
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            ok, message, account_number = create_account(name, phone, pin)
            if ok:
                st.success(message)
                st.info(f"Your Account Number is **{account_number}**. Save it for login.")
            else:
                st.error(message)

    with tab_login:
        st.subheader("Account Login")
        with st.form("login_form"):
            account_number = st.text_input("Account Number", max_chars=8)
            login_pin = st.text_input("PIN", type="password", max_chars=4)
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if account_number in accounts and accounts[account_number]["pin"] == login_pin:
                st.session_state.logged_in = account_number
                st.rerun()
            else:
                st.error("Invalid account number or PIN.")

    st.divider()
    st.caption("Demo note: accounts are stored in session memory and reset when the app session restarts.")

else:
    account_number = st.session_state.logged_in
    account = accounts[account_number]

    st.success(f"Welcome, {account['name']}!")
    st.write(f"**Account Number:** `{account_number}`")
    st.metric("Current Balance", f"₹{account['balance']:.2f}")

    menu = st.selectbox(
        "Account Menu",
        [
            "Check Balance",
            "Deposit",
            "Withdraw",
            "Transfer",
            "Transaction History",
            "Change PIN",
        ],
    )

    if menu == "Check Balance":
        st.subheader("💰 Account Balance")
        st.metric("Available Balance", f"₹{account['balance']:.2f}")

    elif menu == "Deposit":
        st.subheader("➕ Deposit Money")
        amount = money_input("Amount to deposit (₹)")
        if st.button("Deposit Money", use_container_width=True):
            if amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                account["balance"] += amount
                add_transaction(account_number, "Deposit", amount)
                st.success(f"₹{amount:.2f} deposited successfully.")
                st.rerun()

    elif menu == "Withdraw":
        st.subheader("➖ Withdraw Money")
        amount = money_input("Amount to withdraw (₹)")
        if st.button("Withdraw Money", use_container_width=True):
            if amount <= 0:
                st.error("Amount must be greater than zero.")
            elif amount > account["balance"]:
                st.error("Insufficient balance.")
            else:
                account["balance"] -= amount
                add_transaction(account_number, "Withdrawal", amount)
                st.success(f"₹{amount:.2f} withdrawn successfully.")
                st.rerun()

    elif menu == "Transfer":
        st.subheader("🔄 Transfer Money")
        receiver = st.text_input("Receiver Account Number", max_chars=8)
        amount = money_input("Amount to transfer (₹)")
        if st.button("Transfer Money", use_container_width=True):
            if receiver not in accounts:
                st.error("Receiver account not found.")
            elif receiver == account_number:
                st.error("You cannot transfer money to your own account.")
            elif amount <= 0:
                st.error("Amount must be greater than zero.")
            elif amount > account["balance"]:
                st.error("Insufficient balance.")
            else:
                account["balance"] -= amount
                accounts[receiver]["balance"] += amount
                add_transaction(account_number, "Transfer", amount, f"Transferred to Account {receiver}")
                add_transaction(receiver, "Transfer Received", amount, f"Received from Account {account_number}")
                st.success(f"₹{amount:.2f} transferred successfully.")
                st.rerun()

    elif menu == "Transaction History":
        st.subheader("📋 Transaction History")
        transactions = account["transactions"]
        if not transactions:
            st.info("No transactions found.")
        else:
            for index, transaction in enumerate(transactions, start=1):
                st.write(
                    f"**{index}. {transaction['type']}** — "
                    f"₹{transaction['amount']:.2f} — {transaction['time']}"
                )
                if transaction["details"]:
                    st.caption(transaction["details"])
                st.divider()

    elif menu == "Change PIN":
        st.subheader("🔐 Change PIN")
        with st.form("change_pin_form"):
            old_pin = st.text_input("Old PIN", type="password", max_chars=4)
            new_pin = st.text_input("New 4-digit PIN", type="password", max_chars=4)
            confirm_pin = st.text_input("Confirm New PIN", type="password", max_chars=4)
            submitted = st.form_submit_button("Change PIN", use_container_width=True)

        if submitted:
            if old_pin != account["pin"]:
                st.error("Incorrect old PIN.")
            elif not new_pin.isdigit() or len(new_pin) != 4:
                st.error("PIN must contain exactly 4 digits.")
            elif new_pin != confirm_pin:
                st.error("New PIN and confirmation do not match.")
            else:
                account["pin"] = new_pin
                st.success("PIN changed successfully.")

    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = None
        st.rerun()
