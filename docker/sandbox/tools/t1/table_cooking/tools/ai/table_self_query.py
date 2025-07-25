import ast
import csv
import inspect
import io
import json
import re
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Any
from typing import Dict, List, Union, Tuple
from typing import Optional, Hashable

import chardet
import matplotlib
import numpy as np
import pandas as pd
import pingouin
import scipy.stats
import statsmodels
import statsmodels.api as sm
from dify_plugin.core.runtime import Session
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage, PromptMessage
from loguru import logger
from pydantic import BaseModel, Field, field_validator

AI_DIR = Path(__file__).parent


PREVIEW_CODE_WRAPPER = """
<segment>
<question>{question}</question>
<question_type>{question_type}</question_type>
<code>
{query_code}
</code>
<output filename="{recommend_filename}">
{result_markdown}
</output>
</segment>
"""

INSTRUCTIONS_CLASSIFIER = """
<task>
You are a question classifier, determining whether a user query is a <basic data query> task. Output "YES" if it is.
</task>
<COT>
Judgment: 1. Does the query explicitly request a query? 2. Does the query request a listing of data?
For example, <not belonging> case: The table is an exam grade sheet, and the query requires calculating the median score of students in a certain region (i.e., data not explicitly given in the grade sheet).
For example, <belonging> case: The table is an exam grade sheet, and the query is to query the scores of a subject or the scores of students in a certain region.
</COT>
<schemas>
Below are the headers, sample data, shape, and description information of the knowledge base tables.
{schemas}
</schemas>
<limitations>
You can only output "YES" or "NO" and cannot output any other information.
</limitations>
"""

PROMPT_GEN_RECOMMEND_NAME = """
<natural_query>
{natural_query}
</natural_query>
<code>
```python
{code}
```
</code>
"""

INSTRUCTIONS_POST_FIXER = """
You are a Python code debugger specializing in Pandas DataFrames. You will be provided with a user's natural language query, the schema of a Pandas DataFrame (including column names, data types, shape, and sample data), a Python code snippet that resulted in an error when operating on the DataFrame, and the error message. Your task is to generate a corrected Python code snippet that addresses the error and accurately reflects the user's intent.

**Constraints:**

*   **Output ONLY the complete, corrected Python code snippet.** Do not include any explanations, comments, or surrounding text.
*   **Focus on fixing the error identified in the error message.** Make only the necessary changes to resolve the error and ensure the code is syntactically and semantically correct.
*   **Preserve the original intent of the code as much as possible.** Avoid introducing new functionality or significantly altering the code's logic unless absolutely necessary to resolve the error.
*   **Adhere to the provided DataFrame schema.** Ensure that all column names, data types, and DataFrame operations used in the corrected code are consistent with the provided schema (columns, dtypes_dict, shape, and sample_data).

**Input:**

*   `Natural Language Query`: The user's original query expressed in natural language.
*   `DataFrame Schema`: The schema of the Pandas DataFrame, including:
    *   `columns`: A list of column names.
    *   `dtypes_dict`: A dictionary mapping column names to their data types.
    *   `shape`: The dimensions (rows, columns) of the DataFrame.
    *   `sample_data`: A small sample of data from the DataFrame.
*   `Erroneous Python Code`: The Python code snippet that resulted in an error when operating on the DataFrame.
*   `Error Message`: The error message generated when executing the erroneous Python code.

**Output:**

*   The complete, corrected Python code snippet.
"""

PROMPT_POST_FIXER = """
Regenerate the correct and runnable Python code based on the following information:

**Natural Language Query:**
{natural_query}

**DataFrame Schema:**
{schemas}

**Erroneous Python Code:**
{error_python_code}

**Error Message:**
{error_message}
"""


class AgentStrategyType(str, Enum):
    TABLE_FILTER = "table_filter"
    TABLE_INTERPRETER = "table_interpreter"
    NAMING_MASTER = "naming_master"
    FDQ = "fdq"
    CLASSIFY = "classify"
    ANSWER = "answer"


class QueryStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class MetaData(BaseModel):
    row_count: int = Field(description="Number of results rows")
    columns: List[str] = Field(description="List of column names")
    dtypes: Dict[Hashable, str] = Field(description="Column data type")

    class Config:
        json_encoders = {np.dtype: str}


