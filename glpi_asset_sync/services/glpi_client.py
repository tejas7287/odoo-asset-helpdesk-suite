"""
services/glpi_client.py
=======================
Stateful, session-based wrapper around the GLPI REST API v1.

GLPI API flow
-------------
    client = GLPIClient(base_url='https://glpi.example.com',
                        app_token='<APP_TOKEN>',
                        user_token='<USER_TOKEN>')
    client.init_session()
    try:
        client.change_active_entity(entities_id=3, is_recursive=1)  # optional
        for computer in client.iter_all_computers():
            process(computer)
    finally:
        client.kill_session()

Authentication
--------------
Every request must carry:
    App-Token: <application token>        — registered in GLPI > Setup > API

Session auth (one of):
    Authorization: user_token <token>     — preferred, from GLPI user profile
    HTTPBasicAuth(username, password)     — fallback when user_token is blank

Reference
---------
https://glpi-project.org/DOC/en/modules/tools/apiv1.html
"""

import logging
import requests
from requests.auth import HTTPBasicAuth

_logger = logging.getLogger(__name__)

# GLPI hard limit: maximum records per collection / search request.
GLPI_MAX_RANGE = 200


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GLPIApiError(Exception):
    """Raised for HTTP errors or GLPI-level error payloads (e.g. ERROR_*)."""


class GLPIAuthError(GLPIApiError):
    """Raised when no valid credentials are provided."""


