from logging import Logger, getLogger
from typing import Any
from json.decoder import JSONDecodeError

from fastapi import APIRouter, Request, Response
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from ecs_py import Base, Source, Http, HttpRequest, Client, Server, Destination
from ecs_tools_py import entries_from_forwarded_header_value, entry_from_host_header_value, url_entry_from_string

LOG: Logger = getLogger(__name__)

ROUTER = APIRouter()


def _get_log_dict_base(request: Request) -> dict[str, Any]:
    """
    Build a dictionary with information about the context to be included in each log message.

    :param request: An incoming HTTP request from which to extract information.
    :return: A dictionary with information about the context.
    """

    source_entry: Source | None = (
        Source(address=request_client.host, port=request_client.port)
        if (request_client := request.client) else None
    )

    base = Base(
        source=source_entry,
        url=url_entry_from_string(url=str(request.url)),
        http=Http(
            request=HttpRequest(
                method=request.method,
                referrer=request.headers.get('Referer')
            )
        )
    )

    if host_value := request.headers.get('Host'):
        base.destination = entry_from_host_header_value(
            host_header_value=host_value,
            entry_type=Destination
        )

    if forwarded_value := request.headers.get('Forwarded'):
        client_entry: Client | None
        server_entry: Server | None
        client_entry, server_entry = entries_from_forwarded_header_value(
            forwarded_header_value=forwarded_value,
            entry_type_for=Client,
            entry_type_host=Server
        )

        base.client = client_entry
        base.server = server_entry

    return dict(base) | dict(_ecs_logger_handler_options=dict(merge_extra=True))


@ROUTER.post('/error')
async def error(request: Request):
    """
    Handle a error report request.

    :param request: An error report HTTP request.
    :return: An HTTP 204 response.
    """

    log_dict_base: dict[str, Any] = {}

    try:
        log_dict_base = _get_log_dict_base(request=request)
    except:
        LOG.exception(
            msg='An unexpected error occurred when attempting to build the log base dict.'
        )

    try:
        error_report = await request.json()

        LOG.info(
            msg='An error report was received.',
            extra=dict(web_log_collector=dict(error_report=error_report)) | log_dict_base
        )
    except JSONDecodeError as e:
        LOG.warning(msg='An error report could not be decoded.', exc_info=e, extra=log_dict_base)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
    except:
        LOG.exception(
            msg='An unexpected error occurred when attempting to obtain an error report.',
            extra=log_dict_base
        )

    return Response(status_code=HTTP_204_NO_CONTENT)


@ROUTER.post('/csp')
async def csp(request: Request):
    """
    Handle a CSP report request.

    :param request: A CSP report HTTP request.
    :return: An HTTP 204 response.
    """

    log_dict_base: dict[str, Any] = {}

    try:
        log_dict_base = _get_log_dict_base(request=request)
    except:
        LOG.exception(
            msg='An unexpected error occurred when attempting to build the log base dict.'
        )

    try:
        csp_report = await request.json()

        if not (isinstance(csp_report, dict) and 'csp-report' in csp_report):
            LOG.warning(msg='A malformed CSP report was received.', extra=log_dict_base)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
        else:
            LOG.info(
                msg='A CSP report was received.',
                extra=dict(web_log_collector=dict(csp_report=csp_report.pop('csp-report'))) | log_dict_base
            )
    except JSONDecodeError as e:
        LOG.warning(msg='A CSP report could not be decoded.', exc_info=e, extra=log_dict_base)
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
    except:
        LOG.exception(msg='An unexpected error occurred when attempting to obtain a CSP report.', extra=log_dict_base)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occurred while parsing the data.')

    return Response(status_code=HTTP_204_NO_CONTENT)
