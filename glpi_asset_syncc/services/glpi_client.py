"""
glpi_client.py
==============
Stateful REST API client for GLPI.

GLPI API reference: http://glpi-project.org/DOC/en/modules/tools/apiv1.html

Authentication flow
-------------------
1. App-Token  — always required; identifies the calling application.
2. User-Token — preferred; no password sent over the wire.
   Fallback: HTTP Basic (username + password) when user_token is absent.

Session flow
------------
    client = GLPIClient(base_url, app_token='...', user_token='...')
    client.init_session()
    try:
        client.change_active_entity(entities_id=3, is_recursive=1)  # optional
        for row in client.iter_all_computers():
            process(row)
    finally:
        client.kill_session()

Key endpoints used
------------------
GET  /initSession               Open session → session_token
GET  /killSession               Close session
POST /changeActiveEntities      Switch to a specific GLPI entity
GET  /listSearchOptions/Computer  Discover field IDs (call once per env)
GET  /Computer/                 Collection read with range parameter
GET  /search/Computer           Criteria + forcedisplay search
"""

import logging
import requests
from requests.auth import HTTPBasicAuth

_logger = logging.getLogger(__name__)

GLPI_MAX_RANGE = 200   # hard limit enforced by GLPI


class GLPIApiError(Exception):
    """Raised for HTTP errors or GLPI-level error payloads."""