class QueryResult(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now, description="Query timestamp")
    query: str = Field(description="Original query")
    query_type: Optional[str] = Field(default="", description="Query Type")
    query_code: Optional[str] = Field(
        default="", description="The generated code for manipulating the table"
    )
    recommend_filename: Optional[str] = Field(default="", description="Recommended file name")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Query result data")
    metadata: MetaData = Field(description="Result metadata")
    error: Optional[str] = Field(default=None, description="Error message")

    class Config:
        json_encoders = {
            np.integer: lambda x: int(x),
            np.floating: float,
            np.ndarray: lambda x: x.tolist(),
            pd.Timestamp: lambda x: x.isoformat(),
            datetime: lambda x: x.isoformat(),
        }

    @field_validator("data", mode="before")
    def convert_nan_to_none(cls, v):
        """Convert NaN value to None"""
        if isinstance(v, list):
            return [{k: None if pd.isna(v) else v for k, v in item.items()} for item in v]
        return v

    def get_recommend_filename(self, suffix: Optional[str] = None):
        """Generate file name suggestions based on query results"""
        name = self.recommend_filename or "output.xlsx"
        if isinstance(suffix, str) and suffix.startswith("."):
            name = f"{Path(name).stem}{suffix}"
        return name.strip()

    def to_llm_ready(self, *, storage_dir: Optional[Path] = None) -> str:
        wrapper_ = PREVIEW_CODE_WRAPPER.format(
            question=self.query,
            question_type=self.query_type,
            query_code=self.query_code,
            recommend_filename=self.get_recommend_filename(suffix=".md"),
            result_markdown=pd.DataFrame.from_records(self.data).to_markdown(index=False),
        ).strip()
        logger.success(f"transformed to LLM ready \n{wrapper_}")

        if isinstance(storage_dir, Path):
            storage_path = storage_dir / self.get_recommend_filename(suffix=".xml")
            storage_path.parent.mkdir(exist_ok=True, parents=True)
            storage_path.write_text(wrapper_, encoding="utf8")

        return wrapper_


class QueryOutputParser:

    @staticmethod
    def parse(
        df_result: Optional[pd.DataFrame],
        query: str,
        *,
        query_type: Optional[str] = "",
        query_code: Optional[str] = "",
        recommend_filename: Optional[str] = "",
        error: Optional[str] = "",
    ) -> QueryResult:
        """
        Convert DataFrame results to a standardized Pydantic model

        Args:
            query_code:
            df_result: Query the returned DataFrame
            query: Original query statement
            error: Error message (if any)
            recommend_filename: Recommended file names
            query_type:

        Returns:
            QueryResult: Standardized query result model
        """
        try:
            if isinstance(df_result, (pd.DataFrame, pd.Series)) and not df_result.empty:
                # 将DataFrame转换为字典列表
                data = df_result.to_dict("records")
                metadata = MetaData(
                    row_count=len(data),
                    columns=list(df_result.columns),
                    dtypes={col: str(dtype) for col, dtype in df_result.dtypes.items()},
                )
            elif df_result is not None:
                data = [{"output": f"{df_result}"}]
                metadata = MetaData(row_count=0, columns=[], dtypes={})
            else:
                data = []
                metadata = MetaData(row_count=0, columns=[], dtypes={})

            # 创建查询结果模型
            result = QueryResult(
                query=query,
                query_type=query_type,
                query_code=query_code,
                recommend_filename=recommend_filename,
                data=data,
                metadata=metadata,
                error=error,
            )

            return result

        except Exception as err:
            # 如果解析过程出错，返回错误结果
            error_result = QueryResult(
                query=query,
                query_type=query_type,
                query_code=query_code,
                recommend_filename=recommend_filename,
                data=[],
                metadata=MetaData(row_count=0, columns=[], dtypes={}),
                error=f"结果解析错误: {str(err)}",
            )
            return error_result


def get_prompt_template(site: AgentStrategyType):
    path_system_prompt_table_filter = "templates/system_prompt_table_filter.xml"
    path_system_prompt_naming_master = "templates/system_prompt_naming_master.xml"
    path_system_prompt_fdq = "templates/system_prompt_fdq.xml"
    path_system_prompt_question_classifier = "templates/system_prompt_question_classifier.xml"
    path_system_prompt_table_interpreter = "templates/system_prompt_table_interpreter.xml"
    path_system_prompt_answer = "templates/system_prompt_answer.xml"

    site2path = {
        "table_filter": path_system_prompt_table_filter,
        "naming_master": path_system_prompt_naming_master,
        "fdq": path_system_prompt_fdq,
        "classify": path_system_prompt_question_classifier,
        "table_interpreter": path_system_prompt_table_interpreter,
        "answer": path_system_prompt_answer,
    }

    if site_path := site2path.get(site):
        return AI_DIR.joinpath(site_path).read_text(encoding="utf8")

    return ""


