from sqlalchemy.orm import Session, joinedload
from .. import models, schemas
from fastapi import HTTPException, status, Response


def get_all(db: Session):
    blogs = (
        db.query(models.Blog)
        .options(joinedload(models.Blog.creator))
        .all()
    )
    return blogs


def create(request: schemas.BlogCreate, db: Session):
    new_blog = models.Blog(title=request.title,
                           body=request.body, user_id=2)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


def destroy(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    blog.delete(synchronize_session=False)
    db.commit()
    return 'done'


def update(id: int, request: schemas.BlogUpdate, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    blog.update({
        "title": request.title,
        "body": request.body
    })
    db.commit()
    return 'updated successfully'


def show(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with the id {id} is not available")
    #   response.status_code = status.HTTP_404_NOT_FOUND
    #   return {'detail': f"Blog with the id {id} is not available"}
    return blog