class GLPIClient:
    """Session-based GLPI REST API client."""

    def __init__(
        self,
        base_url,
        app_token=None,
        user_token=None,
        username=None,
        password=None,
        verify_ssl=True,
        timeout=60,
    ):
        self.api_url = base_url.rstrip('/') + '/apirest.php'
        self.app_token = app_token
        self.user_token = user_token
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session_token = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self):
        """Build request headers. session_token is added after init_session."""
        h = {'Content-Type': 'application/json'}
        if self.app_token:
            h['App-Token'] = self.app_token
        if self.session_token:
            h['Session-Token'] = self.session_token
        return h

    def _check(self, response):
        """
        Validate an HTTP response and return parsed JSON.
        Raises GLPIApiError on:
          - HTTP 4xx / 5xx
          - GLPI error payload: ["ERROR_CODE", "message"]
        """
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            try:
                body = response.json()
            except Exception:
                body = response.text
            raise GLPIApiError(f'HTTP {response.status_code}: {body}') from exc

        try:
            data = response.json()
        except Exception:
            return {}

        # GLPI returns ["ERROR_CODE", "human message"] even on some 2xx responses
        if (
            isinstance(data, list)
            and len(data) == 2
            and isinstance(data[0], str)
            and data[0].startswith('ERROR')
        ):
            raise GLPIApiError(f'GLPI error: {data[0]} – {data[1]}')

        return data

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def init_session(self):
        """
        Open a GLPI API session.

        Sets self.session_token which is automatically included in all
        subsequent request headers via _headers().

        Raises GLPIApiError if credentials are missing or initSession fails.
        """
        url = f'{self.api_url}/initSession'
        headers = self._headers()

        if self.user_token:
            # Preferred: API token auth — no password sent over the wire
            headers['Authorization'] = f'user_token {self.user_token}'
            r = requests.get(url, headers=headers,
                             verify=self.verify_ssl, timeout=self.timeout)
        elif self.username and self.password:
            # Fallback: HTTP Basic auth
            r = requests.get(url, headers=headers,
                             auth=HTTPBasicAuth(self.username, self.password),
                             verify=self.verify_ssl, timeout=self.timeout)
        else:
            raise GLPIApiError(
                'No credentials provided. Supply user_token or username+password.')

        data = self._check(r)
        self.session_token = data.get('session_token')
        if not self.session_token:
            raise GLPIApiError('initSession returned no session_token.')
        _logger.debug('GLPI session opened (token prefix: %s…)', self.session_token[:8])
        return data

    def kill_session(self):
        """
        Close the active GLPI session. Safe to call even if no session is open.
        Errors are logged and suppressed so finally-blocks always complete.
        """
        if not self.session_token:
            return {}
        try:
            r = requests.get(
                f'{self.api_url}/killSession',
                headers=self._headers(),
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            data = self._check(r)
        except Exception as exc:
            _logger.warning('GLPI killSession failed (suppressed): %s', exc)
            data = {}
        finally:
            self.session_token = None
        _logger.debug('GLPI session closed.')
        return data

    # ------------------------------------------------------------------
    # Entity management
    # ------------------------------------------------------------------

    def change_active_entity(self, entities_id, is_recursive=0):
        """
        Switch the session context to a specific GLPI entity.

        Args:
            entities_id: integer GLPI entity ID (0 = root)
            is_recursive: 1 to include child entities, 0 for exact entity only
        """
        payload = {'entities_id': entities_id, 'is_recursive': is_recursive}
        r = requests.post(
            f'{self.api_url}/changeActiveEntities',
            headers=self._headers(),
            json=payload,
            verify=self.verify_ssl,
            timeout=self.timeout,
        )
        return self._check(r)

    # ------------------------------------------------------------------
    # Field discovery
    # ------------------------------------------------------------------

    def list_search_options(self, itemtype='Computer'):
        """
        Return the complete field-ID map for an itemtype.

        Call once per environment to discover the integer field IDs for
        fields like UUID, Inventory Number, Serial Number, Manufacturer.
        Use those IDs in forcedisplay when calling search_computers().

        Example response structure:
            {
              "1":  {"name": "Name",             "field": "name",        ...},
              "2":  {"name": "ID",               "field": "id",          ...},
              "65": {"name": "UUID",             "field": "uuid",        ...},
              "160":{"name": "Inventory number", "field": "otherserial", ...},
              ...
            }
        """
        r = requests.get(
            f'{self.api_url}/listSearchOptions/{itemtype}',
            headers=self._headers(),
            verify=self.verify_ssl,
            timeout=self.timeout,
        )
        return self._check(r)

    # ------------------------------------------------------------------
    # Collection API — preferred for a full sync
    # ------------------------------------------------------------------

    def get_computers(self, start=0, end=199):
        """
        Fetch a single page of Computer records using the collection endpoint.

        GET /Computer/?range=<start>-<end>

        Returns a list of dicts. Returns [] when the range exceeds the total
        (GLPI signals this with HTTP 400 ERROR_RANGE_EXCEED_TOTAL).

        Each dict contains all default fields GLPI returns for a Computer,
        typically including: id, name, uuid, serial, otherserial,
        manufacturers_id, entities_id, is_deleted, is_template, ...
        """
        params = {'range': f'{start}-{end}'}
        r = requests.get(
            f'{self.api_url}/Computer/',
            headers=self._headers(),
            params=params,
            verify=self.verify_ssl,
            timeout=self.timeout,
        )

        # HTTP 400 with ERROR_RANGE_EXCEED_TOTAL = pagination is complete
        if r.status_code == 400:
            try:
                body = r.json()
            except Exception:
                body = []
            if isinstance(body, list) and body and body[0] == 'ERROR_RANGE_EXCEED_TOTAL':
                return []
            raise GLPIApiError(f'HTTP 400: {body}')

        data = self._check(r)
        if isinstance(data, list):
            return data
        # Some GLPI versions wrap results in {"data": [...]}
        return data.get('data', []) if isinstance(data, dict) else []

    # ------------------------------------------------------------------
    # Search API — use for filtered or field-specific results
    # ------------------------------------------------------------------

    def search_computers(self, criteria=None, forcedisplay=None, start=0):
        """
        Search Computer records using GLPI's search endpoint.

        GET /search/Computer?criteria[0][field]=...&forcedisplay[0]=...

        Args:
            criteria: list of dicts, each with keys:
                        link        — "AND" | "OR" (default "AND")
                        field       — integer field ID from list_search_options
                        searchtype  — "contains" | "equals" | "notequals" | ...
                        value       — search value string
            forcedisplay: list of integer field IDs to include in results.
                          Without this, GLPI returns its default display columns.
            start: pagination offset (no range header; GLPI uses fixed page size)

        Returns:
            dict with keys: totalcount, count, data (list of dicts keyed by field ID)

        Example — fetch UUID and inventory number for all computers:
            opts = client.list_search_options()
            # Inspect opts to find the right IDs for your GLPI version:
            #   "65"  → UUID
            #   "160" → Inventory number (otherserial)
            #   "11"  → Serial number
            #   "23"  → Manufacturer
            results = client.search_computers(forcedisplay=[2, 1, 65, 160, 11, 23])
            for row in results.get('data', []):
                uuid = row.get('65')
                inventory = row.get('160')
        """
        params = {'start': start}

        if criteria:
            for i, c in enumerate(criteria):
                params[f'criteria[{i}][link]'] = c.get('link', 'AND')
                params[f'criteria[{i}][field]'] = c['field']
                params[f'criteria[{i}][searchtype]'] = c['searchtype']
                params[f'criteria[{i}][value]'] = c['value']

        if forcedisplay:
            for i, fid in enumerate(forcedisplay):
                params[f'forcedisplay[{i}]'] = fid

        r = requests.get(
            f'{self.api_url}/search/Computer',
            headers=self._headers(),
            params=params,
            verify=self.verify_ssl,
            timeout=self.timeout,
        )
        return self._check(r)

    # ------------------------------------------------------------------
    # Convenience: paginated generator over all computers
    # ------------------------------------------------------------------

    def iter_all_computers(self, batch_size=GLPI_MAX_RANGE):
        """
        Generator — yields every Computer record one dict at a time.
        Handles pagination transparently using the collection API.

        Usage:
            for computer in client.iter_all_computers():
                process(computer)
        """
        start = 0
        while True:
            batch = self.get_computers(start=start, end=start + batch_size - 1)
            if not batch:
                break
            yield from batch
            if len(batch) < batch_size:
                break
            start += batch_size

    # ------------------------------------------------------------------
    # Connection test helper
    # ------------------------------------------------------------------

    def test_connection(self):
        """
        Open a session, call getMyProfiles to verify credentials, then
        close the session. Returns the profile payload on success.
        Raises GLPIApiError on any failure.
        """
        self.init_session()
        try:
            r = requests.get(
                f'{self.api_url}/getMyProfiles',
                headers=self._headers(),
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            return self._check(r)
        finally:
            self.kill_session()
