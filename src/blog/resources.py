from fastapi import APIRouter, status, HTTPException

from blog.domains import Admin
from blog.schemas import (
    GetArticlesModel,
    CreateArticleModel,
    LoginModel,
    GetArticleModel,
    ErrorModel,
)

from blog import services
from blog.repositories import ShelveArticlesRepository, MemoryUsersRepository

router = APIRouter()


@router.get("/articles", response_model=GetArticlesModel)
def get_articles() -> GetArticlesModel:
    articles = services.get_articles(articles_repository=ShelveArticlesRepository())
    return GetArticlesModel(
        items=[
            GetArticleModel(id=article.id, title=article.title, content=article.content)
            for article in articles
        ]
    )


@router.post(
    "/articles",
    response_model=GetArticleModel, # 201 статус код потому что мы создаем объект – стандарт HTTP
    status_code=status.HTTP_201_CREATED,
    responses={201: {"model": GetArticleModel}, 401: {"model": ErrorModel}},
    # Это нужно для сваггера. Мы перечисляем ответы эндпоинта, чтобы получить четкую документацию.
)
# credentials – тело с логином и паролем.
# Обычно аутентификация выглядит сложнее, но для нашего случая пойдет и так.
def create_article(article: CreateArticleModel, credentials: LoginModel):
    current_user = services.login(
        username=credentials.username,
        password=credentials.password,
        users_repository=MemoryUsersRepository(),
    )

    # Authentication
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user"
        )

    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden resource"
        )

    article = services.create_article(
        title=article.title,
        content=article.content,
        articles_repository=ShelveArticlesRepository(),
    )

    return GetArticleModel(id=article.id, title=article.title, content=article.content)
