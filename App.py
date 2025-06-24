import streamlit as st
import pandas as pd
import requests
import json
st.set_page_config(page_title="QBO Journal Uploader", layout="wide")
st.title("📤 Upload Journal Excel File")

# 🔹 Step 1: Define the payload function
def generate_payload(df):
    journal_lines = []

    for _, row in df.iterrows():
        if pd.notna(row.get("Account")) and pd.notna(row.get("amount")):
            journal_lines.append({
                "DetailType": "JournalEntryLineDetail",
                "Amount": abs(float(row["amount"])),
                "JournalEntryLineDetail": {
                    "PostingType": "Debit" if row["amount"] >= 0 else "Credit",
                    "AccountRef": {
                        "name": row["Account"],
                        "value": "1"
                    }
                },
                "Description": row.get("Description", "")
            })

    payload = {
        "Line": journal_lines,
        "TxnDate": "2025-03-31",
        "PrivateNote": "Posted via Streamlit App"
    }

    return payload

# 🔹 Step 2: Upload and process Excel
uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully!")
    st.subheader("📊 Data Preview")
    st.dataframe(df)


def loadpayloadsilently():
    try:
        with open("payload.json", "r") as file:
            return json.load(file)
    except Exception as e:
        return None
    payload = load_payload_silently()
    if payload:
        if st.button("Send to QuickBooks"):
            st.success("✅ Sent silently!")
        else:
            st.warning("📂 payload.json file not found.")

def save_payload_to_file(payload, filename="payload.json"):
    try:
        with open(filename, "w") as f:
            json.dump(payload, f, indent=4)
        print(f"✅ Payload saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving payload: {e}")
        save_payload_to_file(payload)
        df = pd.read_excel(uploaded_file)
        payload = generate_payload(df)
        save_payload_to_file(payload, "payload.json")



# 🔹 Step 4: Send to QuickBooks
if st.button("🚀 Push to QuickBooks"):
    try:
        access_token = st.secrets["ACCESS_TOKEN"]
        realm_id = st.secrets["Realm_ID"]

        url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/journalentry"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            st.success("🎉 Successfully posted to QuickBooks!")
            st.json(response.json())
        else:
            st.error(f"❌ Failed to post! Status: {response.status_code}")
            st.json(response.json())

    except Exception as e:
        st.error(f"🔐 Error sending to QBO: {e}")
