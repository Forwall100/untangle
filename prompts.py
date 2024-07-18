from langchain_core.prompts import ChatPromptTemplate

text_analyze_prompt_ru = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Вы - высококвалифицированный эксперт по анализу контента и информационной архитектуре.
        Ваша задача - глубоко проанализировать предоставленный текст и предоставить точную, информативную и полную информацю для последущей категоризации.
        """,
        ),
        (
            "human",
            """Внимательно проанализируйте следующий текст:\n\n{text}\n\n
        Предоставьте:
        1. ЛАКОНИЧНОЕ название (МАКСИМУМ 5 СЛОВ), отражающее суть текста.
        2. СЖАТОЕ, но ИНФОРМАТИВНОЕ описание (50-100 СЛОВ), охватывающее ключевые аспекты текста.
        3. РАЗНООБРАЗНЫЙ набор тегов (ОТ 5 ДО 20 БЕЗ ПОВТОРЕНИЙ), включающий:

        а) ОБЩИЕ теги (МИНИМУМ 2-10 ТЭГОВ):
        - Основные области (например, наука, искусство, технологии, общество)
        - Широкие темы (например, образование, здоровье, финансы, экология)
        - Жанры или типы контента (например, новости, инструкция, обзор, анализ)
        - Целевая аудитория (например, специалисты, студенты, родители)
        - Эмоциональный тон (например, вдохновляющее, критическое, юмористическое)
        - Тип важности информации (например, полезное, важное, интересное)

        б) КОНКРЕТНЫЕ теги (МИНИМУМ 3-10 ТЭГОВ):
        - Точные термины, концепции, методологии
        - Имена людей, организаций, брендов
        - Названия продуктов, технологий, инструментов
        - Географические локации
        - Временные периоды или даты
        - Уникальные идентификаторы или ключевые слова из текста

        ВАЖНО:
        - Выбирайте наиболее релевантные и точные теги, отражающие глубину и нюансы текста.
        - Не ограничивайтесь приведенными примерами, мыслите широко и креативно.
        - Если текст соответсвтует какому-то из уже существующих тэгов, то ОБЯЗАТЕЛЬНО использовать его

        СПИСОК СУЩЕСТВУЮЩИХ ТЭГОВ:
        {all_tags}

        Ответ предоставьте СТРОГО в формате JSON на РУССКОМ ЯЗЫКЕ:
        {{
            "title": "краткое название",
            "summary": "информативное описание",
            "tags": ["тег1", "тег2", "тег3", ...]
        }}
        """,
        ),
    ]
)


text_analyze_prompt_en = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a highly skilled expert in content analysis and information architecture.
        Your task is to deeply analyze the provided text and provide accurate, informative, and comprehensive information for subsequent categorization.
        """,
        ),
        (
            "human",
            """Carefully analyze the following text:\n\n{text}\n\n
        Please provide:
        1. A CONCISE title (UP TO 5 WORDS MAXIMUM) that reflects the essence of the text.
        2. A CONCISE but INFORMATIVE description (50-100 WORDS) covering key aspects of the text.
        3. A DIVERSE set of tags (FROM 10 TO 50 WITHOUT REPEATS), including:

        a) GENERAL tags (AT LEAST 5-25 TAGS):
        - Main areas (e.g., science, art, technology, society)
        - Broad topics (e.g., education, health, finance, environment)
        - Genres or content types (e.g., news, instruction, review, analysis)
        - Target audience (e.g., professionals, students, parents)
        - Emotional tone (e.g., inspiring, critical, humorous)
        - Importance of information type (e.g., useful, important, interesting)

        b) SPECIFIC tags (AT LEAST 5-25 TAGS):
        - Exact terms, concepts, methodologies
        - Names of people, organizations, brands
        - Product names, technologies, tools
        - Geographic locations
        - Time periods or dates
        - Unique identifiers or keywords from the text

        IMPORTANT:
        - Choose the most relevant and precise tags that reflect the depth and nuances of the text.
        - Do not limit yourself to the examples provided; think broadly and creatively.
        - If the text corresponds to any of the existing tags, be SURE to use it.

        LIST OF EXISTING TAGS:
        {all_tags}

        Please provide your answer STRICTLY in JSON format IN ENGLISH!:
        {{
            "title": "brief title",
            "summary": "informative description",
            "tags": ["tag1", "tag2", "tag3", ...]
        }}
        """,
        ),
    ]
)
