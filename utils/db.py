"""
============================================================
  utils/db.py
  MongoDB client — CRUD operations for analysis records.
  Collection: sentiment_db.analyses
============================================================
"""

from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict
import os


class MongoDBClient:
    """
    Handles all MongoDB interactions for the Sentiment Analyzer.

    Environment Variables (optional overrides):
        MONGO_URI  — default: mongodb://localhost:27017/
        MONGO_DB   — default: sentiment_db
    """

    def __init__(self):
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
        db_name   = os.environ.get("MONGO_DB",  "sentiment_db")

        try:
            self.client     = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            self.client.admin.command("ping")          # verify connection
            self.db         = self.client[db_name]
            self.collection = self.db["analyses"]

            # Indexes for efficient querying
            self.collection.create_index([("timestamp", DESCENDING)])
            self.collection.create_index("label")

            print(f"  → MongoDB connected: {mongo_uri} | DB: {db_name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"  [!] MongoDB unavailable ({e}). Using in-memory fallback.")
            self.collection = None
            self._memory_store = []    # Fallback list-based store

    # ── Write ────────────────────────────────────────────────────────────────

    def insert_analysis(self, record: dict):
        """
        Insert a new analysis record.

        Args:
            record (dict): { text, label, confidence, all_scores, timestamp, source }

        Returns:
            str | int: Inserted document _id (ObjectId str or fallback int index)
        """
        if self.collection is not None:
            result = self.collection.insert_one(record)
            return result.inserted_id
        else:
            # In-memory fallback
            record["_id"] = len(self._memory_store)
            self._memory_store.append(record)
            return record["_id"]

    # ── Read ─────────────────────────────────────────────────────────────────

    def get_all_analyses(self, limit: int = 50) -> list:
        """
        Fetch the most recent `limit` analysis records, newest first.

        Returns:
            list[dict]: Serializable list of records.
        """
        if self.collection is not None:
            cursor = self.collection.find().sort("timestamp", DESCENDING).limit(limit)
            records = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])   # ObjectId → str for JSON
                records.append(doc)
            return records
        else:
            # In-memory fallback
            return list(reversed(self._memory_store[-limit:]))

    def get_summary_stats(self) -> dict:
        """
        Compute aggregate statistics for the History page.

        Returns:
            dict: {
                total (int),
                label_counts { POSITIVE, NEGATIVE, NEUTRAL },
                avg_confidence (float),
                daily_counts  [{ date, count }, ...]   — last 7 days
            }
        """
        if self.collection is not None:
            total = self.collection.count_documents({})

            # Label distribution
            pipeline_labels = [
                {"$group": {"_id": "$label", "count": {"$sum": 1}}}
            ]
            label_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            for doc in self.collection.aggregate(pipeline_labels):
                label_counts[doc["_id"]] = doc["count"]

            # Average confidence
            pipeline_conf = [
                {"$group": {"_id": None, "avg": {"$avg": "$confidence"}}}
            ]
            avg_conf_result = list(self.collection.aggregate(pipeline_conf))
            avg_confidence  = round(avg_conf_result[0]["avg"] * 100, 1) if avg_conf_result else 0

            # Daily counts — last 7 days
            seven_days_ago = (datetime.utcnow() - timedelta(days=6)).strftime("%Y-%m-%d")
            pipeline_daily = [
                {"$project": {"date": {"$substr": ["$timestamp", 0, 10]}}},
                {"$group": {"_id": "$date", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}},
            ]
            daily_raw    = list(self.collection.aggregate(pipeline_daily))
            daily_counts = [{"date": d["_id"], "count": d["count"]} for d in daily_raw]

        else:
            # In-memory fallback
            records = self._memory_store
            total   = len(records)
            label_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            for r in records:
                label_counts[r.get("label", "NEUTRAL")] += 1
            avg_confidence = (
                round(sum(r.get("confidence", 0) for r in records) / total * 100, 1)
                if total else 0
            )
            # Group by date
            day_map = defaultdict(int)
            for r in records:
                day_map[r.get("timestamp", "")[:10]] += 1
            daily_counts = [{"date": k, "count": v} for k, v in sorted(day_map.items())]

        return {
            "total":          total,
            "label_counts":   label_counts,
            "avg_confidence": avg_confidence,
            "daily_counts":   daily_counts,
        }

    # ── Delete ───────────────────────────────────────────────────────────────

    def delete_analysis(self, doc_id: str) -> bool:
        """
        Delete a single analysis record by its _id.

        Returns:
            bool: True if deleted, False if not found.
        """
        if self.collection is not None:
            try:
                result = self.collection.delete_one({"_id": ObjectId(doc_id)})
                return result.deleted_count == 1
            except Exception:
                return False
        else:
            before = len(self._memory_store)
            self._memory_store = [r for r in self._memory_store if str(r.get("_id")) != str(doc_id)]
            return len(self._memory_store) < before
