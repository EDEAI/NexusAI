from typing import Annotated, Any, Generator

from dify_easy.model import (
    BasePlugin,
    FormType,
    MetaInfo,
    Param,
    ParamType,
    provider,
    tool,
)
from pydantic import BaseModel
from transformers import AutoTokenizer


class TokenizerCredential(BaseModel):
    """
    Credential for the Tokenizer plugin.
    This is a placeholder as the tokenizer does not require any specific credentials.
    """

    pass


class TokenizerPlugin(BasePlugin):

    credentials: BaseModel = TokenizerCredential()

    @provider
    def verify(self) -> None:
        """
        Verify the plugin.
        """
        pass

    """
    class Param(
        *,
        name: str = short_name_field(),
        label: str = str(name),
        description: str = "",
        llm_description: str = description,
        type: ParamType = ParamType.string,
        required: bool = True,
        form: FormType = FormType.llm
    )"""

    @tool(
        name="tokenize",
        label="Tokenize Text",
        description="Tokenizes the input text using the specified tokenizer.",
    )
    def tokenize(
        self,
        text: Annotated[
            str,
            Param(
                name="text",
                label="Text",
                description="The text to tokenize",
                required=True,
                type=ParamType.string,
            ),
        ],
        tokenizer: Annotated[
            str,
            Param(
                name="tokenizer",
                label="Tokenizer",
                description="The tokenizer to use for tokenization. For example, 'gpt2', etc. Default is 'gpt2'.",
                required=True,
                type=ParamType.string,
                form=FormType.schema,
            ),
        ] = "gpt2",
    ) -> Generator[Any, None, None]:
        """
        Tokenize the input text using the specified tokenizer.

        Args:
            text (str): The text to tokenize.
            tokenizer (str): The tokenizer to use.

        Yields:
            str: The tokens generated from the input text.
        """
        # Load the tokenizer
        tokenizer_instance = AutoTokenizer.from_pretrained(tokenizer)
        tokens = tokenizer_instance(text)

        yield {
            "token_count": len(tokens["input_ids"]),
        }
        yield str(len(tokens["input_ids"]))


plugin = TokenizerPlugin(
    meta=MetaInfo(
        name="tokenizer",
        author="jingfelix",
        version="0.0.1",
        label="Tokenizer",
        description="Tokenizing text using various tokenizers. Returns the tokens and token count.",
        icon="icon.svg",
    )
)
