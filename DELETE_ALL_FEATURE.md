# Delete All Documents Feature

## Overview
The "Delete All" feature allows you to permanently remove all documents from your knowledge base with a single click.

## How to Use

### From the Web Interface

1. **Navigate to the main page** at http://localhost:8000
2. **Look for the Documents section** - You'll see a red "🗑️ Delete All" button next to the document count
3. **Click the "Delete All" button**
4. **Confirm the action** - You'll see TWO confirmation dialogs:
   - **First confirmation**: Warns you about permanent deletion
   - **Second confirmation**: Final safety check before deletion
5. **Wait for completion** - The button will show "⏳ Deleting..." while processing
6. **See the results** - A success message will show how many documents were deleted

### Safety Features

⚠️ **Double Confirmation**: You must confirm TWICE to prevent accidental deletions

🔒 **No Undo**: Once deleted, documents cannot be recovered

📊 **Detailed Feedback**: Shows exactly how many documents were deleted and if any failed

### What Gets Deleted

When you click "Delete All":
- ✅ All document files from the upload directory
- ✅ All document chunks from the vector store
- ✅ All embeddings associated with the documents
- ✅ All metadata and references

### API Endpoint

**Endpoint**: `DELETE /api/documents/all`

**Response**:
```json
{
  "message": "Successfully deleted 5 document(s)",
  "deleted_count": 5,
  "failed_count": 0,
  "failed_deletions": []
}
```

**Example using curl**:
```bash
curl -X DELETE "http://localhost:8000/api/documents/all"
```

### Error Handling

If some documents fail to delete:
- The operation continues for remaining documents
- Failed deletions are reported in the response
- You'll see which specific documents failed and why

### When to Use

Use "Delete All" when you want to:
- 🔄 Start fresh with a new set of documents
- 🧹 Clean up test data
- 🗑️ Remove all documents before uploading a new batch
- 🔧 Reset your knowledge base

### Important Notes

1. **Backup First**: If you need to keep any documents, download them before using Delete All
2. **No Recovery**: There is no way to undo this operation
3. **Affects Search**: After deletion, searches will return no results until you upload new documents
4. **Chat History**: Chat sessions are NOT deleted, only the documents

## Technical Details

### Backend Implementation
- Located in `app/api/routes.py`
- Endpoint: `@router.delete("/documents/all")`
- Iterates through all documents and deletes them individually
- Returns detailed statistics about the operation

### Frontend Implementation
- Button located in `frontend/index.html`
- JavaScript function `deleteAllDocuments()` in `frontend/app.js`
- Includes double confirmation dialogs
- Shows loading state during deletion
- Displays success/failure messages

## Troubleshooting

**Button is disabled or grayed out**
- Check if there are any documents to delete
- The button is only active when documents exist

**Deletion fails**
- Check server logs for specific errors
- Ensure you have write permissions to the upload directory
- Verify the vector store is accessible

**Some documents fail to delete**
- Check the error message for specific document IDs
- Try deleting failed documents individually
- Check file permissions in the upload directory

