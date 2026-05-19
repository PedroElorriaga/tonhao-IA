import base64
import mimetypes
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from langchain_core.messages import HumanMessage

from src.database.sqlite_config import SessionLocal, get_db
from src.modules.agent.graph import get_graph
from src.modules.auth.dependencies import get_current_user, require_agent
from src.modules.auth.model import User
from src.modules.ticket.model import Ticket, TicketReply
from src.modules.ticket.schema import (
    PaginatedTicketsResponse,
    ReplyCreate,
    ReplyResponse,
    ReplyUpdate,
    TicketResponse,
    TicketStatus,
    TicketPriority,
    TicketUpdate,
)

UPLOADS_DIR = os.path.join(os.path.dirname(
    __file__), "..", "..", "..", "uploads")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

_SUPPORTED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _build_message_content(text: str, attachment_path: str | None) -> str | list:
    """Return plain text or a multimodal list depending on the attachment type."""
    if not attachment_path:
        return text

    mime_type, _ = mimetypes.guess_type(attachment_path)

    if mime_type in _SUPPORTED_IMAGE_MIMES:
        try:
            with open(attachment_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            return [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {
                    "url": f"data:{mime_type};base64,{image_data}"}},
            ]
        except Exception:
            return text

    if mime_type == "application/pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(attachment_path)
            pdf_text = "\n".join(page.extract_text()
                                 or "" for page in reader.pages)
            return f"{text}\n\n[Conteúdo do anexo PDF]:\n{pdf_text}"
        except Exception:
            return text

    return text


router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Depends(get_current_user)],  # all routes require auth
)


@router.get("", response_model=PaginatedTicketsResponse)
def list_tickets(
    db: Session = Depends(get_db),
    status: TicketStatus | None = Query(None),
    priority: TicketPriority | None = Query(None),
    category: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    if user.role == "agent":
        q = db.query(Ticket)
    else:
        q = db.query(Ticket).filter(Ticket.client_name == user.name)

    if status:
        q = q.filter(Ticket.status == status)
    if priority:
        q = q.filter(Ticket.priority == priority)
    if category:
        q = q.filter(Ticket.category == category)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Ticket.title.ilike(term),
                Ticket.description.ilike(term),
                Ticket.client_name.ilike(term),
            )
        )

    total = q.count()
    items = q.order_by(Ticket.created_at.desc()).offset(
        (page - 1) * page_size).limit(page_size).all()

    return PaginatedTicketsResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


def __generate_first_ai_reply(
    ticket_id: str,
    title: str,
    category: str,
    description: str | None,
    attachment_path: str | None = None,
) -> None:
    db = SessionLocal()
    try:
        ai_text = (
            f"titulo: {title}\n"
            f"categoria: {category}\n"
            f"descrição: {description}\n"
        )
        message_content = _build_message_content(ai_text, attachment_path)
        graph = get_graph()
        result = graph.invoke(
            {"messages": [HumanMessage(content=message_content)]},
            config={"configurable": {"thread_id": ticket_id}},
        )
        ai_text = result["messages"][-1].content
        if isinstance(ai_text, list):
            ai_text = ai_text[0]["text"]

        first_reply = TicketReply(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            author="AI Assistant",
            body=ai_text,
            is_ai=True,
        )
        db.add(first_reply)
        db.commit()
    except Exception:
        pass
    finally:
        db.close()


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    title: str = Form(...),
    category: str = Form(...),
    description: str | None = Form(None),
    priority: TicketPriority = Form("medium"),
    attachment: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
):
    attachment_url: str | None = None
    attachment_name: str | None = None

    if attachment and attachment.filename:
        content = attachment.file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413, detail="Attachment exceeds maximum allowed size")

        ext = os.path.splitext(attachment.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        upload_path = os.path.abspath(os.path.join(UPLOADS_DIR, filename))
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)

        with open(upload_path, "wb") as f:
            f.write(content)

        attachment_url = f"/uploads/{filename}"
        attachment_name = attachment.filename

    ticket = Ticket(
        id=str(uuid.uuid4()),
        title=title,
        client_name=current_user.name,
        category=category,
        description=description,
        priority=priority,
        attachment_url=attachment_url,
        attachment_name=attachment_name,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    background_tasks.add_task(
        __generate_first_ai_reply,
        ticket.id,
        ticket.title,
        ticket.category,
        ticket.description,
        upload_path if attachment and attachment.filename else None,
    )

    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_agent),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_agent),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()


@router.get("/{ticket_id}/replies", response_model=list[ReplyResponse])
def list_replies(ticket_id: str, db: Session = Depends(get_db)):
    if db.get(Ticket, ticket_id) is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return (
        db.query(TicketReply)
        .filter(TicketReply.ticket_id == ticket_id)
        .order_by(TicketReply.created_at)
        .all()
    )


@router.post("/{ticket_id}/replies", response_model=ReplyResponse, status_code=201)
def create_reply(ticket_id: str, payload: ReplyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.get(Ticket, ticket_id) is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    reply = TicketReply(
        id=str(uuid.uuid4()),
        ticket_id=ticket_id,
        author=current_user.name,
        body=payload.body,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


@router.patch("/{ticket_id}/replies/{reply_id}", response_model=ReplyResponse)
def update_reply(
    ticket_id: str,
    reply_id: str,
    payload: ReplyUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_agent),
):
    reply = db.get(TicketReply, reply_id)
    if reply is None or reply.ticket_id != ticket_id:
        raise HTTPException(status_code=404, detail="Reply not found")
    if not reply.is_ai:
        raise HTTPException(
            status_code=403, detail="Only AI replies can be edited")

    reply.body = payload.body
    db.commit()
    db.refresh(reply)
    return reply


@router.post("/{ticket_id}/ai-reply", response_model=ReplyResponse, status_code=201)
def ai_reply(
    ticket_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_agent),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status == "closed":
        raise HTTPException(
            status_code=403, detail="Cannot generate AI reply for a closed ticket")

    last_ai_reply = (
        db.query(TicketReply)
        .filter(TicketReply.ticket_id == ticket_id, TicketReply.is_ai == True)
        .order_by(TicketReply.created_at.desc())
        .first()
    )

    if last_ai_reply is None:
        content = (f"titulo: {ticket.title}\n"
                   f"categoria: {ticket.category}\n"
                   f"descrição: {ticket.description}\n"
                   )
    else:
        new_user_replies = (
            db.query(TicketReply)
            .filter(
                TicketReply.ticket_id == ticket_id,
                TicketReply.is_ai == False,
                TicketReply.created_at > last_ai_reply.created_at,
            )
            .order_by(TicketReply.created_at)
            .all()
        )
        if not new_user_replies:
            raise HTTPException(
                status_code=400, detail="No new user replies to respond to")

        content = "\n".join(r.body for r in new_user_replies)

    graph = get_graph()
    result = graph.invoke(
        {"messages": [HumanMessage(content=content)]}, config={"configurable": {"thread_id": ticket_id}})

    ai_text = result["messages"][-1].content
    if isinstance(ai_text, list):
        ai_text = ai_text[0]["text"]

    reply = TicketReply(
        id=str(uuid.uuid4()),
        ticket_id=ticket_id,
        author="AI Assistant",
        body=ai_text,
        is_ai=True,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply
