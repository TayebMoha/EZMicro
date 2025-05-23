# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictStr  # noqa: F401


def test_read_page1(client: TestClient):
    """Test case for read_page1

    Return page1 HTML with square(4) result
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/page1",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_read_page2(client: TestClient):
    """Test case for read_page2

    Return page2 HTML with cube(2) result
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/page2",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_read_page3(client: TestClient):
    """Test case for read_page3

    Return page3 HTML with combined result of add_five, cube, and square
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/page3",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_read_root(client: TestClient):
    """Test case for read_root

    Return the index HTML page
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

