from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pydantic import BaseModel
import tempfile
from app.services.pdf_rag_service import PdfRagService

router = APIRouter()
pdf_service = PdfRagService()

class QuestionRequest(BaseModel):
    question: str

@router.post("/pdf", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)):
    """
    1) Save the uploaded PDF to a temporary file on disk.
    2) Pass that file path to PdfRagService, which uses PyPDFLoader.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Create a named temporary file (on disk) to store PDF bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            # Read the uploaded file bytes
            contents = await file.read()
            # Write them to the temp file
            tmp.write(contents)
            tmp_path = tmp.name

        # Now pass the temporary file path to our service
        await pdf_service.create_vectorstore_from_pdf(tmp_path)

        return {"message": "PDF uploaded and indexed in-memory successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/question", status_code=status.HTTP_201_CREATED)
async def ask_question(request: QuestionRequest):
    """
    Pass the question to PdfRagService, which retrieves context and calls GPT.
    """
    try:
        answer = await pdf_service.answer_query_with_vectorstore(request.question)
        return {"question": request.question, "answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
