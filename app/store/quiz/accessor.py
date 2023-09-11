from operator import and_
from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Answer,
    AnswerModel,
    Question,
    QuestionModel,
    Theme,
    ThemeModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        async with self.app.database.session() as s:
            query_create_theme = insert(ThemeModel).values(
                title=title
            )
            await s.execute(query_create_theme)
            await s.commit()

        return await self.get_theme_by_title(title=title)

    async def get_theme_by_title(self, title: str) -> Theme | None:
        async with self.app.database.session() as s:
            query_select_theme = select(ThemeModel).where(
                ThemeModel.title == title
            )

            result = await s.execute(query_select_theme)
        theme = result.scalar()

        return None if theme is None else theme.get_object()

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        async with self.app.database.session() as s:
            query_select_theme_id = select(ThemeModel).where(
                ThemeModel.id == id_
            )

            result = await s.execute(query_select_theme_id)
            theme = result.scalar()

        return None if theme is None else theme.get_object()

    async def list_themes(self) -> list[Theme]:
        async with self.app.database.session() as s:
            query_select_theme_all = select(ThemeModel)

            result = await s.execute(query_select_theme_all)
            themes = result.scalars().all()

        return None if themes is None else themes

    async def create_answers(
        self, question_id: int, answers: list[Answer]
    ) -> list[Answer]:
        async with self.app.database.session() as s:
            query_create_answers = insert(AnswerModel).values(
                [
                    {
                        "title": answer.title,
                        "is_correct": answer.is_correct,
                        "question_id": question_id,
                    }
                    for answer in answers
                ]
            )

            await s.execute(query_create_answers)
            await s.commit()

            query_select_answers = select(AnswerModel).where(
                AnswerModel.question_id == question_id
            )
            result = await s.execute(query_select_answers)
            answers_list = result.scalars().all()

        return [answer.get_object() for answer in answers_list]

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        async with self.app.database.session() as s:
            query_create_question = insert(QuestionModel).values(
                title=title,
                theme_id=theme_id
            )
            await s.execute(query_create_question)
            await s.commit()

            select_new_question = select(QuestionModel).where(
                and_(
                    QuestionModel.title == title,
                    QuestionModel.theme_id == theme_id
                )
            )
            new_question_raw = await s.execute(select_new_question)
            new_question = new_question_raw.scalar()

            new_question.__init__()
   
            answers_list = await self.create_answers(
                question_id=new_question.id,
                answers=answers
            )

            question_obj = new_question.get_object()
            question_obj.answers = answers_list

            return question_obj

    async def add_answer_to_question(self, question: QuestionModel) -> Question:
        question.__init__()
        answea_list = [answer.get_object() for answer in question.answers]
        question_obj = question.get_object()
        question_obj.answers = answea_list
        
        return question_obj

    async def get_question_by_title(self, title: str) -> Question | None:
        async with self.app.database.session() as s:
            query_select_question = (
                    select(QuestionModel)
                    .options(joinedload(QuestionModel.answers))
                    .where(QuestionModel.title==title)
            )
            questions = await s.execute(query_select_question)
            
            question_obj: Question = None
            for question in questions.scalars().unique():
                question_obj = await self.add_answer_to_question(question=question)

            return question_obj
            

    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        async with self.app.database.session() as s:
            if theme_id:
                stmt = (
                    select(QuestionModel)
                    .options(joinedload(QuestionModel.answers))
                    .where(QuestionModel.theme_id==int(theme_id))
                )
            else:
                stmt = (
                    select(QuestionModel)
                    .options(joinedload(QuestionModel.answers))
                )

            questions = await s.execute(stmt)
            questions_list =[]
  
            for question in questions.scalars().unique():
                questions_list.append(
                    await self.add_answer_to_question(question=question)
                )

            return questions_list
