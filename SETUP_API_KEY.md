# Setting Up Your OpenAI API Key

The RAG Knowledge Base requires an OpenAI API key to function. Follow these steps to set it up:

## Step 1: Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)
5. **Important**: Save it somewhere safe - you won't be able to see it again!

## Step 2: Add the Key to Your .env File

1. Open the `.env` file in the root directory of this project
2. Find the line that says:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Replace `your_openai_api_key_here` with your actual API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
4. Save the file

## Step 3: Restart the Application

The server will automatically reload when you save the `.env` file. If not, restart it:

```bash
# Stop the server (Ctrl+C in the terminal)
# Then restart it
./run.sh
```

## Step 4: Test the Upload

1. Go to http://localhost:8000
2. Try uploading a document (PDF, TXT, or DOCX)
3. You should see a success message!

## Troubleshooting

### "Invalid API key" Error
- Make sure you copied the entire key (starts with `sk-`)
- Check for extra spaces before or after the key
- Make sure the key is on the same line as `OPENAI_API_KEY=`

### "Insufficient quota" Error
- Your OpenAI account needs to have credits
- Add a payment method at https://platform.openai.com/account/billing

### Still Not Working?
- Check the terminal/console for error messages
- Make sure the `.env` file is in the root directory
- Try restarting the server completely

## Cost Information

The application uses:
- **Embeddings**: `text-embedding-ada-002` (~$0.0001 per 1K tokens)
- **LLM**: `gpt-4o-mini` by default (~$0.15 per 1M input tokens)

For typical documents:
- Uploading a 10-page PDF: ~$0.01
- Asking a question: ~$0.001-0.01

You can monitor your usage at: https://platform.openai.com/usage

## Alternative: Use a Different Model

If you want to use a different model, edit the `.env` file:

```bash
# For cheaper/faster responses
LLM_MODEL=gpt-3.5-turbo

# For more powerful responses
LLM_MODEL=gpt-4-turbo-preview

# For the latest model (default)
LLM_MODEL=gpt-4o-mini
```

---

**Need help?** Check the [OpenAI Documentation](https://platform.openai.com/docs) or create an issue in this repository.

