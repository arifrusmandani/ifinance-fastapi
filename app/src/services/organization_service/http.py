from app.src.utils.httpx_client import httpx_context
from app.src.core.config import ORGANIZATION_SERVICE_URL as host, APP_CODE


class OrganizationServices:
    endpoints = {
        "login": host + "/user/token",
        "login_by_ad": host + "/user/loginbyad",
        "logout": host + "/user/logout",
        "authorization_url": host + "/user/me",
        "employee_authorization": host + "/user/me/permissions",
        "employee_detail": host + "/employee/detail/{id}",
        "employee_position": host + "/employee/{id}/position",
        "position_detail": host + "/position/{id}",
        "has_permission": host + "/user/me/has-permission",
        "branch": host + "/branch/?",
        "refresh_token": host + "/user/refresh-token"
    }
    is_success = lambda x: 200 <= x.status_code <= 299
    get_response_data = lambda x: x.json().get("data") if x.json().get("data") else x.json()

    @classmethod
    async def auth_login(cls, username, password):
        """
        Asynchronously logs in a user with the given username and password.
        """
        url = cls.endpoints["login"]
        json = {
            "username": username,
            "password": password,
            "app_code": APP_CODE
        }
        async with httpx_context() as client:
            response = await client.post(url=url, data=json)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    response.json(),
                )
        return False, {}

    @classmethod
    async def auth_login_by_ad(cls, username, password, ip_source: str):
        """
        Asynchronously logs in a user with the given username and password.
        """
        url = cls.endpoints["login_by_ad"]
        json = {
            "username": username,
            "password": password,
            "app_code": APP_CODE,
            "ip_source": ip_source
        }
        async with httpx_context() as client:
            response = await client.post(url=url, data=json)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    response.json(),
                )
        return False, {}

    @classmethod
    async def logout(cls, token):
        """
        Logout a user with the given token.
        """
        url = cls.endpoints["logout"]

        async with httpx_context() as client:
            client.headers["Authorization"] = f"Bearer {token}"
            response = await client.post(url=url)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    response.json(),
                )
        return False, {}

    @classmethod
    async def check_authorization(cls, token):
        url = cls.endpoints["authorization_url"]
        async with httpx_context() as client:
            client.headers["Authorization"] = f"Bearer {token}"
            response = await client.get(url=url)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    cls.get_response_data(response),
                )
        return False, {}

    @classmethod
    async def get_employee_position(cls, id):
        url = cls.endpoints["employee_position"].format(id=id)
        async with httpx_context() as client:
            response = await client.get(url=url)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    cls.get_response_data(response),
                )
        return False, {}

    @classmethod
    async def get_employee_detail(cls, user_token, id):
        url = cls.endpoints["employee_detail"].format(id=id)
        async with httpx_context() as client:
            client.headers["Authorization"] = f"Bearer {user_token}"
            response = await client.get(url=url)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    cls.get_response_data(response),
                )
        return False, {}

    @classmethod
    async def get_position(cls, user_token, id):
        url = cls.endpoints["position_detail"].format(id=id)
        async with httpx_context() as client:
            client.headers["Authorization"] = f"Bearer {user_token}"
            response = await client.get(url=url)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    cls.get_response_data(response),
                )
        return False, {}

    @classmethod
    async def has_permission(cls, token, permission_page):
        url = cls.endpoints["has_permission"]
        json = {
            "permission_page": permission_page
        }
        async with httpx_context() as client:
            client.headers["Authorization"] = f"Bearer {token}"
            response = await client.post(url=url, json=json)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    response.json().get("data"),
                )
        return False, {}

    @classmethod
    async def employee_authorization(cls, token):
        url = cls.endpoints["employee_authorization"]
        params = {
            'app_code': APP_CODE
        }
        async with httpx_context() as client:
            client.headers["Authorization"] = f'Bearer {token}'
            response = await client.get(url=url, params=params)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    cls.get_response_data(response),
                )
        return False, {}

    @classmethod
    async def get_branch(cls, token, region_name, city):
        parameter=[]
        if city:
            parameter.append(f"keyword={city}")

        if region_name:
            parameter.append(f"region_name={region_name}")

        url = cls.endpoints["branch"] + "&".join(parameter)
        async with httpx_context() as client:
            client.headers["Authorization"] = f'Bearer {token}'
            response = await client.get(url=url)
            response_json= cls.get_response_data(response)
            if response.status_code != 500:
                # validation below is required as the API response does not consistent
                # if records found response JSON contains list of data,
                # otherwise: {'message': 'success', 'data': [], 'status': True, 'record_count': 0}
                if "record_count" in response_json and response_json.get("record_count") == 0:
                    return False, {}

                for item in response_json:
                    if item.get("name").lower() == city.lower():
                        return True, {"region_id":item.get("region_id"),"branch_id": item.get("id")}
        return False, {}

    @classmethod
    async def refresh_token(cls, token):
        url = cls.endpoints["refresh_token"]
        async with httpx_context() as client:
            client.headers["Authorization"] = f'Bearer {token}'
            response = await client.post(url=url)
            if response.status_code != 500:
                return (
                    cls.is_success(response),
                    {"token": response.json().get("token")},
                )
        return False, {}
