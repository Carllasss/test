from rapidfuzz import fuzz
import re


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def product_score(product: dict, query: str) -> int:
    text = normalize(
        str(product.get("Название", "")) + " " +
        str(product.get("Группа", ""))
    )
    return fuzz.partial_ratio(normalize(query), text)


def filter_products(
    products: list[dict],
    question: str,
    limit: int = 3,
    threshold: int = 50
) -> list[dict]:
    scored = []

    for p in products:
        score = product_score(p, question)
        if score >= threshold:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [p for _, p in scored[:limit]]


def build_products_context(products: list[dict]) -> str:
    blocks = []

    for p in products:
        blocks.append(
            f"""
Название: {p.get('Название')}
Цена: {p.get('Цена за шт в рублях', 'не указана')}
Группа: {p.get('Группа', '—')}
""".strip()
        )

    return "\n\n".join(blocks)