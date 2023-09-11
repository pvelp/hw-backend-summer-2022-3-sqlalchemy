from dataclasses import dataclass
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    ForeignKey,
    VARCHAR,
)
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Theme:
    id: int or None
    title: str


class ThemeModel(db):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(50), nullable=False, unique=True)

    def get_object(self) -> Theme:
        return Theme(id=self.id, title=self.title)


@dataclass
class Answer:
    title: str
    is_correct: bool


class AnswerModel(db):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(50), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )
    question = relationship("QuestionModel", back_populates="answers")

    def get_object(self) -> Answer:
        return Answer(title=self.title, is_correct=self.is_correct)


@dataclass
class Question:
    id: int or None
    title: str
    theme_id: int
    answers: list["Answer"]


class QuestionModel(db):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(50), nullable=False, unique=True)
    theme_id = Column(
        Integer,
        ForeignKey("themes.id", ondelete="CASCADE"),
        nullable=False,
    )
    answers = relationship("AnswerModel", back_populates="question")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._answers: List[AnswerModel] = list()

    def get_object(self) -> Question:
        return Question(
            id=self.id,
            title=self.title,
            theme_id=self.theme_id,
            answers = [answer.get_object() for answer in self._answers]
        )
