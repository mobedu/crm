from crm.db import db, BaseModel


class KnowledgeBase(db.Model, BaseModel):

    __tablename__ = "knowledgebases"

    title = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    category_id = db.Column(
        db.String(5),
        db.ForeignKey("knowledgebase_categories.id")
    )

    author_id = db.Column(
        db.String(5),
        db.ForeignKey("users.id")
    )

    content = db.Column(
        db.Text(),
        index=True
    )

    tasks = db.relationship(
        "Task",
        backref="knowledge_base"
    )

    comments = db.relationship(
        "Comment",
        backref="knowledge_base"
    )

    def __str__(self):
        return self.title


class KnowledgeBaseCategory(db.Model, BaseModel):

    __tablename__ = "knowledgebase_categories"

    name = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    description = db.Column(
        db.Text()
    )

    knowledge_bases = db.relationship(
        "KnowledgeBase",
        backref="category"
    )

    def __str__(self):
        return self.name
