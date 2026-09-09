import re


class QueryRewriter:

    FOLLOW_UP_WORDS = [
        "this",
        "that",
        "it",
        "scheme",
        "service",
        "program"
    ]

    def rewrite(self, query, entity):

        if not entity:
            return query

        lower = query.lower()

        if any(word in lower for word in self.FOLLOW_UP_WORDS):

            rewritten = re.sub(
                r"\b(this|that|it|scheme|service|program)\b",
                entity,
                query,
                flags=re.IGNORECASE
            )

            return rewritten

        # If user omitted the entity entirely
        if (
            entity.lower() not in lower
            and any(
                word in lower
                for word in [
                    "eligible",
                    "apply",
                    "benefit",
                    "document",
                    "status",
                    "registration"
                ]
            )
        ):
            return f"{query} for {entity}"

        return query