class GLPISessionError(GLPIApiError):
    """Raised when a session cannot be established or has expired."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class GLPIClient:
    """
    Session-based GLPI REST API client.

    Parameters
    ----------
    base_url : str
        Root URL of the GLPI server, e.g. ``https://glpi.example.com``.
        Do not include ``/apirest.php``.
    app_token : str
        GLPI application token (required). Created in
        GLPI > Setup > General > API > Add application token.
    user_token : str, optional
        GLPI user API token (preferred auth method). Generated in
        GLPI user profile > Remote access keys.
    username : str, optional
        GLPI username. Used only when ``user_token`` is blank.
    password : str, optional
        GLPI password. Used only when ``user_token`` is blank.
    verify_ssl : bool
        Verify TLS certificates. Set ``False`` only for self-signed certs
        in staging environments.
    timeout : int
        Request timeout in seconds (default 60).
    """

    def __init__(
        self,
        base_url: str,
        app_token: str = None,
        user_token: str = None,
        username: str = None,
        password: str = None,
        verify_ssl: bool = True,
        timeout: int = 60,
    ):
        if not base_url:
            raise GLPIAuthError('base_url is required.')
        self.api_url = base_url.rstrip('/') + '/apirest.php'
        self.app_token = app_token
        self.user_token = user_token
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session_token: str | None = None

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _headers(self) -> dict:
        """Build request headers. App-Token and Session-Token are always included."""
        headers = {'Content-Type': 'application/json'}
        if self.app_token:
            headers['App-Token'] = self.app_token
        if self.session_token:
            headers['Session-Token'] = self.session_token
        return headers

    def _check(self, response: requests.Response):
        """
        Validate an API response.

        Raises
        ------
        GLPIApiError
            On HTTP 4xx/5xx or a GLPI-level error payload such as
            ``["ERROR_GLPI_LOGIN", "Incorrect username or password."]``.
        """
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            try:
                body = response.json()
            except Exception:
                body = response.text
            raise GLPIApiError(
                f'HTTP {response.status_code} from {response.url}: {body}'
            ) from exc

        # Parse body
        try:
            data = response.json()
        except Exception:
            return {}

        # GLPI wraps some errors as ["ERROR_CODE", "human message"] even on 200
        if (
            isinstance(data, list)
            and len(data) == 2
            and isinstance(data[0], str)
            and data[0].startswith('ERROR')
        ):
            raise GLPIApiError(f'GLPI error: {data[0]} — {data[1]}')

        return data

    # -----------------------------------------------------------------------
    # Session management
    # -----------------------------------------------------------------------

    def init_session(self) -> dict:
        """
        Open a GLPI API session.

        Uses ``user_token`` if provided, otherwise falls back to HTTP Basic
        with ``username`` / ``password``. Stores the returned session_token
        for all subsequent requests.

        Returns
        -------
        dict
            Raw GLPI initSession response (contains ``session_token``).

        Raises
        ------
        GLPIAuthError
            If no credentials are configured.
        GLPISessionError
            If the server does not return a session_token.
        """
        url = f'{self.api_url}/initSession'
        headers = self._headers()

        if self.user_token:
            headers['Authorization'] = f'user_token {self.user_token}'
            response = requests.get(
                url, headers=headers,
                verify=self.verify_ssl, timeout=self.timeout,
            )
        elif self.username and self.password:
            response = requests.get(
                url, headers=headers,
                auth=HTTPBasicAuth(self.username, self.password),
                verify=self.verify_ssl, timeout=self.timeout,
            )
        else:
            raise GLPIAuthError(
                'No credentials configured. Provide user_token or username + password.'
            )

        data = self._check(response)
        self.session_token = data.get('session_token')
        if not self.session_token:
            raise GLPISessionError(
                'initSession succeeded but server returned no session_token.'
            )
        _logger.info('GLPI session opened (token prefix: %s…)', self.session_token[:8])
        return data

    def kill_session(self) -> dict:
        """
        Close the current GLPI API session.

        Safe to call even when no session is active (returns ``{}``).
        Failure to close is logged as a warning but never raises.
        """
        if not self.session_token:
            return {}
        try:
            response = requests.get(
                f'{self.api_url}/killSession',
                headers=self._headers(),
                verify=self.verify_ssl, timeout=self.timeout,
            )
            data = self._check(response)
        except Exception as exc:
            _logger.warning('GLPI killSession failed (ignored): %s', exc)
            data = {}
        finally:
            self.session_token = None
        _logger.info('GLPI session closed.')
        return data

    # -----------------------------------------------------------------------
    # Entity management
    # -----------------------------------------------------------------------

    def change_active_entity(self, entities_id: int, is_recursive: int = 0) -> dict:
        """
        Switch the session scope to a specific GLPI entity.

        Parameters
        ----------
        entities_id : int
            Target entity ID. Use ``0`` for the root entity.
        is_recursive : int
            Pass ``1`` to include all child entities (sub-entities).

        Returns
        -------
        dict
            GLPI API response.
        """
        payload = {'entities_id': entities_id, 'is_recursive': is_recursive}
        response = requests.post(
            f'{self.api_url}/changeActiveEntities',
            headers=self._headers(), json=payload,
            verify=self.verify_ssl, timeout=self.timeout,
        )
        result = self._check(response)
        _logger.debug(
            'GLPI entity switched to %s (recursive=%s)', entities_id, is_recursive
        )
        return result

    # -----------------------------------------------------------------------
    # Field discovery
    # -----------------------------------------------------------------------

    def list_search_options(self, itemtype: str = 'Computer') -> dict:
        """
        Return the complete field-ID map for the given itemtype.

        Call this once per environment to discover the numeric field IDs for
        fields such as UUID and Inventory number, which differ between GLPI
        versions. Use those IDs in ``forcedisplay`` when calling
        ``search_computers``.

        Parameters
        ----------
        itemtype : str
            GLPI itemtype, e.g. ``'Computer'``, ``'NetworkEquipment'``.

        Returns
        -------
        dict
            ``{field_id: {name, table, field, datatype, ...}, ...}``

        Example
        -------
        ::

            opts = client.list_search_options('Computer')
            # Find UUID field:
            uuid_field = next(
                (fid for fid, meta in opts.items()
                 if 'uuid' in meta.get('name', '').lower()), None
            )
        """
        response = requests.get(
            f'{self.api_url}/listSearchOptions/{itemtype}',
            headers=self._headers(),
            verify=self.verify_ssl, timeout=self.timeout,
        )
        return self._check(response)

    # -----------------------------------------------------------------------
    # Collection API  — preferred for full sync
    # -----------------------------------------------------------------------

    def get_computers(self, start: int = 0, end: int = None) -> list:
        """
        Retrieve a paginated batch of Computer records from the collection API.

        GLPI collection endpoint: ``GET /apirest.php/Computer/``

        Parameters
        ----------
        start : int
            Zero-based first record index.
        end : int, optional
            Last record index (inclusive). Defaults to ``start + 199``.

        Returns
        -------
        list[dict]
            List of Computer records. Returns ``[]`` when the range exceeds
            the total record count (GLPI ``ERROR_RANGE_EXCEED_TOTAL``).

        Notes
        -----
        GLPI returns HTTP 206 when more records exist beyond the requested
        range, and HTTP 200 on the final page. Both are treated as success.
        The total count is available in the ``Content-Range`` response header
        as ``0-199/1543``.
        """
        if end is None:
            end = start + GLPI_MAX_RANGE - 1

        params = {'range': f'{start}-{end}'}
        response = requests.get(
            f'{self.api_url}/Computer/',
            headers=self._headers(), params=params,
            verify=self.verify_ssl, timeout=self.timeout,
        )

        # GLPI 400 + ERROR_RANGE_EXCEED_TOTAL = we have fetched all records
        if response.status_code == 400:
            try:
                body = response.json()
            except Exception:
                body = []
            if isinstance(body, list) and body and body[0] == 'ERROR_RANGE_EXCEED_TOTAL':
                _logger.debug('GLPI: all records fetched (range exceeded total).')
                return []
            raise GLPIApiError(f'HTTP 400: {body}')

        data = self._check(response)

        total = response.headers.get('Content-Range', '')
        _logger.debug('GLPI Computer batch %s-%s  Content-Range: %s', start, end, total)

        if isinstance(data, list):
            return data
        # Some GLPI versions wrap results in {'data': [...]}
        if isinstance(data, dict):
            return data.get('data', [])
        return []

    # -----------------------------------------------------------------------
    # Search API  — use for filtered or field-specific results
    # -----------------------------------------------------------------------

    def search_computers(
        self,
        criteria: list = None,
        forcedisplay: list = None,
        start: int = 0,
    ) -> dict:
        """
        Search Computer records via ``GET /apirest.php/search/Computer``.

        Use this instead of ``get_computers`` when you need:

        * Specific fields via ``forcedisplay`` (field IDs from
          ``list_search_options``).
        * Filtered results via ``criteria``.
        * Incremental sync (filter by last-modified date field).

        Parameters
        ----------
        criteria : list[dict], optional
            List of search criterion dicts, each with keys:
            ``link`` (AND/OR), ``field`` (int ID), ``searchtype``
            (``contains``, ``equals``, ``greater``, etc.), ``value``.

            Example::

                criteria = [
                    {'link': 'AND', 'field': 1,
                     'searchtype': 'contains', 'value': 'DESKTOP'},
                ]

        forcedisplay : list[int], optional
            Field IDs to include in the response. Obtain IDs from
            ``list_search_options``. Common IDs (may vary by GLPI version):

            * 2  — ID
            * 1  — Name
            * 65 — UUID
            * 160 — Inventory number (otherserial)
            * 5  — Serial number

        start : int
            Offset for pagination (default 0).

        Returns
        -------
        dict
            Raw GLPI search response containing:
            ``totalcount``, ``count``, ``data`` (list of row dicts).

        Example
        -------
        ::

            # Discover field IDs first
            opts = client.list_search_options('Computer')

            # Then fetch with explicit fields
            result = client.search_computers(
                forcedisplay=[2, 1, 65, 160, 5],
            )
            for row in result.get('data', []):
                glpi_id   = row.get('2')
                name      = row.get('1')
                uuid      = row.get('65')
                inv_no    = row.get('160')
        """
        params: dict = {'itemtype': 'Computer', 'start': start}

        if criteria:
            for idx, c in enumerate(criteria):
                params[f'criteria[{idx}][link]'] = c.get('link', 'AND')
                params[f'criteria[{idx}][field]'] = c['field']
                params[f'criteria[{idx}][searchtype]'] = c['searchtype']
                params[f'criteria[{idx}][value]'] = c['value']

        if forcedisplay:
            for idx, field_id in enumerate(forcedisplay):
                params[f'forcedisplay[{idx}]'] = field_id

        response = requests.get(
            f'{self.api_url}/search/Computer',
            headers=self._headers(), params=params,
            verify=self.verify_ssl, timeout=self.timeout,
        )
        data = self._check(response)
        _logger.debug(
            'GLPI search/Computer start=%s  total=%s  count=%s',
            start,
            data.get('totalcount', '?'),
            data.get('count', '?'),
        )
        return data

    # -----------------------------------------------------------------------
    # Generic item fetch
    # -----------------------------------------------------------------------

    def get_item(self, itemtype: str, item_id: int) -> dict:
        """
        Fetch a single GLPI item by its ID.

        Parameters
        ----------
        itemtype : str
            GLPI itemtype, e.g. ``'Computer'``.
        item_id : int
            GLPI primary key.

        Returns
        -------
        dict
            Full item payload.
        """
        response = requests.get(
            f'{self.api_url}/{itemtype}/{item_id}',
            headers=self._headers(),
            verify=self.verify_ssl, timeout=self.timeout,
        )
        return self._check(response)

    # -----------------------------------------------------------------------
    # Convenience: paginated generator over all computers
    # -----------------------------------------------------------------------

    def iter_all_computers(self, batch_size: int = GLPI_MAX_RANGE):
        """
        Yield every Computer record one at a time, handling pagination.

        Uses the collection API (``get_computers``) internally.

        Parameters
        ----------
        batch_size : int
            Records per API request. Maximum is ``200`` (GLPI limit).

        Yields
        ------
        dict
            Individual Computer record dict.

        Example
        -------
        ::

            client.init_session()
            try:
                for computer in client.iter_all_computers():
                    print(computer['name'], computer.get('uuid'))
            finally:
                client.kill_session()
        """
        batch_size = min(batch_size, GLPI_MAX_RANGE)
        start = 0
        fetched = 0
        while True:
            batch = self.get_computers(start=start, end=start + batch_size - 1)
            if not batch:
                break
            yield from batch
            fetched += len(batch)
            _logger.debug('GLPI iter_all_computers: fetched %s so far', fetched)
            if len(batch) < batch_size:
                break
            start += batch_size
        _logger.info('GLPI iter_all_computers: total yielded %s records', fetched)