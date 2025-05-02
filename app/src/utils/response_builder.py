BASE_RESPONSE = {"message": None, "data": None}


class ResponseBuilder:
    def __init__(self):
        self.__response = {"message": None, "data": None, "status": True, "code": 200}

    @property
    def message(self):
        return self.__response["message"]

    @message.setter
    def message(self, value):
        if self.status is True and value == "":
            self.__response["message"] = "Process is success"
        self.__response["message"] = value

    @property
    def data(self):
        return self.__response["data"]

    @data.setter
    def data(self, value):
        self.__response["data"] = value

    @property
    def status(self):
        return self.__response["status"]

    @status.setter
    def status(self, value):
        if isinstance(value, bool):
            self.__response["status"] = value
        else:
            raise ValueError("invalid value")

    @property
    def code(self):
        return self.__response["code"]

    @code.setter
    def code(self, value):
        if isinstance(value, int):
            self.__response["code"] = value
        else:
            raise ValueError("invalid value")

    @property
    def errors(self):
        return self.__response["errors"]

    @errors.setter
    def errors(self, value):
        self.__response["errors"] = value

    def add_attribute(self, attribute):
        self.__response[attribute] = None

    def update_value(self, attribute, value):
        if attribute not in self.__response.keys():
            raise KeyError("attribute not found")
        else:
            self.__response[attribute] = value
        return self

    def to_dict(self):
        return self.__response


class ResponseListBuilder:
    def __init__(self):
        self.__response = {"message": None, "data": None, "status": True, "code": 200, "record_count": 0}

    @property
    def message(self):
        return self.__response["message"]

    @message.setter
    def message(self, value):
        if self.status is True and value == "":
            self.__response["message"] = "Process is success"
        self.__response["message"] = value

    @property
    def data(self):
        return self.__response["data"]

    @data.setter
    def data(self, value):
        self.__response["data"] = value

    @property
    def status(self):
        return self.__response["status"]

    @status.setter
    def status(self, value):
        if isinstance(value, bool):
            self.__response["status"] = value
        else:
            raise ValueError("invalid value")

    @property
    def code(self):
        return self.__response["code"]

    @code.setter
    def code(self, value):
        if isinstance(value, int):
            self.__response["code"] = value
        else:
            raise ValueError("invalid value")

    def add_attribute(self, attribute):
        self.__response[attribute] = None

    def update_value(self, attribute, value):
        if attribute not in self.__response.keys():
            raise KeyError("attribute not found")
        else:
            self.__response[attribute] = value
        return self

    def to_dict(self):
        return self.__response

    @property
    def record_count(self):
        return self.__response["record_count"]

    @record_count.setter
    def record_count(self, value):
        if isinstance(value, int):
            self.__response["record_count"] = value
        else:
            raise ValueError("invalid value")

    def to_dict(self):
        return self.__response
