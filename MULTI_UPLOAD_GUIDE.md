# Multi-File Upload Feature Guide

## ✨ What's New

Your RAG Knowledge Base now supports **multi-file upload**! You can upload multiple documents at once, making it much faster to build your knowledge base.

## 🚀 Features

### 1. **Multiple File Selection**
- Click the upload area and select multiple files at once
- Hold `Cmd` (Mac) or `Ctrl` (Windows/Linux) to select multiple files
- Or use `Shift` to select a range of files

### 2. **Drag and Drop**
- Drag multiple files from your file explorer
- Drop them onto the upload area
- Files will be uploaded automatically

### 3. **Batch Processing**
- All files are processed in parallel
- See real-time progress for each file
- Get detailed success/failure reports

### 4. **Smart Error Handling**
- If some files fail, others continue processing
- Clear error messages for each failed file
- Successful uploads are saved even if others fail

## 📖 How to Use

### Method 1: Click to Select Multiple Files

1. Go to http://localhost:8000
2. Click on the "📄 Upload Documents" area
3. In the file picker:
   - **Mac**: Hold `Cmd` and click multiple files
   - **Windows/Linux**: Hold `Ctrl` and click multiple files
   - **Range**: Click first file, hold `Shift`, click last file
4. Click "Open"
5. Files will upload automatically

### Method 2: Drag and Drop

1. Open your file explorer/finder
2. Select multiple files (same keyboard shortcuts as above)
3. Drag them to the browser
4. Drop them on the upload area
5. Files will upload automatically

## 📊 Upload Status

After uploading, you'll see:

### ✅ Success Message
```
✅ Successfully uploaded 3 file(s)! Created 245 chunks total.
• document1.pdf (68 chunks)
• document2.txt (92 chunks)
• document3.docx (85 chunks)
```

### ❌ Error Messages (if any)
```
❌ Failed to upload 1 file(s):
• invalid_file.xyz: Unsupported file format. Supported: .pdf, .txt, .docx
```

## 🎯 Supported File Types

- **PDF** (`.pdf`) - Portable Document Format
- **Text** (`.txt`) - Plain text files
- **Word** (`.docx`) - Microsoft Word documents

## 💡 Tips for Best Results

### 1. **File Size**
- Keep individual files under 50MB for best performance
- Very large files may take longer to process

### 2. **File Names**
- Use descriptive filenames
- Avoid special characters
- Good: `company_policy_2024.pdf`
- Avoid: `doc!!!@#$.pdf`

### 3. **Content Quality**
- Ensure PDFs contain actual text (not just images)
- Use clear, well-formatted documents
- Remove unnecessary pages to reduce processing time

### 4. **Batch Size**
- Upload 5-10 files at a time for optimal performance
- For larger batches, consider splitting into multiple uploads

## 🔧 Troubleshooting

### Problem: "Upload failed" for all files

**Cause**: Missing or invalid OpenAI API key

**Solution**:
1. Check the `.env` file in the project root
2. Make sure `OPENAI_API_KEY` is set to your actual key
3. See `SETUP_API_KEY.md` for detailed instructions
4. Restart the server after updating the key

### Problem: Some files fail with "Unsupported file format"

**Cause**: File type not supported

**Solution**:
- Only upload PDF, TXT, or DOCX files
- Convert other formats to one of these types first
- Check file extensions are correct

### Problem: Upload is very slow

**Cause**: Large files or many files at once

**Solution**:
- Upload fewer files at a time
- Split large documents into smaller sections
- Check your internet connection
- Ensure your OpenAI API has sufficient quota

### Problem: Files upload but don't appear in the list

**Cause**: Browser cache or display issue

**Solution**:
- Refresh the page (F5 or Cmd+R)
- Check the browser console for errors (F12)
- Verify files are in the `data/uploads` directory

## 🎨 UI Improvements

### Visual Feedback
- **Hover Effect**: Upload area highlights when you hover
- **Drag Feedback**: Border changes color when dragging files
- **Progress Indicator**: Loading animation during upload
- **Status Messages**: Clear success/error messages with details

### Better Error Messages
- Specific error for each failed file
- Helpful tips for common issues
- Link to setup documentation

## 📝 API Endpoint

If you're using the API directly:

```bash
# Upload multiple files
curl -X POST "http://localhost:8000/api/documents/upload-multiple" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt" \
  -F "files=@document3.docx"
```

Response:
```json
{
  "successful_uploads": [
    {
      "document_id": "abc-123",
      "filename": "document1.pdf",
      "file_size": 102400,
      "file_type": "pdf",
      "chunks_created": 68
    }
  ],
  "failed_uploads": [],
  "total_uploaded": 1,
  "total_failed": 0
}
```

## 🔄 What Happens During Upload

1. **File Validation**: Checks file format is supported
2. **Content Extraction**: Extracts text from the document
3. **Chunking**: Splits text into manageable chunks
4. **Embedding**: Creates vector embeddings using OpenAI
5. **Storage**: Saves to vector database for searching
6. **Confirmation**: Shows success message with details

## 🎯 Next Steps

After uploading your documents:

1. **Ask Questions**: Use the search box to query your knowledge base
2. **View Documents**: See all uploaded documents in the left panel
3. **Delete Documents**: Remove documents you no longer need
4. **Rate Answers**: Help improve the system by rating responses

## 📚 Related Documentation

- `SETUP_API_KEY.md` - How to configure your OpenAI API key
- `QUICKSTART.md` - Complete getting started guide
- `USAGE.md` - Detailed usage instructions
- `README.md` - Project overview

## 🆘 Need Help?

If you encounter issues:

1. Check the terminal/console for error messages
2. Review the documentation files
3. Verify your OpenAI API key is configured
4. Check the browser console (F12) for JavaScript errors
5. Ensure the server is running on http://localhost:8000

---

**Enjoy your enhanced multi-file upload experience! 🎉**

