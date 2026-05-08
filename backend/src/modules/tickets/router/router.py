import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.settings import get_db
from modules.tickets.model.model import Ticket
from modules.tickets.schema.schema import (
    PaginatedTicketsResponse,
    TicketResponse,
    TicketStatus,
    TicketPriority,
    TicketUpdate,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=PaginatedTicketsResponse)
async def list_tickets(
    db: AsyncSession = Depends(get_db),
    status: TicketStatus | None = Query(None),
    priority: TicketPriority | None = Query(None),
    category: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    stmt = select(Ticket)

    if status:
        stmt = stmt.where(Ticket.status == status)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    if category:
        stmt = stmt.where(Ticket.category == category)
    if search:
        term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Ticket.title.ilike(term),
                Ticket.description.ilike(term),
                Ticket.client_name.ilike(term),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    items_stmt = (
        stmt.order_by(Ticket.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(items_stmt)
    items = result.scalars().all()

    return PaginatedTicketsResponse(items=list(items), total=total, page=page, page_size=page_size)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    db: AsyncSession = Depends(get_db),
    title: str = Form(...),
    client_name: str = Form(...),
    category: str = Form(...),
    description: str | None = Form(None),
    priority: TicketPriority = Form("medium"),
    attachment: UploadFile | None = File(None),
):
    attachment_url: str | None = None
    attachment_name: str | None = None

    if attachment and attachment.filename:
        content = await attachment.read()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="Attachment exceeds maximum allowed size")

        ext = os.path.splitext(attachment.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        upload_path = os.path.join(os.path.abspath(settings.upload_dir), filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)

        with open(upload_path, "wb") as f:
            f.write(content)

        attachment_url = f"/uploads/{filename}"
        attachment_name = attachment.filename

    ticket = Ticket(
        id=str(uuid.uuid4()),
        title=title,
        client_name=client_name,
        category=category,
        description=description,
        priority=priority,
        attachment_url=attachment_url,
        attachment_name=attachment_name,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    db: AsyncSession = Depends(get_db),
):
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)

    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await db.delete(ticket)
    await db.commit()
