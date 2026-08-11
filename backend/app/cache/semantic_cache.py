from app.config.constants import (
    CACHE_SIMILARITY_THRESHOLD
)

from app.database.database import SessionLocal
from app.database.models import Cache

from app.memory.embedding import create_embedding


class SemanticCache:
    """
    Persistent semantic cache backed by SQLite.
    """

    @staticmethod
    def cosine_similarity(
        vector1,
        vector2
    ):

        dot_product = sum(
            a * b
            for a, b in zip(
                vector1,
                vector2
            )
        )

        magnitude1 = sum(
            a * a
            for a in vector1
        ) ** 0.5

        magnitude2 = sum(
            b * b
            for b in vector2
        ) ** 0.5

        if (
            magnitude1 == 0
            or magnitude2 == 0
        ):
            return 0.0

        return dot_product / (
            magnitude1 * magnitude2
        )

    def add_cache(
        self,
        user_id: int,
        question: str,
        answer: str
    ):

        embedding = create_embedding(
            question
        )

        if not embedding:
            raise ValueError(
                "Could not create an embedding "
                "for the cache entry."
            )

        db = SessionLocal()

        try:

            existing = (
                db.query(Cache)
                .filter(
                    Cache.user_id == user_id,
                    Cache.query == question
                )
                .first()
            )

            if existing:

                existing.answer = answer
                existing.similarity = 1.0

            else:

                db.add(
                    Cache(
                        user_id=user_id,
                        query=question,
                        answer=answer,
                        similarity=1.0
                    )
                )

            db.commit()

            return {
                "success": True,
                "user_id": user_id,
                "query": question
            }

        except Exception:

            db.rollback()
            raise

        finally:

            db.close()

    def search_cache(
        self,
        user_id: int,
        query: str
    ):

        query_embedding = create_embedding(
            query
        )

        if not query_embedding:
            return {
                "found": False,
                "answer": None
            }

        db = SessionLocal()

        try:

            entries = (
                db.query(Cache)
                .filter(
                    Cache.user_id == user_id
                )
                .order_by(
                    Cache.created_at.desc()
                )
                .all()
            )

            best_match = None
            best_similarity = 0.0

            for item in entries:

                item_embedding = create_embedding(
                    item.query
                )

                similarity = (
                    self.cosine_similarity(
                        query_embedding,
                        item_embedding
                    )
                )

                if similarity > best_similarity:

                    best_similarity = similarity
                    best_match = item

            if (
                best_match is not None
                and best_similarity
                >= CACHE_SIMILARITY_THRESHOLD
            ):

                return {
                    "found": True,
                    "answer": best_match.answer,
                    "query": best_match.query,
                    "similarity": best_similarity
                }

            return {
                "found": False,
                "answer": None,
                "similarity": best_similarity
            }
        

        finally:

            db.close()
    # ========================================================
    # Delete Cache Entry
    # ========================================================

    def delete_cache(
        self,
        user_id: int,
        query: str
    ):
        """
        Delete an exact cached question for a user.

        Used to remove stale or incorrect cache entries.
        """

        db = SessionLocal()

        try:

            deleted = (
                db.query(Cache)
                .filter(
                    Cache.user_id == user_id,
                    Cache.query == query
                )
                .delete(
                    synchronize_session=False
                )
            )

            db.commit()

            return {
                "success": True,
                "user_id": user_id,
                "query": query,
                "deleted": deleted
            }

        except Exception:

            db.rollback()
            raise

        finally:

            db.close()        


semantic_cache = SemanticCache()