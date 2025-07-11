# RAG Chatbot Configuration Guide

## 🚀 Quick Start: Moving from Demo to Full Mode

Your RAG chatbot is currently running in **DEMO MODE**. Follow this guide to enable full functionality.

## 📋 Prerequisites

### 1. Snowflake Account
- **Option A: Free Trial** → [Sign up here](https://signup.snowflake.com/)
- **Option B: Organization Account** → Contact your admin

### 2. Mistral API Key
- **Sign up** → [Mistral Console](https://console.mistral.ai/)
- **Free tier available** with generous credits

---

## 🔧 Configuration Steps

### Step 1: Get Snowflake Credentials

**If using Free Trial:**
1. Go to https://signup.snowflake.com/
2. Choose cloud provider (AWS/Azure/GCP)
3. Complete registration
4. Note down:
   - Account identifier (e.g., `abc12345.us-east-1.aws`)
   - Username
   - Password
   - Warehouse (usually `COMPUTE_WH`)

**If using Organization Account:**
Ask your Snowflake admin for:
- Account URL/identifier
- Your username and password
- Warehouse name
- Database creation permissions

### Step 2: Set Up Snowflake Database

1. **Login to Snowflake** using your credentials
2. **Run the setup SQL** from `config/snowflake_setup.sql`:

```sql
-- Create database and schema for RAG chatbot
CREATE DATABASE IF NOT EXISTS RAG_CHATBOT_DB;
USE DATABASE RAG_CHATBOT_DB;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- Create table for storing documents
CREATE TABLE IF NOT EXISTS DOCUMENTS (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    FILENAME VARCHAR(500) NOT NULL,
    CONTENT TEXT NOT NULL,
    METADATA VARIANT,
    UPLOAD_TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PROCESSED BOOLEAN DEFAULT FALSE
);

-- Create table for storing document chunks
CREATE TABLE IF NOT EXISTS DOCUMENT_CHUNKS (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    DOCUMENT_ID NUMBER NOT NULL,
    CHUNK_TEXT TEXT NOT NULL,
    CHUNK_INDEX NUMBER NOT NULL,
    CHUNK_METADATA VARIANT,
    EMBEDDING ARRAY,
    FOREIGN KEY (DOCUMENT_ID) REFERENCES DOCUMENTS(ID)
);

-- Create table for storing chat history
CREATE TABLE IF NOT EXISTS CHAT_HISTORY (
    ID NUMBER AUTOINCREMENT PRIMARY KEY,
    SESSION_ID VARCHAR(100) NOT NULL,
    USER_QUESTION TEXT NOT NULL,
    BOT_RESPONSE TEXT NOT NULL,
    RETRIEVED_DOCUMENTS VARIANT,
    TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create Cortex Search service for semantic search
-- IMPORTANT: Replace YOUR_WAREHOUSE with your actual warehouse name
CREATE OR REPLACE CORTEX SEARCH SERVICE DOCUMENT_SEARCH_SERVICE
ON CHUNK_TEXT
WAREHOUSE = COMPUTE_WH  -- Update this with your warehouse name
TARGET_LAG = '1 minute'
AS (
    SELECT 
        ID,
        CHUNK_TEXT,
        CHUNK_METADATA,
        DOCUMENT_ID
    FROM DOCUMENT_CHUNKS
);
```

### Step 3: Get Mistral API Key

1. **Go to** [Mistral Console](https://console.mistral.ai/)
2. **Sign up** for an account
3. **Navigate to** API Keys section
4. **Create** new API key
5. **Copy** the key (starts with `mistral-`)

### Step 4: Update Environment Variables

Edit your `.env` file in the project root:

```bash
# Change demo mode to false
DEMO_MODE=false

# Add your real Snowflake credentials
SNOWFLAKE_ACCOUNT=your_actual_account_identifier
SNOWFLAKE_USER=your_actual_username
SNOWFLAKE_PASSWORD=your_actual_password
SNOWFLAKE_WAREHOUSE=your_actual_warehouse
SNOWFLAKE_DATABASE=RAG_CHATBOT_DB
SNOWFLAKE_SCHEMA=PUBLIC

# Add your Mistral API key
MISTRAL_API_KEY=your_actual_mistral_api_key

# Application Configuration (optional)
APP_TITLE=RAG Chatbot
APP_DESCRIPTION=AI-powered document Q&A system using Snowflake Cortex Search and Mistral LLM
```

### Step 5: Restart the Application

```bash
# Stop the current app (if running)
# Then restart:
streamlit run app.py
```

---

## 🎯 Example Configurations

### Example 1: Snowflake Free Trial
```bash
DEMO_MODE=false
SNOWFLAKE_ACCOUNT=abc12345.us-east-1.aws
SNOWFLAKE_USER=john_doe
SNOWFLAKE_PASSWORD=mySecurePassword123
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=RAG_CHATBOT_DB
SNOWFLAKE_SCHEMA=PUBLIC
MISTRAL_API_KEY=mistral-abc123def456ghi789
```

### Example 2: Organization Account
```bash
DEMO_MODE=false
SNOWFLAKE_ACCOUNT=mycompany.us-west-2.aws
SNOWFLAKE_USER=jane_smith
SNOWFLAKE_PASSWORD=companyPassword456
SNOWFLAKE_WAREHOUSE=ANALYTICS_WH
SNOWFLAKE_DATABASE=RAG_CHATBOT_DB
SNOWFLAKE_SCHEMA=PUBLIC
MISTRAL_API_KEY=mistral-xyz987uvw654rst321
```

---

## 🔍 Troubleshooting

### Common Issues:

**1. Snowflake Connection Failed**
- ✅ Check account identifier format
- ✅ Verify username/password
- ✅ Ensure warehouse exists and you have access
- ✅ Check network connectivity

**2. Cortex Search Not Available**
- ✅ Ensure you're using a supported Snowflake edition
- ✅ Contact Snowflake support if needed

**3. Mistral API Errors**
- ✅ Verify API key format
- ✅ Check API quota/rate limits
- ✅ Ensure billing is set up (if needed)

**4. Database Permissions**
- ✅ Ensure you can create databases/tables
- ✅ Ask admin for necessary permissions

### Testing Your Configuration:

1. **Health Check** - Use the app's built-in health check
2. **Simple Query** - Try uploading a document and asking a question
3. **Logs** - Check the terminal for detailed error messages

---

## 💡 Tips for Success

### Snowflake Tips:
- Start with the free trial for testing
- Use the default `COMPUTE_WH` warehouse initially
- Ensure Cortex Search is enabled in your region

### Mistral Tips:
- Start with the free tier
- Monitor your usage in the console
- Use `mistral-large-latest` model for best results

### General Tips:
- Keep credentials secure and don't commit to version control
- Test with small documents first
- Monitor costs in both platforms

---

## 🎊 Success!

Once configured, you'll have:
- ✅ Real document upload and processing
- ✅ Intelligent semantic search
- ✅ AI-powered responses
- ✅ Persistent chat history
- ✅ Production-ready RAG pipeline

**Your enterprise-grade RAG chatbot will be fully operational!** 🤖✨ 