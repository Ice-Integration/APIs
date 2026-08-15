from strawberry.test import BaseGraphQLTestClient

from app.graphql.schema import schema


class Client(BaseGraphQLTestClient):
    def request(self, body, headers=None, files=None):
        return schema.execute_sync(body["query"])

    def _decode(self, response, type):
        return {"data": response.data, "errors": response.errors}


def test_services_query_exposes_operational_state() -> None:
    result = schema.execute_sync("{ services { name owner tier status } }")
    assert result.errors is None
    assert result.data["services"][0]["name"] == "checkout-api"
