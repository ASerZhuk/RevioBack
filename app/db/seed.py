import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_config import AppConfig

DEFAULT_CONFIG: list[dict] = [
    # ── Ozon selectors ───────────────────────────────────────────
    {
        "key": "ozon.selectors.container",
        "value": json.dumps(["[data-widget=\"webMobListReviews\"]", "[data-widget=\"webListReviews\"]", "[data-widget=\"reviewsList\"]", "[data-widget=\"webReviews\"]"]),
        "description": "Контейнеры блока отзывов",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.item",
        "value": json.dumps(["[data-review-uuid]", "[publishedat][ordertype]", "[data-review-id]"]),
        "description": "Отдельный отзыв (атрибут-якорь)",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.text",
        "value": json.dumps(["[data-widget*=\"reviewText\"]", "[class*=\"reviewText\"]", "[class*=\"body\"]", "p", "div"]),
        "description": "Текст отзыва (fallback-цепочка)",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.pros",
        "value": json.dumps(["[class*=\"advantage\"]", "[class*=\"pros\"]", "[data-widget*=\"pros\"]"]),
        "description": "Достоинства",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.cons",
        "value": json.dumps(["[class*=\"disadvantage\"]", "[class*=\"cons\"]", "[data-widget*=\"cons\"]"]),
        "description": "Недостатки",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.author",
        "value": json.dumps(["[class*=\"userName\"]", "[class*=\"author\"]", "[data-widget*=\"author\"]"]),
        "description": "Автор отзыва",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.date",
        "value": json.dumps(["time", "[class*=\"date\"]", "[data-widget*=\"date\"]"]),
        "description": "Дата отзыва",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.rating",
        "value": json.dumps(["[aria-label*=\"из 5\"]", "[aria-label*=\"out of 5\"]", "[class*=\"rating\"]", "[data-widget*=\"rating\"]"]),
        "description": "Рейтинг отзыва",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.price",
        "value": json.dumps(["[data-widget=\"webPrice\"]", "[data-widget=\"webPdpGrid\"] [data-widget=\"webPrice\"]", "[data-widget=\"webPdpGrid\"] .tsHeadline600Large", ".tsHeadline600Large", "[data-widget*=\"price\"]"]),
        "description": "Цена товара",
        "is_secret": False,
    },
    {
        "key": "ozon.selectors.expand_button_pattern",
        "value": json.dumps("показать полностью|читать полностью|развернуть|show more|read more"),
        "description": "Regex кнопки «Показать полностью»",
        "is_secret": False,
    },

    # ── Wildberries ───────────────────────────────────────────────
    {
        "key": "wb.selectors.reviews_link",
        "value": json.dumps("a[data-testid=\"product-page-reviews\"]"),
        "description": "Ссылка на отзывы на странице товара",
        "is_secret": False,
    },
    {
        "key": "wb.selectors.product_title",
        "value": json.dumps("h2.mo-typography_variant_title3[class*=\"productTitle--\"]"),
        "description": "Заголовок товара на странице отзывов",
        "is_secret": False,
    },
    {
        "key": "wb.api.feedbacks_url",
        "value": json.dumps("https://feedbacks2.wb.ru/feedbacks/v2/"),
        "description": "Базовый URL API отзывов WB (+ imtId)",
        "is_secret": False,
    },
    {
        "key": "wb.fields.text",
        "value": json.dumps(["text", "reviewText", "comment"]),
        "description": "JSON-поля текста отзыва (приоритет слева)",
        "is_secret": False,
    },
    {
        "key": "wb.fields.pros",
        "value": json.dumps(["pros", "pro"]),
        "description": "JSON-поля достоинств",
        "is_secret": False,
    },
    {
        "key": "wb.fields.cons",
        "value": json.dumps(["cons", "con"]),
        "description": "JSON-поля недостатков",
        "is_secret": False,
    },
    {
        "key": "wb.fields.author",
        "value": json.dumps(["userName", "user", "name"]),
        "description": "JSON-поля автора отзыва",
        "is_secret": False,
    },
    {
        "key": "wb.fields.date",
        "value": json.dumps(["createdDate", "updatedDate", "date"]),
        "description": "JSON-поля даты отзыва",
        "is_secret": False,
    },
    {
        "key": "wb.fields.rating",
        "value": json.dumps("productValuation"),
        "description": "JSON-поле рейтинга (число)",
        "is_secret": False,
    },

    # ── LLM ──────────────────────────────────────────────────────
    {
        "key": "llm.api_url",
        "value": json.dumps(""),
        "description": "URL API (OpenAI-совместимый, /chat/completions)",
        "is_secret": False,
    },
    {
        "key": "llm.api_key",
        "value": json.dumps(""),
        "description": "API-ключ",
        "is_secret": True,
    },
    {
        "key": "llm.model",
        "value": json.dumps(""),
        "description": "Название модели",
        "is_secret": False,
    },
    {
        "key": "llm.temperature",
        "value": json.dumps(0.2),
        "description": "Температура генерации (0.0–2.0)",
        "is_secret": False,
    },
    {
        "key": "llm.system_prompt",
        "value": json.dumps("Проанализируй отзывы и самостоятельно определи реальные плюсы и минусы товара. Не раскладывай отдельные отзывы по плюсам и минусам, а сделай общий вывод по товару. Напиши не больше 5 плюсов, не больше 5 минусов и общий вердикт: стоит ли брать товар или нет, исходя из отзывов и найденных плюсов и минусов."),
        "description": "Системный промпт",
        "is_secret": False,
    },
    {
        "key": "llm.user_prompt_prefix",
        "value": json.dumps("Верни только JSON без markdown и без пояснений.\nФормат: {\"pros\":[\"...\"],\"cons\":[\"...\"],\"summary\":\"...\"}\npros и cons — это выводы о товаре по всем отзывам, а не пересказ отдельных отзывов.\nНе помещай один и тот же аспект одновременно в pros и cons; выбери итоговую сторону по общему смыслу отзывов."),
        "description": "Пользовательский промпт (перед JSON отзывов)",
        "is_secret": False,
    },

    # ── Telegram ─────────────────────────────────────────────────
    {
        "key": "telegram.bot_token",
        "value": json.dumps(""),
        "description": "Токен Telegram-бота (@BotFather)",
        "is_secret": True,
    },
    {
        "key": "telegram.chat_id",
        "value": json.dumps(""),
        "description": "ID чата/канала для уведомлений (например -1001234567)",
        "is_secret": False,
    },
    {
        "key": "telegram.enabled",
        "value": json.dumps(False),
        "description": "Включить уведомления в Telegram",
        "is_secret": False,
    },

    # ── App ───────────────────────────────────────────────────────
    {
        "key": "app.reviews_limit",
        "value": json.dumps(50),
        "description": "Максимальное число отзывов для анализа",
        "is_secret": False,
    },
    {
        "key": "app.initial_user_tokens",
        "value": json.dumps(3),
        "description": "Начальное количество токенов для нового пользователя",
        "is_secret": False,
    },
]


async def seed_default_config(session: AsyncSession) -> None:
    for item in DEFAULT_CONFIG:
        existing = await session.get(AppConfig, item["key"])
        if existing is None:
            session.add(AppConfig(**item))
    await session.commit()
