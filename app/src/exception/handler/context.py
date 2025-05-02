import traceback
from contextlib import contextmanager

import psycopg2
import logging
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError

from app.src.exception.auth import UnauthorizedError
from app.src.exception.custom import AttendanceError
from app.src.utils.response_builder import ResponseBuilder, ResponseListBuilder


@contextmanager
def api_exception_handler(res, response_type=None):
    response = ResponseListBuilder() if response_type == 'list' else ResponseBuilder()
    try:
        yield response

    except psycopg2.Error as error:
        res.status_code = status.HTTP_400_BAD_REQUEST
        response.status = False
        response.code = res.status_code

    except ValueError as error:
        res.status_code = status.HTTP_400_BAD_REQUEST
        response.status = False
        response.code = res.status_code
        response.message = str(error)

    except IntegrityError as error:
        logging.error("IntegrityError: %s", error)
        try:
            message = error.orig.diag.message_detail
        except:
            message = str(error.__dict__['orig'])
        res.status_code = status.HTTP_400_BAD_REQUEST
        response.status = False
        response.code = res.status_code
        response.message = message

    except FileNotFoundError as error:
        res.status_code = status.HTTP_404_NOT_FOUND
        response.status = False
        response.code = res.status_code
        response.message = str(error) if str(error) else "Data tidak ditemukan"

    except UnauthorizedError as error:
        res.status_code = status.HTTP_401_UNAUTHORIZED
        response.status = False
        response.code = res.status_code
        response.message = str(error)

    except AttendanceError as error:
        res.status_code = status.HTTP_400_BAD_REQUEST
        response.status = False
        response.code = res.status_code
        response.message = error.message
        response.data = error.data

    # except sqlalchemy.exc.IntegrityError as error:
    #     errormessage = ""
    #     if error.orig.pgcode == "23503":
    #         errormessage = "tidak dapat menghapus data, karena data masih digunakan"
    #     elif error.orig.pgcode == "23505":
    #         errormessage = "applicaton sudah ada, gunakan name yang berbeda"
    #
    #     res.status_code = status.HTTP_409_CONFLICT
    #     response.status = False
    #     response.message = str(errormessage)

    except HTTPException as error:
        logging.warning(traceback.format_exc())
        res.status_code = error.status_code
        response.status = False
        response.code = res.status_code
        response.message = error.detail

    except Exception as error:
        traceback.print_exc()
        logging.warning(traceback.format_exc())
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.status = False
        response.code = res.status_code
        response.message = str(error)
