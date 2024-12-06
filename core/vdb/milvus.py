from typing import Callable, List, Optional

from langchain_milvus.vectorstores.milvus import (
    Milvus as OriginalMilvus,
    logger
)


class Milvus(OriginalMilvus):
    def _select_relevance_score_fn(self) -> Callable[[float], float]:
        return lambda x: x
    
    def delete(  # type: ignore[no-untyped-def]
        self, ids: Optional[List[str]] = None, expr: Optional[str] = None, **kwargs: str
    ):
        """Delete by vector ID or boolean expression.
        Refer to [Milvus documentation](https://milvus.io/docs/delete_data.md)
        for notes and examples of expressions.

        Args:
            ids: List of ids to delete.
            expr: Boolean expression that specifies the entities to delete.
            kwargs: Other parameters in Milvus delete api.
        """
        if isinstance(ids, list):
            if expr is not None:
                logger.warning(
                    "Both ids and expr are provided. " "Ignore expr and delete by ids."
                )
            expr = f"{self._primary_field} in {[int(id_) for id_ in ids]}"
        else:
            assert isinstance(
                expr, str
            ), "Either ids list or expr string must be provided."
        if self.col is not None:
            self.col.delete(expr=expr, **kwargs)  # type: ignore[union-attr]
        return True
    
    def delete_dataset(self) -> bool:
        if self.col is not None:
            self.col.drop()
            self.col = None
        return True
    