def summarize_excel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a comprehensive summary of any DataFrame.

    Args:
        df: Input DataFrame to be summarized

    Returns:
        DataFrame containing summary information
    """
    # Initialize results dictionary
    results: Dict[str, List[Any]] = {"Summary Type": [], "Information": [], "Details": []}

    # Basic information
    results["Summary Type"].append("基本信息")
    results["Information"].append(f"表格大小")
    results["Details"].append(f"{df.shape[0]}行 × {df.shape[1]}列")

    # Column types summary
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

    results["Summary Type"].append("列类型分布")
    results["Information"].append("列类型统计")
    results["Details"].append(
        f"数值型: {len(numeric_cols)}列, 类别型: {len(categorical_cols)}列, 日期型: {len(datetime_cols)}列"
    )

    # Missing values
    missing_data = df.isnull().sum()
    cols_with_missing = missing_data[missing_data > 0]

    if len(cols_with_missing) > 0:
        results["Summary Type"].append("数据完整性")
        results["Information"].append("缺失值情况")
        missing_summary = ", ".join(
            [
                f"{col}: {count}个 ({count / len(df):.1%})"
                for col, count in cols_with_missing.items()
            ]
        )
        results["Details"].append(missing_summary if missing_summary else "无缺失值")
    else:
        results["Summary Type"].append("数据完整性")
        results["Information"].append("缺失值情况")
        results["Details"].append("所有列均无缺失值")

    # Numeric columns statistics
    if numeric_cols:
        # Overall statistics
        results["Summary Type"].append("数值统计")
        results["Information"].append("数值型列概览")
        results["Details"].append(
            f"共{len(numeric_cols)}列: {', '.join(numeric_cols[:5])}"
            + (f"等{len(numeric_cols)}列" if len(numeric_cols) > 5 else "")
        )

        # Get statistics for each numeric column (up to 5)
        for col in numeric_cols[:5]:
            results["Summary Type"].append("数值统计")
            results["Information"].append(f"'{col}'列统计")
            stats = df[col].describe()
            results["Details"].append(
                f"均值: {stats['mean']:.2f}, 中位数: {stats['50%']:.2f}, "
                + f"最小值: {stats['min']:.2f}, 最大值: {stats['max']:.2f}"
            )

    # Categorical columns statistics
    if categorical_cols:
        results["Summary Type"].append("类别统计")
        results["Information"].append("类别型列概览")
        results["Details"].append(
            f"共{len(categorical_cols)}列: {', '.join(categorical_cols[:5])}"
            + (f"等{len(categorical_cols)}列" if len(categorical_cols) > 5 else "")
        )

        # Get top categories for each categorical column (up to 5)
        for col in categorical_cols[:5]:
            value_counts = df[col].value_counts()
            if len(value_counts) <= 5:
                # If 5 or fewer categories, show all
                cat_summary = ", ".join(
                    [
                        f"{cat}: {count}个 ({count / len(df):.1%})"
                        for cat, count in value_counts.items()
                    ]
                )
            else:
                # Otherwise show top 3
                top_cats = value_counts.head(3)
                cat_summary = ", ".join(
                    [f"{cat}: {count}个 ({count / len(df):.1%})" for cat, count in top_cats.items()]
                )
                cat_summary += f" 等{len(value_counts)}个不同值"

            results["Summary Type"].append("类别统计")
            results["Information"].append(f"'{col}'列分布")
            results["Details"].append(cat_summary)

    # Date columns if any
    if datetime_cols:
        for col in datetime_cols[:3]:
            results["Summary Type"].append("时间统计")
            results["Information"].append(f"'{col}'列时间范围")
            results["Details"].append(
                f"从 {df[col].min()} 到 {df[col].max()}, 跨度 {(df[col].max() - df[col].min()).days} 天"
            )

    # Correlation between numeric columns
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        # Get top 3 highest correlations (excluding self-correlations)
        corrs = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                corrs.append((numeric_cols[i], numeric_cols[j], corr_matrix.iloc[i, j]))

        corrs.sort(key=lambda x: abs(x[2]), reverse=True)

        if corrs:
            results["Summary Type"].append("相关性分析")
            results["Information"].append("主要相关性")
            corr_text = ""
            for col1, col2, corr_val in corrs[:3]:
                corr_text += f"'{col1}' 与 '{col2}': {corr_val:.2f}, "
            results["Details"].append(corr_text[:-2])  # Remove trailing comma and space

    # Create summary DataFrame
    summary_df = pd.DataFrame(results)

    return summary_df


def get_function_source(func: Callable[..., Any]) -> str:
    """
    Returns the complete source code of a function as a string.

    Args:
        func: The function object to extract source code from

    Returns:
        A string containing the complete function definition including signature and body

    Raises:
        TypeError: If the input is not a function
        ValueError: If the source code cannot be retrieved
    """
    if not callable(func):
        raise TypeError("Input must be a callable function")

    try:
        # Get the source code of the function
        source_code = inspect.getsource(func)
        return source_code
    except (TypeError, OSError) as e:
        raise ValueError(f"Could not retrieve source code for function '{func.__name__}': {str(e)}")


class TableLoader:
    def __init__(self):
        self.df = None
        self.schema_info = {}
        self.sample_data = []

    @staticmethod
    def _detect_file_encoding(file_path: Path) -> str:
        """Detect file encoding"""
        with open(file_path, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result["encoding"]

    @staticmethod
    def _find_valid_table_range(df: pd.DataFrame) -> Tuple[int, int]:
        """Find the start and end row index of a valid table"""

        # Count the number of non-null values per row
        row_counts = df.notna().sum(axis=1)
        max_count = row_counts.max()

        # Find the row range with stable number of data columns
        # 20% tolerance allowed
        valid_rows = row_counts[row_counts >= max_count * 0.8]
        start_idx = valid_rows.index[0]
        end_idx = valid_rows.index[-1]

        return start_idx, end_idx

    def _process_csv(self, file_stream: Union[Path, io.BytesIO]) -> pd.DataFrame:
        """Processing CSV files"""
        # 处理不同类型的输入
        if isinstance(file_stream, Path):
            # 如果是文件路径，使用原来的方法
            encoding = self._detect_file_encoding(file_stream)
            with open(file_stream, "r", encoding=encoding) as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
        elif isinstance(file_stream, io.BytesIO):
            # 如果是BytesIO对象，直接读取
            content = file_stream.getvalue().decode("utf-8")
            file_stream.seek(0)  # 重置文件指针位置
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
        else:
            raise ValueError("不支持的文件输入类型")

        # 转换为DataFrame进行处理
        raw_df = pd.DataFrame(rows)
        start_idx, end_idx = self._find_valid_table_range(raw_df)

        # 提取有效数据范围
        valid_df = raw_df.iloc[start_idx : end_idx + 1].reset_index(drop=True)
        return valid_df

    def format_stock_codes(self, keywords: List[str] = None) -> None:
        """
        Scan the column name of the DataFrame and format the columns containing keywords and of type int:
        1. Convert to str type
        2. Complement zero to 6 digits for non-null values

        Args:
            keywords:

        Returns:

        """
        if keywords is None:
            keywords = ["证券代码", "code_id", "symbol"]

        # 获取所有列名
        columns = self.df.columns.tolist()

        # 遍历列名
        for col in columns:
            # 检查列名是否包含关键词
            if any(keyword.lower() in col.lower() for keyword in keywords):
                # 检查数据类型是否为int
                if pd.api.types.is_integer_dtype(self.df[col]):
                    # 转换为字符串类型
                    self.df[col] = self.df[col].astype(str)

                    # 对非空值补零到6位
                    self.df[col] = self.df[col].apply(lambda x: x.zfill(6) if pd.notna(x) else x)

                    logger.debug(f"列 '{col}' 已格式化为6位证券代码")

        return None

    @staticmethod
    def _detect_header_row(df: pd.DataFrame) -> Union[int, None]:
        """
        Automatically detect the row where the table header is located. Returns the row index (starting from 0), and None if not detected.

        Improved detection rules:
        1. Basic conditions: The number of non-null values in the row is sufficient (>50%), and the value is basically unique
        2. Data type characteristics: The header is usually a string type
        3. Length characteristics: The length of the header string is usually moderate, not too long or too short
        4. Numerical ratio: The header row usually does not contain a large number of numerical values
        5. Repeat value: The table header row should have fewer duplicate values
        """
        max_check_rows = min(15, len(df))
        best_score = -1
        best_row = None

        for idx in range(max_check_rows):
            row = df.iloc[idx]
            score = 0

            # 1. 检查非空值比例和唯一值
            num_non_na = row.notna().sum()
            num_unique = row.nunique()
            non_na_ratio = num_non_na / len(df.columns)

            if non_na_ratio < 0.5:  # 非空值比例过低
                continue

            # 基础分数：非空值比例 * 唯一值比例
            score += non_na_ratio * (num_unique / num_non_na)

            # 2. 检查数据类型
            str_count = sum(1 for x in row if isinstance(x, str))
            str_ratio = str_count / num_non_na
            score += str_ratio * 2  # 字符串比例权重加倍

            # 3. 检查字符串长度
            if str_count > 0:
                str_lengths = [len(str(x)) for x in row if isinstance(x, str)]
                avg_len = sum(str_lengths) / len(str_lengths)
                # 理想的表头长度在2-20之间
                if 2 <= avg_len <= 20:
                    score += 1
                elif avg_len > 50:  # 可能是数据行
                    score -= 1

            # 4. 检查数值比例
            num_count = sum(
                1 for x in row if isinstance(x, (int, float)) and not isinstance(x, bool)
            )
            num_ratio = num_count / num_non_na
            if num_ratio > 0.5:  # 数值比例过高
                score -= 1

            # 5. 检查重复值
            duplicate_ratio = 1 - (num_unique / num_non_na)
            if duplicate_ratio > 0.2:  # 重复值比例过高
                score -= 1

            # 6. 检查特殊标记（可选）
            special_keywords = {
                "序号",
                "编号",
                "名称",
                "代码",
                "日期",
                "id",
                "name",
                "code",
                "date",
            }
            keyword_matches = sum(
                1
                for x in row
                if isinstance(x, str) and any(k in str(x).lower() for k in special_keywords)
            )
            if keyword_matches > 0:
                score += 0.5

            # 更新最佳分数
            if score > best_score:
                best_score = score
                best_row = idx

        # 要求最小分数阈值
        return best_row if best_score >= 1.5 else None

    def _extract_schema_and_samples(self) -> None:
        """Extract table schema information and sample data"""

        def _convert_for_json(obj):
            """Convert an object to make it JSON serializable"""
            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Series):
                return obj.tolist()
            return str(obj)

        # 获取schema信息
        self.schema_info = {
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "shape": self.df.shape,
        }

        # 获取随机样例(最多b行)
        sample_size = min(5, len(self.df))
        samples = self.df.sample(n=sample_size).to_dict("records")
        self.sample_data = [
            {k: _convert_for_json(v) for k, v in record.items()} for record in samples
        ]

    def load_table(self, file_stream: io.BytesIO, extension: str) -> None:
        """Load the table file, process the head and tail comments, and automatically detect the head rows of the table"""
        if extension.lower() == ".csv":
            valid_df = self._process_csv(file_stream)
        elif extension.lower() in [".xlsx", ".xls"]:
            valid_df = pd.read_excel(file_stream, header=None)
        else:
            raise ValueError("Unsupported file formats. Please use table file")

        # 检测表头行
        header_row = self._detect_header_row(valid_df)
        if header_row is not None:
            self.df = valid_df.iloc[header_row:].reset_index(drop=True)
            self.df.columns = valid_df.iloc[header_row]
        else:
            # 默认使用第一行作为表头
            self.df = valid_df.iloc[1:].reset_index(drop=True)
            self.df.columns = valid_df.iloc[0]

        self.format_stock_codes()
        self._extract_schema_and_samples()


class TableQueryEngine:
    def __init__(self, session: Session, dify_model_config: LLMModelConfig):
        self.session = session
        self.dify_model_config = dify_model_config

        self.df = None
        self.schema_info = {}
        self.sample_data = []

    def load_table(self, file_stream: io.BytesIO, extension: str) -> None:
        tl = TableLoader()
        tl.load_table(file_stream, extension)

        self.df = tl.df
        self.schema_info = tl.schema_info
        self.sample_data = tl.sample_data

    def query(
        self, natural_query: str, enable_classifier: bool = True, retry_times: int = 5
    ) -> QueryResult | None:
        if self.df is None:
            return QueryOutputParser.parse(None, natural_query, error="Tabular data not loaded")

        try:

            # ====================
            # Task Classifier
            # ====================
            runtime_agent_strategy = AgentStrategyType.TABLE_FILTER
            if enable_classifier:
                is_search = self._classify(natural_query)
                runtime_agent_strategy = (
                    AgentStrategyType.TABLE_FILTER
                    if "YES" in is_search
                    else AgentStrategyType.TABLE_INTERPRETER
                )

            # ====================
            # Task Execution
            # ====================
            # Generate code
            query_code = self._gen_query_code(
                natural_query=natural_query,
                agent_strategy=(
                    AgentStrategyType.TABLE_FILTER
                    if runtime_agent_strategy == "DataQuery"
                    else AgentStrategyType.TABLE_INTERPRETER
                ),
            )
            print(f"**Strategy:**\n{runtime_agent_strategy}\n")
            print(f"**Query:**\n{natural_query}\n")
            print(f"**Code:**\n{query_code}\n")

            # The user problem description causes the code to fail
            if not query_code:
                df_result = summarize_excel(self.df)
                return QueryOutputParser.parse(
                    df_result,
                    natural_query,
                    query_type=runtime_agent_strategy.value,
                    query_code=get_function_source(summarize_excel),
                    recommend_filename="summary_tabular.md",
                )

            # == Execute code == #
            df_result = None
            tracking_messages = []
            for _ in range(retry_times):
                df_result = self._execute_query_code(query_code)

                # What is returned is not an error message
                if not isinstance(df_result, str):
                    break

                logger.warning("trying to restore order...")
                query_code = self._invoke_post_fixer(
                    natural_query=natural_query,
                    error_python_code=query_code,
                    error_message=df_result,
                    tracking_messages=tracking_messages,
                )

            # ========================================
            # Generate recommended file names
            # ========================================
            recommend_filename = self._gen_recommend_name(natural_query, query_code)

            # ========================================
            # Parses and returns the result
            # ========================================
            result = QueryOutputParser.parse(
                df_result,
                natural_query,
                query_type=runtime_agent_strategy.value,
                query_code=query_code,
                recommend_filename=recommend_filename,
            )
            return result

        except Exception as err:
            return QueryOutputParser.parse(pd.DataFrame(), natural_query, error=str(err))

    def _invoke_dify_llm(
        self,
        user_content: str,
        system_prompt: str = None,
        temperature: float = 0,
        max_tokens: int = 4096,
    ) -> str:
        model_config = self.dify_model_config.model_dump().copy()
        model_config["completion_params"] = {"max_tokens": max_tokens, "temperature": temperature}
        llm_result = self.session.model.llm.invoke(
            model_config=model_config,
            prompt_messages=[
                SystemPromptMessage(content=system_prompt),
                UserPromptMessage(content=user_content),
            ],
            stream=False,
        )

        return llm_result.message.content

    def _classify(self, natural_query: str) -> str:
        schemas = {
            "columns": self.schema_info["columns"],
            "dtypes_dict": self.schema_info["dtypes"],
            "shape": self.schema_info["shape"],
            "sample_data": json.dumps(self.sample_data[0], indent=2, ensure_ascii=False),
        }
        system_prompt = INSTRUCTIONS_CLASSIFIER.format(schemas=schemas).strip()
        response = self.session.model.llm.invoke(
            model_config=LLMModelConfig(
                provider=self.dify_model_config.provider,
                model=self.dify_model_config.model,
                mode=self.dify_model_config.mode,
                completion_params={"max_tokens": 200, "temperature": 0},
            ),
            prompt_messages=[
                SystemPromptMessage(content=system_prompt),
                UserPromptMessage(content=natural_query),
            ],
            stream=False,
        )
        return response.message.content

    def _gen_query_code(self, natural_query: str, agent_strategy: AgentStrategyType) -> str:
        system_prompt = get_prompt_template(agent_strategy).format(
            columns_list=self.schema_info["columns"],
            dtypes_dict=self.schema_info["dtypes"],
            shape_tuple=self.schema_info["shape"],
            sample_data=json.dumps(self.sample_data, indent=2, ensure_ascii=False),
        )
        user_content = f"<query>{natural_query}<query>"

        try:
            response = self.session.model.llm.invoke(
                model_config=LLMModelConfig(
                    provider=self.dify_model_config.provider,
                    model=self.dify_model_config.model,
                    mode=self.dify_model_config.mode,
                    completion_params={"max_tokens": 4096, "temperature": 0},
                ),
                prompt_messages=[
                    SystemPromptMessage(content=system_prompt),
                    UserPromptMessage(content=user_content),
                ],
                stream=False,
            )
            answer = response.message.content
            if "```python" in answer:
                code = answer.split("```python")[1].split("```")[0].strip()
                return code
            if "def execute_query" in answer:
                return answer
        except Exception as err:
            logger.error(f"Error when invoke drawer: {err}")

        return ""

    def _invoke_post_fixer(
        self,
        natural_query: str,
        error_python_code: str,
        error_message: str,
        tracking_messages: List[PromptMessage] | None = None,
    ) -> str | None:
        schemas = {
            "columns": self.schema_info["columns"],
            "dtypes_dict": self.schema_info["dtypes"],
            "shape": self.schema_info["shape"],
            "sample_data": json.dumps(self.sample_data[0], indent=2, ensure_ascii=False),
        }
        system_prompt = INSTRUCTIONS_POST_FIXER.strip()
        user_prompt = PROMPT_POST_FIXER.format(
            natural_query=natural_query,
            schemas=schemas,
            error_python_code=error_python_code,
            error_message=error_message,
        )

        if not tracking_messages:
            tracking_messages = [
                SystemPromptMessage(content=system_prompt),
                UserPromptMessage(content=user_prompt),
            ]
        else:
            tracking_messages.append(UserPromptMessage(content=user_prompt))

        try:
            response = self.session.model.llm.invoke(
                model_config=LLMModelConfig(
                    provider=self.dify_model_config.provider,
                    model=self.dify_model_config.model,
                    mode=self.dify_model_config.mode,
                    completion_params={"max_tokens": 4096, "temperature": 0},
                ),
                prompt_messages=tracking_messages,
                stream=False,
            )
            answer = response.message.content
            tracking_messages.append(response.message)
            if "```python" in answer:
                pattern = r"```python\s*(.*?)\s*```"
                match = re.search(pattern, answer, re.DOTALL)
                if match:
                    debugger_code = match.group(1).strip()
                    return debugger_code
            elif "def execute_query" in answer:
                return answer
        except Exception as err:
            logger.error(f"Error when invoke fixer: {err}")

    def _gen_recommend_name(self, natural_query: str, code: str) -> str:
        system_prompt = get_prompt_template(AgentStrategyType.NAMING_MASTER)
        user_content = PROMPT_GEN_RECOMMEND_NAME.format(
            natural_query=natural_query, code=code
        ).strip()

        response = self.session.model.llm.invoke(
            model_config=LLMModelConfig(
                provider=self.dify_model_config.provider,
                model=self.dify_model_config.model,
                mode=self.dify_model_config.mode,
                completion_params={"max_tokens": 200, "temperature": 0.3},
            ),
            prompt_messages=[
                SystemPromptMessage(content=system_prompt),
                UserPromptMessage(content=user_content),
            ],
            stream=False,
        )
        return response.message.content

    def _execute_query_code(self, code: str) -> Any:
        """
        Safely execute dynamically generated code

        Args:
            code: Python code to execute

        Returns:
        """
        try:
            # Parse the code to ensure the syntax is correct
            ast.parse(code)

            # Create an isolated namespace
            namespace = {
                # Basic library
                "pd": pd,
                "np": np,
                "df": self.df,
                # Statistical related
                "sm": sm,
                "statsmodels": statsmodels,
                "scipy": scipy,
                "stats": scipy.stats,
                "pingouin": pingouin,
                # DrawIO
                "matplotlib": matplotlib,
            }

            # Execute function definitions using exec
            exec(code, namespace)

            # Call the generated function
            if "execute_query" not in namespace:
                return pd.DataFrame()

            return namespace["execute_query"](self.df)

        except Exception as e:
            logger.error(f"Code execution failed - error_context={str(e)}")
            return str(traceback.format_exc())
