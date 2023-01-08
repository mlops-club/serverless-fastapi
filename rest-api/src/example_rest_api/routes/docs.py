from typing import Any, Dict, List, Union
from pydantic import BaseModel


class ExampleResponse(BaseModel):
    title: str
    body: Dict[str, Union[str, Any]]  # jsonable dict


class DuplicateExampleTitle(Exception):
    """Raised when two examples of the same content type have the same title."""


def make_openapi_example_responses_obj(example_responses: Dict[str, List[ExampleResponse]]) -> dict:
    """
    Return a dictionary used to document the possible responses
    for a single HTTP status code.
    """
    swagger_example_responses_obj = {}
    for content_type, examples in example_responses.items():
        swagger_example_responses_obj = deeply_merge_dicts(
            swagger_example_responses_obj,
            make_apidocs_responses_obj_for_content_type(content_type, examples),
        )
    return swagger_example_responses_obj


def make_apidocs_responses_obj_for_content_type(content_type: str, examples: List[ExampleResponse]):
    """
    Return a dictionary used to document the possible responses
    for a single HTTP status code.
    """
    swagger_example_responses_obj = {
        "content": {
            content_type: {
                "examples": {
                    # "Invalid breakdown": {
                    #     "value": {
                    #         "detail": PARTS_DONT_SUM_TO_WHOLE_WORD_MSG.format(
                    #             submitted_breakdown="при-каз-ывать", word="приказать"
                    #         )
                    #     }
                    # }
                }
            }
        }
    }
    for example_response in examples:
        examples = swagger_example_responses_obj["content"][content_type]["examples"]
        if example_response.title in examples.keys():
            raise DuplicateExampleTitle(
                f"Example response title {example_response.title} appears twice for this endpoint."
            )
        examples[example_response.title] = {
            "value": example_response.body,
        }

    return swagger_example_responses_obj


def deeply_merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Return the dictionary resulting from recursively merging the two input dicts."""
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict and isinstance(merged_dict[key], dict) and isinstance(value, dict):
            merged_dict[key] = deeply_merge_dicts(merged_dict[key], value)
        else:
            merged_dict[key] = value
    return merged_dict
