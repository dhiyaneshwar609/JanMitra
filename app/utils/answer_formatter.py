import re


class AnswerFormatter:

    @staticmethod
    def format(answer: str) -> str:

        # Remove Markdown headings (###, ##, #)
        answer = re.sub(r"^#{1,6}\s*", "", answer, flags=re.MULTILINE)

        # Remove bold markdown
        answer = re.sub(r"\*\*(.*?)\*\*", r"\1", answer)

        # Remove excessive blank lines
        answer = re.sub(r"\n{3,}", "\n\n", answer.strip())

        headings = {
            "overview": "📍 Overview",
            "scheme name": "📍 Scheme Name",
            "objective": "📌 Objective",
            "eligibility": "👤 Eligibility",
            "benefits": "🎁 Benefits",
            "required documents": "📄 Required Documents",
            "documents required": "📄 Required Documents",
            "application process": "📝 Application Process",
            "how to apply": "📝 Application Process",
            "important notes": "⚠️ Important Notes",
            "note": "⚠️ Note",
            "official website": "🌐 Official Website",
            "official sources": "🌐 Official Sources",
            "sources": "🌐 Official Sources"
        }

        for key, value in headings.items():

            pattern = rf"^{re.escape(key)}\s*:?\s*$"

            answer = re.sub(
                pattern,
                value,
                answer,
                flags=re.IGNORECASE | re.MULTILINE
            )
            # Convert numbered lists to bullets
            answer = re.sub(
                r"^\d+\.\s+",
                "• ",
                answer,
                flags=re.MULTILINE
            )

        return answer