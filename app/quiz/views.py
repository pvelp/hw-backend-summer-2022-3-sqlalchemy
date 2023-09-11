from typing import List, Optional
from aiohttp_apispec import (
    docs,
    querystring_schema,
    request_schema,
    response_schema
)
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPConflict,
)

from app.quiz.models import Answer, Theme
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @docs(
        tags=['VKBot'],
        summary='Adding a new theme',
        description='Add new theme in database'
    )
    @response_schema(OkResponseSchema, 200)
    async def post(self) -> Optional[Theme]:
        title = self.data.get("title")

        if await self.store.quizzes.get_theme_by_title(title=title):
            raise HTTPConflict

        theme = await self.store.quizzes.create_theme(title=title)

        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(
        tags=['VKBot'],
        summary='List all themes',
        description='List all themes from database'
    )
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme.get_object()) for theme in themes]

        return json_response(data={'themes': raw_themes})


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=['VKBot'],
        summary='Adding a new question',
        description='Adding a new question in database'
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):

        MIN_ANSWERS = 2
        answers = self.data.get('answers')
        title = self.data.get('title')
        theme_id=self.data.get('theme_id')
        count_correct_answers = 0
        answers_list: List[Answer] = list()

        if len(answers) < MIN_ANSWERS:
            raise HTTPBadRequest
        
        for answer in answers:
            if answer['is_correct'] == True:
                count_correct_answers += 1
            answers_list.append(Answer(**answer))
        
        if count_correct_answers != 1:
            raise HTTPBadRequest

        if not await self.store.quizzes.get_theme_by_id(id_=theme_id):
            raise HTTPNotFound

        if await self.store.quizzes.get_question_by_title(title=title):
            raise HTTPConflict
        
        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers = answers_list
        )
        # question = await self.store.quizzes.create_question(**self.data)

        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=['VKBot'],
        summary='List all Questions',
        description='List all Questions from database'
    )
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        theme_id = self.request.query.get('theme_id')
        
        list_questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        
        raw_questions = [QuestionSchema().dump(q) for q in list_questions]

        return json_response(data={'questions': raw_questions})
